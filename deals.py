"""案件データの読み込み・絞り込み・集計。"""
from datetime import date
from pathlib import Path

import pandas as pd

from stages import CLOSED_STAGES, STAGES

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


def update_stage(df, deal_id, new_stage, today):
    """案件のステージと最終更新日を変えた、新しいデータを返す。元のデータは変更しない。

    現在と同じステージのときは、最終更新日も変えない。
    存在しない案件IDと、ステージ定義にないステージは ValueError。
    """
    if new_stage not in STAGES:
        raise ValueError(f"不正なステージです: {new_stage}")
    mask = df["deal_id"] == deal_id
    if not mask.any():
        raise ValueError(f"存在しない案件IDです: {deal_id}")

    updated = df.copy()
    if (updated.loc[mask, "stage"] == new_stage).all():
        return updated
    updated.loc[mask, "stage"] = new_stage
    updated.loc[mask, "updated_at"] = today.isoformat()
    return updated


def save_deals(df, path=DEALS_CSV):
    """案件データを CSV(UTF-8、BOMなし)に保存する。書き込めない場合は OSError。"""
    df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")


OVERDUE = "期限切れ"
DUE_SOON = "7日以内"
NOT_TARGET = "対象外"
DUE_SOON_DAYS = 7


def _to_date(value):
    """期限の値(文字列・日付・空)を date にする。空は None。"""
    if value is None or pd.isna(value) or value == "":
        return None
    if isinstance(value, str):
        return date.fromisoformat(value)
    return pd.Timestamp(value).date()


def classify_deadline(due_date, stage, today=None):
    """期限の状態を返す。戻り値は OVERDUE(期限切れ)、DUE_SOON(7日以内)、NOT_TARGET(対象外)。

    残り日数 = 期限 - 基準日。0 未満が期限切れ、0 以上 7 以下が 7日以内。
    受注・失注、または期限が空の案件は、期限が過去でも対象外。
    基準日(today)を省略すると今日。
    """
    today = today or date.today()
    due = _to_date(due_date)
    if stage in CLOSED_STAGES or due is None:
        return NOT_TARGET
    remaining = (due - today).days
    if remaining < 0:
        return OVERDUE
    if remaining <= DUE_SOON_DAYS:
        return DUE_SOON
    return NOT_TARGET


def get_alerts(df, today=None):
    """期限アラートの対象案件を返す。{OVERDUE: 案件, DUE_SOON: 案件} で、各々期限の早い順。"""
    today = today or date.today()
    status = df.apply(lambda r: classify_deadline(r["due_date"], r["stage"], today), axis=1)
    return {
        label: df[status == label].sort_values("due_date", kind="stable")
        for label in (OVERDUE, DUE_SOON)
    }
