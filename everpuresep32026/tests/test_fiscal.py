from finagent.fiscal import fiscal_label, fiscal_quarter, fiscal_year, months_for_quarter


def test_february_opens_the_next_fiscal_year():
    assert fiscal_year("2025-02-01") == 2026
    assert fiscal_quarter("2025-02-01") == "Q1"
    assert fiscal_label("2025-04-30") == "Q1 FY2026"


def test_january_closes_the_current_fiscal_year():
    assert fiscal_year("2026-01-20") == 2026
    assert fiscal_quarter("2026-01-20") == "Q4"
    assert fiscal_label("2026-01-20") == "Q4 FY2026"


def test_q1_fy2026_months():
    assert months_for_quarter(2026, "Q1") == ["2025-02", "2025-03", "2025-04"]
