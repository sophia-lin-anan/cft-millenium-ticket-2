"""LangGraph: deterministic metrics followed by an explicit review branch."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class PodState(TypedDict, total=False):
    daily_returns: list[float]
    average_return: float
    route: str
    review_note: str


def calculate_metrics(state: PodState) -> PodState:
    returns = state["daily_returns"]
    if not returns:
        raise ValueError("daily_returns must contain at least one value")

    average = sum(returns) / len(returns)
    return {
        "average_return": average,
        "route": "human_review" if average < -0.01 else "done",
    }


def choose_next(state: PodState) -> str:
    return state["route"]


def flag_for_review(_: PodState) -> PodState:
    return {"review_note": "Human review required; no automated trade action."}


def build_graph():
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
    return builder.compile()


def main() -> None:
    result = build_graph().invoke({"daily_returns": [-0.02, -0.01, -0.03]})
    print(result)


if __name__ == "__main__":
    main()
