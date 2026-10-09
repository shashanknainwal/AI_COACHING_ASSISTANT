---
title: "Module A2 Quiz"
type: quiz
minutes: 12
questions:
  - q: "An AWS customer says, \"We'll just use Claude through AWS.\" What's the most important clarifying question?"
    options:
      - "Which AWS region is closest to your users?"
      - "Do you mean Amazon Bedrock, which AWS operates, or Claude Platform on AWS, which Anthropic operates?"
      - "Do you have an AWS Enterprise Support plan?"
      - "Will you use the AWS CLI or the console?"
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
      - "All five platforms"
      - "Bedrock and Vertex AI only"
      - "Claude API, Bedrock and Foundry"
    answer: 0
    explain: "Batches is available on the Anthropic-operated Claude API and Claude Platform on AWS, and not on Bedrock, Vertex AI or Foundry. Choosing one of those means giving up the batch discount or redesigning the job."
  - q: "A European bank asks whether Claude API inference can be pinned to the EU with inference_geo. What's accurate today?"
    options:
      - "Yes, set inference_geo to \"eu\""
      - "Yes, but only on Claude Opus models"
      - "inference_geo only applies to Bedrock"
      - "No: inference_geo offers \"us\" and \"global\". Bedrock and Vertex AI offer EU endpoint options; confirm the needed model is available there"
    answer: 3
    explain: "Anthropic's data residency page lists only us and global for inference_geo. Bedrock (EU inference profiles) and Vertex AI (the eu multi-region) offer EU options, and model availability varies by region."
  - q: "A customer with zero data retention (ZDR) wants to use the Batches API. What should you tell them?"
    options:
      - "The API will reject Batches requests for ZDR organizations"
      - "Batches is covered by ZDR like any Messages call"
      - "The API won't block it, but Batches isn't ZDR-eligible (it retains data for 29 days), so that data is outside the ZDR arrangement"
      - "Batches is ZDR-eligible only with the 1-hour cache TTL"
    answer: 2
    explain: "Under ZDR, non-eligible features aren't blocked; using them steps outside ZDR for that data. Enforce a feature allowlist yourself, or redesign the job."
  - q: "On Amazon Bedrock and Google Cloud Vertex AI, who is the data processor for prompts and outputs, according to Anthropic's data retention page?"
    options:
      - "The cloud provider, so its retention and compliance docs apply"
      - "Anthropic, under the same ZDR arrangement as the Claude API"
      - "Both jointly, under Anthropic's BAA"
      - "Nobody; the data is never processed"
    answer: 0
    explain: "Anthropic's page says the cloud provider is the processor on Bedrock and Google Cloud and points to their documentation. Anthropic is the processor on the Claude API, Claude Platform on AWS and Foundry."
  - q: "A CISO says, \"Just confirm for my notes that you're ISO 27001 and SOC 2 Type II certified.\" What's the best response?"
    options:
      - "Confirm both; every major AI vendor has them"
      - "Say you'll send the current reports from Anthropic's Trust Center (and the cloud provider's compliance pages) rather than confirm from memory"
      - "Say certifications don't matter for AI systems"
      - "Confirm SOC 2 only, since it's the most common"
    answer: 1
    explain: "Certification lists change and are documented in the Trust Center. Naming one from memory is the most common way architects overclaim."
  - q: "A hospital network on Azure wants to send protected health information through Claude in Microsoft Foundry under Anthropic's HIPAA readiness. What do Anthropic's docs say?"
    options:
      - "HIPAA readiness is automatic on Foundry"
      - "HIPAA readiness requires Hosted on Anthropic deployments"
      - "HIPAA readiness only needs ZDR to be enabled"
      - "HIPAA readiness isn't available on Foundry or Claude Platform on AWS; the Claude API supports it with a signed BAA"
    answer: 3
    explain: "The data retention page lists Foundry and Claude Platform on AWS as not covered. On the Claude API, HIPAA readiness needs a BAA and a HIPAA-enabled organization; keep PHI out of JSON schemas."
  - q: "Which statement about the Commercial Terms and training can you put in a questionnaire answer?"
    options:
      - "Anthropic never sees or stores any customer data"
      - "Anthropic may not train models on Customer Content from the Services; the customer keeps rights to inputs and owns outputs (cite the Commercial Terms)"
      - "Anthropic trains only on anonymized customer data"
      - "Training policy depends on which model you use"
    answer: 1
    explain: "That's what the Commercial Terms say, and it should be cited. 'Never sees or stores' is a different, false claim: for example, flagged content may be retained up to 2 years even under ZDR."
  - q: "A CTO worries about lock-in. Which answer is most accurate?"
    options:
      - "There's no lock-in: every feature works identically on every platform"
      - "Lock-in is unavoidable, so pick the cheapest platform"
      - "The Messages API request shape and SDKs are close to portable across platforms; each platform-specific feature you adopt (Batches, code execution, Skills, Files API) narrows where you can move, so record that tradeoff"
      - "Use a different model on each platform to avoid dependence"
    answer: 2
    explain: "The client class, credentials and model ID change, but the request body is the Messages API everywhere. Feature adoption is the real portability cost, and it belongs in the design record."
---

Ten questions on deployment options, data handling and security reviews. You need 8 correct to pass.
