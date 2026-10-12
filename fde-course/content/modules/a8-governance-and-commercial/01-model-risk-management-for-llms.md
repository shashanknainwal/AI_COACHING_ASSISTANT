---
title: "Model Risk Management: Getting an LLM Through a Bank's Validation"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to explain what a bank's model risk function needs before an LLM application goes live, map the main supervisory expectations (US SR 11-7 / OCC 2011-12 and the UK PRA's SS1/23) to evidence you can actually produce, turn your evals into validation evidence, and design change control for the day the model version changes.

## How this comes up in the job and the interview

Anthropic's applied AI postings for architects describe working with large enterprises in regulated industries, including financial services (**Official**, job postings; check the current wording). In a bank, the person who can stop a launch is often not the CTO or the CISO. It's the model risk function: a second-line team that independently validates models before they're used and keeps validating them afterwards.

No public candidate account confirms that architect interviews include a model risk scenario, so treat this as preparation for the job and for any case study set in a bank. Practice prompts at the end are original, written "in the style of" a case discussion.

This lesson is general education about published supervisory guidance, not legal or compliance advice. Each bank interprets the guidance in its own model risk policy. In front of a customer, ask for their policy and work to it.

## What a model risk function is

Banks use quantitative models everywhere: credit scoring, capital, pricing, fraud. Bad models have caused real losses, so supervisors expect banks to manage **model risk**: the chance of loss from a model that's wrong or misused.

The usual structure is three lines:

| Line | Who | What they do with your LLM application |
|---|---|---|
| First line | The business and the team that builds or owns the model | Develops, documents, tests and monitors it. You support them. |
| Second line | Model risk management (MRM), often a validation team | Independently challenges the design, tests it, approves or rejects use, sets conditions |
| Third line | Internal audit | Checks that the first two lines followed the bank's policy |

The phrase you'll hear most is **effective challenge**: critical review by people who are independent, competent and have enough influence to make the developers change things. The validator's job is to find what's wrong with your system. Help them do it.

## The guidance in brief

### United States: SR 11-7 and OCC 2011-12

The Federal Reserve's SR 11-7 and the OCC's Bulletin 2011-12 (both 2011, the same "Supervisory Guidance on Model Risk Management") are the reference most US banks build their policies on. Read the source: [SR 11-7](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm). Check whether it has been updated or supplemented before quoting it in writing.

In plain terms it expects:

- **A broad definition of "model".** A quantitative method that turns inputs into estimates or outputs, including approaches that rely partly on judgment. Many banks have decided that LLM applications fall inside that definition, or inside a parallel AI risk framework with similar controls. Which one is the bank's decision, not yours.
- **Sound development, implementation and use.** Clear purpose, documented design, testing, and use within the limits the model was built for.
- **Validation** with three core parts: evaluation of **conceptual soundness** (is the design reasonable for the purpose?), **ongoing monitoring** (does it still work?), and **outcomes analysis** (do outputs match reality?).
- **Governance**: policies, a model inventory, clear roles, and documentation detailed enough that someone unfamiliar with the model could understand it.
- **Vendor models get validated too.** The bank can't skip validation because it bought the model. It should get enough information from the vendor to understand the model, and where the vendor won't disclose internals, rely more on testing, benchmarking and monitoring of the bank's own use.

That last point is your whole job in an LLM validation. Anthropic won't hand over model weights or training data. The bank's validators will test the **system** the bank built: the prompt, the tools, the retrieval, the guardrails and the human review, on the bank's own data.

### United Kingdom: PRA SS1/23

The Prudential Regulation Authority's Supervisory Statement **SS1/23**, "Model risk management principles for banks", took effect in May 2024 ([PRA SS1/23](https://www.bankofengland.co.uk/prudential-regulation/publication/2023/may/model-risk-management-principles-for-banks-ss)). It applies directly to UK banks and building societies with approval to use internal models for regulatory capital, and the PRA has said others may find it useful. Check the scope paragraph against your customer before saying it applies to them.

It sets five principles:

1. **Model identification and model risk classification.** A clear definition of a model, a complete inventory, and a tiering of models by risk.
2. **Governance.** Board-level oversight, a senior manager accountable for model risk, policies.
3. **Model development, implementation and use.** Including data quality, testing and documentation.
4. **Independent model validation.** Including validation before use and periodic revalidation.
5. **Model risk mitigants.** For example restrictions on use, adjustments, or extra human review when a model has known weaknesses.

SS1/23 explicitly expects banks to think about models whose behaviour is harder to explain, which is why UK validators will ask how you'll detect when the system is wrong, not just how accurate it was in testing.

## What's different about validating an LLM application

Traditional validation assumes a model that's deterministic, has a small number of inputs and was trained by the bank. An LLM application breaks all three. Name these differences early; the validator is already thinking about them.

| Traditional assumption | LLM reality | What you offer instead |
|---|---|---|
| Same input, same output | Outputs vary between runs | Run each eval case several times. Report the variance and the worst case, not just the average. |
| The bank can inspect the model | Vendor model, closed weights | Test the system on the bank's data; document the vendor's published model card, system card and lifecycle policy; benchmark against an alternative |
| A fixed, narrow input space | Free text, documents, conversations | A representative eval set plus adversarial cases (prompt injection, out-of-scope requests, missing data) |
| Retrained on a schedule the bank controls | New model versions from the vendor; old ones retire | Change control tied to model version (below) |
| Output is a number | Output is text, sometimes an action | A rubric, human-labelled reference answers, and limits on what the system can do without a person |

On current Claude models, sampling parameters such as `temperature` are rejected on the newest models, so you can't promise determinism by setting temperature to zero. Say so plainly. Determinism was never the real requirement anyway; the requirement is that the bank can measure how much outputs vary and show that the variation doesn't change decisions in ways that matter.

## Turning evals into validation evidence

You already know how to build evals (Engineer track module E4, and the bake-off in A4). The skill here is mapping that work onto the categories a validator uses. Build this table with the first-line owner and give it to the validator before they ask.

| Validation element | Evidence from your LLM work |
|---|---|
| Purpose and scope | One-page design: what decisions the system supports, who uses it, what it must never do |
| Conceptual soundness | Design doc: why an LLM, why this model tier, prompt and tool design, retrieval design, guardrails, human review step. Alternatives considered and rejected. |
| Data | Where the eval set came from, how it was sampled, how it represents real traffic (segments, languages, edge cases), who labelled it and how disagreements were settled |
| Outcomes analysis | Eval results by segment, with the number of cases and an uncertainty range, an error taxonomy, and the cost of each error type in business terms |
| Benchmarking | The same frozen eval set run on an alternative: another model tier, the current manual process, or the incumbent tool |
| Sensitivity and stability | Repeated runs (variance), paraphrased inputs, reordered documents, long versus short inputs, and the effect of `effort` settings |
| Limitations | A written list of known weaknesses and where the system should not be used |
| Ongoing monitoring | Production sampling and human review rates, drift checks, refusal rate, escalation rate, alert thresholds and who acts on them |
| Vendor information | Model card or system card, the deprecation policy, the platform the bank uses and who operates it, data handling terms |

Two habits make this credible:

- **Report the denominator.** "92% correct" means nothing without "on 400 cases, of which 60 were the hard segment, where it scored 78%."
- **Write the acceptance threshold before the final run.** The same rule as a fair bake-off: a threshold set after seeing results isn't a threshold.

## Change control when the model changes

A bank validates a specific system. When any part changes, the bank's policy decides whether it needs revalidation. The model is the part that changes on someone else's schedule.

What you can say from Anthropic's documentation (checked October 2026):

- **Models retire.** Anthropic's [model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations) page says customers with active deployments get **at least 60 days' notice** before retirement for publicly released models, and lists each model's tentative retirement date ("not sooner than" a date for active models).
- **Retirement dates differ by platform.** The dates on that page apply to the Claude API, Claude Platform on AWS and Microsoft Foundry. Amazon Bedrock and Google Cloud set their own schedules.
- **A new model is a new rate-limit pool.** Anthropic's rate-limit docs give each current model its own limits. Moving traffic to a new model doesn't carry headroom across, so capacity is part of the change plan (lesson 05).
- **Behaviour changes are documented as breaking changes.** Anthropic's migration guide lists changes such as rejected parameters or new refusal behaviour per model. Read it for the target model before you plan the test.

What you should **not** assert without checking: whether the model behind a given model ID can change over time, and how such a change would be announced. Make it an open item for the account team and record the answer in the validation pack.

A change-control design you can propose:

1. **Pin the model ID in configuration**, not in code scattered across services. One gateway owns it (module A6 patterns).
2. **Tier the changes.** Agree with MRM which changes need full revalidation (new model family or version), which need a targeted re-run (prompt edit, new tool, `effort` change), and which need only a log entry (logging format).
3. **Keep the frozen eval set and the acceptance thresholds** from the original validation. A model upgrade re-runs exactly that set, plus any cases added from production incidents.
4. **Shadow before switching.** Run the new model on a copy of live traffic, compare, then move a small share of traffic, then all of it, with a rollback path to the old model while it's still available.
5. **Start early.** With at least 60 days' notice, the validation cycle has to fit inside the window. Ask MRM how long a revalidation takes and plan backwards from the retirement date, not forwards from the announcement.

## Practice prompts (original, in the style of a case discussion)

1. "Our model risk team says an LLM can't be validated because it isn't deterministic. How do you respond?"
2. "Your vendor won't give us the training data. Why should our validators sign off on it?"
3. "The model we validated retires in five months. Walk me through the plan."

> **Key takeaways**
> - In a bank, model risk management is a second-line function that can stop a launch. Work with it early, and help it challenge your design.
> - SR 11-7 / OCC 2011-12 (US) and PRA SS1/23 (UK) expect sound development, independent validation, governance and an inventory. Vendor models still need validation; the bank tests the system it built on its own data.
> - LLM validation replaces determinism with measured variance, closed weights with system testing and benchmarking, and a fixed model with change control.
> - Map your evals to validation categories: conceptual soundness, data, outcomes, benchmarking, sensitivity, limitations, monitoring and vendor information. Report denominators and set thresholds before the final run.
> - Anthropic gives at least 60 days' notice before retiring a publicly released model, and Bedrock and Google Cloud set their own dates. Pin the model ID, tier changes with MRM, keep the frozen eval set and plan revalidation backwards from the retirement date.
