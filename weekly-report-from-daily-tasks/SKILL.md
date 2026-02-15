---
name: weekly-report-from-daily-tasks
description: 毎日のタスク記録ファイルを運用し、週次でその記録を集約して週報(Markdown)を生成するSkill。ユーザーが「日次タスクを簡易に記録したい」「日次ログから週報を作りたい」「プロジェクト名/進捗記録/ひとことの3枠で管理したい」と依頼したときに使う。Slack/Teams等の広範なチャット収集ではなく、ノイズの少ない日次タスク管理を情報源にする運用で使う。
---

# 目的
日次タスク管理を最小負荷で継続し、週報作成時はCodex/Claude Codeが日次ログを読み取って所定フォーマットへ整理する。

## 運用方針
- 日次記録を主情報源にする
- 1日1回、終業前に短く記録する
- 週報は事実ベースで作成し、推測を混ぜない
- 書式を固定して迷いを減らす

## ディレクトリ構成
- 日次ログ（作業中）: `./reports/daily/current/YYYY-MM-DD.md`
- 週報（作業中）: `./reports/weekly/current/week-report-YYYY-MM-DD_to_YYYY-MM-DD.md`
- 日次ログ（アーカイブ）: `./reports/archive/daily/YYYY/MM/YYYY-MM-DD.md`
- 週報（アーカイブ）: `./reports/archive/weekly/YYYY/week-report-YYYY-MM-DD_to_YYYY-MM-DD.md`

必要ならパスはコマンド引数で上書きする。
上記ディレクトリはスキルに同梱しているため、初回からそのまま運用開始できる。

## 日次記録フロー
1. その日のログファイルを生成する。
```bash
python3 scripts/init_daily_log.py --daily-dir ./reports/daily/current
```
2. 終業前に `プロジェクト進捗` テーブルを更新する。
3. 必要なら `メモ` を追記する。

`プロジェクト進捗` は次の3枠で記録する。
- `プロジェクト名`
- `進捗記録`
- `ひとこと`

テンプレートは `references/daily-log-template.md` を参照する。
コマンドはこのスキルディレクトリ（`weekly-report-from-daily-tasks/`）で実行する。

## 週報作成フロー（推奨: AIエージェントで直接作成）
1. 週の開始日と終了日を決める（省略時は今週の月曜〜日曜）。
2. 対象期間の `./reports/daily/current/YYYY-MM-DD.md` だけを読む。
3. `references/weekly-report-format.md` の書式で週報を作成する。
4. 週報を `./reports/weekly/current/week-report-YYYY-MM-DD_to_YYYY-MM-DD.md` に保存する。
5. 古い記録を `archive` へ移す。
```bash
python3 scripts/archive_reports.py
```
`--dry-run` で移動予定だけ確認できる。

週報テンプレートは `references/weekly-report-format.md` を参照する。
必要なら `scripts/build_weekly_report.py` で下書きを作成し、その後にAIエージェントで整形してもよい。

## 品質ルール
- 日次ログにない内容は「要確認」として扱う
- 週報ではプロジェクト単位で進捗を整理して要約する
- `ひとこと` は `今週のひとこと一覧` セクションにのみ表示する
- 週報作成時は対象の1週間だけ読み込む（全履歴は読まない）
- 日次ログの全レコードが、週報のどこかに必ず反映されるようにする
- 週報生成後に表現だけ整え、事実は改変しない
- 記録欠損日がある場合は欠損日を明示する
