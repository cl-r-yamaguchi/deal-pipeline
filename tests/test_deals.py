from datetime import date

import pandas as pd
import pytest

from deals import (
    DEALS_CSV,
    DealsLoadError,
    filter_by_stages,
    load_deals,
    save_deals,
    summarize_by_stage,
    update_stage,
)
from stages import STAGES

TODAY = date(2026, 11, 10)


def make_df():
    return pd.DataFrame({
        "deal_id": ["D-001", "D-002", "D-003"],
        "name": ["案件1", "案件2", "案件3"],
        "customer": ["顧客1", "顧客2", "顧客3"],
        "owner": ["担当者A", "担当者B", "担当者C"],
        "stage": [STAGES[0], STAGES[1], STAGES[1]],
        "amount": [1000000, 2000000, 3000000],
        "probability": [10, 30, 30],
        "due_date": ["2026-11-20", "", "2026-12-01"],
        "updated_at": ["2026-10-01", "2026-10-02", "2026-10-03"],
    })


def test_update_stage_changes_stage_and_updated_at():
    df = make_df()
    result = update_stage(df, "D-001", STAGES[2], TODAY)
    row = result[result["deal_id"] == "D-001"].iloc[0]
    assert row["stage"] == STAGES[2]
    assert row["updated_at"] == "2026-11-10"


def test_update_stage_does_not_change_other_rows_or_columns():
    df = make_df()
    result = update_stage(df, "D-001", STAGES[2], TODAY)
    others = result["deal_id"] != "D-001"
    pd.testing.assert_frame_equal(result[others], df[others])
    changed = result[result["deal_id"] == "D-001"].drop(columns=["stage", "updated_at"])
    pd.testing.assert_frame_equal(changed, df[df["deal_id"] == "D-001"].drop(columns=["stage", "updated_at"]))


def test_update_stage_does_not_modify_original():
    df = make_df()
    update_stage(df, "D-001", STAGES[2], TODAY)
    pd.testing.assert_frame_equal(df, make_df())


def test_update_stage_same_stage_changes_nothing():
    df = make_df()
    result = update_stage(df, "D-002", STAGES[1], TODAY)
    pd.testing.assert_frame_equal(result, df)


def test_update_stage_unknown_deal_id():
    with pytest.raises(ValueError):
        update_stage(make_df(), "D-999", STAGES[2], TODAY)


def test_update_stage_invalid_stage():
    with pytest.raises(ValueError):
        update_stage(make_df(), "D-001", "存在しないステージ", TODAY)


def test_save_deals_roundtrip(tmp_path):
    df = make_df()
    path = tmp_path / "deals.csv"
    save_deals(df, path)
    pd.testing.assert_frame_equal(load_deals(path), df)


def test_save_deals_raises_when_unwritable(tmp_path):
    with pytest.raises(OSError):
        save_deals(make_df(), tmp_path / "no_such_dir" / "deals.csv")


def test_filter_by_stages():
    df = make_df()
    assert len(filter_by_stages(df, [STAGES[1]])) == 2
    assert len(filter_by_stages(df, [STAGES[0], STAGES[1]])) == 3
    assert len(filter_by_stages(df, [])) == 3


def test_summarize_by_stage_includes_zero_stages():
    summary = summarize_by_stage(make_df())
    assert list(summary["stage"]) == STAGES
    assert list(summary["count"]) == [1, 2, 0, 0, 0, 0]
    assert list(summary["amount"]) == [1000000, 5000000, 0, 0, 0, 0]


def test_load_deals_errors(tmp_path):
    with pytest.raises(DealsLoadError):
        load_deals(tmp_path / "missing.csv")
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(DealsLoadError):
        load_deals(empty)
    no_cols = tmp_path / "no_cols.csv"
    no_cols.write_text("deal_id,name\nD-001,案件1\n", encoding="utf-8")
    with pytest.raises(DealsLoadError):
        load_deals(no_cols)


def test_dummy_data_distribution():
    df = load_deals(DEALS_CSV)
    assert len(df) == 25
    assert df["deal_id"].is_unique
    summary = summarize_by_stage(df)
    assert list(summary["count"]) == [5, 5, 5, 4, 3, 3]
