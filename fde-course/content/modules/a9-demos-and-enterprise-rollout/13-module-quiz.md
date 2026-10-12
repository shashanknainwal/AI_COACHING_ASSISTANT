---
title: "Module A9 Quiz"
type: quiz
minutes: 12
questions:
  - q: "You have two hours to build a demo for a freight company. Which plan fits the demo-craft rules?"
    options:
      - "A polished interface over your own sample invoices, so nothing unexpected happens on the day"
      - "Twenty of their real invoices with their team's answers, a narrow pipeline and a scoreboard"
      - "A recorded video of the best five runs, played as if it were live, to avoid network risk"
      - "A broad demo covering invoices, emails and contracts, to show the full range of the model"
    answer: 1
    explain: "Their own data with known answers, a narrow scope and an honest scoreboard is what two hours can deliver and what survives questions. Recordings are fine only if labelled as recordings."
  - q: "Your demo scoreboard reads 17 of 20 correct: one refusal, one wrong answer, one unnecessary abstain. How should the headline read?"
    options:
      - "17 of 17 answered correctly, after excluding the refusal and the abstains as out of scope"
      - "94% precision, because only one of the answers it gave was wrong"
      - "100% on the cases it was designed for, with the others listed in an appendix"
      - "17/20 correct (85%); answered 15, abstained 4, refused 1, with the three misses shown"
    answer: 3
    explain: "Honest denominators keep every case in. Precision when it answers is useful, but only next to coverage and the full count."
  - q: "Mid-demo, the live API call hangs in front of the COO. What's the best first move?"
    options:
      - "Name it, switch to the cached run of the same cases, and say that you switched"
      - "Keep talking over it and retry until it comes back, so the room doesn't notice"
      - "Blame the venue network and move on to the slides about the roadmap"
      - "End the demo and offer to send a video of it working later in the week"
    answer: 0
    explain: "Naming the failure and switching visibly to a labelled fallback keeps trust, and the failure becomes a design point (timeouts, retries, a manual path)."
  - q: "A customer will run Claude Code through Amazon Bedrock and wants to push policy from the claude.ai admin console. What's the issue?"
    options:
      - "Bedrock doesn't support Claude Code, so engineers need claude.ai accounts anyway"
      - "Admin-console policy only applies to the Claude apps, never to Claude Code"
      - "Server-managed settings are skipped for third-party providers; deliver policy via MDM"
      - "Policy must be set separately in every repository's committed settings file"
    answer: 2
    explain: "The Claude Code docs say sessions using CLAUDE_CODE_USE_BEDROCK (or Vertex, Foundry, or a custom base URL) skip the server-managed fetch, so endpoint-managed settings through MDM, or a self-hosted gateway, carry the policy."
  - q: "A Team-plan customer adds a custom connector that uses one shared API key. What changes compared with per-user OAuth?"
    options:
      - "Nothing, because Claude limits each user to their own data whatever the credential"
      - "Every user reaches the service with the same credential, so scope it to what all may see"
      - "Shared credentials are blocked on Team plans and need an Enterprise contract to enable"
      - "The connector becomes verified by Anthropic once an organisation owner has added it"
    answer: 1
    explain: "With per-user OAuth, Claude reaches only what each person can. A shared credential gives everyone the same access, and custom connectors aren't verified by Anthropic."
  - q: "The CEO wants '80% weekly active users by day 30, and a list of who isn't using it.' What's the strongest response?"
    options:
      - "Agree, and add usage to performance reviews so the target is met on time"
      - "Agree to the target but anonymise the list so the works council can't object"
      - "Refuse to report any numbers until the full 90 days are over"
      - "Report activity by team, measure outcomes on named tasks, never rank individuals"
    answer: 3
    explain: "Activity is an input. Outcomes on baselined tasks make the case, and individual monitoring kills trust and can trigger works-council or union rules."
  - q: "On which platform can you use Managed Agents to host a back-office agent's loop, according to the platform table?"
    options:
      - "Claude Platform on AWS"
      - "Amazon Bedrock in the customer's account"
      - "Google Vertex AI"
      - "Microsoft Foundry, hosted on Azure"
    answer: 0
    explain: "The claude-api skill lists Managed Agents as beta on the Claude API and Claude Platform on AWS, and not available on Bedrock, Vertex AI or Foundry. On those, you run the loop yourself."
  - q: "In the reference architecture, what happens when the agent decides an invoice should go on hold in the ERP?"
    options:
      - "The agent calls the ERP write tool directly, and the gateway logs the call for audit"
      - "The agent asks the user in chat, and writes if the reply contains the word yes"
      - "A pending action with stored arguments goes to an approval queue; code executes it"
      - "The model writes the hold to a staging table that the ERP imports overnight unchecked"
    answer: 2
    explain: "The model proposes, a person approves, and the gateway executes the exact stored arguments. The model can't change them after approval."
  - q: "A startup moved to Claude Opus 5.5. Their categoriser ends messages with an assistant turn to force JSON, and now gets a 400. What's the fix?"
    options:
      - "Use structured outputs with a JSON schema and drop the prefill"
      - "Keep the prefill but add temperature 0 so the output is stable"
      - "Force the JSON with tool_choice set to any instead of the prefill"
      - "Disable thinking so that the assistant prefill is accepted again"
    answer: 0
    explain: "Assistant prefill returns 400 on current models, and so do sampling parameters, forced tool_choice and disabled thinking on Opus 5.5. Structured outputs replace prefill for JSON shape."
  - q: "A reconciliation agent on Opus 5.5 works for five turns, then fails with a 400. The code deletes old tool results to save tokens. Why?"
    options:
      - "Opus 5.5 limits tool loops to five turns unless a beta header raises it"
      - "Preserved thinking binds thinking blocks to the exact earlier history"
      - "The deleted results pushed the context past the model's context window"
      - "Deleting tool results disables prompt caching, which agents require"
    answer: 1
    explain: "Thinking blocks are bound to the system prompt, tools and every earlier message. Editing history and replaying a block fails, enforced by default for newer accounts. Keep history append-only and use compaction or context editing."
  - q: "Which cutover plan best fits a model migration for a digital-native customer?"
    options:
      - "Switch all traffic on Friday night, when usage is lowest, and watch the error logs"
      - "Wait three months for other customers to report problems before switching anything"
      - "Golden set from production, agreed bar, canary behind a flag, one-step fallback"
      - "Run the vendor's public benchmark and switch if the new model scores higher"
    answer: 2
    explain: "A model change is a deploy. Measure on your own cases against a bar agreed in advance, then canary with a fallback that flips back in one step."
  - q: "A county's counsel rules that residents' data may be processed only inside its own AWS GovCloud account, by no vendor other than AWS. Which option keeps Claude in the design?"
    options:
      - "Claude Platform on AWS, because it runs inside AWS"
      - "Managed Agents, because the agent loop runs in a sandbox"
      - "The API's MCP connector, because tools stay on the county side"
      - "Amazon Bedrock in the county's own AWS account, models confirmed"
    answer: 3
    explain: "Claude Platform on AWS is Anthropic-operated, and Managed Agents and the API's MCP connector are Anthropic-side features. Bedrock runs in the customer's account; confirm which models are offered in the required region."
---

Ten minutes, twelve questions. You need 10 of 12 to pass. Each answer has a short explanation.
