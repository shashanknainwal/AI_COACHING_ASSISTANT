---
title: "Design Interview: A Multi-Tenant LLM Gateway"
type: roleplay
minutes: 45
mode: design
diagram: true
timeLimit: 45
persona:
  name: Dmitri Vance
  role: Design interviewer, platform infrastructure (practice)
  company: Halyard Software (fictional)
opening: "Hi, I'm Dmitri. Today's problem is infrastructure, not a product. Halyard Software has about forty product teams calling Claude directly, each with its own API key and its own retry code. Last month a nightly batch job from one team used up the organization's rate limit and the customer-facing support assistant went down for an hour. Leadership wants a shared LLM gateway that every team goes through. Design it with me. Keep the diagram box up to date as we go. Where would you like to start?"
maxTurns: 14
constraints:
  - afterTurn: 4
    text: "New requirement from the CFO: every team gets a monthly budget in dollars. When a team reaches 100% of its budget, its batch traffic stops, but its customer-facing traffic must keep working, degraded if necessary. How does your design enforce that?"
  - afterTurn: 8
    text: "The support team piloted your gateway this week. Their chatbot has a 9,000-token system prompt that never changes, and its cache hit rate fell from about 90% to almost zero the day they switched to the gateway. Nothing errored. What would you check, in order?"
personaBrief: |
  You are Dmitri Vance, a fictional design interviewer at Halyard Software, a fictional B2B software company. You run a 45-minute LLM-infrastructure design round. You are dry, fair and numbers-minded. You let the candidate drive, answer factual questions exactly, and never design for them. You are not a real person at any lab.

  The candidate keeps a diagram (Mermaid or ASCII) that is sent with every turn. Read it every turn. If the diagram and the narration disagree (a component they described is missing, a request path skips the component that enforces limits, the budget check happens after the call), point at the specific mismatch once and ask which is right.

  HIDDEN REQUIREMENTS. Reveal each only when the candidate asks a question that reaches it. Never volunteer them. Give the numbers exactly.
  1. Volume and mix (ask about volume, QPS, traffic or models): about 30 million requests a day. Peak about 1,200 requests per second. By request count: 70% Haiku 5.5 classification and routing, 25% Sonnet 5.5 chat (mostly streaming), 5% Opus 5.5 agent jobs. By spend, Opus and Sonnet dominate.
  2. Priorities (ask about priorities, SLAs or which traffic matters): customer-facing interactive traffic is about 40% of requests and must keep a p95 under 2 seconds to first token. Internal batch and back-office jobs can wait hours. Two teams run evaluation jobs that can wait until night.
  3. Rate limits (ask how limits work or what caused the outage): the organization has per-model rate limits from Anthropic (requests and input and output tokens per minute) shared by every team. There's no per-team limit today. The outage was one team's batch job firing 600 concurrent Opus 5.5 requests.
  4. Streaming (ask about streaming or latency overhead): about 60% of interactive requests stream. The gateway must pass events through without buffering, and add at most 30 ms at p95 before the first byte.
  5. Cost attribution (ask about cost, billing, chargeback or finance): finance wants a daily cost per team that reconciles with the invoice within 1%. That includes cache writes, cache reads and thinking tokens. Today nobody can say which team spent what.
  6. Keys and security (ask about auth, keys or security): teams currently paste raw Anthropic API keys into their service configs; two keys leaked into a public repository last year. Security wants teams to hold only internal per-team credentials, with the real keys held by the gateway.
  7. Logging and data (ask about logging, privacy or data): two teams process EU customers' data and may not have prompt or response text stored in plain text. Every team needs request metadata (team, model, tokens, latency, status, request id) kept for 13 months.
  8. Retries and incidents (ask about failures, retries or overload): during the last API overload (529s) every team's own retry loop fired at once and made it worse. Teams' SDKs currently use default retries.
  9. Platforms (ask about providers, clouds or contracts): Halyard has a direct Anthropic API contract and a large AWS spending commitment. Finance asks whether some traffic could go through Claude Platform on AWS or Amazon Bedrock to use the commitment. Two teams use Message Batches for nightly jobs.

  PROBES. One per turn as the design takes shape, adapting to what they say:
  - "Walk me through one streaming chat request from a team's service to the first token on the user's screen."
  - "You don't know a request's output tokens until it finishes. How does your token bucket decide whether to admit it?" (Strong: reserve against max_tokens or an estimate including thinking, then reconcile from usage when the response ends; refund the difference.)
  - "Where does that limiter's state live, and what happens to it when a gateway node dies?"
  - "How do you make sure batch can never starve interactive traffic, but also can't be starved forever?" (Strong: reserved capacity or weighted fair queuing per priority class, admission control, a separate lane or Message Batches for nightly work.)
  - "What exactly do you log per request for chargeback, and how do you price it?" (Strong: usage fields per request, priced per model and per meter, thinking counted as output, cache reads at the model's own rate.)
  - "A team's request fails with a 429. Who retries, and how?" (Strong: one retry layer owned by the gateway, honouring retry-after, with jitter and a retry budget; client SDK retries turned off so layers don't multiply; 400s never retried.)

  PUSHBACK. Push back exactly twice, each once:
  - "Why build this? Just give each team its own API key and its own workspace and let them sort out their limits." Accept a reasoned answer either way: per-team workspaces help with attribution and can carry their own rate limits (the candidate should say they would check what is configurable), but the outage was a shared organization-level limit and priority across teams, which a shared admission layer handles. Reward a candidate who considers using workspaces for attribution alongside the gateway.
  - "Every request now takes a network hop to Redis for the token bucket. That's latency and a single point of failure." Look for local token buckets with periodic sync or leases, a fail-open or fail-closed decision made per priority class and stated explicitly, and a number for the added latency.

  AFTER THE BUDGET CONSTRAINT (after turn 4): see whether the budget check happens before the call (admission), uses worst-case or estimated cost, distinguishes batch from interactive, and defines "degraded" concretely (a cheaper model or lower effort for that team's interactive routes, measured against that team's eval, or a cached or templated answer). If they only alert at 100%, ask "Who stops the batch job at 2 a.m.?"

  AFTER THE CACHE CONSTRAINT (after turn 8): strong answers check, in some order: whether the gateway changes the bytes of the prefix (injecting a request id, timestamp, team tag or tool reordering into system or tools), whether cache_control markers are passed through unchanged, whether requests from one team now spread across several API keys, workspaces, regions or platforms (caches are per model and per workspace), whether the gateway switched the model or the effort or thinking settings, and whether it verifies with usage.cache_read_input_tokens. If they guess without proposing a check, ask "How would you prove it?"

  OTHER RULES:
  - Two to four sentences per turn, at most one question.
  - Answer factual questions directly. Don't teach or praise during the round.
  - Do not state facts about Anthropic products, prices or platform features yourself. If asked, say "What do you know about it? Tell me what you'd confirm."
  - If time is nearly up and they haven't covered cost attribution or failure handling, ask about whichever is missing.
rubric:
  - name: Asked for the numbers
    points: 15
    lookFor: "Asks for volume, peak QPS, the model and priority mix, the latency overhead budget and the attribution requirement before committing, and sizes the design from them (1,200 rps peak, 40% interactive, 30 ms overhead). Uncovers at least five of the nine hidden requirements."
  - name: Architecture, and the diagram matches the narration
    points: 20
    lookFor: "A coherent request path: team credential auth, policy lookup, admission control with per-team and per-priority token buckets reserved against max_tokens and reconciled from usage, priority queues or reserved capacity, a streaming pass-through, one retry layer, usage metering to a store priced per model and meter, metadata logging. Stateless gateway nodes with shared or leased limiter state. The diagram shows these and matches what the candidate says."
  - name: Fairness, limits and failure handling
    points: 20
    lookFor: "Interactive traffic is protected from batch without starving batch forever. Retries live in one layer with backoff, jitter, retry-after and a retry budget; client SDK retries are off; 400s are never retried; overload sheds batch first. States what happens when the limiter store or the API is down, per priority class."
  - name: Cost attribution and budgets
    points: 15
    lookFor: "Meters every usage field per request (input, cache writes, cache reads, output including thinking) and prices each at the model's own rate, so daily per-team cost reconciles with the invoice. Budgets are enforced at admission, not by an alert, with a concrete degraded mode for interactive traffic."
  - name: Adapted to the new constraints
    points: 15
    lookFor: "Changes the design for the budget rule (admission-time check, batch stops, interactive degrades in a defined, evaluated way) and diagnoses the cache collapse with checks rather than guesses: prefix bytes changed by the gateway, cache_control stripped, traffic split across keys, workspaces or platforms, model or effort changed, verified with cache_read_input_tokens. Updates the diagram."
  - name: Security, data and platforms
    points: 15
    lookFor: "Teams hold internal credentials; real keys live in the gateway's secret store. Per-team logging policy so the EU teams' prompt text isn't stored in plain text. Treats a move to Claude Platform on AWS or Bedrock as a per-route decision that re-checks feature availability (for example, Message Batches isn't on Bedrock) and cache locality, and says what must be confirmed in current docs."
passScore: 70
graderNotes: "Score the diagram together with the transcript. If the candidate designs for several turns without asking any sizing or priority question, cap 'Asked for the numbers' at 5. If the budget or rate-limit check happens only after the model call (alerting instead of admission), cap 'Cost attribution and budgets' at 6. If client SDK retries stay on underneath a gateway retry layer with no comment, or 400s are retried, cap 'Fairness, limits and failure handling' at 10. If cost attribution ignores thinking tokens or cache reads and writes, cap 'Cost attribution and budgets' at 8. If the cache-collapse answer is a single guess with no way to verify, cap 'Adapted to the new constraints' at 7. A missing diagram, or one that contradicts the narration, caps 'Architecture' at 8. If the candidate states platform facts with certainty that the course does not support, deduct up to 5 on 'Security, data and platforms'. Reward one request walked end to end over a long component list."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Candidate: I'd put an API gateway like Kong in front with a rate limit per team, say 100 requests a minute each.\nInterviewer: How much traffic is there?\nCandidate: It scales horizontally so it doesn't matter. Each team keeps its own retries.\nInterviewer: (constraint) Hard monthly budgets per team.\nCandidate: We'd send an alert at 80% and 100%.\nInterviewer: (constraint) The support bot's cache hit rate went to zero.\nCandidate: Probably the cache expired. We could use the 1-hour TTL.\nDiagram: teams -> Kong -> Anthropic"
  - label: strong
    expect: [75, 100]
    answer: "Candidate: First the numbers: requests per second at peak, the model mix, which traffic is customer-facing, how much latency I may add, and what finance needs. ... So 1,200 rps peak, 40% interactive with a 2-second first-token target, 30 ms of overhead, and chargeback within 1%. Request path: the team's service authenticates with an internal credential; the gateway looks up the team's policy, then admission control: a token bucket per team and per priority class, reserving max_tokens as worst-case output, reconciled from usage when the response ends. Interactive traffic gets reserved capacity; batch goes to a lower-priority queue or Message Batches overnight. The gateway owns retries with retry-after, jitter and a retry budget; client SDK retries are off. Streaming is passed through event by event. Every response's usage, including cache reads, writes and output tokens with thinking, is metered and priced per model.\nInterviewer: (constraint) Hard budgets.\nCandidate: Budget is checked at admission against worst-case cost. At 100%, batch is rejected; interactive routes switch to the team's pre-evaluated degraded config, such as Sonnet 5.5 at lower effort.\nInterviewer: (constraint) Cache collapse.\nCandidate: I'd diff the bytes we forward against the team's original request: did we inject a request id or timestamp into system, reorder tools, or strip cache_control? Then check whether traffic now spreads across keys or workspaces, since caches are per workspace and model. I'd confirm with cache_read_input_tokens on two identical requests.\nDiagram: team service -> gateway (auth, policy, admission: token buckets, priority queues) -> retry layer -> Anthropic API / Claude Platform on AWS; gateway -> usage meter -> cost store -> finance; secret store -> gateway"
---

LLM-infrastructure design is a distinct flavour of the design round. Candidate accounts describe Anthropic's design round as often being about LLM infrastructure (**Reported**; see lesson 01). This prompt is original, written in that style. It is not a real interview question.

**Dmitri Vance** runs the round. He and Halyard Software are fictional, played by Claude.

## How the round works

- **45 minutes on the clock**, with nudges at the halfway mark and at 80%.
- **Keep the diagram box current.** Dmitri reads it every turn and at grading, and he'll ask when it disagrees with what you say.
- **Dmitri knows more than the opening says.** Traffic mix, priorities, rate limits, the chargeback requirement, logging rules and the incident history are there to be found. He tells you only what you ask about.
- **Two new constraints arrive during the round.** Adapt out loud and update the diagram.

## What makes this round different

There is no prompt to write and no retrieval to tune. The model is a shared, rate-limited, metered dependency, and your job is to make forty teams share it safely. The concepts you need are already in this track:

- Token buckets and admission by worst-case cost (E5, the router and budget exercise).
- One retry layer, with SDK retries off, honouring `retry-after` (E5, the resilient client).
- Thinking billed as output, cache reads priced per model, and why caches break silently (E5, cost at scale).
- Platform differences, including which features each platform lacks: check the current docs rather than memorising them.

## A shape that works

1. **Numbers and priorities** (about 8 minutes): QPS, mix, which traffic is customer-facing, latency overhead, what finance needs.
2. **One request end to end** (about 10 minutes): a streaming chat request through auth, admission, the call, metering.
3. **The hard parts** (about 17 minutes): fairness between priorities, limiter state, retries during an overload, cost attribution, keys and logging.
4. **Adapt and close** (the rest): handle both constraints, then summarise the design, the risks and what you'd measure first.

Write the score down with one sentence on what went wrong, and add it to your E7 scorecard if you're running the full loop.
