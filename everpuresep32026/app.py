"""Streamlit chat UI for the AetherData finance analyst agent."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finagent.agent import FinanceAgent  # noqa: E402
from finagent.config import active_provider  # noqa: E402
from finagent.prompts import greeting  # noqa: E402
from finagent.samples import SAMPLE_QUESTIONS  # noqa: E402
from finagent.store import DataStore  # noqa: E402

st.set_page_config(page_title="AetherData Finance Agent", page_icon="◈", layout="wide")


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #0f1720; color: #e8eef4; }
        [data-testid="stSidebar"] { background: #15202b; }
        h1, h2, h3 { color: #f4f7fb !important; letter-spacing: -0.02em; }
        .hero-card {
            border: 1px solid #2a3b4d;
            background: linear-gradient(135deg, #173246 0%, #101820 100%);
            padding: 1.1rem 1.3rem;
            border-radius: 16px;
            margin-bottom: 0.8rem;
        }
        .muted { color: #9db0c0; font-size: 0.92rem; }
        .chip {
            display: inline-block;
            background: #1d3344;
            border: 1px solid #33556c;
            color: #d5e6f3;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.75rem;
            margin-right: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_store() -> DataStore:
    return DataStore()


@st.cache_resource
def get_agent() -> FinanceAgent:
    return FinanceAgent(get_store())


def _format_trace(trace: dict) -> None:
    st.markdown(f"**{trace['tool']}**")
    st.json({"arguments": trace.get("arguments", {}), "result": trace.get("result", {})})


def main() -> None:
    _inject_css()
    store = get_store()
    agent = get_agent()
    catalog = store.catalog()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "traces" not in st.session_state:
        st.session_state.traces = []

    with st.sidebar:
        st.markdown("### AetherData")
        st.caption("Fictional data-platform company used for the Everpure agentic exercise.")
        st.markdown(
            f'<span class="chip">{active_provider()}</span>'
            f'<span class="chip">{catalog["metric_count"]} metrics</span>'
            f'<span class="chip">{catalog["event_count"]} events</span>',
            unsafe_allow_html=True,
        )
        st.write("")
        st.markdown("**Fiscal calendar**")
        st.caption(catalog["fiscal_calendar"])
        st.caption(f"Metrics coverage: {catalog['metrics_period_range'][0]} → {catalog['metrics_period_range'][1]}")
        st.markdown("**Sample questions**")
        for question in SAMPLE_QUESTIONS:
            if st.button(question, key=f"sample-{question}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.traces = []
            st.rerun()

        st.markdown("**How answers are grounded**")
        st.caption(
            "The model cannot see the raw CSVs. It has to call query, trend, "
            "anomaly, or event tools. Offline mode uses the same tools."
        )

    st.markdown(
        """
        <div class="hero-card">
          <h1>Finance analyst agent</h1>
          <p class="muted">
            Ask about revenue, ARR, trends, anomalies, or the events that sit next to a change.
            Answers are computed from the supplied metrics and events datasets.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chat_tab, data_tab, design_tab = st.tabs(["Chat", "Data", "Design"])

    with chat_tab:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                traces = message.get("traces") or []
                if traces:
                    with st.expander(f"Tool traces ({len(traces)})"):
                        for trace in traces:
                            _format_trace(trace)

        if not st.session_state.messages:
            st.info(greeting())

        prompt = st.chat_input("Ask a question about the AetherData datasets")
        pending = st.session_state.pop("pending_question", None)
        question = prompt or pending
        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
                if m["role"] in {"user", "assistant"}
            ]
            with st.chat_message("assistant"):
                with st.spinner("Querying datasets…"):
                    response = agent.ask(question, history=history)
                st.markdown(response.answer)
                if response.traces:
                    with st.expander(f"Tool traces ({len(response.traces)}) · {response.provider}"):
                        for trace in response.traces:
                            _format_trace(trace)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response.answer,
                    "traces": response.traces,
                    "provider": response.provider,
                }
            )
            st.session_state.traces.extend(response.traces)

    with data_tab:
        left, right = st.columns(2)
        with left:
            st.subheader("Metrics")
            st.caption("Long-format monthly KPIs. Company totals are the default query grain.")
            st.dataframe(store.metrics, use_container_width=True, hide_index=True, height=420)
        with right:
            st.subheader("Events")
            st.caption("Business events aligned to the same fiscal calendar.")
            st.dataframe(store.events.drop(columns=["date_parsed"], errors="ignore"), use_container_width=True, hide_index=True, height=420)

        st.subheader("Quarterly company revenue")
        quarterly = store.query_metrics(metric="revenue_usd", aggregation="quarterly")
        if not quarterly.empty:
            chart = quarterly.set_index("fiscal_period")["metric_value"] / 1_000_000
            st.bar_chart(chart, use_container_width=True)
            st.caption("USD millions")

    with design_tab:
        st.markdown(
            """
            **What this application is**

            A small agentic system for the Everpure hands-on exercise. A chat UI
            talks to an LLM-backed (or deterministic) controller. The controller
            can only see the business data through tools.

            **Minimum requirements coverage**

            - Chat UI: this Streamlit app (Cursor default) or `gradio_app.py`
            - LLM-powered backend: OpenAI or Anthropic tool calling when an API key is present
            - Data query / analysis mechanism: `query_metrics`, `analyze_trend`, `detect_anomalies`, `search_events`, `explain_change`
            - Grounded answers: the system prompt forbids invented numbers; every answer is built from tool results

            See `docs/SDLC.md` and `docs/SETUP.md`. The Colab walkthrough is
            `notebooks/Everpure_Agentic_Finance_Agent.ipynb`.

            **Why these two datasets**

            Metrics answer “what changed”. Events answer “what was happening then”.
            `explain_change` joins a metric delta to nearby events without claiming causation.

            **Swapping in the interview files**

            Replace `data/metrics.csv` and `data/events.csv`, or point `FINAGENT_DATA_DIR`
            at a folder that contains them. Column names are aliased, so `date`/`month`,
            `kpi`/`metric`, and `value`/`amount` all load.
            """
        )
        st.code(json.dumps(catalog, indent=2, default=str)[:1800] + "\n…")


if __name__ == "__main__":
    main()
