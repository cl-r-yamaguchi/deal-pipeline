from datetime import date

import pandas as pd
import pytest

from deals import DUE_SOON, NOT_TARGET, OVERDUE, classify_deadline, get_alerts
from stages import CLOSED_STAGES, STAGES

TODAY = date(2026, 11, 10)
OPEN_STAGE = STAGES[1]


@pytest.mark.parametrize(
    "due_date, stage, expected",
    [
        ("2026-11-09", OPEN_STAGE, OVERDUE),
        ("2026-11-10", OPEN_STAGE, DUE_SOON),
        ("2026-11-17", OPEN_STAGE, DUE_SOON),
        ("2026-11-18", OPEN_STAGE, NOT_TARGET),
        ("", OPEN_STAGE, NOT_TARGET),
        ("2026-11-09", CLOSED_STAGES[0], NOT_TARGET),
        ("2026-11-09", CLOSED_STAGES[1], NOT_TARGET),
    ],
)
def test_classify_deadline_boundaries(due_date, stage, expected):
    assert classify_deadline(due_date, stage, TODAY) == expected


def test_classify_deadline_accepts_empty_values_and_dates():
    assert classify_deadline(None, OPEN_STAGE, TODAY) == NOT_TARGET
    assert classify_deadline(float("nan"), OPEN_STAGE, TODAY) == NOT_TARGET
    assert classify_deadline(date(2026, 11, 9), OPEN_STAGE, TODAY) == OVERDUE


def test_classify_deadline_defaults_to_today():
    assert classify_deadline(date.today().isoformat(), OPEN_STAGE) == DUE_SOON


def test_get_alerts_on_dummy_data():
    from scripts.reset_data import build_rows

    df = pd.DataFrame(build_rows(TODAY))
    alerts = get_alerts(df, TODAY)
    assert len(alerts[OVERDUE]) == 3
    assert len(alerts[DUE_SOON]) == 4
    # 受注・失注の期限切れと、期限が空の案件、8日後の案件は含まれない
    flagged = pd.concat(alerts.values())
    assert not flagged["stage"].isin(CLOSED_STAGES).any()
    assert (flagged["due_date"] != "").all()
    assert not (flagged["due_date"] == "2026-11-18").any()
    # 期限の早い順
    assert alerts[OVERDUE]["due_date"].is_monotonic_increasing
    assert alerts[OVERDUE]["due_date"].iloc[0] == "2026-10-31"
