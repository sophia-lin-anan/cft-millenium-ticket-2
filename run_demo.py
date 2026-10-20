"""Run one of the five isolated demos by a short name."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEMOS = {
    "decisions": "01_decisions_api.py",
    "responses": "02_responses_api.py",
    "langgraph": "03_langgraph.py",
    "openai-agents": "04_openai_agents_sdk.py",
    "claude-agent": "05_claude_agent_sdk.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo", choices=[*DEMOS, "all"])
    args = parser.parse_args()

    selected = DEMOS.items() if args.demo == "all" else [(args.demo, DEMOS[args.demo])]
    for name, filename in selected:
        print(f"\n=== {name} ===", flush=True)
        subprocess.run([sys.executable, str(ROOT / filename)], check=True)


if __name__ == "__main__":
    main()
