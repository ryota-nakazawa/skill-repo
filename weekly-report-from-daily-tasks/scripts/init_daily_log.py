#!/usr/bin/env python3
"""Create a daily task log file from a fixed template."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a daily task log markdown file.")
    parser.add_argument(
        "--daily-dir",
        default="./reports/daily/current",
        help="Directory where daily logs are stored (default: ./reports/daily/current)",
    )
    parser.add_argument(
        "--date",
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite file if it already exists",
    )
    return parser.parse_args()


def resolve_date(raw_date: str | None) -> dt.date:
    if raw_date is None:
        return dt.date.today()
    return dt.date.fromisoformat(raw_date)


def build_template(date_str: str) -> str:
    return f"""# Daily Task Log {date_str}

## プロジェクト進捗
| プロジェクト名 | 進捗記録 | ひとこと |
| --- | --- | --- |
|  |  |  |

## メモ
- 
"""


def main() -> int:
    args = parse_args()
    target_date = resolve_date(args.date)
    date_str = target_date.isoformat()

    daily_dir = Path(args.daily_dir)
    daily_dir.mkdir(parents=True, exist_ok=True)

    output_path = daily_dir / f"{date_str}.md"
    if output_path.exists() and not args.force:
        print(f"[skip] Already exists: {output_path}")
        return 0

    output_path.write_text(build_template(date_str), encoding="utf-8")
    print(f"[ok] Created: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
