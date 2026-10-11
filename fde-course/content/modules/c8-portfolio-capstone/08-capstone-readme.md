---
title: "Capstone README and Decision Record"
type: written
minutes: 60
sections:
  - key: overview
    label: 1. What it is and your part
    prompt: "Track, domain and the user problem in two or three sentences. What the system does, how to run it and its eval (commands), the model and effort. Then say exactly what you built yourself versus what came from the kit, and how you used AI tools while building."
    words: [80, 300]
  - key: architecture
    label: 2. How it works
    prompt: "The request path from input to answer: components, tools or retrieval, where the model is called, what is validated in code, and what needs human approval. A short ASCII or Mermaid diagram is welcome."
    words: [100, 400]
  - key: results
    label: 3. Results
    prompt: "Golden set (size, source, who labelled it, edge cases, held-out slice), headline results as counts with 95% intervals over at least 3 runs, run-to-run spread, errors and refusals, judge calibration (kappa), and the cost and latency table from measured usage."
    words: [120, 450]
  - key: decisions
    label: 4. Decision record
    prompt: "Three to five decisions. For each: the options, what you measured or reasoned, what you chose, what it cost, and what would make you revisit it. One of them should be your one measured improvement, with before and after numbers."
    words: [180, 600]
  - key: limits
    label: 5. Failures and limits
    prompt: "Your failure log in brief (failure types with counts and one real example), what your eval can't tell you, and what production would need that you didn't build."
    words: [80, 350]
rubric:
  - name: Clear scope and an obvious personal part
    points: 15
    lookFor: "A reviewer knows in a minute what it does, for whom, how to run it, which model and effort, and what the learner built versus what came from the kit. AI-tool use while building is disclosed."
  - name: Architecture a reviewer can follow
    points: 15
    lookFor: "The request path is concrete: components, model calls, tools or retrieval, validation in code, approval for writes, how stop reasons and errors are handled. Any diagram matches the text."
  - name: Evidence, not adjectives
    points: 25
    lookFor: "Golden set of 40 or more labelled cases with deliberate edge cases and a held-out slice; results as counts with intervals over 3 or more runs; spread reported; errors and refusals separate; judge kappa; cost and latency from measured usage with thinking tokens included."
  - name: Decisions with rejected alternatives
    points: 30
    lookFor: "Three to five real decisions, each with options, evidence, choice, cost and a revisit trigger. At least one measured improvement with before and after numbers and an honest read of whether the gap beats the noise."
  - name: Honest failures and limits
    points: 15
    lookFor: "Failure types with counts and a real example; what the eval can't show (sample size, synthetic data, one domain); a realistic production list (monitoring, human review, data handling, a regression gate)."
passScore: 70
graderNotes: "This README is read later by deep-dive personas, so grade it as a reviewer would before an interview. Reward evidence and judgement, not length or polish. If results have no case counts, cap 'Evidence, not adjectives' at 10. If there are fewer than 40 cases with no acknowledgement, cap it at 14. If cost ignores thinking tokens or isn't from measured usage, deduct 5 from 'Evidence, not adjectives'. If no decision names a rejected alternative, cap 'Decisions with rejected alternatives' at 10. If 'we' is used throughout with no stated personal part, cap 'Clear scope and an obvious personal part' at 6. If the project appears to use a real employer's or customer's confidential data, say so in feedback and cap 'Honest failures and limits' at 5. If the learner says plainly the project is not finished and reports partial results honestly, grade what is there; don't punish honesty."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Overview: We built an AI agent for customer support using Claude. Architecture: the user asks a question, Claude answers using tools. Results: it works really well, about 95% accurate in testing. Decisions: we chose Claude because it is the best model and used RAG because it reduces hallucinations. Limits: none major, it is production ready."
  - label: strong
    expect: [75, 100]
    answer: "Overview: Engineer track. A question-answering agent over my city's public permit-office help pages (212 pages scraped from the public site) for residents planning home renovations. `python -m app.agent`, `python -m evals.run_evals --runs 3`. claude-haiku-5-5 at effort low for answers, claude-sonnet-5-5 low as judge. I replaced the kit's data, tools and golden set, wrote the hybrid retriever and the permit-type router; the loop, gate and stats come from the kit. I used a coding assistant for test scaffolding and wrote the README myself. Architecture: question -> router (Haiku, structured output: permit type or 'unsure') -> hybrid retrieval (BM25 plus embeddings, top 6 chunks) -> answer with citations -> code checks that every citation id exists, else one retry, else 'I'm not sure, here's the office number'. One write tool (book an appointment) is stubbed and needs approval. Results: 56 cases written from the pages before tuning, 14 edge cases (out of scope, outdated rules, two permit types, an injection in a page), 12 held out. 3 runs: 41, 43 and 42 of 56 (pooled 126/168, 75%, Wilson 68% to 81%); 5 flaky cases, all two-permit questions; 2 errors (timeouts) excluded; 0 refusals in 168 (upper bound about 2%). Judge kappa 0.78 against my labels on 30 items. Cost from usage: mean 3,900 input, 310 output including 120 thinking: $0.00055 per question on Haiku; p50 2.1 s, p95 4.8 s. Decisions: (1) Hybrid retrieval over BM25 alone: recall@5 31/50 vs 42/50 on chunk-labelled queries; costs an embedding index. (2) Haiku low over Sonnet low for answers: 42/56 vs 45/56 mean over 3 runs, inside overlapping intervals, at about a twentieth of the price; revisit if the held-out gap grows. (3) Refuse rather than guess when citations fail: cost 4 'not sure' answers on answerable questions. Failures: 8 wrong permit type (two-permit questions), 4 answers citing an outdated page, 2 missed the fee. Limits: one city, synthetic questions written by me, no real users; production needs freshness checks on pages, a feedback button, weekly sampled human review and the CI gate on every prompt change."
---

This is the README for your Foundations portfolio capstone: the document a reviewer reads first. It's also the lesson other modules point to. The deep-dive personas in E7 (Marcus), FDE module 11 (Theo) and the practice reviewer in the next-but-one lesson receive what you write here as context before they question you. Write it as if a staff engineer will read it the night before your interview, because in the role-plays one will.

Write it yourself. Anthropic's [candidate AI guidance](https://www.anthropic.com/candidate-ai-guidance) asks for your own first drafts (**Official**), and you'll need to defend every sentence out loud.

## Before you start

- Run your eval at least three times and keep the results files open. Every number below should come from them.
- Use `capstone-kit/README.md`'s deliverables checklist and your track brief in `capstone-kit/briefs/`.
- Keep confidential data out. If your domain uses a fictional customer, say so.

## What good looks like

Five sections, the same order a reviewer reads in. Counts, not just percentages. Each decision has an alternative you rejected and the evidence. Limits are stated before the reviewer has to ask. If your project isn't finished, say what is and isn't done: an honest partial README beats a polished fiction, and the personas are told to probe claims that don't add up.

Paste the same text into the `README.md` of your repository.
