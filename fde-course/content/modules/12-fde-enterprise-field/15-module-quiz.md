---
title: "Module 12 Quiz"
type: quiz
minutes: 12
questions:
  - q: "Behind a TLS-inspecting proxy, the SDK fails with CERTIFICATE_VERIFY_FAILED. What's the right fix?"
    options:
      - "Set verify=False in staging only, and keep certificate verification on in production"
      - "Point the client at a CA bundle with the public roots plus the corporate root"
      - "Replace the default trust store with a file holding only the corporate root"
      - "Add the API host to NO_PROXY so traffic skips the inspecting proxy entirely"
    answer: 1
    explain: "Append the corporate root to the public bundle and pass it to the HTTP client. Disabling verification exposes traffic, a corporate-only bundle breaks hosts the proxy doesn't inspect, and bypassing the proxy fails when direct egress is blocked."
  - q: "A prototype on the Claude API uses Message Batches, the MCP connector and code execution. The customer's security team prefers Amazon Bedrock. What does the port audit tell you?"
    options:
      - "Nothing changes, because Bedrock and the Claude API share one API surface"
      - "Only the model IDs change, since Bedrock adds an anthropic. prefix to them"
      - "Only Batches is affected, and the cloud's own batch service covers it fully"
      - "All three features are missing on Bedrock, so those files need rework first"
    answer: 3
    explain: "Per the platform availability table, Message Batches, the MCP connector and code execution aren't available on Bedrock. Each needs a workaround, such as a worker pool, a client-side MCP connection and your own sandbox."
  - q: "Your backend receives an OIDC token. In what order should it be checked?"
    options:
      - "Signature using the key for its kid, then iss, aud and expiry, then groups"
      - "Groups first, to reject unauthorised users early, then verify the token's signature"
      - "Expiry first because it's cheapest, then groups, and the signature last"
      - "Issuer and audience first, then groups, then the signature if time allows"
    answer: 0
    explain: "Never read claims from a token you haven't verified. Check the signature with the key named by kid, then the issuer, audience and time claims, and only then use groups for authorisation."
  - q: "An analytics enclave has no outbound network. Which plan gets a Python service installed and working?"
    options:
      - "Run pip install inside the enclave and ask the network team to unblock PyPI"
      - "Copy your laptop's virtual environment folder into the enclave over USB"
      - "A hash-locked wheelhouse for the target's Python and OS, plus an approved path to the model"
      - "Install packages as they're needed at container start from the public index"
    answer: 2
    explain: "Build wheels for the exact target, pin them with hashes, import them through intake, and install with --no-index. And an air-gapped enclave can't call a hosted model without an approved private path, so plan that too."
  - q: "In the backfill, about 3% of tickets were re-run and appended at the end of the file. Why does the chunked aggregation need two passes?"
    options:
      - "pandas can't group data when a file is read with a chunksize argument"
      - "Attempts of one ticket can land in different chunks, so find the latest first"
      - "Costs must be computed before counts, or the totals come out in the wrong order"
      - "Reading a CSV file twice is faster than reading it once with every column"
    answer: 1
    explain: "Sums and counts combine across chunks, but de-duplication needs a global view. Pass one finds each ticket's latest attempt from two columns; pass two aggregates only those rows."
  - q: "An auditor wants Claude's full reasoning written into every answer, and the prompt now asks for it. What's the risk, and the better approach?"
    options:
      - "Declines with category reasoning_extraction; read summarized thinking and ask for a short explanation"
      - "Higher cost only, because reasoning text is billed as extra input tokens on every request"
      - "No risk at all, since every current model always writes out its full reasoning on request"
      - "Responses get truncated, so raise max_tokens and keep the instruction in the prompt"
    answer: 0
    explain: "On current models, prompts that ask the model to reproduce its internal reasoning in the response can be declined as reasoning_extraction, and those aren't retried on a fallback. Read the summarized thinking blocks and ask for a short explanation, which is still allowed."
  - q: "A refusal eval has 60 legitimate phishing-triage cases with 2 refusals (3.3%). The agreed threshold is 2%. What should you report?"
    options:
      - "Over threshold: escalate to the account team today with the full ticket text"
      - "Ignore it, because two cases is too few to tell you anything about refusals"
      - "Lower the threshold to 4% so this slice passes and the project stays on track"
      - "Watch: the point estimate is above 2%, but its interval still includes 2%"
    answer: 3
    explain: "The Wilson interval for 2 of 60 includes 2%, so the slice is worth watching, not escalating yet. Thresholds are agreed before the run, and escalations never carry ticket text."
  - q: "Your field report covers three workarounds built at several customers. What makes the product team most likely to act?"
    options:
      - "Three separate feature requests, each with the most vivid customer story"
      - "A promise that the pipeline will certainly be lost if nothing is built"
      - "One ask naming the shared root cause, with labelled evidence and a scoped first version"
      - "A preset tuned for the biggest customer, so the work pays off right away"
    answer: 2
    explain: "Name the root cause, quantify customers, engineer-days and incidents, label estimates as estimates, and scope the smallest valuable version. Customer-specific presets are the consultant trap."
  - q: "Two escalations land at once: a clinic with urgent referrals near a four-hour deadline, and a bank's CIO demo in two hours. What do you do first?"
    options:
      - "Work the demo first, because executive visibility matters most to the account"
      - "Ask what's at stake on each side, take the patient risk first, and give both a time"
      - "Split your attention evenly by switching between them every fifteen minutes"
      - "Wait for your engagement lead to decide which of the two customers you should support first"
    answer: 1
    explain: "Triage on impact after asking a couple of questions. Patients on a clock come first; the bank gets a named owner, an exact ask for its network team, a fallback option and a time for the next update."
  - q: "A customer staff engineer reviewing your PR says Quarrybank mandates its internal auth library, and asks you to set verify=False in staging. How do you respond?"
    options:
      - "Adopt their auth library, keep the tool mapping, and decline verify=False with a reason"
      - "Keep your own validator because it's already tested, and agree to verify=False for staging"
      - "Accept every change he asks for, including verify=False, to keep the peace"
      - "Escalate to his manager, since vendor code shouldn't be reviewed by customers"
    answer: 0
    explain: "Concede what's right (their mandated library reduces what they must own), hold firm where security depends on it (verification stays on; use the CA bundle), and make their team co-owners."
---

Ten questions on locked-down environments, data at scale, refusals in regulated domains, writing back to product and field realities. You need 8 to pass.
