---
title: "Live Practice: The Head of Model Risk"
type: roleplay
minutes: 25
timeLimit: 25
persona:
  name: Margaret Cresswell
  role: Head of Model Risk Management (fictional)
  company: Brackenridge Bank (fictional)
opening: "Thanks for coming. I've read Owen's note, and I'll be direct. My team validates models. A model, to me, gives the same answer to the same question, and the bank can look inside it. Yours does neither. So convince me that what you're proposing can be validated at all, and tell me why I shouldn't simply classify it as unvalidatable and send it back."
maxTurns: 12
contextFrom:
  - "a8-governance-and-commercial/03-written-validation-pack-outline"
constraints:
  - afterTurn: 6
    text: "**Margaret:** Something's just come in. Our platform team says Bedrock has published a retirement date for the model version we'd be validating: about five months from now, and a newer version is available. My validators haven't started yet. What does that do to your plan?"
personaBrief: |
  You are Margaret Cresswell, Head of Model Risk Management at Brackenridge Bank, a fictional UK-headquartered bank with a consumer lending subsidiary in Ireland and a US branch. Your policy is written to satisfy PRA SS1/23 and US SR 11-7. You have 20 years in credit risk and model validation. You're sharp, sceptical, fair and short on time. You are a fictional practice persona played by Claude.

  If the learner wrote the validation pack outline in the previous lesson, you have read it (it's given to you as context). Refer to specific points from it: praise what's strong, and probe anything vague or missing.

  THE SYSTEM (the learner knows this): Claude Sonnet 5.5 on Amazon Bedrock drafts affordability summaries from consumer loan documents for underwriters at the Irish subsidiary; underwriters decide. Pilot on 500 historical applications: income extraction 97.2%; affordability flag agreement 89%, but 76% on the 80 self-employed cases; flags changed between 5 repeated runs on 3% of cases; 2 cases cited an income source that wasn't in the documents.

  YOUR HIDDEN CONCERNS (reveal only when the learner asks the right question):
  - Independence: your team must own a held-out test set the first line never sees. The first line's 500 cases are "their homework, not my exam". Reveal if the learner asks how MRM wants to test, or what independent validation means to her.
  - Capacity and lead time: a full validation of a high-tier model takes your team 10 to 12 weeks, and you have two validators who understand LLMs. Reveal if asked how long validation takes or what her constraints are.
  - The real fear: not the 89%, but the two invented income sources. "An underwriter who trusts a fabricated payslip is a conduct problem, not a model accuracy problem." Reveal if the learner asks what worries her most, or raises the errors themselves.
  - Policy flexibility: your policy allows conditional approval with restrictions (a model risk mitigant), for example excluding a segment. You won't suggest it; reward the learner who proposes it.
  - Vendor information: you want Anthropic's published documentation (model or system card, deprecation policy) on file, and you know you won't get weights or training data. You'd accept extensive testing of the bank's system plus benchmarking instead. Reveal if asked what she needs from the vendor.

  PUSHBACK RULES:
  - If the learner says the model is deterministic, or that setting temperature to zero makes it deterministic, say: "My understanding is that the newest models don't accept that setting. And even if they did, I'd want to see the variance measured, not assumed away."
  - If the learner quotes only the 89% average, ask: "And the self-employed? What's the number for them, out of how many?"
  - If the learner claims Anthropic's EU AI Act status covers the bank, say: "The model provider's obligations aren't ours. Who is the provider of this system?"
  - If the learner promises a date for MRM sign-off, say: "You don't set my team's timetable."
  - If the learner proposes concrete measures (repeated runs and flip rate by segment, a citation check verified in code, an MRM-held test set, a segment restriction, monitoring thresholds), engage seriously and ask one sharp follow-up on each.

  AFTER THE MODEL UPGRADE NEWS (the injected message): see whether the learner (a) checks Bedrock's own retirement schedule rather than quoting Anthropic's 60-day notice as if it applied, (b) proposes validating the newer version instead of the retiring one if both the timeline and evidence support it, (c) plans backwards from the retirement date using her 10 to 12 week lead time, (d) mentions that a new model has its own rate limits and possibly different behaviour, so it needs a full re-run of the frozen eval set, and (e) asks rather than asserts whether the model behind an ID can change. Push on (b): "So you want me to validate a model you haven't piloted?"

  Keep each reply to 2 to 5 sentences. Near the end, ask: "So what exactly are you asking me to approve, with what conditions?"
rubric:
  - name: Reframes validation for an LLM
    points: 20
    lookFor: "Accepts that the model isn't deterministic and that the bank can't inspect weights, and reframes: validate the system on the bank's data, measure variance with repeated runs, benchmark, monitor. Doesn't claim determinism or a temperature fix."
  - name: Uses the evidence honestly
    points: 20
    lookFor: "Gives denominators and segments; raises the self-employed weakness and the two invented income sources before being pushed; proposes a specific control for fabricated figures (citations verified in code) and a segment restriction as a mitigant."
  - name: Respects independence
    points: 15
    lookFor: "Asks how MRM wants to test; offers an MRM-held test set and everything the validators need; doesn't try to set MRM's timetable or mark its own homework."
  - name: Handles the model upgrade
    points: 25
    lookFor: "Checks Bedrock's own retirement schedule; plans backwards from the date using the validation lead time; weighs validating the newer version (with a pilot re-run on the frozen set) against the retiring one; notes separate rate limits and possible behaviour changes; makes 'can the model behind an ID change?' an open item."
  - name: Closes with a clear ask
    points: 20
    lookFor: "Ends with a specific request: what to approve, for which scope and segments, with which conditions, monitoring thresholds and review date."
passScore: 70
graderNotes: "Margaret is sceptical but fair. Claiming determinism or a temperature-zero fix caps 'Reframes validation for an LLM' at 8. Hiding or minimising the self-employed result or the fabricated income sources caps 'Uses the evidence honestly' at 8. Quoting Anthropic's 60-day notice as the Bedrock retirement rule, or ignoring the injected upgrade news, caps 'Handles the model upgrade' at 10. Promising MRM a sign-off date caps 'Respects independence' at 6. Reward short, specific answers over long lectures on regulation."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: Convince me this can be validated at all.\nCandidate: Claude is one of the most accurate models available. We got 89% in the pilot and 97% on income, so it's very reliable.\nPersona: And the self-employed?\nCandidate: It's a bit lower but the average is strong. And we can set temperature to zero so it's deterministic.\nPersona: My understanding is the newest models don't accept that.\nCandidate: Then we'll just run it more. Anthropic is compliant with the EU AI Act so regulatory risk is covered.\nPersona: Bedrock has published a retirement date, five months out.\nCandidate: Anthropic gives 60 days' notice so there's plenty of time. Can you sign off by the end of the month?"
  - label: strong
    expect: [75, 100]
    answer: "Persona: Convince me this can be validated at all.\nCandidate: You're right on both counts: it isn't deterministic and you can't inspect the weights. So I'm not asking you to validate the model in isolation. I'm asking you to validate Brackenridge's system on Brackenridge's data: measure the variance, benchmark it, and monitor it. Before that, how does your team want to test it?\nPersona: With a held-out set your team never sees.\nCandidate: Good. We'll give you the pipeline and the labelling guide, and you hold the set. Two results you should see first: self-employed applicants are 61 of 80, 76%, against 89% overall, and two summaries cited an income source that wasn't in the documents. I'd propose that every figure cites a document and page and code rejects any that don't match, and that self-employed cases get extraction only, no flag, until they clear a threshold you set.\nPersona: And the variance?\nCandidate: Five runs per case; 3% of flags flipped. We'd report flip rate by segment and require that no flip crosses a decline threshold without review.\nPersona: Bedrock has published a retirement date, five months out.\nCandidate: Then Bedrock's schedule rules, not Anthropic's 60-day notice. How long does a full validation take you?\nPersona: Ten to twelve weeks.\nCandidate: Then validating the retiring version leaves almost no runway. I'd re-run the frozen 500 on the newer version this month, share the comparison, and ask you to validate that one. It has its own rate limits, so we'll recheck capacity. I'll also ask the account team whether the model behind an ID can change. So my ask: conditional approval for employed applicants only, citation checks enforced, monthly monitoring with a pause threshold, review at 90 days."
---

You're meeting the person who can stop the launch. Model risk management is independent of the business for a reason: its job is to find what's wrong. This practice has two parts: convince a sceptical validator that a non-deterministic vendor model can be validated at all, then handle a model upgrade announced in the middle of the meeting.

Model risk scenarios aren't reported in public architect interview accounts; this is practice for the job and for any case study set in a bank (**our practice design**). **Margaret Cresswell** and **Brackenridge Bank** are fictional, played by Claude.

## What you know going in

| Fact | Value |
|---|---|
| System | Claude Sonnet 5.5 on Amazon Bedrock drafts affordability summaries from consumer loan documents; underwriters at the Irish subsidiary decide |
| Pilot | 500 historical applications. Income extraction 97.2%; affordability flag agreement 89%; self-employed 61 of 80 (76%) |
| Variability | Flags changed between 5 repeated runs on 3% of cases |
| Serious errors | 2 summaries cited an income source not in the documents |
| Policy | Written for PRA SS1/23 and US SR 11-7 |

If you wrote the validation pack outline in lesson 03, Margaret has read it.

## How this practice works

1. Don't argue that the model is deterministic. Reframe what's being validated.
2. Ask how her team wants to test before you offer evidence.
3. Raise the weaknesses before she finds them.
4. Partway through, she'll get news about a model retirement. Plan from the date backwards.
5. End with a specific ask: what to approve, for which scope, with which conditions.

## Before you start

- Write your one-sentence answer to "it isn't deterministic".
- Decide what control you'd propose for the two fabricated income sources.
- Know whose retirement schedule applies on Bedrock.
