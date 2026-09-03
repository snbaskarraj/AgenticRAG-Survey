"""CLI for the finance agent: python ask.py "What was the revenue in Q1 FY2026?" """

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from finagent.agent import FinanceAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the AetherData finance agent a question")
    parser.add_argument("question", nargs="+", help="Question to ask")
    parser.add_argument("--show-traces", action="store_true")
    args = parser.parse_args()
    question = " ".join(args.question)
    response = FinanceAgent().ask(question)
    print(response.answer)
    if args.show_traces:
        print("\n--- tool traces ---")
        print(json.dumps(response.traces, indent=2, default=str))


if __name__ == "__main__":
    main()
