from stages import CLOSED_STAGES, STAGES


def test_stages_and_closed_stages():
    assert STAGES == ["リード", "商談", "提案", "見積", "受注", "失注"]
    assert "受注" in CLOSED_STAGES
    assert "失注" in CLOSED_STAGES
