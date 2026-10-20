# Millenium decision and agent demos

These deliberately tiny Python examples fill section **5. Demo** of `Sophia Lin _ Millenium Deliverable 10_20.pdf`. They reuse the paper's section 4 example: assess a trading pod from already-computed metrics. The numbers are fake, no trading system is connected, and no snippet is authorized to trade, write files, run shell commands, or make a final risk decision.

> Runnable versions now live in `01_decisions_api.py` through `05_claude_agent_sdk.py`. See `README.md` or run `python run_demo.py --help` after activating `.venv`.

## Setup

```bash
python -m pip install "openai>=3.26.0" openai-agents langgraph claude-agent-sdk
export OPENAI_API_KEY="..."      # OpenAI snippets only
export ANTHROPIC_API_KEY="..."   # Claude snippet only
```

Each block is standalone. Run only the block you want.

## 1. OpenAI Decisions API: bounded routing decision

The answer space is fixed before inference. This is the paper's suggested use case: use the model as an intermediate signal, not as the final decision-maker.

```python
from openai import OpenAI

client = OpenAI()

decision = client.decisions.create(
    model="gpt-6-luna",
    input="Pod Atlas: 20-day return -3.2%; max drawdown 6.8%; volatility 1.7x baseline.",
    questions=[
        {
            "type": "choice",
            "name": "review_route",
            "instructions": "Which review queue should receive this pod? This is triage only.",
            "choices": [
                {"value": "normal_variation", "description": "No unusual evidence."},
                {"value": "investigate", "description": "Needs a human risk review."},
                {"value": "strategy_review", "description": "Evidence may indicate strategy degradation."},
            ],
        }
    ],
)

answer = decision.answers[0]
print(answer.choice, answer.confidence, answer.probabilities)
```

Why this demonstrates the API: `input` supplies shared evidence, `questions` declares a typed `choice`, and the response returns the chosen value plus confidence/probabilities. Production code should calibrate a threshold on labeled data and route low-confidence cases to a person.

## 2. OpenAI Responses API: one constrained explanation

This is for open-ended language, not arithmetic. The metrics are assumed to have been calculated deterministically upstream.

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-astra",
    instructions=(
        "Explain supplied risk metrics; do not recalculate them, recommend trades, "
        "or claim causation. Return at most three bullets."
    ),
    input="Pod Atlas: 20-day return -3.2%; max drawdown 6.8%; volatility 1.7x baseline.",
    max_output_tokens=400,
    store=False,
)

print(response.output_text)
```

Why this demonstrates the API: it makes one direct model call with separate `instructions` and `input`, caps output, enables no tools, and opts out of response storage.

## 3. LangGraph: deterministic workflow and explicit branch

No model or network call occurs here. The graph shows why the paper proposes LangGraph for orchestration: deterministic calculations stay deterministic, and the branch is visible in code.

```python
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class PodState(TypedDict, total=False):
    daily_returns: list[float]
    average_return: float
    route: str
    review_note: str


def calculate_metrics(state: PodState) -> PodState:
    average = sum(state["daily_returns"]) / len(state["daily_returns"])
    return {
        "average_return": average,
        "route": "human_review" if average < -0.01 else "done",
    }


def choose_next(state: PodState) -> str:
    return state["route"]


def flag_for_review(_: PodState) -> PodState:
    return {"review_note": "Human review required; no automated trade action."}


builder = StateGraph(PodState)
builder.add_node("calculate_metrics", calculate_metrics)
builder.add_node("flag_for_review", flag_for_review)
builder.add_edge(START, "calculate_metrics")
builder.add_conditional_edges(
    "calculate_metrics",
    choose_next,
    {"human_review": "flag_for_review", "done": END},
)
builder.add_edge("flag_for_review", END)
graph = builder.compile()

print(graph.invoke({"daily_returns": [-0.02, -0.01, -0.03]}))
```

Why this demonstrates the framework: state moves through named nodes, a conditional edge controls the next step, and the workflow terminates explicitly at `END`.

## 4. OpenAI Agents SDK: one specialist, no tools

This mirrors the paper's idea of a specialist risk-analysis agent while deliberately omitting functions, handoffs, web access, and filesystem access.

```python
import asyncio

from agents import Agent, Runner


agent = Agent(
    name="Pod risk explainer",
    model="gpt-6-astra",
    instructions=(
        "Explain only the supplied metrics. Do not calculate new metrics, use tools, "
        "recommend trades, or make a final risk decision. Answer in two sentences."
    ),
    tools=[],
)


async def main() -> None:
    result = await Runner.run(
        agent,
        "Pod Atlas: max drawdown 6.8%; volatility 1.7x baseline.",
        max_turns=1,
    )
    print(result.final_output)


asyncio.run(main())
```

Why this demonstrates the SDK: `Agent` packages a named specialist's model and instructions; `Runner` owns the agent loop. `tools=[]` and `max_turns=1` reduce this demo to one bounded inference.

## 5. Claude Agent SDK: one tool-less agent turn

The Agent SDK is shown rather than the lower-level Messages API. Built-in tools are denied explicitly, inherited project/user settings are ignored, and the run is capped at one turn.

```python
import asyncio

from claude_agent_sdk import ClaudeAgentOptions, query


BLOCKED_TOOLS = [
    "Bash", "Edit", "Write", "Read", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task",
]


async def main() -> None:
    options = ClaudeAgentOptions(
        model="claude-sonnet-5",
        system_prompt=(
            "Explain only supplied metrics. Do not calculate new metrics, recommend "
            "trades, or make a final risk decision. Answer in two sentences."
        ),
        allowed_tools=[],
        disallowed_tools=BLOCKED_TOOLS,
        setting_sources=[],
        max_turns=1,
    )

    async for message in query(
        prompt="Pod Atlas: max drawdown 6.8%; volatility 1.7x baseline.",
        options=options,
    ):
        print(message)


asyncio.run(main())
```

Why this demonstrates the SDK: `query()` starts a stateless agent interaction and `ClaudeAgentOptions` configures the model, system prompt, tools, settings, and turn bound.

## What each snippet proves

| Technology | Control surface demonstrated | Appropriate role from the attached deliverable |
|---|---|---|
| OpenAI Decisions API | Declared answer space and probabilities | Classification/routing as an intermediate signal |
| OpenAI Responses API | Direct model request | Short explanation from supplied evidence |
| LangGraph | State, nodes, and conditional edges | Explicit deterministic + agentic orchestration |
| OpenAI Agents SDK | Agent definition and managed run loop | A focused specialist agent |
| Claude Agent SDK | Agent query plus strict tool/turn policy | A bounded autonomous analysis step |

## Current primary documentation

- [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions)
- [OpenAI Responses API reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
- [OpenAI Agents SDK quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart?lang=python)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Claude Agent SDK cookbook](https://platform.claude.com/cookbook/claude-agent-sdk-00-the-one-liner-research-agent)
