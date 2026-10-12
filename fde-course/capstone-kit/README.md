# FDE Playbook capstone kit

A small, real repository template for the **Foundations portfolio capstone** (course module C8). You copy it, run it on your own machine with your own Anthropic API key, make it your own, and end up with a project you can defend in a project deep dive.

The browser course runs a simulator that never calls a real model. This kit is where real outputs, real variance, real refusals, real latency and real cost show up.

What's inside:

| Folder | What it is |
|---|---|
| `app/` | A tool-using support agent (manual tool loop on the real SDK), a tiny BM25 retriever, a fake "customer system", a hand-written MCP server and client, and a stdlib HTTP service |
| `evals/` | Golden set (JSONL), runner over N runs with Wilson intervals, LLM judge with rubric and rationale, judge calibration with Cohen's kappa, CI gate |
| `labs/` | Four real-model labs that mirror in-course exercises, each with a results template you paste into C8 |
| `briefs/` | Capstone briefs for three tracks: engineer, architect, FDE |
| `typescript/` | `@anthropic-ai/sdk` streaming chat route, tool loop and MCP server, with vitest tests that run without a key |
| `infra/` | Dockerfile and a commented Terraform skeleton |
| `.github/workflows/evals.yml` | Runs unit tests, then the evals and the gate against the real model |
| `tests/` | Unit tests for the pure parts (statistics, gate, retrieval, costs, agent loop with a fake client, MCP) |

The sample data describes **Quillfeather Stationery**, a fictional online shop. It exists so everything runs on day one. Replace it.

## Setup (10 minutes)

You need Python 3.11 or newer. Node 20+ only for `typescript/`.

```bash
cp -r capstone-kit ~/my-capstone && cd ~/my-capstone && git init
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                 # or: python -m unittest discover -s tests -t .   (no key needed)

export ANTHROPIC_API_KEY=sk-ant-...  # from the Claude Console; never commit it
python -m app.agent "Where is my order QF-1002?"
```

The agent prints its answer to stdout and a JSON trace (tool calls, stop reasons, usage, cost, request ids) to stderr.

Run everything from the repo root, because the scripts use `python -m` module paths.

## Budget (target: under $5 for the whole capstone)

You pay for your own usage. The course owner never sees your key or your bill. Keep it cheap on purpose:

1. **Set a spend limit in the Claude Console** before you start. Check the Console for where limits live on your account.
2. **Default to Claude Haiku 5.5** (`claude-haiku-5-5`, $0.10 input / $0.50 output per million tokens for prompts up to 100K tokens). Use **Claude Sonnet 5.5** (`claude-sonnet-5-5`, $2 / $10) for the judge and for one comparison run. Prices were checked on 2026-10-10; check the pricing page again before you quote them.
3. **Always set `effort` explicitly.** All three current models think by default (adaptive thinking). Defaults differ: Haiku 5.5 and Opus 5.5 default to `medium`, Sonnet 5.5 to `high`. Thinking tokens are billed as output, count against `max_tokens`, and sit inside time to first token. This kit sends `effort: "low"` unless you change it.
4. **Cache the stable prefix.** The kit puts a `cache_control` breakpoint on the system prompt. It only helps when the prefix is at least 512 tokens (current models) and is reused within 5 minutes. Cache writes cost about 1.25x input; reads cost 0.05x input on Sonnet 5.5 and Opus 5.5 and 0.1x on Haiku 5.5. Check `cache_read_input_tokens` in the usage to see whether it worked.
5. **Every script stops at `CAPSTONE_BUDGET_USD`** (default $1.00 per run). Raise it on purpose, not by accident.
6. **Smoke-test first:** `python -m evals.run_evals --runs 1 --no-judge --limit 3` costs well under a cent.

Rough costs on the defaults: the four labs together well under $2; a 50-case golden set run 3 times with a Sonnet judge about $1 to $2. Your results files record the measured figure; use those in your README, not these estimates.

## Make it your own

The deep dive will ask "what was your part?" The answer has to be obvious from the repo.

1. **Pick a domain you can explain**, ideally one you know from work or a hobby: a public dataset (government help pages, an open-source project's issues and docs, a public FAQ), or synthetic data you write yourself. Never use a real employer's or customer's confidential data.
2. **Replace `app/data/`** with your documents and records, and rewrite the tools in `app/tools.py` and `app/customer_system.py` for your system.
3. **Write your golden set before you tune anything.** At least 40 to 60 cases, labelled from the source documents, with deliberate edge cases (ambiguity, missing data, injection attempts, out-of-scope). Keep a held-out slice.
4. **Change one big thing** from this template and measure it: hybrid retrieval, a router to a cheaper model, a sub-agent, a different tool design. That change and its numbers are the heart of your story.
5. **Write the decision record as you go**, not at the end. Each decision: the options, what you measured, what you chose, what it cost.

## Deliverables checklist

Pick a track brief in `briefs/` first. Every track needs:

- [ ] A README a reviewer can read in five minutes: what it does, how to run it, results, decisions, limits
- [ ] A golden set of 40+ labelled cases with edge cases, and the eval runner output from at least 3 runs
- [ ] Results as counts with 95% intervals and the run-to-run spread, errors and refusals reported separately
- [ ] A judge calibrated against your own labels (kappa reported), or a stated reason you didn't need one
- [ ] A CI gate that fails on regression (`evals/gate.py` and the workflow)
- [ ] A cost and latency table from measured usage: model, effort, tokens including thinking, cost per request, p50 and p95
- [ ] A failure log: real failing cases, grouped by type, with what you changed
- [ ] A decision record: three to five decisions with rejected alternatives
- [ ] The four lab reports pasted into module C8
- [ ] Track extras from your brief (TCO sheet and memos for architects; MCP, Dockerfile, Terraform and demo script for FDEs)

Then paste your README into the C8 lesson "Capstone README and Decision Record". The practice reviewer in C8, and the deep-dive personas in the E7, A7 and FDE 11 loops, read it before they question you.

## Using AI while you build

Follow the hiring company's rules for any take-home. Anthropic's candidate AI guidance asks for your own first drafts and no AI help in take-homes or live interviews unless permitted. For your own portfolio project there is no rule against coding assistants, but you must be able to explain every line and every number, and you should say in the README how you used them. Claude inside the product is the point of the project; Claude writing your decision record is not.

## Notes on the code

- `app/agent.py` writes the tool loop by hand. The SDK's tool runner (beta) can run it for you; the manual loop is here so you can explain every `stop_reason` branch (`tool_use`, `pause_turn`, `refusal`, `max_tokens`, `end_turn`) and why history is append-only (thinking blocks go back unmodified).
- Forcing a tool call with `tool_choice` returns a 400 on Opus 5.5 and Sonnet 5.5. Steer with the prompt and use `strict: true` tool schemas instead.
- `app/mcp_server.py` is a hand-written, minimal JSON-RPC stdio server, labelled as such. Use an official MCP SDK for anything real and check its current docs.
- Structured outputs use `output_config.format` with a JSON schema; the kit checks `stop_reason` before parsing.
