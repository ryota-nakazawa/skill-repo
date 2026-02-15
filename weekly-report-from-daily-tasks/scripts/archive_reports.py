#!/usr/bin/env python3
"""Move old daily/weekly report files from current directories to archive directories."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import re


DAILY_FILE_PATTERN = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})\.md$")
WEEKLY_FILE_PATTERN = re.compile(
    r"^week-report-(?P<start>\d{4}-\d{2}-\d{2})_to_(?P<end>\d{4}-\d{2}-\d{2})\.md$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive old report files.")
    parser.add_argument(
        "--daily-current-dir",
        default="./reports/daily/current",
        help="Current daily log directory (default: ./reports/daily/current)",
    )
    parser.add_argument(
        "--daily-archive-dir",
        default="./reports/archive/daily",
        help="Archive daily log directory (default: ./reports/archive/daily)",
    )
    parser.add_argument(
        "--weekly-current-dir",
        default="./reports/weekly/current",
        help="Current weekly report directory (default: ./reports/weekly/current)",
    )
    parser.add_argument(
        "--weekly-archive-dir",
        default="./reports/archive/weekly",
        help="Archive weekly report directory (default: ./reports/archive/weekly)",
    )
    parser.add_argument(
        "--keep-daily-days",
        type=int,
        default=21,
        help="Keep this many recent daily files in current (default: 21)",
    )
    parser.add_argument(
        "--keep-weekly-count",
        type=int,
        default=8,
        help="Keep this many recent weekly files in current (default: 8)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without changing files",
    )
    return parser.parse_args()


def move_file(src: Path, dst: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] move {src} -> {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    print(f"[ok] moved {src} -> {dst}")


def archive_daily_files(
    current_dir: Path,
    archive_dir: Path,
    keep_days: int,
    dry_run: bool,
) -> int:
    cutoff = dt.date.today() - dt.timedelta(days=keep_days - 1)
    moved = 0

    if not current_dir.exists():
        return 0

    for file_path in sorted(current_dir.glob("*.md")):
        match = DAILY_FILE_PATTERN.match(file_path.name)
        if not match:
            continue
        file_date = dt.date.fromisoformat(match.group("date"))
        if file_date >= cutoff:
            continue

        dst = archive_dir / str(file_date.year) / f"{file_date.month:02d}" / file_path.name
        move_file(file_path, dst, dry_run=dry_run)
        moved += 1
    return moved


def archive_weekly_files(
    current_dir: Path,
    archive_dir: Path,
    keep_count: int,
    dry_run: bool,
) -> int:
    if not current_dir.exists():
        return 0

    candidates: list[tuple[dt.date, Path]] = []
    for file_path in sorted(current_dir.glob("week-report-*_to_*.md")):
        match = WEEKLY_FILE_PATTERN.match(file_path.name)
        if not match:
            continue
        end_date = dt.date.fromisoformat(match.group("end"))
        candidates.append((end_date, file_path))

    candidates.sort(key=lambda x: x[0], reverse=True)
    to_archive = candidates[keep_count:] if keep_count >= 0 else candidates

    moved = 0
    for _, file_path in to_archive:
        match = WEEKLY_FILE_PATTERN.match(file_path.name)
        if not match:
            continue
        year = dt.date.fromisoformat(match.group("start")).year
        dst = archive_dir / str(year) / file_path.name
        move_file(file_path, dst, dry_run=dry_run)
        moved += 1
    return moved


def main() -> int:
    args = parse_args()

    daily_moved = archive_daily_files(
        current_dir=Path(args.daily_current_dir),
        archive_dir=Path(args.daily_archive_dir),
        keep_days=args.keep_daily_days,
        dry_run=args.dry_run,
    )
    weekly_moved = archive_weekly_files(
        current_dir=Path(args.weekly_current_dir),
        archive_dir=Path(args.weekly_archive_dir),
        keep_count=args.keep_weekly_count,
        dry_run=args.dry_run,
    )

    print(f"[summary] daily moved: {daily_moved}, weekly moved: {weekly_moved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

