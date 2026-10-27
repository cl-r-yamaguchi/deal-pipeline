"""案件データの読み込み・絞り込み・集計。"""
from pathlib import Path

import pandas as pd

from stages import STAGES

DEALS_CSV = Path(__file__).resolve().parent / "data" / "deals.csv"

REQUIRED_COLUMNS = [
    "deal_id", "name", "customer", "owner", "stage",
    "amount", "probability", "due_date", "updated_at",
]


class DealsLoadError(Exception):
    """案件データを読み込めないときのエラー。メッセージは画面にそのまま出せる日本語。"""


def load_deals(path=DEALS_CSV):
    """CSV から案件を読み込む。CSV が無い・空・列が足りない場合は DealsLoadError。"""
    path = Path(path)
    if not path.exists():
        raise DealsLoadError(f"案件データ({path.name})が見つかりません。")
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    except pd.errors.EmptyDataError:
        raise DealsLoadError(f"案件データ({path.name})が空です。") from None
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as e:
        raise DealsLoadError(f"案件データ({path.name})を読み込めません: {e}") from None

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DealsLoadError(f"案件データに必要な列がありません: {', '.join(missing)}")
    if df.empty:
        raise DealsLoadError(f"案件データ({path.name})に案件がありません。")

    try:
        df["amount"] = df["amount"].astype(int)
        df["probability"] = df["probability"].astype(int)
    except ValueError:
        raise DealsLoadError("金額または受注確度に数値でない値があります。") from None
    return df


def filter_by_stages(df, stages):
    """選んだステージの案件だけを返す。何も選んでいないときは全件を返す。"""
    if not stages:
        return df
    return df[df["stage"].isin(stages)]


def summarize_by_stage(df):
    """ステージごとの件数と金額の合計を、ステージ定義の順で返す(0件のステージも含む)。"""
    grouped = df.groupby("stage")["amount"].agg(["count", "sum"])
    grouped = grouped.reindex(STAGES, fill_value=0)
    return pd.DataFrame({
        "stage": STAGES,
        "count": grouped["count"].astype(int).to_numpy(),
        "amount": grouped["sum"].astype(int).to_numpy(),
    })
