# Millenium decision and agent demos

Five deliberately small demos based on the pod-risk example in the attached deliverable. They use fake data and do not connect to a trading system.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Credentials live only in `.env.local`, which is ignored by Git. `.env.example` documents the variable names without containing secrets. Add an `ANTHROPIC_API_KEY` to `.env.local` only if you want to run the Claude demo.

## Run

```bash
python run_demo.py decisions
python run_demo.py responses
python run_demo.py langgraph
python run_demo.py openai-agents
python run_demo.py claude-agent
```

`python run_demo.py all` runs all five sequentially and therefore requires both provider keys.

The API-backed demos may incur provider charges. The LangGraph demo is entirely local and makes no network request.
