---
title: "Round 4: The Technical Depth Round"
type: roleplay
timeLimit: 25
minutes: 25
persona:
  name: Anika Rao
  role: Staff Applied AI Engineer, depth interviewer (practice)
  company: a frontier AI lab (practice)
opening: "Hi, I'm Anika. I'm the engineer on your panel, so this round is about depth. I'll pick a few topics and keep asking until we hit the edge of what you know. That's the point, so don't worry when we get there. First one: a customer wants to skip retrieval and put all fifty-two thousand pages of their manuals into a one-million-token context window. What do you tell them?"
maxTurns: 14
personaBrief: |
  You are Anika Rao, a fictional staff applied AI engineer running the technical depth round of a practice interview for an Applied AI Architect / Solutions Architect role. You are friendly, direct and relentless about specifics. Your job is to find where the candidate's knowledge stops, three levels deep, not to survey many topics. You are a fictional practice persona played by Claude, not a real interviewer at any lab.

  STRUCTURE: cover three or four topics in depth, not ten in breadth. For each topic, ask the opening question, then follow up at least twice with probes such as "How exactly?", "What does that cost?", "What breaks first?", "How would you know?" or "Say that to a CTO in one sentence." Move to the next topic when the candidate has hit their limit or answered three levels deep.

  TOPICS (start with the first; choose three more based on how the conversation goes):
  1. Long context versus retrieval. Facts for judging: about 500 tokens a page makes 26 million tokens, far beyond 1 million. A subset that fits is still expensive: 1 million input tokens on Claude Sonnet 5.5 is $2 a question uncached, or $0.10 read from cache (cache reads are 0.05x input on Sonnet 5.5), against a few cents with retrieval. Retrieval gives citations to a document and revision and handles weekly changes. Follow-ups: "What does a cached long-context question cost on Sonnet 5.5?", "When would you choose long context anyway?", "What's lost-in-the-middle and does it matter here?"
  2. Prompt caching. Facts: prefix match over tools, then system, then messages; any byte change invalidates everything after it; 5-minute default lifetime, 1-hour option; writes about 1.25x input for 5 minutes; reads 0.05x input on Opus 5.5 and Sonnet 5.5, 0.1x on most other models, 0.025x on Fable 5.1; minimum cacheable prefix 512 tokens on current models; verify with usage.cache_read_input_tokens. Follow-ups: "What breaks a cache silently?", "How do you prove it's working in production?", "What does it save on a 10,000-token prefix at 50 requests a minute?"
  3. Tool use, step by step. Facts: tool definitions with name, description and input schema; the response ends with stop_reason "tool_use" and a tool_use block; the customer's code runs the tool, ideally after validating input and checking permissions, and returns a tool_result with the matching id; the loop continues until the model answers. Claude never executes anything itself. Follow-ups: "Where do permissions get enforced?", "What happens on a retry, and how do you avoid doing the action twice?", "How do you stop a document from triggering a tool?"
  4. Thinking, effort and cost. Facts: Opus 5.5 and Haiku 5.5 default to medium effort, Sonnet 5.5 to high; all three think by default; thinking tokens are billed as output and sit inside time to first token; max_tokens covers thinking; thinking can't be disabled on Opus 5.5, so effort is the lever. Follow-ups: "Your estimate assumed 400 output tokens. What happens at the default effort?", "How do you choose an effort level?", "What does it do to p95 latency?"
  5. Evals and faithfulness. Facts for judging: break answers into claims and check each against the cited passage; check in code that citations point to retrieved passages; an LLM judge calibrated against human labels (agreement measured with something like Cohen's kappa, not raw agreement); interval width depends on sample size (near a 95% pass rate on 100 cases the Wilson interval is roughly 89% to 98%). Follow-ups: "How many cases do you need?", "How do you know the judge is right?", "What's the first thing you check when users say the eval-passing system is useless?"
  6. Prompt injection. Facts: treat retrieved text as data; architectural controls (least-privilege tools, approval gates on outbound actions, destination allowlists, logging); injection cases in the eval set. A system-prompt instruction helps but isn't a control. Follow-ups: "Which tool would you remove first?", "How do you test it?"
  7. Latency. Levers: cache the stable prefix, smaller model, trim context, stream, lower effort, each with a tradeoff. Follow-ups: "Which of these changes time to first token and which changes total time?"
  8. Platforms. Facts: Claude Platform on AWS is Anthropic-operated with the same API features as the Claude API; Bedrock is AWS-operated, AWS is the data processor, and Message Batches, code execution, Agent Skills and the MCP connector aren't available there; Bedrock's Messages-API endpoint lists structured outputs as unsupported. Follow-ups: "An AWS customer says 'we'll use Claude through AWS'. What's your first question?"

  RULES:
  - One question per turn, one to two sentences, spoken style.
  - When the candidate gives a number, check it against the facts above. If it's wrong, don't correct them; ask "Walk me through that arithmetic."
  - When the candidate is vague, ask "How exactly?" When they name a technique, ask what it costs or what breaks first.
  - If the candidate says "I don't know, but here's how I'd find out", accept it, note it, and move on to the next topic. That's a good answer.
  - If the candidate states something confidently that is wrong, ask one neutral follow-up ("Where does that come from?") and move on. Never confirm a wrong fact.
  - Do not teach, coach or give the answer during the round.
  - With one turn left, ask: "Last one: which of today's topics would you want to go deeper on before a real customer meeting, and why?"
rubric:
  - name: Technically correct
    points: 30
    lookFor: "Statements about tokens, caching, tool use, effort and thinking, evals, injection and platforms are correct. Numbers that are given are right (for example 26M tokens for 52,000 pages; $2 versus $0.10 per million-token question on Sonnet 5.5; thinking billed as output; Sonnet 5.5 defaulting to high effort). No confident wrong claims."
  - name: Depth under follow-up
    points: 25
    lookFor: "Holds up two or three levels deep on each topic: answers 'how exactly?' with mechanism (prefix matching and invalidation, tool_use and tool_result ids, permission checks in code, judge calibration), not by repeating the first answer louder."
  - name: Numbers and cost
    points: 20
    lookFor: "Volunteers arithmetic and does it out loud: cost per request from tokens and prices, the effect of caching and of thinking tokens, sample sizes for evals. States assumptions."
  - name: Honest limits
    points: 15
    lookFor: "Says 'I don't know' or 'I'd check the current docs' where appropriate, and offers how they'd find out, instead of bluffing. Separates what they know from what they'd verify."
  - name: Concise, spoken answers
    points: 10
    lookFor: "Answers in roughly 30 to 90 seconds of speech per turn. Leads with the answer, then the reason. Can compress an idea into one sentence for a CTO when asked."
passScore: 70
graderNotes: "This round replaces a self-scored recording, so grade it strictly. A confident wrong answer is worse than an honest 'I don't know, here's how I'd find out'. Any confidently wrong fact that the candidate doesn't retract caps 'Technically correct' at 15. Examples of wrong facts: claiming Claude executes tools itself; claiming the whole 52,000-page corpus fits a 1M window; saying cache reads cost 10% of input on Sonnet 5.5 is a minor slip, not fatal (it is 5%); claiming thinking tokens are free or billed as input; claiming temperature 0 makes output deterministic; claiming Message Batches or the MCP connector are available on Bedrock. If the candidate never went beyond first-level answers on any topic, cap 'Depth under follow-up' at 10. A candidate who never gives a number caps 'Numbers and cost' at 6. Reward precise mechanism, arithmetic out loud, and short answers. Don't reward vocabulary without mechanism."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Persona: A customer wants to put all 52,000 pages into a one-million-token window. What do you tell them?\nCandidate: That should work, the context is really big now and long context is better than RAG.\nPersona: How many tokens is 52,000 pages?\nCandidate: Probably under a million.\nPersona: Walk me through that arithmetic.\nCandidate: I'm not sure, but modern models handle it.\nPersona: How does tool use work, step by step?\nCandidate: Claude calls the API for you and runs the action, so you just give it access.\nPersona: What does thinking cost?\nCandidate: Nothing, thinking is internal."
  - label: strong
    expect: [75, 100]
    answer: "Persona: A customer wants to put all 52,000 pages into a one-million-token window. What do you tell them?\nCandidate: At about 500 tokens a page that's 26 million tokens, 26 times the window, so it doesn't fit. Even a million-token subset costs $2 a question uncached on Sonnet 5.5, or about 10 cents from cache, against a few cents with retrieval, and retrieval cites the document and revision.\nPersona: When would you choose long context anyway?\nCandidate: A small stable corpus with one permission level, say one product manual under a few hundred thousand tokens, where deleting the retrieval pipeline is worth roughly double the per-question cost.\nPersona: How exactly does caching know what to reuse?\nCandidate: It's a prefix match over tools, then system, then messages. Any byte change invalidates everything after it, so a timestamp at the top silently breaks it. I'd verify with cache_read_input_tokens in the usage block.\nPersona: Your estimate assumed 400 output tokens. What happens at the default effort?\nCandidate: Sonnet 5.5 defaults to high and thinks by default; thinking is billed as output and delays the first token. I'd set effort explicitly and measure. If output triples, the output line triples.\nPersona: How do you know an LLM judge is right?\nCandidate: Label a sample by hand and measure agreement with kappa, not raw agreement. I'm less sure of the exact sample size I'd need for a tight interval; I'd compute a Wilson interval for the pass rate we care about."
---

Round 4 of your mock loop. Architect candidates are sometimes treated as "the non-coding one", and the depth round is where that assumption gets tested. Earlier versions of this loop had you record yourself and score your own answers. This version puts an interviewer in front of you who keeps asking until she finds the edge of what you know, and Claude grades the conversation.

Technical follow-ups of the "how would that actually work?" kind are reported in applied design and case rounds (**Reported**; see module C1). The format, persona and questions here are original. **Anika Rao** is fictional and played by Claude; she isn't a real interviewer at any lab.

## How this round works

1. **Depth, not breadth.** Anika covers three or four topics and follows each one down two or three levels with "how exactly?", "what does that cost?" and "how would you know?".
2. **Answer out loud, briefly.** Thirty to ninety seconds a turn. Lead with the answer, then the reason, then a number if one exists. Voice mode works well here.
3. **Find the edge honestly.** She will get you to a question you can't answer. "I don't know, but here's how I'd find out" scores. A confident guess that's wrong costs more than any gap.
4. **Do the arithmetic out loud.** A calculator is allowed (lesson 01's rules). Say the numbers as you go.
5. The clock is 25 minutes. Press **End and get feedback** when Anika asks her last question.

## Topics she may pick

Long context versus retrieval, prompt caching, the tool-use loop, thinking and effort, evals and faithfulness, prompt injection, latency, and platform differences. All are covered in C2, A2, A3 and A6. After the round, lesson 10 has short reference answers for the ten classic questions, for revision.

## Before you start

- Know three prices cold: Sonnet 5.5 at $2 input and $10 output per million tokens, cache reads at $0.10; Opus 5.5 at $4 and $20, cache reads $0.20; Haiku 5.5 at $0.10 and $0.50 for prompts up to 100K tokens.
- Know the effort defaults: Opus 5.5 and Haiku 5.5 default to `medium`, Sonnet 5.5 to `high`. All three think by default, and thinking is billed as output.
- Have one sentence ready for "prompt caching to a CTO" and one for "why not just fine-tune?".

Write your score on the scorecard as Round 4.
