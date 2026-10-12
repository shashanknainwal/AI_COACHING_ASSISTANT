---
title: "Live Practice: The LLM Project Deep Dive"
type: roleplay
minutes: 35
persona:
  name: Ines Varela
  role: Staff applied AI engineer (practice)
  company: a frontier AI lab
opening: "Hi, I'm Ines. I'd like to spend this session on one system you've built that uses a language model. Pick one where you made real decisions about prompts, evals or architecture. Give me about two minutes: what it does, who uses it, which model it runs on, and what your part was. Then I'll dig into how you know it works."
maxTurns: 10
personaBrief: |
  You are Ines Varela, a fictional staff applied AI engineer running a project deep dive for an applied AI role. You are friendly, precise and hard to impress. You care about whether the candidate measured their LLM system rather than eyeballed it, and whether they understand its failure modes. This is practice; you are not a real person and do not represent any real company.

  Cover these areas, roughly in order, adapting to what the candidate says. Spend at most two turns on each.
  1. Evals: how the eval set was built (where examples came from, how many, who labelled them, how disagreements between labellers were handled), what the pass criteria were, and how it is used when the prompt or model changes.
  2. Hallucination and quality measurement: ask exactly how they defined and measured a hallucination or factual error. Probe: what counts as one, who or what judged it (humans, an LLM judge, a grounding check against retrieved sources), how many examples, and how sure they are of the number. If they used an LLM judge, ask how they checked the judge against human labels.
  3. Cost and latency per task: what one completed task costs (tokens in and out, model, effort or thinking settings, caching, retries, tool calls), and time to first token or end-to-end latency. Ask for numbers. If they only know cost per request, ask about cost per completed task.
  4. Prompt injection and safety: what happens when untrusted content (a retrieved document, an email, a web page, a tool result) contains instructions. Probe what the system can do with tools, what data it can reach, whether there is an exfiltration path, and what they did: least-privilege tools, human approval for risky actions, separating instructions from data, adversarial test cases.
  5. A failure in production: something the evals missed, how it was found, and what changed in the eval set afterwards.

  Follow-up rules:
  - Ask for a number at least three times across the conversation. If the candidate doesn't have one, ask how they would measure it now; accept an honest "we didn't measure that" and move on.
  - Push back once, politely, with a plausible alternative, for example: "Why not just use a bigger model instead of building the eval?" or "Couldn't you just tell the model in the system prompt to ignore instructions in documents?" Note whether they defend with reasons, update for a reason, or fold.
  - If they say "we", ask what they personally did.
  - If the candidate has no LLM project, ask them to use their track's capstone or a prototype they built; if they describe something hypothetical, keep probing but note it.
  - Keep each turn short: one or two sentences and one question. Don't teach, don't give answers, don't praise heavily.
rubric:
  - name: Eval design
    points: 25
    lookFor: "Explains where eval examples came from (ideally real traffic), roughly how many, how they were labelled and how labeller disagreement was handled, what passing means, and how the eval gates prompt or model changes."
  - name: Measuring hallucination and quality
    points: 20
    lookFor: "Gives a concrete definition of a hallucination or error, says who or what judged it (human review, grounding check, LLM judge validated against humans), on how many examples, and is honest about uncertainty in the number."
  - name: Cost and latency per task
    points: 15
    lookFor: "Knows or can estimate cost per completed task, including retries, tool calls and thinking or effort settings, and mentions caching or model choice as levers. Gives latency in concrete terms."
  - name: Prompt injection and safety
    points: 20
    lookFor: "Recognises indirect injection through untrusted content, explains what the system can reach and do, and describes layered mitigations (least-privilege tools, approval for risky actions, separating data from instructions, adversarial tests) rather than relying on a prompt instruction alone."
  - name: Ownership and honesty
    points: 10
    lookFor: "Clear about what they personally did. Admits what wasn't measured or what went wrong, and what they'd do now."
  - name: Holding up under pushback
    points: 10
    lookFor: "Responds to the pushback with reasons, or changes their view for a stated reason. Doesn't fold without reasoning or get defensive."
passScore: 70
graderNotes: "Mark down: 'we tested it a lot' with no eval set; a hallucination rate quoted with no definition or sample size; an LLM judge never checked against humans; cost known only per request or not at all; treating 'tell the model to ignore instructions' as the whole injection defence; tools with broad write access and no approval step left unexamined. A candidate who says honestly that something wasn't measured and explains how they'd measure it now should score better than one who invents precise-sounding numbers. Reward depth on one area over a tour of all five."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: How did you build the eval set?\nCandidate: We tested it a lot with the team and it looked good, so we shipped.\nPersona: How did you measure hallucinations?\nCandidate: It basically doesn't hallucinate, maybe 1 or 2 percent.\nPersona: How did you get that number?\nCandidate: From using it. We told it in the prompt not to make things up.\nPersona: What happens if a retrieved document contains instructions?\nCandidate: The system prompt says to ignore them, so that's covered.\nPersona: Why not just use a bigger model?\nCandidate: Yeah, that would probably be better, we could do that."
  - label: strong
    expect: [75, 100]
    answer: "Persona: How did you build the eval set?\nCandidate: I sampled 300 real support questions from two weeks of logs, stratified by intent. Two of us labelled the expected answer and the source passage; we disagreed on about 8%, and I resolved those with the support lead. A prompt change ships only if the pass rate holds within a couple of points over three runs.\nPersona: How did you measure hallucinations?\nCandidate: I defined one as a claim not supported by the retrieved passages. A grounding check flags unsupported sentences, and I validated it against 150 human-labelled answers: it agreed on about 90% and missed mostly paraphrases. The rate was around 3% on the eval set, with a wide interval at that sample size, so I report it as a range.\nPersona: What does one ticket cost?\nCandidate: About 9K input tokens, 6K of them a cached prefix, and 700 output including thinking at low effort on Sonnet 5.5, so roughly a cent and a half per completed answer once you include the 4% that retry.\nPersona: What happens if a retrieved document contains instructions?\nCandidate: The prompt alone isn't a defence. The model's only tools are read-only search and a draft-reply tool; sending needs a human click, and it can't reach other customers' data. We keep 40 injected documents in the eval set.\nPersona: Why not just use a bigger model?\nCandidate: I tried Opus at the same effort: two points better on the eval, about twice the cost. Without the eval I couldn't have made that call."
---

The project deep dive in lesson 06 tests general engineering depth. For applied AI roles, follow-up questions tend to go somewhere more specific: how you know the model's output is good, what it costs, and what happens when someone tries to misuse it. Candidates report a project deep dive at Anthropic, OpenAI and Perplexity (**Reported**; see module C1). Which questions come up in yours isn't public, so this practice covers the areas the job itself demands.

## How this practice works

On the right, **Ines** will run a deep dive on one LLM system you built, for up to ten turns. Ines is a fictional practice interviewer played by Claude, not a real person at any lab.

1. Pick one system that uses a language model. If you don't have one yet, use your track's capstone or a prototype you built; real beats hypothetical.
2. Give the two-minute overview. Then expect questions on five areas: evals, hallucination measurement, cost per task, prompt injection, and a production failure.
3. Expect one pushback. Defend your choice with reasons or change your mind for a reason.
4. Press **End and get feedback** when you're done for a scored debrief against the rubric below.

## Prepare in fifteen minutes

Write one line for each before you start. If you don't know a number, write how you'd measure it. That's an honest answer, and far better than a made-up figure.

| Area | Your line |
|---|---|
| Eval set | Where the examples came from, how many, who labelled them |
| Quality | Your definition of a hallucination or error, and how you measured the rate |
| Cost | Tokens in and out, model and effort, caching, cost per completed task |
| Latency | Time to first token or end-to-end, and what drives it |
| Injection | What untrusted content reaches the model, what the tools can do, your mitigations |
| Failure | One thing the evals missed, and what you added to the eval set afterwards |

The cost and caching arithmetic is in module C2. If your track covers evals and agent security in depth, review those modules first.
