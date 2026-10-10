---
title: "Write It: A Cost and Caching Plan"
type: written
minutes: 40
sections:
  - key: assumptions
    label: Assumptions and token budget
    prompt: "List your assumptions (model, effort, tokens per part of the request, output including thinking, traffic shape). Break one request into its parts with a token count for each."
    words: [60, 180]
  - key: estimate
    label: The estimate
    prompt: "Show the daily cost with no caching and with your caching design, with the arithmetic. Name the model and its prices. Include the US-only requirement."
    words: [100, 260]
  - key: layout
    label: Prompt layout for caching
    prompt: "Describe the order of the request (tools, system, messages), where your cache breakpoints go, which TTL you'd use and why."
    words: [80, 200]
  - key: verify
    label: Verification and risks
    prompt: "How will you prove the cache is hitting in production, and what could quietly break it or blow up the estimate?"
    words: [80, 200]
  - key: recommendation
    label: Recommendation
    prompt: "In a few sentences, as you'd say it to the interviewer: what you'd ship first, the number to remember, and the next lever."
    words: [40, 120]
rubric:
  - name: Assumptions and token budget
    points: 15
    lookFor: "States the model, the effort setting and the traffic shape before calculating. Breaks a request into stable prefix (instructions, handbook), per-claim content, question and output, with token counts. Counts thinking inside output or sets effort explicitly."
  - name: Correct arithmetic, model named
    points: 25
    lookFor: "Uncached and cached daily costs follow correctly from the stated assumptions (per million token prices divided correctly, volume applied once). Names the model whenever quoting a cache-read price. Applies the 1.1x US-only multiplier (inference_geo us) or a regional-endpoint premium, and says which platform it assumes."
  - name: Cache-aware prompt design
    points: 20
    lookFor: "Puts the stable handbook first and the volatile question last. Places a breakpoint after the stable prefix, and considers a second breakpoint after the claim file because adjusters ask several questions per claim. Picks a TTL from the request rate (5-minute is warm at this volume) with a reason."
  - name: Effort, thinking and levers
    points: 15
    lookFor: "Sets effort explicitly or shows a thinking-token line. Orders the levers: caching first, then effort, then a smaller model, with an eval gate before switching model. Notes Haiku 5.5's lower price and its 100K-token price step, or another sound model comparison."
  - name: Verification and risks
    points: 15
    lookFor: "Verifies with usage.cache_read_input_tokens and a standing test or monitor. Names concrete silent invalidators (timestamps or IDs in the system prompt, unstable tool or JSON order, model or effort changes, edited history) and estimate risks (longer outputs, retries, tokenizer differences, traffic peaks)."
  - name: Clear, interview-ready communication
    points: 10
    lookFor: "The recommendation leads with the per-request and daily numbers and the next lever, in plain words a design-round interviewer could follow aloud."
passScore: 70
graderNotes: |
  Reference numbers (accept other reasonable assumptions if the arithmetic is consistent with them). Sonnet 5.5 list prices per million tokens: input $2, output $10, 5-minute cache write $2.50, 1-hour write $4, cache read $0.10 (0.05x). Haiku 5.5: $0.10 input, $0.50 output, cache read $0.01, for prompts up to 100K tokens. Opus 5.5: $4 / $20, cache read $0.20.
  With 60K handbook + 8K claim file + 100-token question + 600 output tokens (effort low, thinking included), 30,000 requests a day on Sonnet 5.5: uncached is about 68.1K x $2/M + 600 x $10/M = about $0.142 per request, about $4,270 a day. Caching the handbook only: 60K x $0.10/M + 8K x $2/M + 100 x $2/M + 600 x $10/M = about $0.028 per request, about $850 a day. Also caching the claim file with a second breakpoint, at 5 questions per claim, brings it to roughly $0.017 per request, about $500 a day. US-only on the Claude API multiplies everything by 1.1. 30,000 requests over 10 hours is about 50 a minute, so the 5-minute TTL stays warm; the 1-hour TTL adds cost for no benefit here.
  Mark down: quoting a cache saving without naming the model; using 0.1x reads for Sonnet 5.5 (it is 0.05x) is a minor error, not a fatal one; ignoring thinking entirely and not setting effort; forgetting the US-only multiplier; dividing by 1,000 instead of 1,000,000; caching the per-request question; putting the claim file or a timestamp before the handbook; switching to a smaller model with no eval. Cap 'Correct arithmetic' at 10 if the uncached figure is off by more than 3x from the learner's own assumptions. Do not penalise a learner who chooses Haiku 5.5 or Opus 5.5 if the reasoning and numbers are sound.
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Assumptions: we use Claude. Each request is about 70K tokens. Estimate: 70K tokens x 30,000 = 2.1B tokens, at $2 per token-ish it's expensive, caching saves 90%. Layout: turn on caching for the whole prompt. Verify: check the bill goes down. Recommendation: use caching and a cheaper model."
  - label: strong
    expect: [75, 100]
    answer: "Assumptions: Sonnet 5.5 on the Claude API with inference_geo us, effort low. Per request: 60K handbook, 8K claim file, 100-token question, 600 output tokens including thinking. 30,000 requests over 10 hours, about 50 a minute, about 5 questions per claim. Estimate: uncached 68.1K x $2/M = $0.136 plus 600 x $10/M = $0.006, so $0.142 a request, $4,270 a day, $4,700 with the 1.1x US multiplier. Caching the handbook (Sonnet 5.5 reads at $0.10/M): $0.006 + $0.016 claim + $0.0002 + $0.006 = $0.028, about $850 a day ($930 US-only). A second breakpoint after the claim file gets it to about $0.017, $500 a day ($560). Layout: tools sorted, then system with instructions and handbook, breakpoint; then the claim file as the first user content, breakpoint; then the question. 5-minute TTL: at 50 a minute it never goes cold, and claim follow-ups come within minutes. Verify: a CI test sends two identical requests and asserts cache_read_input_tokens > 0; a dashboard on cache-read share by route. Risks: a timestamp or adjuster name in the system prompt, unsorted tool JSON, varying effort per request, longer answers than assumed, retries. Recommendation: about 2 cents a request and $560 a day instead of $4,700. Ship caching first, then test Haiku 5.5 against an eval of 300 real adjuster questions; if it holds the bar, the bill drops by another order of magnitude."
---

Your interview coach, Nadia Okafor, ends every mock design round the same way: "Good architecture. Now cost it, cache it, and tell me how you'd know it's working." This written exercise is that last ten minutes, done properly once so you can do it fast in the room. The scenario is original and fictional, in the style of an LLM system design round.

## The scenario

Ferncastle Insurance (a fictional company) wants an assistant for its claims adjusters. An adjuster opens a claim and asks questions such as "Does this policy cover water damage from a burst pipe?" The assistant answers from two sources:

- **The policy handbook:** about 60,000 tokens of instructions and coverage rules. It changes once a quarter.
- **The claim file:** about 8,000 tokens per claim. An adjuster usually asks around five questions about the same claim within a few minutes.

Volume and constraints:

- About **30,000 questions a day**, spread over a 10-hour working day.
- Answers are short, about 300 visible tokens.
- **All processing must stay in the US.**
- Adjusters are waiting, so time to first token matters.

## Your task

Write the five sections on the right. Use the prices from lessons 1 and 6 (the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) is the source if you want to check). Pick any current model, but name it, set effort explicitly or include a thinking line, and show your arithmetic. A tidy table is welcome.

You'll be graded on the reasoning as much as the totals. A clear estimate with one wrong multiplication scores better than a correct number with no working.

## Before you submit

- Did you name the model every time you quoted a cache-read price?
- Did you count thinking as output, or set effort?
- Did you apply the US-only requirement to the price?
- Could you say your recommendation out loud in under 30 seconds?
