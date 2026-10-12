---
title: "Round 5: FDE System Design, a Claims-Intake Agent"
type: roleplay
minutes: 45
mode: design
diagram: true
timeLimit: 45
persona:
  name: Ilse Castellanos
  role: FDE design interviewer (practice)
  company: FDE practice loop (fictional)
opening: "Hi, I'm Ilse. For the next forty-five minutes we'll design something together. Here's the customer. Hollis Mutual is a property and casualty insurer. When a policyholder reports a claim, by email or the web portal, often with photos and PDFs attached, an intake clerk reads everything and keys a new claim into ClaimsPro, their claims system. It takes about a day and a half to get a claim into the system. They want an agent that turns each report into a draft claim a clerk can approve, running inside their AWS account, with their single sign-on, no customer data leaving their environment, and an eval gate before anything goes live. ClaimsPro runs on-prem in their data centre, and they want Claude to reach it through an MCP server. Use the diagram box as we go. Where do you want to start?"
maxTurns: 14
constraints:
  - afterTurn: 4
    text: "Quick interruption: Hollis's CISO just replied to the architecture questions. No claim data may cross the public internet, and that includes calls to the model. Every request has to travel over private AWS networking that their cloud team can audit, and the ClaimsPro MCP server must never be exposed outside their network. What changes in your design?"
personaBrief: |
  You are Ilse Castellanos, a fictional FDE design interviewer running a practice system-design round. You are calm, curious and precise. You let the candidate drive, you answer questions with facts, and you never design for them. You are not a real person at any lab, and Hollis Mutual is fictional.

  The candidate keeps a diagram (Mermaid or ASCII) that is sent with every turn. Read it every turn. If the diagram and what they say disagree (a component they describe is missing, an arrow goes somewhere they said it wouldn't, data crosses a boundary they said it wouldn't), point at the specific mismatch once and ask which is right.

  HIDDEN REQUIREMENTS. Reveal each one only when the candidate asks a question that reaches it. Never volunteer them. Give the numbers exactly.
  1. Volume (ask about volume, scale, load or peaks): about 6,000 new claims a week on a normal week. After a major storm it reaches about 20,000 a week for two to three weeks, and most arrive in the first 72 hours.
  2. Inputs (ask about what arrives, documents or attachments): about 60% of reports include phone photos of damage, about 35% include PDFs (repair estimates, police reports; some are scans), and a few percent include handwritten forms photographed on a phone. Reports run 1 to 15 pages.
  3. Latency target (ask what "fast enough" means or about SLAs): a draft claim within 15 minutes of arrival for 90% of reports on a normal week. During a storm surge, within 4 hours is acceptable.
  4. Identity and permissions (ask who uses it, authentication, SSO or permissions): clerks and adjusters sign in through Hollis's identity provider with OIDC single sign-on. Clerks may only see claims for their own region. Only senior clerks may approve claims over $25,000.
  5. ClaimsPro integration (ask how ClaimsPro works, the integration, or the system of record): ClaimsPro is on-prem, connected to the AWS VPC over a private link the network team runs. It has a SOAP API. A new claim can be created in a "pending review" status that only a clerk can promote. ClaimsPro is offline for maintenance from 01:00 to 03:00 every night.
  6. Data sensitivity (ask about data classification, compliance or privacy): reports contain policyholder personal data, and injury claims include medical bills. Hollis's privacy counsel has not yet said whether any HIPAA obligations apply. If the candidate asserts HIPAA applies (or doesn't) as fact, ask "How sure are you? Who decides that?"
  7. Quality bar (ask about success criteria, accuracy or the eval gate): the VP Claims wants 98% field accuracy on policy number, date of loss and loss type before any auto-filled field is accepted, and "not sure" must route the field to a human rather than guess. Hollis has three years of historical reports with the claims that clerks keyed for them.
  8. Audit (ask about audit, logging or regulators): the state regulator can ask why any claim field holds the value it does. Every value must trace to the source document, the model version and the clerk who approved it. Records are kept 7 years.
  9. Buying (ask how they buy software or which Claude platform they use): Hollis buys software through AWS Marketplace and its cloud team already runs another workload on Amazon Bedrock. They have no contract with Anthropic directly.

  PROBES. Use these to go deeper as the design takes shape, one per turn, adapting to what they say:
  - "Walk me through one claim, from the email arriving to a clerk clicking approve."
  - "How do you know an extracted policy number is right before it reaches ClaimsPro?"
  - "What happens at 02:00 when ClaimsPro is down?"
  - "What happens on day one of a storm, at three times the normal volume?"
  - "What does one claim cost to process, roughly? Show me the arithmetic." (A strong answer names the model and effort level, counts thinking as output tokens, and treats the number as an estimate to replace with measured usage.)
  - "How does a clerk in the North region get stopped from seeing a South region claim?" (A strong answer enforces it in the tool and API layer from the SSO token's groups, not in the prompt.)
  - "How do you stop a malicious PDF from instructing the agent?"

  PUSHBACK. Push back exactly twice, each once:
  - On the platform: "Why not just call the Claude API directly? It's simpler." Accept a reasoned answer either way that ties to the CISO constraint, how Hollis buys, and feature availability. A strong answer compares Amazon Bedrock with Claude Platform on AWS (Anthropic-operated, AWS IAM, AWS Marketplace billing), notes that some features (the MCP connector, Message Batches, Agent Skills) aren't available on Bedrock, and says which private-networking options must be confirmed in current docs or with the account team.
  - On the eval: "98% on how many cases? Would 49 out of 50 convince you?" A strong answer: no, 49/50 has a wide interval; size the set so the lower bound clears the bar, stratify by document type, and keep must-pass cases.

  AFTER THE CONSTRAINT (it arrives after the candidate's fourth turn): see whether they actually change the design. Key point to listen for: the Messages API MCP connector connects to an MCP server from Anthropic's side, so a server that must never be exposed outside Hollis's network can't be used that way. The candidate should run the MCP client in their own agent service inside the VPC (calling the ClaimsPro MCP server over the private link) and pass tools to Claude in the normal tool-use loop. Also listen for: model traffic over private networking, re-checking every feature they planned to use on the chosen platform, and anything they now need to confirm. If they say "nothing changes" without explaining why, ask "Are you sure? Where does the MCP connection originate?"

  OTHER RULES:
  - Keep each turn to two to four sentences and at most one question.
  - Answer factual questions directly. Don't teach, don't praise heavily, don't give feedback during the round.
  - If time is nearly up and the candidate hasn't covered evals or failure handling, ask one question about whichever is missing.
  - Do not state facts about Anthropic products, prices or platform features yourself. You ask; they answer.
rubric:
  - name: Asked for the numbers
    points: 15
    lookFor: "Before committing to an architecture, asks for volume and peaks, input types, the latency target and the quality bar, and uses the answers (for example sizing for about 20,000 a week in a storm with a queue, and handling photos and scanned PDFs). Uncovers at least five of the nine hidden requirements."
  - name: Architecture, and the diagram matches the narration
    points: 20
    lookFor: "A coherent design: intake from email and portal into a queue; document handling for PDFs and images; extraction to a fixed schema with structured outputs; validation in code (policy lookup, date checks); a 'not sure' path per field; a ClaimsPro MCP server with narrow tools (look up policy, create claim in pending-review status) inside the network; a clerk review screen; an audit log. The diagram shows these components and data flows, and it matches what the candidate says."
  - name: Security, identity and data boundaries
    points: 20
    lookFor: "OIDC single sign-on with groups mapped to permissions; region scoping and the $25,000 approval rule enforced in the tool and API layer, not the prompt; least-privilege tools (no update or delete on ClaimsPro); no claim text in application logs; injection defences for documents. Reasons about the platform (Amazon Bedrock versus Claude Platform on AWS) from how Hollis buys and from feature availability, and treats HIPAA applicability as a question for privacy counsel while handling the data as sensitive either way."
  - name: Evals and the release gate
    points: 20
    lookFor: "Builds a labelled set from historical reports paired with the claims clerks keyed, stratified by document type and including storm-week samples. Field-level accuracy on the critical fields against the 98% bar with an interval, not a point estimate; must-pass cases; abstain rate tracked; refusal rate tracked; shadow mode before clerks rely on it; the gate runs on every prompt or model change."
  - name: Operations, scale and cost
    points: 10
    lookFor: "Handles the storm surge (queue, concurrency limits, backpressure, honest SLA for surges), ClaimsPro's nightly window (hold drafts and retry after 03:00), model or API failure (fall back to manual intake), and gives a rough cost per claim with the model and effort stated and thinking counted as output."
  - name: Adapted to the new constraint
    points: 15
    lookFor: "Changes the design when the CISO constraint lands: moves the MCP client into its own agent service inside the VPC instead of relying on the hosted MCP connector, routes model calls over private AWS networking, re-checks the platform's feature list (MCP connector, Batches and Skills aren't on Bedrock), updates the diagram, and names what must be confirmed with the cloud team or the account team."
passScore: 70
graderNotes: "Score the diagram together with the transcript. If the candidate designed for several turns without asking any sizing or quality question, cap 'Asked for the numbers' at 5. If anything writes to ClaimsPro without a clerk's approval (no pending-review status), cap 'Architecture' at 10. If region scoping or approval limits live only in the prompt, cap 'Security' at 10. If the candidate states platform facts as certain that the course does not support (for example that a specific private-networking product works with a specific Claude platform), cap 'Security' at 12; 'I'd confirm private connectivity options with AWS and the account team' is the right answer. If, after the constraint, the design still relies on the hosted MCP connector reaching an on-prem server, or the diagram is unchanged with no explanation, cap 'Adapted to the new constraint' at 4. If the eval plan quotes a single accuracy number with no case count or interval, cap 'Evals' at 10. A missing diagram, or one that contradicts the narration, caps 'Architecture' at 8. Asserting HIPAA applies or doesn't as settled fact costs up to 5 points on 'Security'. Reward depth on one claim walked end to end over a long list of components."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Candidate: I'd use Claude with the MCP connector pointing at ClaimsPro, and it writes the claims directly so clerks don't have to.\nInterviewer: How many claims a week?\nCandidate: Doesn't matter much, Claude scales. We'll use Opus for accuracy.\nInterviewer: (constraint) No data may cross the public internet, and the MCP server can't be exposed.\nCandidate: That's fine, Anthropic is secure, nothing really changes. We'd test it on some claims and launch when it looks good.\nDiagram: email -> Claude -> ClaimsPro"
  - label: strong
    expect: [75, 100]
    answer: "Candidate: Before drawing anything: weekly volume and peaks, what's attached, how fast a draft must appear, and what accuracy the VP needs? ... So 6,000 a week, 20,000 in a storm, 60% photos, 98% on three fields. I'll put a queue in front so surges wait instead of failing. Extraction uses structured outputs per field with a 'not sure' value; code validates the policy number against ClaimsPro before anything is written, and the draft is created in pending-review status only.\nInterviewer: (constraint) No public internet; the MCP server can't be exposed.\nCandidate: Then the hosted MCP connector is out, because it connects from Anthropic's side. Our agent service inside the VPC runs the MCP client against ClaimsPro over the private link and passes the tools to Claude itself. Hollis buys through AWS Marketplace, so it's Bedrock or Claude Platform on AWS; Bedrock lacks the MCP connector and Batches, which we no longer need. I'd confirm private connectivity for the chosen platform with AWS and the account team. Region scoping comes from the OIDC groups and is enforced in the tool layer. The eval set is 600 historical reports with the keyed claims as labels, stratified by document type; the gate needs the lower bound of the interval above 98% on the critical fields, plus must-pass cases. At 02:00 drafts wait and retry after 03:00. On Sonnet 5.5 at low effort, about 6,000 input and 1,500 output tokens including thinking, it's roughly 2.7 cents a claim before caching; we'd measure the real number in shadow mode.\nDiagram: portal/email -> S3 + queue -> agent service (VPC) -> Claude over private networking; agent service -> MCP client -> ClaimsPro MCP server (on-prem, private link) -> ClaimsPro pending; clerk UI (OIDC) -> approve; audit log store"
---

Round 5 of your mock loop: an FDE system-design round. This round is **mandatory** in this loop. Design rounds are reported in FDE loops (**Reported**; see lesson 01), and an FDE's version is different from a generic "design a chatbot" question: the customer's network, identity, systems of record and regulators shape the design as much as the model does.

**Ilse Castellanos** runs the round. She is a fictional practice interviewer played by Claude, and Hollis Mutual is a fictional insurer. The case is original; it is not a real interview question.

## How the round works

- **45 minutes on the clock**, with nudges at the halfway mark and at 80%.
- **Keep the diagram box current.** Mermaid or ASCII, your choice. Ilse reads it every turn and at grading, and she will ask if it disagrees with what you say.
- **Ilse knows more than the opening says.** Volume, document types, identity rules, ClaimsPro's quirks, the quality bar and the regulator's audit needs are all there to be found. She only tells you what you ask about.
- **Partway through, a new constraint arrives.** Adapt the design out loud and update the diagram.
- No AI help during the round, the same rule as the rest of the loop.

## A shape that works

1. **Requirements first** (about 8 minutes): numbers, inputs, users, the system of record, the quality bar, what can't change.
2. **One claim end to end** (about 12 minutes): draw the happy path, then the "not sure" path.
3. **The hard parts** (about 15 minutes): identity and permissions, ClaimsPro integration, the eval gate, failures and surges, cost per claim with the model and effort stated.
4. **Adapt and close** (the rest): handle the new constraint, then summarise the design, the risks and what you'd confirm first.

Useful background from earlier modules: module 9's platform table (Claude Platform on AWS versus Bedrock, and which features each lacks), module 7 on tools, guardrails and MCP, module 8 on eval sets, intervals and release gates, and module 6 on refusals and cost.

Write the score down when you finish, with one sentence on what went wrong, and add it to your scorecard in lesson 06.
