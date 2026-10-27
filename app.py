import streamlit as st

from deals import DealsLoadError, filter_by_stages, load_deals, summarize_by_stage
from stages import STAGES

st.set_page_config(page_title="案件パイプライン管理", layout="wide")

st.title("案件パイプライン管理")
st.write("新規事業の案件を管理するためのアプリです。")

try:
    deals = load_deals()
except DealsLoadError as e:
    st.error(str(e))
    st.stop()

st.subheader("ステージ別の集計")
summary = summarize_by_stage(deals)
summary_view = summary.assign(amount=summary["amount"].map("{:,}円".format)).rename(
    columns={"stage": "ステージ", "count": "件数", "amount": "金額合計"}
)
st.dataframe(summary_view, hide_index=True)

st.subheader("案件一覧")
selected = st.multiselect("ステージで絞り込み", STAGES)
filtered = filter_by_stages(deals, selected)
st.caption(f"{len(filtered)}件を表示中")

view = filtered.assign(amount=filtered["amount"].map("{:,}円".format)).rename(columns={
    "deal_id": "案件ID",
    "name": "案件名",
    "customer": "顧客",
    "owner": "担当者",
    "stage": "ステージ",
    "amount": "金額",
    "probability": "受注確度(%)",
    "due_date": "期限",
    "updated_at": "最終更新日",
})
st.dataframe(view, hide_index=True)
