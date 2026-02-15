# skill-repo

`weekly-report-from-daily-tasks` を管理するリポジトリです。

## 含まれるスキル
- `weekly-report-from-daily-tasks`
  - 日次ログ（プロジェクト名 / 進捗記録 / ひとこと）から週報を作成
  - 推奨運用は、Codex/Claude Code が日報を読んで所定フォーマットに整理

## ディレクトリ
- `weekly-report-from-daily-tasks/SKILL.md`
- `weekly-report-from-daily-tasks/references/`
- `weekly-report-from-daily-tasks/scripts/`
- `weekly-report-from-daily-tasks/reports/`
  - `daily/current/` 日報
  - `weekly/current/` 週報
  - `archive/` 過去データ

## 使い方
1. 日報テンプレートを作成
```bash
cd weekly-report-from-daily-tasks
python3 scripts/init_daily_log.py --date 2026-02-09
```

2. `reports/daily/current/YYYY-MM-DD.md` を記入
```md
| プロジェクト名 | 進捗記録 | ひとこと |
| --- | --- | --- |
| プロジェクトA | 〇〇を実装 | レビュー待ち |
```

3. 週報を作成（推奨: AIエージェントに作成依頼）
- 例: 「`reports/daily/current/2026-02-09.md` から `2026-02-13.md` を読んで、`references/weekly-report-format.md` 形式で週報を作成して」

4. スクリプトで下書きを作る場合（任意）
```bash
python3 scripts/build_weekly_report.py --week-start 2026-02-09 --week-end 2026-02-13
```

5. 古い記録をアーカイブ
```bash
python3 scripts/archive_reports.py --dry-run
python3 scripts/archive_reports.py
```
