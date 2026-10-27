"""ダミー案件データ(data/deals.csv)を今日の日付で作り直す(講師用)。

乱数は使わず、固定の表から生成するので、何度実行しても同じ構成になる。
使い方: python scripts/reset_data.py [--today YYYY-MM-DD]
"""
import argparse
import csv
from datetime import date, timedelta
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "deals.csv"

COLUMNS = [
    "deal_id", "name", "customer", "owner", "stage",
    "amount", "probability", "due_date", "updated_at",
]

# (案件名, 顧客, 担当者, ステージ, 金額(万円), 確度, 期限までの日数 or None, 最終更新が何日前か)
# 進行中19件の期限: -10,-3,-1 / 0 / 2,5 / 7 / 8 / 14〜90の10件 / 空1件
ROWS = [
    ("新規事業A 実証実験", "サンプル商事", "担当者A", "リード", 150, 10, -10, 12),
    ("新規事業B 市場調査", "テスト工業", "担当者B", "リード", 150, 10, 2, 3),
    ("新規事業C 共同研究", "デモ製作所", "担当者C", "リード", 200, 15, 21, 25),
    ("新規事業D 試作支援", "見本物流", "担当者D", "リード", 200, 15, 45, 8),
    ("新規事業E 事前相談", "架空食品", "担当者E", "リード", 250, 20, None, 0),
    ("業務改善F 導入検討", "サンプル商事", "担当者A", "商談", 500, 30, -3, 5),
    ("業務改善G 要件整理", "テスト工業", "担当者B", "商談", 600, 30, 0, 1),
    ("業務改善H 現場ヒアリング", "デモ製作所", "担当者C", "商談", 700, 35, 14, 18),
    ("業務改善I 費用試算", "見本物流", "担当者D", "商談", 800, 40, 30, 22),
    ("業務改善J 体制検討", "架空食品", "担当者E", "商談", 900, 40, 60, 29),
    ("データ基盤K 構築提案", "サンプル商事", "担当者A", "提案", 800, 50, -1, 2),
    ("データ基盤L 分析提案", "テスト工業", "担当者B", "提案", 1000, 50, 5, 7),
    ("データ基盤M 移行提案", "デモ製作所", "担当者C", "提案", 1200, 55, 7, 15),
    ("データ基盤N 可視化提案", "見本物流", "担当者D", "提案", 1250, 60, 28, 11),
    ("データ基盤O 運用提案", "架空食品", "担当者E", "提案", 1400, 60, 75, 30),
    ("共創プロジェクトP", "サンプル商事", "担当者A", "見積", 1500, 70, 8, 4),
    ("共創プロジェクトQ", "テスト工業", "担当者B", "見積", 1800, 75, 17, 9),
    ("共創プロジェクトR", "デモ製作所", "担当者C", "見積", 2250, 75, 40, 20),
    ("共創プロジェクトS", "見本物流", "担当者D", "見積", 3000, 80, 90, 6),
    ("定額サービスT 契約", "架空食品", "担当者E", "受注", 2000, 100, -5, 14),
    ("定額サービスU 契約", "サンプル商事", "担当者A", "受注", 2500, 100, None, 19),
    ("定額サービスV 契約", "テスト工業", "担当者B", "受注", 2600, 100, None, 26),
    ("検証案件W 見送り", "デモ製作所", "担当者C", "失注", 500, 0, -12, 16),
    ("検証案件X 見送り", "見本物流", "担当者D", "失注", 700, 0, None, 23),
    ("検証案件Y 見送り", "架空食品", "担当者E", "失注", 1000, 0, None, 28),
]


def build_rows(today):
    rows = []
    for i, (name, customer, owner, stage, man, prob, due, ago) in enumerate(ROWS, start=1):
        rows.append({
            "deal_id": f"D-{i:03d}",
            "name": name,
            "customer": customer,
            "owner": owner,
            "stage": stage,
            "amount": man * 10000,
            "probability": prob,
            "due_date": (today + timedelta(days=due)).isoformat() if due is not None else "",
            "updated_at": (today - timedelta(days=ago)).isoformat(),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description="ダミー案件データを作り直す")
    parser.add_argument("--today", help="基準日(YYYY-MM-DD)。省略時は今日")
    args = parser.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(build_rows(today))
    print(f"{CSV_PATH} を作り直しました(基準日: {today.isoformat()}、{len(ROWS)}件)")


if __name__ == "__main__":
    main()
