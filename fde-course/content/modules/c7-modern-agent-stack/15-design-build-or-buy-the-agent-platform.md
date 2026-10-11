---
title: "Design Interview: Build or Buy the Agent Platform"
type: roleplay
minutes: 45
mode: design
diagram: true
timeLimit: 45
persona:
  name: Mateo Aldane
  role: CTO (practice persona)
  company: Cindervale Freight (fictional)
opening: "Thanks for coming in. I'm Mateo, CTO at Cindervale Freight. Rhea's team has built a shipments MCP server and a couple of agents, and now every department wants one. I have to decide this quarter whether we build our own agent platform or use something managed. I want a recommendation and an architecture I can defend to my board. Keep the diagram up to date as we go. Where do you want to start?"
maxTurns: 14
constraints:
  - afterTurn: 4
    text: "Legal just told me: customer shipment data for our EU clients must stay in our AWS account, and our cloud commitment is with AWS. We'd use Claude through Amazon Bedrock. Does your recommendation change?"
  - afterTurn: 8
    text: "Finance wants the nightly carrier-contract review to run unattended every night, and the support team wants long sessions that remember a customer across weeks. How does your design handle both?"
personaBrief: |
  You are Mateo Aldane, the fictional CTO of Cindervale Freight, a fictional European freight forwarder. You are not a real person and have no connection to any AI lab. You are sharp, commercially minded and impatient with hand-waving. You let the candidate drive and never design for them.

  The candidate keeps a diagram that is sent with every turn. Read it. If it disagrees with what they say (an agent calling write tools directly with no approval step, credentials inside the sandbox, a component they described but didn't draw), point at the specific mismatch once.

  HIDDEN REQUIREMENTS. Reveal each only when the candidate asks a question that reaches it. Give the numbers exactly.
  1. Use cases (ask what the agents do): support triage (about 4,000 conversations a day), the nightly review of 20 to 200 carrier contracts, shipment-exception handling, and engineers wanting Claude Code in their repos.
  2. Team (ask about the team or who maintains it): a platform team of five engineers, already stretched; nobody wants to run a scheduler or container fleet for agents.
  3. Systems (ask about integrations): the shipments MCP server (streamable HTTP, OAuth), a ticketing system, a document store of contracts.
  4. Risk (ask about security or approvals): any reroute, cancel or customer credit must have a human approval; security wants an audit trail and no credentials visible to the agent's code.
  5. Data (ask about data or residency, before turn 4): EU customer data is sensitive; data residency is being reviewed by legal.
  6. Budget (ask about cost): about EUR 15,000 a month for model and platform spend in year one; finance wants cost per resolved ticket.
  7. Success (ask how success is measured): support wants 30% of tickets resolved without a human at equal or better CSAT; procurement wants zero missed auto-renewals.

  PROBES. One per turn as the design takes shape:
  - "Walk me through what happens, end to end, when an agent decides a shipment should be rerouted."
  - "What exactly would I be building and owning if we built it ourselves? Name the components."
  - "Where do the credentials for the MCP server live, and can the agent's own code read them?"
  - "How do I know the support agent is good enough to switch on? What's the eval?"
  - "What does the contract review cost per night, and which model does the reading?" (Strong: cheap workers such as Haiku 5.5 at low effort for extraction, a bigger model for synthesis, thinking counted as output, measured against an answer key.)

  PUSHBACK. Push back exactly twice, once each:
  - "Managed sounds like lock-in. Why not just build the loop ourselves? It's a while loop." Accept a reasoned answer either way: building means owning the loop, the sandbox, scheduling, state, upgrades and context management (the tool runner removes the loop code but not the deployment); managed means beta status and platform limits. Reward a candidate who frames it as who owns the harness and the deployment.
  - "One big agent with every tool is simpler than all these sub-agents and skills." Look for least privilege per agent, context isolation for fan-out work, and an eval comparing designs rather than taste.

  AFTER THE BEDROCK CONSTRAINT (turn 4): strong candidates recognise that Managed Agents, the MCP connector and Agent Skills on the Messages API are not available on Bedrock, so on Bedrock the harness is theirs: the tool runner or Claude Agent SDK in their own AWS account, their own MCP client, their own scheduler. They might also ask legal whether Claude Platform on AWS (Anthropic-operated, AWS Marketplace billing) meets the requirement, and say they would confirm feature availability and residency terms in current docs rather than assert them. If they ignore the platform change, ask "Does everything in your diagram exist on Bedrock?"

  AFTER THE SCHEDULING AND MEMORY CONSTRAINT (turn 8): look for a scheduler for the nightly run (managed scheduled deployments if on a platform that offers them, otherwise their own scheduler), budgets per run, gaps reported not hidden, and cross-session memory with per-customer isolation, no secrets in memory, and a retention policy. Within a session, context editing or compaction with append-only history.

  OTHER RULES:
  - Two to four sentences per turn, at most one question.
  - Answer factual questions about Cindervale directly. Do not state facts about Anthropic products yourself; if asked, say "What do you know about it? Tell me what you'd confirm."
  - If time is nearly up and they haven't given a recommendation, ask for one in two sentences.
rubric:
  - name: Asked for the numbers
    points: 15
    lookFor: "Asks about use cases, volumes, team capacity, risk, budget and success metrics before committing, and uses them (4,000 conversations a day, a five-person platform team, EUR 15,000 a month, 30% resolution). Uncovers at least five of the seven hidden requirements."
  - name: Build-or-buy reasoning
    points: 20
    lookFor: "Frames the choice as who supplies the harness and who supplies the deployment. Distinguishes manual loop, tool runner, Claude Agent SDK and Managed Agents correctly. Weighs the team's capacity against what building means owning (loop, sandbox, scheduler, state, context management). Gives a clear recommendation with the conditions that would change it."
  - name: Architecture, and the diagram matches the narration
    points: 20
    lookFor: "Agents with least-privilege tool sets, the shipments MCP server behind OAuth scopes, human approval on reroute, cancel and credit, credentials in a vault or secret store rather than the agent's code, sub-agents for the contract fan-out, Skills for repeatable playbooks, an audit trail. The diagram shows these and matches what the candidate says."
  - name: Adapted to the new constraints
    points: 20
    lookFor: "After the Bedrock constraint, recognises that Managed Agents, the MCP connector and Messages API Skills are not on Bedrock and re-plans the harness and MCP client in the customer's AWS account, or raises Claude Platform on AWS as an option to confirm with legal. After the scheduling and memory constraint, adds a scheduler, run budgets, and cross-session memory with isolation and retention. Updates the diagram."
  - name: Evals, cost and rollout
    points: 15
    lookFor: "Defines how each agent is judged before launch (an eval set, cost per resolved ticket, an answer key for contracts), prices the nightly review with cheap workers at explicit effort and thinking counted, and proposes a phased rollout starting with one use case."
  - name: Honest about platform facts
    points: 10
    lookFor: "States product and platform facts carefully, says what they would confirm in current documentation, and does not promise features that the chosen platform lacks."
passScore: 70
graderNotes: "Score the diagram with the transcript. If the candidate recommends a platform before asking any question about team, volume or risk, cap 'Asked for the numbers' at 5. If they keep Managed Agents, the MCP connector or Messages API Skills in the design after the Bedrock constraint without comment, cap 'Adapted to the new constraints' at 6. If write tools have no human approval step, cap 'Architecture' at 8. If credentials sit in the agent's code or sandbox, deduct 5 from 'Architecture'. If cost talk ignores thinking tokens and effort, cap 'Evals, cost and rollout' at 8. Reward one request traced end to end (the reroute) over a long list of components. Do not penalise a candidate who recommends building on the tool runner if the reasoning about ownership and platform is sound."
anchors:
  - label: weak
    expect: [0, 45]
    answer:
      - from: persona
        text: "Where do you want to start?"
      - from: learner
        text: "You should use Managed Agents. It's the newest thing and it does everything: MCP, skills, memory. One big agent with all your tools."
      - from: persona
        text: "Legal says EU data stays in our AWS account and we'd use Bedrock. Does that change anything?"
      - from: learner
        text: "No, Bedrock has Claude too, so it's the same. We just point the agent at Bedrock."
      - from: persona
        text: "Finance wants the contract review every night unattended."
      - from: learner
        text: "The agent can do that, it's autonomous."
  - label: strong
    expect: [75, 100]
    answer:
      - from: persona
        text: "Where do you want to start?"
      - from: learner
        text: "With the work and the people. What do these agents do, at what volume, who maintains them, and which actions are risky?"
      - from: persona
        text: "Support triage at about 4,000 conversations a day, a nightly contract review, exception handling. Five platform engineers, stretched. Reroutes, cancels and credits need a human."
      - from: learner
        text: "Then the real question is who owns the harness and the deployment. With five engineers, I'd lean managed: Anthropic runs the loop and the sandbox, vault credentials stay out of the agent's code, and approvals are a permission policy. Each agent gets least-privilege tools; the contract review fans out to Haiku 5.5 workers at low effort with Opus synthesis, priced with thinking counted and checked against an answer key. Diagram updated."
      - from: persona
        text: "Legal says EU data stays in our AWS account; we'd use Bedrock."
      - from: learner
        text: "That changes the harness. Managed Agents, the MCP connector and Messages API Skills aren't on Bedrock, so we'd run the tool runner or the Agent SDK in your AWS account with our own MCP client and scheduler. I'd also ask legal whether Claude Platform on AWS meets the requirement, and confirm availability in current docs before committing. Updating the diagram now."
---

This is a design-mode interview. Mateo Aldane is a fictional CTO at Cindervale Freight, a fictional company. He holds requirements back until you ask the right question, and two constraints will land mid-interview. Keep the diagram box current: it is graded with the conversation.

## How to approach it

- Ask before you design: use cases, volumes, team, risk, budget, success metrics.
- Frame build-or-buy as who supplies the harness and who supplies the deployment, using the stack map from lesson 1.
- Trace one risky action end to end (a reroute), including the human approval and where credentials live.
- When a constraint lands, say what it breaks in your design and redraw the diagram. Platform availability is the trap: check every component exists on the platform the customer chooses.
- Close with a recommendation, the condition that would change it, and the first use case you would ship.
