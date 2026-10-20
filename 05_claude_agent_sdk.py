"""Claude Agent SDK: one stateless, tool-less agent turn."""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from demo_common import POD_SUMMARY, load_project_env, require_env


BLOCKED_TOOLS = [
    "Bash",
    "Edit",
    "Write",
    "Read",
    "Glob",
    "Grep",
    "WebSearch",
    "WebFetch",
    "Task",
]


async def run_agent() -> None:
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

    async for message in query(prompt=POD_SUMMARY, options=options):
        if isinstance(message, ResultMessage):
            print(message.result)


def main() -> None:
    load_project_env()
    require_env("ANTHROPIC_API_KEY")
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
