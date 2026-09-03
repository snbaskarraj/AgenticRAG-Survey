from finagent.agent import FinanceAgent
from finagent.fallback import OfflinePlanner
from finagent.schemas import AgentResponse
from finagent.store import DataStore
from finagent.tools import ToolBox


def test_q1_fy2026_revenue_is_118m():
    store = DataStore()
    rows = store.query_metrics(
        metric="revenue",
        fiscal_year=2026,
        fiscal_quarter="Q1",
        aggregation="quarterly",
    )
    assert len(rows) == 1
    assert rows.iloc[0]["metric_value"] == 118_000_000


def test_company_default_does_not_double_count_segments():
    store = DataStore()
    company = store.query_metrics(metric="revenue_usd", fiscal_year=2026, aggregation="annual")
    enterprise = store.query_metrics(
        metric="revenue_usd",
        fiscal_year=2026,
        segment="Enterprise",
        aggregation="annual",
    )
    assert float(company.iloc[0]["metric_value"]) > float(enterprise.iloc[0]["metric_value"])


def test_win_rate_anomaly_in_fy2025_q4():
    tools = ToolBox(DataStore())
    result = tools.detect_anomalies(
        metric="win_rate_pct",
        aggregation="quarterly",
        z_threshold=1.5,
    )
    periods = {item["period"] for item in result["anomalies"]}
    assert any("FY2025" in period and "Q4" in period for period in periods)


def test_explain_change_links_competitor_event():
    tools = ToolBox(DataStore())
    result = tools.explain_change("win_rate", 2025, "Q4")
    assert result["current_value"] == 19.5
    titles = " ".join(event["title"] for event in result["nearby_events"])
    assert "NimbusBlock" in titles


def test_agent_response_is_pydantic_and_grounded():
    response = FinanceAgent(DataStore()).ask("What was the revenue in Q1 FY2026?")
    assert isinstance(response, AgentResponse)
    assert response.requirement_check()["used_data_tool"] is True
    assert "118" in response.answer


def test_offline_planner_answers_q1_fy2026_revenue():
    planner = OfflinePlanner(ToolBox(DataStore()))
    answer, traces = planner.run("What was the revenue in Q1 FY2026?")
    assert "$118.0M" in answer
    assert traces[0]["tool"] == "query_metrics"


def test_offline_planner_handles_anomaly_question():
    planner = OfflinePlanner(ToolBox(DataStore()))
    answer, traces = planner.run("Which metrics look anomalous in FY2025?")
    assert traces[0]["tool"] == "detect_anomalies"
    assert "Unusual" in answer or "unusual" in answer


def test_offline_planner_compares_enterprise_and_cloud():
    planner = OfflinePlanner(ToolBox(DataStore()))
    answer, traces = planner.run("Compare Enterprise vs Cloud revenue in FY2026.")
    assert traces[0]["tool"] == "query_metrics"
    assert "Enterprise" in answer
    assert "Cloud" in answer
    assert "FY2026" in answer


def test_offline_planner_explains_win_rate_drop():
    planner = OfflinePlanner(ToolBox(DataStore()))
    answer, traces = planner.run("Why did win rate drop in Q4 FY2025?")
    assert traces[0]["tool"] == "explain_change"
    assert "NimbusBlock" in answer
    assert "19.5%" in answer
