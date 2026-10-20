"""OpenAI Responses API: explain supplied metrics in one constrained call."""

from openai import OpenAI

from demo_common import POD_SUMMARY, load_project_env, require_env


def main() -> None:
    load_project_env()
    require_env("OPENAI_API_KEY")

    response = OpenAI().responses.create(
        model="gpt-6-astra",
        instructions=(
            "Explain the supplied risk metrics. Do not recalculate them, recommend "
            "trades, or claim causation. Return at most three bullets."
        ),
        input=POD_SUMMARY,
        # This budget includes reasoning tokens, so leave enough room for the
        # requested three visible bullets.
        max_output_tokens=400,
        store=False,
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
