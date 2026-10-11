---
title: "Written: Outline a Model Risk Validation Pack"
type: written
minutes: 40
sections:
  - key: scope
    label: 1. Purpose, scope and risk tier
    prompt: "What the system does and doesn't do, who uses it, which decisions it supports, and the risk tier you'd propose under the bank's policy. Say how the EU AI Act likely classifies it and who must confirm that."
    words: [100, 250]
  - key: soundness
    label: 2. Conceptual soundness and limitations
    prompt: "Why this design fits the purpose: the model choice, prompt and tools, guardrails and human review. List the known limitations and where the system must not be used."
    words: [120, 300]
  - key: evidence
    label: 3. Testing evidence
    prompt: "Map the pilot results to outcomes analysis, benchmarking and sensitivity testing. Address non-determinism directly. Say what you'd add before go-live and the acceptance thresholds you'd propose."
    words: [150, 350]
  - key: monitoring
    label: 4. Ongoing monitoring
    prompt: "What's measured in production, how often, the thresholds, and who acts when one is breached."
    words: [80, 220]
  - key: change_control
    label: 5. Change control and open items
    prompt: "What happens when the model version, prompt or platform changes, including retirement dates. Finish with open items, each with an owner and a date."
    words: [100, 260]
rubric:
  - name: Validation structure
    points: 20
    lookFor: "Organised around what a validator needs: purpose and scope, conceptual soundness, data, outcomes analysis, benchmarking, sensitivity, limitations, monitoring, vendor information. Uses SR 11-7 / SS1/23 ideas (effective challenge, inventory, tiering, mitigants) correctly without over-quoting."
  - name: Honest use of the evidence
    points: 25
    lookFor: "Reports results with denominators and segments: the self-employed segment (76% on 80 cases) is called out as a weakness, not hidden in the 89% average. Treats the two invented income sources as a serious error class with a mitigation. Addresses non-determinism with repeated runs and the 3% flip rate, and proposes thresholds set before the final run."
  - name: Regulatory accuracy
    points: 20
    lookFor: "Says the use likely falls in Annex III (creditworthiness of natural persons) for the Irish subsidiary, that Brackenridge is likely provider and deployer of the system and Anthropic a GPAI model provider, and that counsel confirms. Mentions deployer-style duties (human oversight, logging, monitoring) as design requirements. Doesn't state the high-risk application date as certain; says check current status. Treats vendor documentation as an input, not as compliance."
  - name: Change control that works
    points: 20
    lookFor: "Pins the model ID in one place; tiers changes with MRM; re-runs the frozen eval set and thresholds on a model change; shadow then staged rollout with rollback; plans revalidation backwards from the retirement date. Knows Bedrock sets its own retirement dates, distinct from Anthropic's page, and that a new model has its own rate limits. Makes 'can the model behind an ID change?' an open item instead of asserting an answer."
  - name: Clear and usable
    points: 15
    lookFor: "Written for a validator: plain, specific, no marketing. Open items have owners and dates."
passScore: 70
graderNotes: "This is an outline, so bullets are fine; judge substance. Mark down hard for burying the self-employed segment result or the invented income sources: an answer that reports only the 89% headline caps 'Honest use of the evidence' at 10. Claiming the system is deterministic, or that setting temperature to zero fixes variability, caps the same criterion at 12 (sampling parameters are rejected on the newest models). Saying the EU AI Act high-risk rules apply from a specific date as settled fact, or that Anthropic's GPAI obligations make the bank compliant, caps 'Regulatory accuracy' at 10. Stating Anthropic's 60-day notice as applying to Bedrock retirements caps 'Change control that works' at 12. Reward an answer that proposes removing or restricting the self-employed segment until it improves (a model risk mitigant) and that ties the two invented income sources to a specific check, such as requiring every extracted figure to cite the source document and page and having code verify it."
anchors:
  - label: weak
    expect: [0, 45]
    answer: "Purpose: an AI assistant that helps underwriters. It's very accurate at 89% and 97% on income. Claude is a leading model and Anthropic is compliant with the EU AI Act, so the bank doesn't need to worry about that. Testing: we tested on 500 applications with great results. To fix non-determinism we set temperature to 0. Monitoring: we'll watch for problems. Change control: Anthropic gives 60 days' notice so we'll upgrade when told. Open items: none."
  - label: strong
    expect: [75, 100]
    answer: "1. Scope: drafts an affordability summary from consumer loan documents for underwriters at the Irish lending subsidiary; the underwriter decides. Never approves, declines or prices. Proposed tier: high under Brackenridge policy because it influences credit decisions on individuals. Under the EU AI Act this likely falls in Annex III (creditworthiness of natural persons); Brackenridge is likely provider and deployer of the system, Anthropic a GPAI model provider. Counsel to confirm by 14 Nov. High-risk application date: delayed by an amending regulation; check current status, design for it now.\n2. Soundness: Sonnet 5.5 at an explicit effort level; extraction with every figure citing document and page, verified in code; underwriter reviews every summary. Limitations: weak on self-employed income (76% on 80 cases); restrict that segment to 'extract only, no affordability flag' until it passes. Not for business lending.\n3. Evidence: 500 historical applications labelled by two senior underwriters. Income extraction 486/500 (97.2%); affordability flag agreement 445/500 (89%), but self-employed 61/80. Two invented income sources: a critical error class; the citation check must catch 100% of a seeded test set. Non-determinism: five runs per case, 3% of flags flipped; report flip rate by segment, require that flips never cross a decline threshold without review. Benchmark: same set against the current manual process and Haiku 5.5. Add 150 adversarial and recent cases before go-live. Thresholds written before the final run: flag agreement at least 88% overall and 85% per segment, zero uncited figures.\n4. Monitoring: 5% weekly sample double-reviewed; override rate, flip rate, refusal rate, uncited-figure alerts; MRM and the product owner review monthly; breach of a threshold pauses the segment.\n5. Change control: model ID pinned in the gateway config; MRM agrees tiers (new model = full re-run of the frozen set; prompt edit = targeted re-run). Shadow, then 10%, then 100%, with rollback while the old model is available. On Bedrock, AWS sets the retirement schedule, so track Bedrock's dates, not only Anthropic's 60-day notice. A new model has its own rate limits: re-check capacity. Open items: can the model behind an ID change (account team, 7 Nov); revalidation lead time (MRM, 7 Nov); log retention period (compliance, 14 Nov)."
---

This lesson is practice at the document that decides whether a bank's LLM project goes live: the validation pack the first line hands to model risk management. You're outlining it, not writing all 40 pages. Validators will read your outline to decide whether the full pack will be worth their time.

## The situation

**Brackenridge Bank** (fictional) is headquartered in the UK, with a consumer lending subsidiary in Ireland and a branch in the US. Its model risk policy is written to satisfy both the PRA's SS1/23 and the US SR 11-7 guidance. Owen Hartwell (fictional), Head of AI Platform, asks you to help his team outline the validation pack for a pilot that's going well.

| Fact | Value |
|---|---|
| Use case | Drafts an affordability summary from consumer loan documents (payslips, bank statements, employment letters) for underwriters at the Irish subsidiary. The underwriter makes every decision. |
| Model and platform | Claude Sonnet 5.5 on Amazon Bedrock, using an EU inference option the platform team confirmed. Effort set explicitly. |
| Design | Extract income and commitments as structured fields, each citing a source document and page; draft a summary; raise an "affordability concern" flag where the numbers suggest one |
| Pilot | 500 historical applications labelled by two senior underwriters |
| Income extracted correctly | 486 of 500 (97.2%) |
| Affordability flag agrees with underwriters | 445 of 500 (89%) |
| Self-employed applicants | 80 of the 500; flag agreement 61 of 80 (76%) |
| Repeated runs | Each case run 5 times: the flag changed between runs on 3% of cases |
| Serious errors | 2 cases where the summary cited an income source that wasn't in the documents |
| Platform note | Bedrock sets its own model retirement schedule |

Lessons 01 and 02 have what you need. Write for the validator: what they'll test, what you already know is weak, and what you propose to do about it.

## What good looks like

- Results reported with denominators and segments, weaknesses named first.
- Non-determinism handled with measurement, not denial.
- Regulatory roles and tiers stated as assumptions with an owner who confirms them.
- Change control that would still work on the day the model retires.
- Open items with owners and dates.

Brackenridge Bank, Owen Hartwell and every figure above are fictional.
