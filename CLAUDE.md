# 案件パイプライン管理アプリ

Streamlit と pandas で作る、案件の一覧・ステージ更新を行うアプリ。データは `data/deals.csv` の 1 ファイル。

## ルール

- 画面の文言(ボタン、メッセージ、ラベル)は日本語にする
- ステージ名は `stages.py` の定義を使い、直書きしない
- 集計や更新の処理は関数に分けて、`tests/` にテストを書く
- テストは pytest で実行する

## コマンド

- 起動: `streamlit run app.py`
- テスト: `pytest`
- ダミーデータの作り直し: `python scripts/reset_data.py`
