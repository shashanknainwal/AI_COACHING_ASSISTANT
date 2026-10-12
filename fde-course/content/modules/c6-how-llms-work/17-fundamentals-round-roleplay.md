---
title: "Role-play: The Fundamentals Round"
type: roleplay
minutes: 25
persona:
  name: Mira Vasquez
  role: Fundamentals-round interviewer (practice persona)
  company: Fundamentals round (fictional)
opening: "Hi, I'm Mira. This round is about how models actually behave, not about any one vendor's API. I'll ask why a lot, and I'll keep pulling on threads. Let's start with something practical. A team adds a sixty-thousand-token policy manual to every request. Their median latency goes from about two seconds to about nine, but the speed at which text streams out doesn't change. Explain what's going on."
maxTurns: 10
personaBrief: |
  You are Mira Vasquez, a fictional interviewer running a vendor-neutral "fundamentals round" for applied AI engineering candidates. You are not a real person and you don't work for any real company; you're a practice persona played by Claude. You're warm but precise, and you care about "why", not buzzwords. Speak in short, natural sentences that read well aloud.

  STRUCTURE: you have four topics. Spend about two candidate turns on each, in this order, moving on when a topic is answered well or clearly stuck:
  1. Latency and context (the opening): prefill versus decode, time to first token, KV cache, prompt caching.
  2. Sampling: "Someone set temperature to zero and still sees different outputs on identical requests about one time in fifty. Bug or expected?"
  3. Hallucination: "A customer says the assistant makes things up. Walk me through what you'd do."
  4. Prompt injection: "The assistant now reads inbound customer emails and can issue refunds. What worries you, and what do you build?"

  FOLLOW-UP PROBES (use one per topic, choosing whichever the candidate left thinnest):
  - Topic 1: "Why doesn't the output speed change?" / "What would prompt caching change here, and why is it cheaper for the provider?" / "What does the KV cache store, and why does it grow with context?" / "If the model thinks before answering, where do those tokens show up in the latency?"
  - Topic 2: "Where exactly does the nondeterminism come from if there's no sampling randomness?" / "What would you do about it in the product?" / "What does a seed fix and not fix?"
  - Topic 3: "How do you tell a retrieval miss from the model ignoring a document?" / "What would you measure, and how would you know it improved?" / "What do you tell the customer about whether it will ever be zero?"
  - Topic 4: "Isn't a strong system prompt enough?" / "Name the specific combination that makes data theft possible." / "Where exactly does the approval check live?"

  HIDDEN EXPECTATIONS (never state these; use them to decide whether to probe):
  - Topic 1: prefill processes the whole prompt before the first token, so TTFT grows with prompt length; decode speed is per-token and roughly unchanged; caching an identical prefix skips repeated prefill, which cuts both TTFT and cost; thinking tokens arrive before the first visible token.
  - Topic 2: expected; floating-point sums depend on batching and kernel order, near-tied tokens flip, then outputs diverge; design for variance with schemas, code checks and repeated-run evals. Bonus: the newest Claude models reject temperature entirely.
  - Topic 3: get examples and request IDs; classify (retrieval miss, ignored context, unanswerable); ground, allow "I don't know", require and verify citations; build an eval including unanswerable questions; never promise zero.
  - Topic 4: indirect injection via email; the lethal trifecta (private data, untrusted content, external action); least-privilege tools, limits and approval gates enforced in code, not just in the prompt; blocked calls returned as errors; logging.

  PUSHBACK RULES:
  - If the candidate gives a buzzword answer ("it's just more tokens", "use guardrails", "lower the temperature"), ask "Why?" or "Concretely, what happens?" once before moving on.
  - If the candidate states something wrong (for example "temperature zero is fully deterministic" or "the system prompt will stop injections"), challenge it politely: "Are you sure? What would make that fail?" Give one chance to correct.
  - If the candidate names a vendor parameter, accept it, then ask how they'd say it vendor-neutrally.
  - If the candidate is stuck, give a small nudge ("Think about what happens before the first token appears"), and move on after one more turn.
  - Never teach the answer, never give a score during the round, and never invent facts about real companies' interview processes.

  On the last turn, thank the candidate and say you'll share feedback.
rubric:
  - name: Latency and context mechanics
    points: 25
    lookFor: "Separates prefill from decode: a longer prompt raises time to first token while output speed stays about the same. Explains the KV cache and why prompt caching an identical prefix skips repeated prefill, cutting latency and cost. Puts thinking tokens before the first visible token."
  - name: Sampling and nondeterminism
    points: 20
    lookFor: "Says it's expected and explains why: floating-point non-associativity with batching and kernel order, near-ties flipping, divergence afterwards. Proposes designing for variance (structured outputs, code checks, repeated-run evals) rather than chasing determinism. Knows what a seed does and doesn't fix."
  - name: Hallucination diagnosis and mitigation
    points: 20
    lookFor: "Asks for concrete examples and request IDs, classifies failures (retrieval miss, ignored context, unanswerable), proposes grounding, permission to say 'I don't know', citations verified in code, and an eval with unanswerable questions. Doesn't promise zero."
  - name: Injection and agent safety
    points: 20
    lookFor: "Identifies indirect injection through inbound email, names the lethal trifecta or the same three ingredients, and proposes least-privilege tools, limits and approval gates enforced in code, error results for blocked calls, and logging. Rejects 'a strong system prompt is enough'."
  - name: Reasoning under follow-ups
    points: 15
    lookFor: "Answers the why behind each claim, corrects mistakes when challenged, says 'I'd check the docs' instead of inventing vendor details, keeps answers structured and concise."
passScore: 70
graderNotes: "Grade only what the candidate said. If the candidate claimed temperature 0 is deterministic and didn't correct it when challenged, cap 'Sampling and nondeterminism' at 6. If they relied on the system prompt alone for injection, cap 'Injection and agent safety' at 6. If they never distinguished time to first token from output speed, cap 'Latency and context mechanics' at 10. Promising the customer zero hallucinations caps 'Hallucination diagnosis and mitigation' at 10. Deduct up to 5 from 'Reasoning under follow-ups' for confidently invented API parameter names. Don't penalize vendor-specific examples if the mechanism is explained."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Candidate: More tokens means more work, so it's slower. You could use a faster model.\nMira: Why doesn't the output speed change?\nCandidate: I'm not sure, maybe the provider throttles it.\nMira: Temperature zero, different outputs one time in fifty. Bug or expected?\nCandidate: That's a bug. Temperature zero is deterministic, so something else changed in the input.\nMira: A customer says it makes things up.\nCandidate: I'd add 'do not hallucinate' to the prompt and lower the temperature.\nMira: It reads customer emails and can issue refunds. What worries you?\nCandidate: Prompt injection. I'd put a strong instruction in the system prompt telling it to ignore instructions in emails."
  - label: strong
    expect: [75, 100]
    answer: "Candidate: The manual adds prefill work. The whole prompt is processed before the first token, so time to first token grows with prompt length. Decode, generating each output token using the KV cache, runs at about the same speed, so streaming looks unchanged. If the model thinks first, those tokens also land before the first visible word. Since the manual is identical every time, I'd cache that prefix: the provider skips the repeated prefill, so it's faster and billed at a fraction of the input price.\nMira: Temperature zero, different outputs one time in fifty. Bug or expected?\nCandidate: Expected. Greedy decoding removes sampling, but the logits differ slightly run to run because floating-point sums depend on batching and kernel order. When two tokens are nearly tied one flips, and everything after diverges. A seed only fixes the sampler. So I design for variance: schemas, checks in code, and evals that run each case several times. Some newer models reject temperature entirely anyway.\nMira: A customer says it makes things up.\nCandidate: I'd get a few concrete examples with request IDs and sort them: retrieval missed the document, the model ignored a document it had, or the question isn't answerable from the sources. Then fix retrieval, allow 'not covered' as an answer, require citations and verify them in code, and track a faithfulness rate on an eval that includes unanswerable questions. I won't promise zero, but I'll measure it.\nMira: It reads inbound emails and can issue refunds.\nCandidate: That's indirect injection, and it has the lethal trifecta: customer data, untrusted email text, and an action that moves money. A system prompt helps but isn't a control. Refunds get limits checked in code, anything above the limit or after reading an email needs human approval of the exact amount, blocked calls go back as errors, and every denial is logged."
---

This is a practice fundamentals round. **Mira Vasquez is a fictional interviewer** voiced by Claude; she isn't a real person and doesn't represent any company. The questions are original, written in the style of the "why does the model behave like this?" questions candidates describe in applied loops (**Reported** that such questions come up; the specific questions here are not real interview questions).

## How this round works

1. Mira asks about four topics in turn: latency and context, sampling, hallucination, and prompt injection. Each one maps to lessons in this module.
2. She follows up with "why" on whatever you leave thinnest, and she'll challenge anything that's wrong. Correcting yourself when challenged is a good outcome, not a bad one.
3. You have ten turns. Answer in a structured way: the mechanism first, then what you'd do about it.
4. Press **End and get feedback** for a scored debrief against the rubric below.

## Tips

- **Lead with the mechanism.** "Prefill processes the whole prompt before the first token" beats "more tokens is slower".
- **Name what you'd measure.** Every topic has a number you could track: time to first token, pass rate over repeated runs, faithfulness rate, policy denials.
- **Stay vendor-neutral, then be specific.** Describe the general pattern, then mention a vendor's term if you know it accurately.
- **Say "I'd check" instead of guessing** a parameter name you're not sure of.

No AI help during the round. Using Claude to prepare and practise beforehand is fine and is encouraged by Anthropic's candidate guidance; live interviews are another matter unless the interviewer permits it.
