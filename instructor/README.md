# 講師用 README

参加者に配るフォルダには、`instructor/` を含めないでください。4 章の Skill と 5 章の Hooks は別に配ります。

## 事前準備

1. 当日の朝に `python scripts/reset_data.py` を実行し、`data/deals.csv` を今日の日付で作り直す(期限が当日から数えられる)
2. `pip install -r requirements.txt`(Python 3.11 以上)
3. 全員の承認モードを Default(都度確認)に揃える
4. `git switch solution/chN` で各章の完成版に切り替えられることを試す

## ブランチ

| ブランチ | 中身 |
|---|---|
| main | 土台(第 0 版)。参加者の開始地点 |
| solution/ch2 | main + 案件一覧画面 |
| solution/ch3 | ch2 + ステージ更新フォーム、CLAUDE.md、settings.json、テスト |
| solution/ch4 | ch3 + weekly-report Skill |
| solution/ch5 | ch4 + 期限アラート、テスト、Hooks 設定 |
| solution/ch7 | ch5 を main に merge した完了形 |

## 各章で配るもの

- 4 章: `instructor/ch4/weekly-report/SKILL.md` を `.claude/skills/weekly-report/` に置かせる。危険性デモは `instructor/ch4/suspicious-skill/`(解説は `講師用メモ.md`)
- 5 章: プロジェクトのルートで `python instructor/ch5/install_hooks.py`(`.claude/` へのコピーと settings.json への追記を行う)。Hooks のコマンドは `python` で呼ぶので、macOS で `python` が無い場合は `.claude/settings.json` の `python` を `python3` に直す

## リセット手順

| 状況 | 戻し方 |
|---|---|
| データが壊れた | `python scripts/reset_data.py` |
| コードが壊れた(未コミット) | `git restore .`(未コミットの変更をすべて破棄) |
| 章をやり直したい | `git switch solution/chN`(参加者の変更は破棄される) |
| Skills や Hooks の設定を入れ直す | `instructor/` から `.claude/` にコピーし直す(Hooks は `install_hooks.py`) |
| 全部を真っさらに戻す | `git switch main`、`git restore .`、`git clean -fd` の順。未追跡ファイル(CLAUDE.md、.claude/、reports/)も消えるので、取り消せないことを確認してから実行する |

## 7 章の予備手順

`/rewind` で戻せるのは Claude のファイル編集ツールによる変更だけです。Claude が `sed` などの Bash コマンドで書き換えた場合は、`git restore .` で戻します。
