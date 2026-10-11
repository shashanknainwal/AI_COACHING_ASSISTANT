---
title: "Module A2 Quiz"
type: quiz
minutes: 12
questions:
  - q: "An AWS customer says, \"We'll just use Claude through AWS.\" What's the most important clarifying question?"
    options:
      - "Which AWS region is closest to most of your users, so we can keep latency low?"
      - "Bedrock, which AWS operates, or Claude Platform on AWS, which Anthropic operates?"
      - "Do you have an AWS Enterprise Support plan that covers third-party model services?"
      - "Will your team call it through the AWS CLI, the console or an infrastructure-as-code tool?"
    answer: 1
    explain: "They're different products. On Bedrock AWS operates inference and is the data processor; on Claude Platform on AWS, Anthropic operates the stack and is the processor, with typically same-day feature parity. Features, retention answers and model IDs all differ."
  - q: "Which model ID calls Claude Opus 5.5 on the Bedrock Messages API endpoint (Claude in Amazon Bedrock)?"
    options:
      - "claude-opus-5-5"
      - "claude-opus-5-5@latest"
      - "anthropic.claude-opus-5-5"
      - "projects/anthropic/models/opus-5-5"
    answer: 2
    explain: "Bedrock model IDs carry an anthropic. prefix. The Claude API, Claude Platform on AWS and Vertex AI use the bare ID, and Foundry uses your deployment name (default claude-opus-5-5)."
  - q: "A design depends on the Message Batches API for a large overnight job. Per Anthropic's platform availability reference, where is Batches available?"
    options:
      - "Claude API and Claude Platform on AWS"
      - "All five platforms, at the same 50% discount"
      - "Amazon Bedrock and Google Vertex AI only"
      - "Claude API, Amazon Bedrock and Microsoft Foundry"
    answer: 0
    explain: "Batches is available on the Anthropic-operated Claude API and Claude Platform on AWS, and not on Bedrock, Vertex AI or Foundry. Choosing one of those means giving up the batch discount or redesigning the job."
  - q: "A German manufacturer asks: \"Can inference for current Claude models stay in Germany only?\" What's the accurate answer today?"
    options:
      - "Yes: set inference_geo to \"de\" on the Claude API or Claude Platform on AWS"
      - "Yes: Bedrock's Frankfurt region serves current models in-region with no routing"
      - "Yes: Vertex AI's single-region German endpoint serves every current model"
      - "No documented option; EU-only works on Bedrock or Vertex AI"
    answer: 3
    explain: "inference_geo offers us and global. Bedrock lists Frankfurt as 'Global, EU', not in-region, and Vertex AI's single-region endpoints serve only Sonnet 4.6 and earlier, so current models use the eu multi-region. Ask whether the real requirement is the EU, and confirm in the current docs."
  - q: "A customer with zero data retention (ZDR) wants to use the Batches API. What should you tell them?"
    options:
      - "The API will reject every Batches request from an organization that has ZDR enabled"
      - "Batches is covered by ZDR exactly like any other Messages API call, so there's no issue"
      - "It isn't blocked, but Batches isn't ZDR-eligible, so that data falls outside ZDR"
      - "Batches becomes ZDR-eligible as long as every request uses the 1-hour cache TTL"
    answer: 2
    explain: "Under ZDR, non-eligible features aren't blocked; using them steps outside ZDR for that data. Enforce a feature allowlist yourself, or redesign the job."
  - q: "On Amazon Bedrock and Google Cloud Vertex AI, who is the data processor for prompts and outputs, according to Anthropic's data retention page?"
    options:
      - "The cloud provider, so its retention and compliance documentation applies"
      - "Anthropic, under the same ZDR and HIPAA arrangements as on the Claude API"
      - "Both companies jointly, under a shared business associate agreement"
      - "Nobody, because prompts are never stored or processed outside the request"
    answer: 0
    explain: "Anthropic's page says the cloud provider is the processor on Bedrock and Google Cloud and points to their documentation. Anthropic is the processor on the Claude API, Claude Platform on AWS and Foundry."
  - q: "An EU insurer runs on Azure and wants Claude in Microsoft Foundry with inference kept in the EU. What do Anthropic's Foundry docs support?"
    options:
      - "An EU Data Zone deployment, Hosted on Azure, for all current models"
      - "Global Standard or US Data Zone only; there's no EU data zone in Foundry"
      - "Any EU Azure region, as long as the deployment is Hosted on Anthropic"
      - "EU residency for Sonnet 5.5 only, through a Regional Standard deployment"
    answer: 1
    explain: "Foundry offers Global Standard and US Data Zone Standard (Hosted on Azure) and Global Standard (Hosted on Anthropic). Sonnet 5.5 is Global Standard only. EU-only inference means Bedrock or Vertex AI, which is a cross-cloud conversation."
  - q: "A hospital network on Azure wants to send protected health information through Claude in Microsoft Foundry under Anthropic's HIPAA readiness. What do Anthropic's docs say?"
    options:
      - "HIPAA readiness is switched on automatically for every Foundry deployment"
      - "HIPAA readiness is available, but only on Hosted on Anthropic deployments"
      - "HIPAA readiness only requires zero data retention to be enabled first"
      - "Not on Foundry; the Claude API supports it with a signed BAA"
    answer: 3
    explain: "The data retention page lists Foundry and Claude Platform on AWS as not covered. On the Claude API, HIPAA readiness needs a BAA and a HIPAA-enabled organization; keep PHI out of JSON schemas."
  - q: "Which statement about the Commercial Terms and training can you put in a questionnaire answer?"
    options:
      - "Anthropic never sees, logs or stores any customer data sent through the API"
      - "Anthropic may not train on Customer Content from the Services (cite the terms)"
      - "Anthropic trains only on customer data after it has been fully anonymized"
      - "Whether customer data is used for training depends on which model you call"
    answer: 1
    explain: "That's what the Commercial Terms say, and it should be cited, along with the customer keeping rights to inputs and owning outputs. 'Never sees or stores' is a different, false claim: for example, flagged content may be retained up to 2 years even under ZDR."
  - q: "A CTO worries about lock-in. Which answer is most accurate?"
    options:
      - "There's no lock-in at all, because every feature works identically on every platform"
      - "Lock-in is unavoidable whatever you do, so the only sensible choice is the cheapest platform"
      - "The API is close to portable; each platform-only feature narrows where you can move"
      - "Use a different model on each platform so that no single vendor becomes a dependency"
    answer: 2
    explain: "The client class, credentials and model ID change, but the request body is the Messages API everywhere. Feature adoption (Batches, code execution, Skills, Files API) is the real portability cost, and it belongs in the design record."
---

Ten questions on deployment options, data handling and security reviews. You need 8 correct to pass.
