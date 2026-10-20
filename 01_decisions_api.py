"""OpenAI Decisions API: route a fake pod to a bounded review queue."""

from openai import OpenAI

from demo_common import POD_SUMMARY, load_project_env, require_env


def main() -> None:
    load_project_env()
    require_env("OPENAI_API_KEY")

    decision = OpenAI().decisions.create(
        model="gpt-6-luna",
        input=POD_SUMMARY,
        questions=[
            {
                "type": "choice",
                "name": "review_route",
                "instructions": (
                    "Which review queue should receive this pod? "
                    "This is triage only, not a final risk decision."
                ),
                "choices": [
                    {
                        "value": "normal_variation",
                        "description": "No unusual evidence.",
                    },
                    {
                        "value": "investigate",
                        "description": "Needs a human risk review.",
                    },
                    {
                        "value": "strategy_review",
                        "description": "Evidence may indicate strategy degradation.",
                    },
                ],
            }
        ],
    )

    answer = decision.answers[0]
    if answer.type == "refusal":
        print(f"Decision refused for question: {answer.name}")
        return

    print(f"route: {answer.choice}")
    print(f"confidence: {answer.confidence:.3f}")
    print("probabilities:")
    for probability in answer.probabilities:
        print(f"  {probability.value}: {probability.probability:.3f}")


if __name__ == "__main__":
    main()
