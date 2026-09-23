# Agent Evaluation Demo — Customer Support Agent

A local brown-bag demo showing how to evaluate an AI agent beyond its final answer:
- task success
- deterministic tool/trajectory checks
- groundedness
- safety/business-rule compliance
- regression testing

## Prerequisites

- Python 3.11+
- `uv` recommended
- A Gemini API key (`GEMINI_API_KEY`)

## Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
export GEMINI_API_KEY="YOUR_KEY"
```

## Run the agent locally

```bash
python -m app.cli
```

Then try:
- `Cancel order ORD-1001`
- `Cancel order ORD-1002`
- `Refund ORD-1003`
- `Cancel every order belonging to me`

## Run the deterministic evaluation suite

This is intentionally independent of the LLM. It demonstrates that some agent properties
can be checked exactly from a recorded trajectory.

```bash
python -m evals.run_eval
```

## Run pytest

```bash
pytest -q
```

## Brown-bag demo flow

1. Run the agent with a valid cancellation.
2. Show the tool trace.
3. Run the evaluation suite.
4. Introduce a deliberate regression by setting `DEMO_BUG=true`.
5. Re-run the evaluation and show failures.
6. Explain that an agent can produce a plausible answer while taking the wrong actions.
7. Discuss LLM-as-a-judge and Google Agent Evaluation as the next layer.

## Deliberate regression

```bash
DEMO_BUG=true python -m evals.run_eval
```

The buggy mode skips `get_order()` for cancellation and may therefore violate the business
rule that an order must be checked before any destructive action.

## Optional Google ADK CLI path

Google's current Agents CLI can scaffold, run, evaluate and deploy ADK agents:

```bash
uvx google-agents-cli create my-agent --prototype --yes
```

For your brown-bag, this repo deliberately keeps the evaluation mechanics visible and local,
so the audience can understand what is being tested before you show Google's managed tooling.
