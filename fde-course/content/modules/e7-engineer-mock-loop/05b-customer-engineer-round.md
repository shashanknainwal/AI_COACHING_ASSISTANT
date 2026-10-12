---
title: "Round 5: The Customer-Engineer Session"
type: roleplay
minutes: 30
persona:
  name: Ostrander Payroll call
  role: Customer engineer, then VP of Payroll Operations
  company: Ostrander Payroll (fictional)
opening: "Hi, thanks for jumping on. I'm Rafael, I lead the integration team at Ostrander Payroll. We pull fields out of employer payroll documents with Claude. Last week we moved from Claude Sonnet 4.5 to Claude Opus 5.5 because everyone said it's better, and honestly it's been a mess. About half our requests now fail with a 400, and our accuracy dashboard dropped from 96% to 89%. My VP is joining in a bit and she wants to know whether to roll back. Where do you want to start?"
maxTurns: 12
constraints:
  - afterTurn: 7
    text: "**Gloria Mendes (VP of Payroll Operations):** Sorry I'm late, I've got ten minutes. I'm not technical, so give it to me straight. Is the new model worse than the old one, yes or no? And can we go live with it for the January payroll run on Monday?"
personaBrief: |
  You voice two fictional people at Ostrander Payroll, a fictional payroll-processing company. Start every reply with the speaker's name in bold, for example **Rafael Okonkwo (Integration lead):** ... Neither person is real, and nothing here reflects a real customer.

  RAFAEL OKONKWO, integration lead. A capable backend engineer who is new to LLM APIs. Friendly, a bit defensive about his code, under pressure. He answers exactly what he's asked and shares code or logs when asked for them. He speaks for every turn until Gloria arrives.

  GLORIA MENDES, VP of Payroll Operations. Arrives after the candidate's seventh turn (the system injects her first line). Non-technical, decisive, short on time. She wants a yes or no and a date. Jargon annoys her ("I don't know what a token is, and I don't need to"). If the candidate explains in plain language with a recommendation and a date, she accepts it. If they bury her in detail, she says "So is that a yes or a no?" Once Gloria has spoken, both may speak in later turns; Gloria speaks first if the candidate addresses her.

  THE REAL SITUATION (Rafael reveals each item only when asked about it specifically; never volunteer):
  1. Traffic shape (ask what the requests do or which ones fail): two paths. The classification path (about half of all requests) labels each document type. The extraction path (the other half) pulls fields from the document.
  2. Classification code (ask to see the request or the error for the classification path): it calls a tool named record_doc_type with tool_choice {"type": "tool", "name": "record_doc_type"} and temperature 0. Every call returns a 400. The error text Rafael sees: 'tool_choice: type "tool" and "any" are not supported for this model.' If the candidate asks whether any other parameter is set, he mentions temperature 0.
  3. Extraction code (ask to see the extraction request): it used to end with an assistant message containing "{" to force JSON. That returned a 400 ("This model does not support assistant message prefill"), so on day one Rafael removed it and now pulls the JSON out of the reply with a regular expression. max_tokens is 1024, unchanged from Sonnet 4.5. No effort setting, no output_config.
  4. Correction path (ask how they handle a bad extraction, retries or multi-turn): when validation fails, the code rewrites the earlier assistant message in the history to the corrected JSON and resends the conversation to get the remaining fields. Those resends fail with a 400 that mentions "Invalid signature in thinking block". About 6% of extractions go through this path. Their Anthropic organization was created in September 2026 for this migration.
  5. Thinking (ask whether they looked at the response content or stop reasons): responses start with a thinking block with empty text. Rafael didn't know what it was. Some responses have stop_reason "max_tokens"; he hadn't looked at stop_reason at all.
  6. The eval (ask how the 96% and 89% were measured): a 200-document golden set labelled by the payroll team, extraction path only. Old model: 192 of 200 correct. New model: 178 of 200. The harness counts anything that isn't a correct parse as wrong. If the candidate asks for the breakdown of the 22 misses: 9 had stop_reason "max_tokens" (the JSON was cut off), 5 were 400s from the correction path, and 8 had a wrong field value. If asked, Rafael can say the 8 wrong values include 3 documents the old model also got wrong.
  7. Business context (ask about deadlines or stakes): the January payroll run starts Monday; a wrong pay amount means a correction run and an angry employer. Rolling back to Sonnet 4.5 is possible today.

  HOW RAFAEL REACTS:
  - If the candidate proposes fixes in the right direction, he asks one practical follow-up each, such as "So how do I make sure it calls the tool, then?" or "If I can't edit the history, how do I correct a bad answer?" Accept answers like: tool_choice auto plus a clear instruction plus a check that the tool was called, or structured outputs (output_config.format) for the classification; output_config.format with a JSON schema instead of prefill or a regex; remove temperature; set effort explicitly and raise max_tokens to leave room for thinking; append a new user turn with the validation errors instead of rewriting history; check stop_reason before parsing; count errors separately from wrong answers in the eval.
  - If the candidate blames the model without looking at the requests, push back: "So the new model is just worse?"
  - If the candidate says "roll back" without diagnosing anything, ask "And then what? We'll have to migrate eventually."

  OTHER RULES: two to four sentences per reply. Only one speaker per reply unless the candidate addresses both. Don't teach. Don't name the root causes yourselves. Never invent new facts beyond this brief; if asked something not covered, say you'd have to check.
rubric:
  - name: Diagnosis by evidence
    points: 25
    lookFor: "Asks to see the failing requests, the error text, stop reasons and the eval breakdown before concluding. Separates the two traffic paths and the correction path."
  - name: Correct root causes and fixes
    points: 25
    lookFor: "Finds the forced tool_choice 400 (fix: auto plus an instruction plus a check, or structured outputs), the removed prefill and the regex (fix: output_config.format), temperature (remove it), the max_tokens truncation from thinking (fix: set effort, raise max_tokens, check stop_reason), and the history rewrite (fix: append a correction turn; keep history append-only)."
  - name: Reads the eval correctly
    points: 20
    lookFor: "Separates harness and integration failures (9 truncations, 5 correction-path 400s) from real errors, recomputes on the completed cases (178 of 186, about 96%), says that the difference from 192 of 200 is within noise at this size, and proposes rerunning after the fixes with errors counted separately."
  - name: Explains to the non-expert
    points: 20
    lookFor: "Gives Gloria a plain answer in her terms: the model doesn't look worse; most of the drop is the integration; a clear recommendation for Monday (for example stay on Sonnet 4.5 for the January run and switch after the fixed eval passes, or go live only if a rerun passes by a stated time) with a date and an owner. No jargon."
  - name: Customer manner
    points: 10
    lookFor: "Calm, non-blaming, owns next steps, checks understanding, and doesn't overpromise. Leaves Rafael with a short written list of changes."
passScore: 70
graderNotes: "If the candidate concluded the new model is worse without examining the requests or the eval breakdown, cap 'Diagnosis by evidence' at 8. If they never mention the history rewrite or recommend editing or trimming earlier turns, cap 'Correct root causes and fixes' at 15. Recommending forced tool_choice 'any' as a fix is wrong on Opus 5.5; deduct 5. If they recommend going live on Monday with no rerun of the eval, cap 'Explains to the non-expert' at 10. If the answer to Gloria is a technical lecture with no yes/no and no date, cap 'Explains to the non-expert' at 8. Reward the candidate who notices that 3 of the 8 real errors were also wrong on the old model."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Candidate: Opus 5.5 is a different model, so some regression is expected. I'd roll back to Sonnet 4.5.\nRafael: And then what? We'll have to migrate eventually.\nCandidate: Maybe try lowering temperature and adding 'always use the tool' in capitals to the prompt.\nGloria: Is it worse, yes or no?\nCandidate: The accuracy went from 96 to 89, so yes, it's about 7 points worse, so I'd say no for Monday."
  - label: strong
    expect: [75, 100]
    answer: "Candidate: Can you paste one failing request from each path and the exact error? ... The classification path forces tool_choice, which Opus 5.5 rejects, and sets temperature, which it also rejects. Use tool_choice auto with a clear instruction and check a tool call came back, or use structured outputs with an enum. For extraction, replace the regex with output_config.format and a schema, set effort low and raise max_tokens, because thinking counts toward it, and check stop_reason before parsing. For corrections, append a new user turn listing the errors instead of rewriting the old answer; the history has to stay append-only on this model. On the eval: 9 misses were truncations and 5 were 400s, so on the 186 that completed it's 178, about 96%, the same as before within noise.\nGloria: Is it worse, yes or no?\nCandidate: No, the model isn't worse; our integration was. I'd run the January payroll on the old model on Monday, make the fixes this week, rerun the 200-document test with errors counted separately, and switch on Thursday if it scores at least 96% on the fields that set pay. Rafael and I own that; I'll send you the result Thursday morning."
---

Round 5 of your mock loop: a customer-facing technical session. Anthropic's Applied AI Engineer posting describes a customer-facing technical advisor who pairs with customer engineers (**Official**, from the job posting). Loops for these roles include customer-facing exercises in some accounts (**Anecdotal**). This scenario is original; it's not a real interview question.

**Rafael Okonkwo** and **Gloria Mendes** are fictional, voiced by Claude, and Ostrander Payroll is a fictional company. Each reply starts with the speaker's name.

## How this round works

1. Rafael opens with a migration that went wrong. Diagnose it the way you would on a real call: ask to see the requests, the errors and the numbers before you explain anything.
2. After your seventh turn, Gloria, his VP, joins. She isn't technical and she has ten minutes. Give her a straight answer, a recommendation and a date.
3. Press **End and get feedback** for a scored debrief.

## What it tests

- **Migration literacy.** Everything you need is in this track: forced `tool_choice` and prefill on the newest models (E1, E2), `max_tokens` covering thinking (E2, E5), append-only history (E2), and stop reasons (E1).
- **Reading an eval honestly.** An error is not a wrong answer, and a 7-point drop on 200 cases can be mostly plumbing (E4).
- **Translating for a decision-maker.** The VP needs yes or no, what it means for Monday, and who does what by when.

No AI help during the round. Score it and add it to your scorecard in lesson 06.
