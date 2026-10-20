"""OpenAI Agents SDK: one specialist, one turn, and no tools."""

import asyncio

from agents import Agent, Runner

from demo_common import POD_SUMMARY, load_project_env, require_env


async def run_agent() -> str:
    agent = Agent(
        name="Pod risk explainer",
        model="gpt-6-astra",
        instructions=(
            "Explain only the supplied metrics. Do not calculate new metrics, use "
            "tools, recommend trades, or make a final risk decision. Answer in two "
            "sentences."
        ),
        tools=[],
    )
    result = await Runner.run(agent, POD_SUMMARY, max_turns=1)
    return str(result.final_output)


def main() -> None:
    load_project_env()
    require_env("OPENAI_API_KEY")
    print(asyncio.run(run_agent()))


if __name__ == "__main__":
    main()
