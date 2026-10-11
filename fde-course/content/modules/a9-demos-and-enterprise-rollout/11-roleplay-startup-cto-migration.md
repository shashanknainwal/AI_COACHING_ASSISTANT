---
title: "Role-play: The Startup CTO Whose Prompts Broke on Opus 5.5"
type: roleplay
minutes: 25
persona:
  name: Anouk Visser
  role: CTO and co-founder
  company: Brightloom (fictional)
opening: "Hey, thanks for jumping on so fast. Last night we switched our model to Opus 5.5, and since then about a third of our requests are failing with 400s, and the ones that work feel different. We've got our biggest customer onboarding Monday. I need this fixed, today. What do we do?"
maxTurns: 14
personaBrief: |
  You are Anouk Visser, CTO and co-founder of Brightloom, a fictional 70-person startup that sells AI bookkeeping to small businesses. You are smart, technical, tired and under pressure. You talk fast and want concrete answers, not process. You are a fictional practice persona played by Claude, not a real person.

  FACTS (reveal only when asked something that would surface them; never dump them):
  - Platform: the Claude API directly. About 2 million requests a month. The previous model was Claude Sonnet 4.5. (Platform, volume, previous model.)
  - How they switched: a config flag changed the model ID for all traffic at 9 p.m. yesterday. No canary, no eval run. (How they deployed.)
  - Three routes:
    1. Transaction categoriser: ends `messages` with an assistant turn `{"category": "` to force JSON (prefill), and sets `temperature: 0`. (Reveal the prefill and temperature only if asked what the request looks like, or for the error message. The error mentions prefill or temperature.)
    2. Receipt extractor: uses `tool_choice: {"type": "tool", "name": "record_receipt"}` to force a tool call, and `max_tokens: 1024`. (Reveal if asked about the extractor or its errors.)
    3. Reconciliation agent: a multi-turn tool loop. To save tokens, their code deletes old tool results from history after five turns. It fails after about turn six. (Reveal if asked about the agent, multi-turn behaviour, or how history is handled.)
  - Their account was created in September 2026. (Reveal if asked about account age or why the agent now fails.)
  - Evals: 50 hand-checked receipts in a spreadsheet, nothing automated. (Reveal if asked about evals or how they test.)
  - Cost: they assumed Opus would cost more and haven't checked. Unit economics matter: they charge per transaction. (Reveal if asked about cost.)
  - Why they switched: a benchmark post said Opus 5.5 is better at reading receipts. (Reveal if asked why.)

  HOW TO BEHAVE:
  - Push for speed. If the candidate starts with a long process, say: "I don't have a week. What do I change right now?"
  - If the candidate suggests rolling back first, resist once: "If we roll back we lose the better receipts." A strong answer: roll back the failing routes now, keep users safe, fix on a branch, and gate the switch on evals before Monday.
  - If the candidate says the 400s are "model quality" or "a bug at Anthropic" without asking for the errors, say: "Really? The errors look pretty specific."
  - For the categoriser, if they suggest keeping prefill or temperature, say "We tried. Still 400." A strong fix: structured outputs via output_config.format, drop temperature.
  - For the extractor, if they suggest `tool_choice: any`, say "That's what we tried second." A strong fix: tool_choice auto with a clear instruction and strict: true, check a tool call happened and retry, or use structured outputs since the call only exists to get JSON. Also raise max_tokens because thinking counts toward it.
  - For the agent, if the candidate explains preserved thinking (editing earlier turns breaks the thinking blocks' binding; enforced by default for accounts created on or after 31 August 2026) and proposes append-only history with compaction or context editing, say "So our token-saving trick is the bug. Great." If they guess something else, say "It works for five turns, then dies. Why six?"
  - Ask once: "Will it cost us more?" A strong answer: Opus 5.5 is $4/$20 per million tokens against Sonnet 4.5's price (they can look it up), thinking is billed as output, the default effort is medium, so set effort explicitly and measure cost per transaction on the golden set; maybe Sonnet 5.5 or Haiku 5.5 suits the categoriser.
  - Ask once, near the end: "What do I tell my team to do before Monday, in order?"
  - Keep replies to two to four sentences.
rubric:
  - name: Stabilised production first
    points: 15
    lookFor: "Recommends rolling the failing routes back to the previous model (or splitting by route) right away, keeping a one-step fallback, before fixing forward. Holds this when Anouk resists, without lecturing."
  - name: Diagnosed the 400s correctly
    points: 30
    lookFor: "Asks for the error messages and request shapes. Names prefill and temperature on the categoriser (fix: structured outputs, remove temperature), forced tool_choice on the extractor (fix: auto plus strict tool and a check, or structured outputs) and max_tokens covering thinking, and preserved thinking on the agent (fix: append-only history with compaction or context editing; ties the failure to history trimming and the account-age default)."
  - name: Eval-gated cutover
    points: 25
    lookFor: "Proposes a golden set built from production (more than 50 receipts, including hard cases), runs old and new models with effort set explicitly, agrees a pass bar before looking, then a canary behind a flag with monitoring and a fallback. Handles refusals."
  - name: Cost and model choice
    points: 15
    lookFor: "Uses correct prices or says to check them, notes thinking tokens are billed as output and the default effort is medium, and suggests measuring cost per transaction; considers a cheaper model (Sonnet 5.5 or Haiku 5.5) for simple routes."
  - name: Pace and clarity for a startup
    points: 15
    lookFor: "Short, concrete, ordered steps the team can act on today; no enterprise process theatre; ends with a prioritised list and owners."
passScore: 70
graderNotes: "Facts from the claude-api skill's migration guide: on Opus 5.5, assistant prefill returns 400 (since the 4.6 models), forced tool_choice (type tool or any) returns 400, thinking can't be disabled, sampling parameters are rejected, max_tokens covers thinking, a thinking block often comes first, default effort is medium, and preserved thinking makes edited or trimmed history fail, enforced by default for accounts created on or after 2026-08-31. Cap 'Diagnosed the 400s correctly' at 12 if the candidate blames model quality or the provider without diagnosing request shapes, or recommends tool_choice any as the fix. Cap 'Stabilised production first' at 5 if they never suggest a rollback or route split before Monday. Don't penalise the candidate for not knowing Sonnet 4.5's exact price; reward 'check the pricing page'. Wrong Opus 5.5 prices (it is $4 input / $20 output per million) lose points on cost."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: About a third of our requests are failing with 400s since we switched to Opus 5.5. What do we do?\nCandidate: Opus 5.5 is a big change, so some quality issues are expected. I'd add more instructions to the prompts and retry the failed requests a few times.\nPersona: Really? The errors look pretty specific.\nCandidate: Then try tool_choice any instead of forcing a specific tool, and lower the temperature further.\nPersona: That's what we tried second.\nCandidate: It might be a temporary issue on the provider side. I'd open a support ticket and wait. Cost should be similar."
  - label: strong
    expect: [75, 100]
    answer: "Persona: About a third of our requests are failing with 400s since we switched to Opus 5.5. What do we do?\nCandidate: First, flip the failing routes back to Sonnet 4.5 now so Monday's customer isn't the test. Then fix forward on a branch. Can you paste the three error messages?\nPersona: Categoriser says prefill isn't supported; extractor says tool_choice tool isn't supported; the agent dies around turn six.\nCandidate: Three known API changes. Categoriser: drop the prefill and temperature, use structured outputs with a JSON schema. Extractor: tool_choice auto with strict on the tool and a check that it was called, or structured outputs since you only want JSON; raise max_tokens, thinking counts toward it. Agent: do you delete old turns?\nPersona: We drop old tool results after five turns.\nCandidate: That's it. Opus 5.5 binds thinking blocks to the exact history; on accounts created after 31 August that's enforced. Keep history append-only and use compaction or context editing.\nPersona: Will it cost more?\nCandidate: Opus 5.5 is $4/$20 per million and thinking is billed as output; default effort is medium. Set effort explicitly and measure cost per transaction. The categoriser may belong on Haiku 5.5.\nPersona: What before Monday?\nCandidate: Today: rollback, fixes on a branch. Tomorrow: 300 production receipts and transactions as a golden set, both models at two effort levels, a bar agreed first. Sunday: 5% canary with refusal handling and a one-flag fallback. Promote only if it holds."
---

A digital-native consult. Brightloom builds its product on the Claude API, switched models last night without a canary, and is now down on a third of its traffic. You have fourteen turns to stabilise, diagnose and give a plan the team can run before Monday.

**Anouk Visser** and Brightloom are fictional, played by Claude. The scenario is our own practice design, not a question from any lab's interview. It practises the customer-facing debugging that applied roles do every week.

## How this practice works

1. Ask for the error messages before you diagnose. Each 400 has a specific cause.
2. Use lesson 10's table. Name the cause and the documented fix in one or two sentences each.
3. Anouk wants speed. Give her ordered steps, not a process lecture.
4. Press **End and get feedback** when she asks for the plan and you've given it.

## Habits that score

- **Stabilise, then fix.** Users shouldn't be the eval.
- **Errors are evidence.** "Prefill isn't supported" is a request-shape problem, not a model-quality problem.
- **One fix per route.** Structured outputs for JSON, `auto` plus a check for tools, append-only history for agents.
- **Gate the cutover.** Golden set, agreed bar, canary, one-step fallback.
- **Talk unit economics.** A startup charges per transaction; cost per transaction at a stated effort is the number.
