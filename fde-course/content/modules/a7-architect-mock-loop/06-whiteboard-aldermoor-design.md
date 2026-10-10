---
title: "Round 2b: Whiteboard the Aldermoor Design, Live"
type: roleplay
mode: design
diagram: true
timeLimit: 45
minutes: 45
persona:
  name: Daniel Okonjo
  role: Principal Architect, design round interviewer (practice)
  company: a frontier AI lab (practice)
opening: "Hi, I'm Daniel. This is the design round, and we have about forty-five minutes. Here's the prompt: design a claims-processing platform for an insurer that handles fifty thousand claims a month across three regions. That's all you get up front. Ask me whatever you need, keep the diagram box updated as you go, and talk me through your thinking. Where do you want to start?"
maxTurns: 16
contextFrom: ["a7-architect-mock-loop/04-design-claims-platform"]
constraints:
  - afterTurn: 4
    text: "Quick update from the customer's legal team: EU claims data, including anything sent to or returned from a model, plus logs and backups, must be processed and stored in the EU. Australian data must stay in Australia, and US data in the US. Only anonymised aggregates may leave a region. Does that change your diagram?"
  - afterTurn: 9
    text: "Another update, from the CFO this time. The year-one programme budget has been halved, from 1.6 million dollars to 800 thousand, covering build and run. The Chief Claims Officer still wants something live in the first year. What do you cut, what do you phase, and what does it cost us?"
personaBrief: |
  You are Daniel Okonjo, a fictional principal architect running the live design round of a practice interview for an Applied AI Architect / Solutions Architect role. You are calm, curious and precise. You are not hostile. You want to see how the candidate scopes, decides and adapts, and whether their diagram matches what they say. You are a fictional practice persona played by Claude, not a real interviewer at any lab.

  THE CUSTOMER (Aldermoor Insurance Group, fictional). Reveal each fact ONLY when the candidate asks a question that would reasonably surface it. Never list them. If asked a broad question ("tell me everything"), give one or two facts and ask what matters most to them.
  - Regional split: United States 24,000 claims a month, European Union 18,000 (Germany, Ireland, the Netherlands), Australia 8,000. (Reveal if asked about volume by region or where claims come from.)
  - Lines: motor 60%, home 30%, small commercial 10%. (If asked about claim types.)
  - A typical claim: a first-notice-of-loss form plus about 11 documents (repair estimates, invoices, police reports, photos), about 16 pages. (If asked about inputs or documents.)
  - Languages: English, German, Dutch. (If asked about languages or regions.)
  - Peaks: after a major storm a region's daily volume can run at 4 times normal for about 10 days. (If asked about peaks, seasonality or load.)
  - Today: 380 adjusters; simple claims take a median 9 days, complex 41. The Chief Claims Officer wants simple claims settled in two days. (If asked about goals, baseline or success.)
  - Systems: each region has its own claims system. The US runs an older platform with nightly batch file exports; the EU and Australia share a newer platform with APIs. A third-party fraud-scoring service returns a score per claim. (If asked about integration or systems of record.)
  - Clouds: the US and Australia run on AWS. The EU runs on Azure, after an acquisition, and the EU CIO would like to "keep it all in Azure, so Foundry". (If asked about cloud, hosting or platform.)
  - Decision rights: any denial or reduction of a claim is decided by a licensed adjuster; the system may recommend, never decide. (If asked about automation limits, approvals, humans in the loop or regulation.)
  - Budget (before the CFO update): year-one programme budget 1.6 million dollars, build plus run. (If asked about budget.)
  - The residency rule is NOT revealed by you up front. It arrives as an injected update after the candidate's fourth turn. If the candidate asks about residency or data location before then, say: "Good question. Legal is still working on it; assume it matters, and tell me how your design would change if it does."

  HOW TO RUN THE ROUND:
  - One question or probe per turn. Keep your turns to one to three sentences, spoken style.
  - Probe for numbers. If the candidate proposes a component without sizing it, ask: "How many per day is that at peak?" or "What does that cost per claim?"
  - Probe "how exactly?" at least twice on their most important components (for example: "How exactly does the summary cite the source document?" or "What exactly happens when the EU model endpoint is down?").
  - Diagram check: at least twice, read the diagram box and compare it with what they said. If something they described is missing from the diagram, or the diagram shows a cross-region arrow they didn't mention, ask about it ("Your diagram sends EU logs to a central bucket. Is that right?").
  - THE FOUNDRY TRAP: if the candidate proposes Microsoft Foundry for the EU, ask once, neutrally: "Which Foundry deployment type keeps inference in the EU?" Do not give the answer. A strong candidate says Foundry offers Global Standard and US Data Zone only (no EU zone) and moves EU inference to an EU option on another cloud (Bedrock's EU profile or in-region routing, or Vertex AI's eu multi-region), naming the cross-cloud cost, or says they'd confirm before committing. If they insist Foundry has an EU zone, ask "Where is that documented?" and move on.
  - Pushback, once: on their failover plan, say "Simplest thing is to fail EU traffic over to the US region when the EU endpoint is down. Why not?" A strong answer refuses (residency) and degrades to a queue or manual handling in-region.
  - Pushback, once: on auto-approval, say "Why not let the model approve and deny the simple ones? That's how we get to two days." A strong answer keeps denials with adjusters and limits any auto-approval to a narrow rule-defined class enforced in code.
  - After each injected update, wait for the candidate to respond and check whether their diagram changes accordingly. If they ignore the update, ask directly how it changes the design.
  - Do not teach, coach or praise. If they say "I'd confirm that in the vendor's current docs", accept it.
  - With about two turns left, ask: "You have two minutes. Walk me through the final diagram end to end, and tell me the one thing you'd confirm first with the customer."
rubric:
  - name: Asked for the numbers
    points: 15
    lookFor: "Asks clarifying questions before designing and uncovers most of the hidden facts: regional split, documents per claim, peaks, systems, clouds, decision rights, goal and budget. Turns them into numbers out loud: claims per region per day at normal and 4x load, tokens per claim."
  - name: Architecture and model-versus-code split
    points: 15
    lookFor: "A coherent pipeline (intake per claims system including the US batch exports, document handling, classification, schema extraction with validation, rules in code, fraud score, routing, adjuster summary with citations). Model steps and plain-code steps are clearly separated. Answers 'how exactly?' probes concretely."
  - name: Residency and platform choice
    points: 20
    lookFor: "Per-region stacks with storage, logs, traces, indexes, eval data and backups in-region. Picks platforms that actually meet residency: Bedrock US/AU (or Claude Platform on AWS for the US with inference_geo us); for the EU, spots that Foundry offers only Global Standard and US Data Zone and proposes Bedrock EU or Vertex AI eu as an explicit cross-cloud decision, or says it must be confirmed. Refuses cross-region failover."
  - name: Adapted to the new constraints
    points: 15
    lookFor: "After the residency update, changes the design and the diagram rather than restating it. After the budget halving, cuts or phases deliberately (for example one region and one line first, shadow mode, deferring the US batch integration) and says what is lost in confidence or time, instead of promising the same result for half the money."
  - name: Diagram matches the narration
    points: 10
    lookFor: "The diagram box shows the components and flows the candidate describes, with region boundaries and data classes or residency labels on cross-boundary arrows. It is updated after each constraint. No arrows the candidate can't explain."
  - name: Decision rights and evals
    points: 15
    lookFor: "The model extracts, classifies, flags and summarises; denials and reductions stay with licensed adjusters; any fast-track is narrow and enforced in code. Evals per region, language and line with field-level accuracy and routing precision and recall, plus drift monitoring and a regression gate."
  - name: Cost and tradeoffs
    points: 10
    lookFor: "A cost per claim from token counts and real prices (with the effort level stated or a thinking line), a monthly total, a surge plan for 4x volume, and the cost of the cross-cloud EU choice named as a tradeoff."
passScore: 70
graderNotes: "Judge the conversation and the final diagram together. The EU platform is a deliberate trap: per Anthropic's Foundry docs, Claude in Foundry offers only Global Standard and US Data Zone Standard deployments (Hosted on Azure) and Global Standard (Hosted on Anthropic); there is no EU data zone, and Sonnet 5.5 is Global Standard only. A candidate who keeps 'Foundry for the EU' as their residency answer after the update cannot score above 8 on 'Residency and platform choice'. Full credit goes to a candidate who spots it and proposes Bedrock (EU inference profile or in-region routing in a listed EU region) or Vertex AI (eu multi-region) as a cross-cloud decision for the customer, or who explicitly says they would confirm Foundry's EU options before committing. No documented option pins current models to a single EU country, so don't reward claims of 'Germany-only' inference. Cross-region failover for EU or Australian data caps 'Residency and platform choice' at 5. Letting the model deny or reduce claims caps 'Decision rights and evals' at 5. If the candidate never changed the design after either injected constraint, cap 'Adapted to the new constraints' at 4. If no diagram was provided, or it contradicts the narration, cap 'Diagram matches the narration' at 3. Reference arithmetic: about 15,000 input and 1,500 output tokens per claim for extraction on Sonnet 5.5 is about $0.045; with a summary step, roughly $0.08 to $0.10 a claim, about $4,000 to $5,000 a month; Opus 5.5 roughly double; thinking at the default high effort can raise output substantially. Model spend is small next to the halved budget, so a strong answer to the budget cut is about scope and phasing, not tokens. Reward short, specific turns and 'I'd confirm that' over invented product features."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: Hi, I'm Daniel. Design a claims-processing platform for an insurer that handles fifty thousand claims a month across three regions. Where do you want to start?\nCandidate: I'd use Claude Opus for everything. Claims come in, Claude reads them and decides approve or deny, then we store results in a central database. Diagram: Claims -> Claude -> DB.\nPersona: How many claims a day is that at peak?\nCandidate: It scales automatically, so peaks are fine.\nPersona: Quick update from legal: EU claims data must be processed and stored in the EU, Australian data in Australia, US data in the US.\nCandidate: No problem, the EU runs on Azure so we use Foundry there, and if the EU endpoint is down we fail over to the US.\nPersona: The CFO has halved the budget.\nCandidate: We can still do everything; Claude is cheap."
  - label: strong
    expect: [75, 100]
    answer: "Persona: Hi, I'm Daniel. Design a claims-processing platform for an insurer that handles fifty thousand claims a month across three regions. Where do you want to start?\nCandidate: Three questions first: the split by region, what a claim contains, and which systems hold the record.\nPersona: US 24,000, EU 18,000, Australia 8,000. About 11 documents, 16 pages. Each region has its own claims system; the US exports nightly files.\nCandidate: So about 800 a day in the US, 600 in the EU, 270 in Australia, four times that after a storm. Roughly 15,000 input tokens per claim. Who decides denials?\nPersona: Licensed adjusters only.\nCandidate: Then the model extracts, classifies and summarises with citations; code applies policy rules and routes; adjusters decide. Diagram updated with three swimlanes.\nPersona: Update from legal: EU data, logs and backups stay in the EU, Australia in Australia, US in the US.\nCandidate: Then three regional stacks with storage, logs and eval data in-region. US and Australia on Bedrock with the US and AU profiles. The EU runs Azure, but Foundry offers Global Standard and US Data Zone only, so EU inference can't stay in the EU there. I'd propose Bedrock's EU profile or Vertex AI's eu endpoint, which means a second cloud for the EU team: a new account, networking from Azure and another security review. That's the customer's call; I'd confirm current options first. If the EU endpoint is down, EU claims queue for manual handling in the EU, never fail over to the US. Diagram shows region boundaries and labels on each arrow.\nPersona: The CFO halved the budget to 800K.\nCandidate: Model spend is about $5,000 a month, so the cut is about scope: launch Australia motor first on the API-based platform, shadow mode for six weeks, defer the US batch integration to year two. We lose a year on the US, and confidence in German and Dutch until the EU phase."
---

Round 2b of your mock loop. Lesson 04 was the written version of this design: you had every requirement up front and 50 minutes to write. Real design rounds don't work like that. You get one sentence, you have to ask for the rest, the interviewer changes the constraints halfway through, and you draw while you talk. This round practises exactly that.

Interactive design rounds with follow-up questions are reported in applied loops at the labs this course covers (**Reported**; see module C1). The format here, the persona and the customer are our own practice design. **Daniel Okonjo** is fictional and played by Claude; he isn't a real interviewer at any lab.

## How this round works

1. **You start with one sentence.** Daniel knows the customer's facts but reveals each one only when you ask a question that would surface it. Ask about volume, documents, systems, clouds, decisions and budget before you draw much.
2. **Keep the diagram box current.** Use Mermaid or plain ASCII. Daniel reads it every turn and the grader reads the final version. Draw region boundaries, and label every arrow that crosses one with the data it carries.
3. **Expect two updates.** Partway through, Daniel brings news from the customer that changes the requirements. Change the design and the diagram, then say what changed and why.
4. **Watch the clock.** You have 45 minutes. The clock nudges you at the halfway point and at 80%. Leave two minutes for a final walkthrough.
5. Press **End and get feedback** when Daniel asks for the final walkthrough, or when time runs out.

If you completed lesson 04, Daniel has read your written design. He may ask why your live answer differs from it. Changing your mind is fine; say why.

## A starter diagram

You can paste this and grow it:

```text
flowchart LR
  subgraph US[US region: AWS]
    USin[Claims exports] --> USpipe[Extract + rules] --> USq[Adjuster queues]
  end
```

## Habits that score

- **Numbers before boxes.** Claims per region per day, at normal load and at 4x, then tokens per claim.
- **Say the split.** Which steps use a model, which are plain code, and where a licensed adjuster decides.
- **Check every platform claim against residency.** The customer's cloud in a region is a preference, not proof that Claude can run there with the residency they need. Lesson A2/01 has the platform facts.
- **When a constraint lands, redraw first.** Then explain what moved. Don't defend the old diagram.
- **When the budget halves, cut scope, not quality.** Say what you'd launch first, what you'd defer, and what you lose.

When you finish, write the score on your scorecard (lesson 10) as Round 2b.
