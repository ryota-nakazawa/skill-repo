#!/usr/bin/env python3
"""Build a weekly report from project-based daily task log markdown files."""

from __future__ import annotations

import argparse
from collections import defaultdict
import datetime as dt
import re
from pathlib import Path


LIST_ITEM_PATTERN = re.compile(r"^\s*-\s+(?P<body>.+?)\s*$")
ACTION_HINT_KEYWORDS = ("待ち", "確認", "レビュー", "議論", "対応", "予定", "来週")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build weekly report from daily logs.")
    parser.add_argument(
        "--daily-dir",
        default="./reports/daily/current",
        help="Directory where daily logs are stored (default: ./reports/daily/current)",
    )
    parser.add_argument(
        "--weekly-dir",
        default="./reports/weekly/current",
        help="Directory where weekly reports are written (default: ./reports/weekly/current)",
    )
    parser.add_argument("--week-start", help="Start date in YYYY-MM-DD")
    parser.add_argument("--week-end", help="End date in YYYY-MM-DD")
    parser.add_argument("--out", help="Output markdown file path")
    return parser.parse_args()


def week_range(today: dt.date) -> tuple[dt.date, dt.date]:
    start = today - dt.timedelta(days=today.weekday())
    end = start + dt.timedelta(days=6)
    return start, end


def resolve_period(raw_start: str | None, raw_end: str | None) -> tuple[dt.date, dt.date]:
    if raw_start and raw_end:
        start = dt.date.fromisoformat(raw_start)
        end = dt.date.fromisoformat(raw_end)
    elif raw_start and not raw_end:
        start = dt.date.fromisoformat(raw_start)
        end = start + dt.timedelta(days=6)
    elif raw_end and not raw_start:
        end = dt.date.fromisoformat(raw_end)
        start = end - dt.timedelta(days=6)
    else:
        start, end = week_range(dt.date.today())

    if start > end:
        raise ValueError("week-start must be earlier than or equal to week-end")
    return start, end


def daterange(start: dt.date, end: dt.date) -> list[dt.date]:
    days = (end - start).days
    return [start + dt.timedelta(days=offset) for offset in range(days + 1)]


def unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        key = item.strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        output.append(key)
    return output


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def shorten(text: str, limit: int = 90) -> str:
    clean = normalize_text(text)
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1] + "…"


def parse_table_cells(raw_line: str) -> list[str]:
    line = raw_line.strip()
    if not line.startswith("|"):
        return []
    if line.endswith("|"):
        content = line[1:-1]
    else:
        content = line[1:]
    cells = [cell.strip() for cell in content.split("|")]
    while len(cells) < 3:
        cells.append("")
    return cells


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    for cell in cells:
        compact = cell.replace("-", "").replace(":", "").replace(" ", "")
        if compact:
            return False
    return True


def parse_daily_file(path: Path, day: dt.date) -> dict[str, list[dict[str, str]] | list[str]]:
    entries: list[dict[str, str]] = []
    notes: list[str] = []

    section = ""
    prefix = f"[{day.isoformat()}]"

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            section = line[3:].strip()
            continue

        if section == "プロジェクト進捗":
            cells = parse_table_cells(raw_line)
            if len(cells) < 2:
                continue

            if cells[0] == "プロジェクト名" and cells[1] == "進捗記録" and cells[2] == "ひとこと":
                continue
            if is_separator_row(cells):
                continue

            project = cells[0]
            progress = cells[1]
            comment = cells[2]
            if not (project or progress or comment):
                continue

            entries.append(
                {
                    "date": day.isoformat(),
                    "project": project or "(未設定プロジェクト)",
                    "progress": progress or "記録なし",
                    "comment": comment or "-",
                }
            )
            continue

        listed = LIST_ITEM_PATTERN.match(raw_line)
        if not listed:
            continue

        body = listed.group("body").strip()
        if not body:
            continue

        item = f"{prefix} {body}"
        if section == "メモ":
            notes.append(item)

    return {
        "entries": entries,
        "notes": notes,
    }


def markdown_list(title: str, items: list[str]) -> list[str]:
    lines = [f"## {title}"]
    if items:
        for item in items:
            lines.append(f"- {item}")
    else:
        lines.append("- 該当なし")
    lines.append("")
    return lines


def summarize_project_entries(entries: list[dict[str, str]]) -> dict[str, list[str] | str]:
    progresses = unique_keep_order(
        [normalize_text(item["progress"]) for item in entries if item["progress"] != "記録なし"]
    )
    comments = unique_keep_order(
        [normalize_text(item["comment"]) for item in entries if item["comment"] != "-"]
    )

    if not progresses:
        summary = "今週の進捗記録はありません。"
    elif len(progresses) == 1:
        summary = f"今週は1件の進捗。{shorten(progresses[0], 110)}"
    else:
        summary = (
            f"今週は{len(progresses)}件の進捗を記録。"
            f"開始時点: {shorten(progresses[0], 55)} / 直近: {shorten(progresses[-1], 55)}"
        )

    highlights = [shorten(text, 110) for text in progresses[:3]]
    if not highlights:
        highlights = ["記録なし"]

    action_candidates: list[str] = []
    action_candidates.extend(comments)
    for text in reversed(progresses):
        if any(keyword in text for keyword in ACTION_HINT_KEYWORDS):
            action_candidates.append(text)

    actions = [shorten(text, 110) for text in unique_keep_order(action_candidates)[:3]]
    if not actions:
        actions = ["特記事項なし"]

    return {
        "summary": summary,
        "highlights": highlights,
        "actions": actions,
    }


def build_report(
    start: dt.date,
    end: dt.date,
    found_files: list[Path],
    missing_days: list[dt.date],
    project_entries: dict[str, list[dict[str, str]]],
    comments: list[str],
    total_records: int,
    notes: list[str],
) -> str:
    total_days = (end - start).days + 1
    recorded_days = len(found_files)
    missing_count = len(missing_days)

    lines: list[str] = []
    lines.append(f"# 週報 ({start.isoformat()} 〜 {end.isoformat()})")
    lines.append("")
    lines.append("## サマリー")
    lines.append(
        f"- 対象: {total_days}日 / 記録あり: {recorded_days}日 / 欠損: {missing_count}日"
    )
    lines.append(
        f"- プロジェクト数: {len(project_entries)}件 / 進捗記録: {total_records}件"
    )
    lines.append("")

    lines.append("## プロジェクト別報告（自動整理）")
    if project_entries:
        for project in sorted(project_entries.keys()):
            digest = summarize_project_entries(project_entries[project])
            lines.append(f"### {project}")
            lines.append(f"- 要約: {digest['summary']}")
            for idx, item in enumerate(digest["highlights"], start=1):
                lines.append(f"- 主要進捗{idx}: {item}")
            for idx, item in enumerate(digest["actions"], start=1):
                lines.append(f"- 次アクション/確認{idx}: {item}")
            lines.append("")
    else:
        lines.append("- 該当なし")
        lines.append("")

    lines.extend(markdown_list("補足メモ", notes))
    lines.extend(markdown_list("今週のひとこと一覧", comments))

    lines.append("## 収集元ファイル")
    if found_files:
        for file_path in found_files:
            lines.append(f"- {file_path.as_posix()}")
    else:
        lines.append("- 該当なし")
    lines.append("")

    lines.append("## 欠損日")
    if missing_days:
        for day in missing_days:
            lines.append(f"- {day.isoformat()}")
    else:
        lines.append("- なし")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    start, end = resolve_period(args.week_start, args.week_end)

    daily_dir = Path(args.daily_dir)
    weekly_dir = Path(args.weekly_dir)
    weekly_dir.mkdir(parents=True, exist_ok=True)

    project_entries: dict[str, list[dict[str, str]]] = defaultdict(list)
    comments: list[str] = []
    total_records = 0
    notes: list[str] = []
    found_files: list[Path] = []
    missing_days: list[dt.date] = []

    for day in daterange(start, end):
        daily_file = daily_dir / f"{day.isoformat()}.md"
        if not daily_file.exists():
            missing_days.append(day)
            continue

        found_files.append(daily_file)
        parsed = parse_daily_file(daily_file, day)
        entries = parsed["entries"]

        for entry in entries:
            project = entry["project"]
            comment_text = entry["comment"]
            project_entries[project].append(entry)
            if comment_text != "-":
                date_label = entry["date"]
                comments.append(f"[{project}][{date_label}] {comment_text}")

        total_records += len(entries)
        notes.extend(parsed["notes"])

    report = build_report(
        start=start,
        end=end,
        found_files=found_files,
        missing_days=missing_days,
        project_entries={k: v for k, v in project_entries.items()},
        comments=unique_keep_order(comments),
        total_records=total_records,
        notes=unique_keep_order(notes),
    )

    if args.out:
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = weekly_dir / f"week-report-{start.isoformat()}_to_{end.isoformat()}.md"

    output_path.write_text(report, encoding="utf-8")
    print(f"[ok] Wrote: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
