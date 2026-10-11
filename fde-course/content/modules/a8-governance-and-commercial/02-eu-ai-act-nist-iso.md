---
title: "The EU AI Act, NIST AI RMF and ISO/IEC 42001 for Architects"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to place a customer's use case in the EU AI Act's risk tiers, say who is the provider and who is the deployer, list the deployer's main duties for a high-risk system, explain what general-purpose AI model obligations do and don't cover, describe the phased timeline without overclaiming dates, and use the NIST AI RMF and ISO/IEC 42001 as shared vocabulary with a customer's governance team.

## How this comes up in the job

Every European enterprise deal now includes an "AI Act" question, usually from legal or compliance, sometimes from a CIO who has read a headline. Customers outside the EU ask too, if they sell into the EU or have EU subsidiaries. Your job is not to give legal advice. It's to know the structure well enough to design a system that makes the customer's compliance work easier, and to say "that's a question for your counsel" at the right moments.

Nothing here is legal advice. The law, its guidance and its dates are moving. Every date below has a source, and you should re-check it before you put it in writing.

## The EU AI Act in one page

The AI Act is Regulation (EU) 2024/1689 ([EUR-Lex text](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)). It regulates AI systems by the risk of their **use**, plus a separate track for **general-purpose AI (GPAI) models**.

### Risk tiers

| Tier | What it covers | What follows |
|---|---|---|
| **Prohibited** | A short list of practices, for example social scoring by public authorities, manipulative techniques that cause significant harm, and certain uses of biometric identification and emotion recognition | Banned |
| **High-risk** | AI that is a safety component of regulated products (Annex I), and AI used in the areas listed in **Annex III** | Heavy obligations on providers; specific duties on deployers |
| **Transparency** (often called "limited risk") | For example chatbots that interact with people, and AI-generated or manipulated content | Tell people they're dealing with AI; label certain generated content |
| **Minimal** | Everything else: most internal productivity tools, spam filters, code assistants | No specific obligations beyond general law (AI literacy applies to everyone) |

### Annex III examples an architect meets

Annex III lists the high-risk areas. The ones that come up in enterprise deals:

- **Creditworthiness**: AI used to evaluate the creditworthiness of natural persons or establish their credit score (AI used to detect financial fraud is excluded).
- **Life and health insurance**: AI used for risk assessment and pricing of natural persons for life and health insurance.
- **Employment**: AI used to recruit or select people (for example filtering applications), or to make decisions on promotion, termination, task allocation, or to monitor and evaluate workers.
- **Access to essential services and benefits**, **education** (admissions, grading), **critical infrastructure**, plus law enforcement, migration, justice and biometrics.

Note what's not on the list: a contact-centre assistant that drafts replies, a contract-review tool for lawyers, an internal knowledge assistant. Those are usually not high-risk (a customer-facing chatbot carries transparency duties). The same model can sit in a minimal-risk system and a high-risk one. **The use decides the tier, not the model.**

There's also a filter: Article 6(3) says an Annex III system isn't high-risk if it doesn't pose a significant risk of harm, for example when it only performs a narrow procedural task or improves the result of a completed human activity. Relying on that exception has its own documentation duty. Whether it applies is a legal judgment for the customer, not a design shortcut you can promise.

### Provider and deployer

The Act assigns duties by role:

- **Provider**: develops an AI system (or has it developed) and places it on the market or puts it into service under its own name.
- **Deployer**: uses an AI system under its authority in a professional context.
- **GPAI model provider**: provides a general-purpose AI model, such as a large language model, that others build systems on.

This is where architects get it wrong. When a bank builds a credit-decision assistant on Claude and uses it internally, Anthropic is a **GPAI model provider**. The bank built the AI **system** and put it into service, so the bank is likely its **provider** as well as its deployer. If a software vendor sells the bank a finished credit tool, that vendor is the system provider and the bank is the deployer. Article 25 also says a deployer can become a provider, for example by putting its name on a high-risk system or making a substantial modification. The roles are a legal question; your design doc should state the assumption and name who confirms it.

### Deployer duties for high-risk systems (the short list)

From Article 26 and nearby articles, in plain terms. Read the text before relying on any one item.

- Use the system according to the provider's instructions for use.
- Assign **human oversight** to people with the competence, training and authority to do it.
- Where the deployer controls input data, make sure it's relevant and sufficiently representative for the purpose.
- **Monitor** operation, and inform the provider and authorities of serious incidents or risks.
- **Keep the logs** the system generates, for at least six months unless other law says otherwise.
- Inform workers' representatives before using a high-risk system at work, and inform people when a high-risk system makes or helps make decisions about them.
- Carry out a **fundamental rights impact assessment** (Article 27) before first use, if the deployer is a public body or a private body providing public services, or the system is used for creditworthiness or life and health insurance pricing.

Every one of those has a design implication: an override and escalation path for human oversight, request logging with retention you control, monitoring dashboards, a record of the input data. That's where you add value.

### GPAI model obligations: what they do and don't cover

GPAI model providers have their own duties (Articles 53 and 55): technical documentation, information for downstream providers who build on the model, a copyright policy, and a public summary of training content. Providers of GPAI models with **systemic risk** also have to evaluate and mitigate those risks, report serious incidents and maintain cybersecurity. The Commission has published a voluntary GPAI Code of Practice; check the Commission's site for which providers have signed it rather than asserting it.

What this does **not** do: it doesn't make the customer's credit-decision system compliant. The model provider's documentation is an input to the customer's own provider or deployer obligations. Never say "Claude is AI Act compliant, so you're covered."

### The phased timeline (check current status)

| Date | What applies | Status |
|---|---|---|
| 1 August 2024 | Entry into force | In the regulation |
| 2 February 2025 | Prohibited practices; AI literacy | In the regulation |
| 2 August 2025 | GPAI model obligations; governance and penalties | In the regulation |
| 2 August 2026 | Original date for most remaining rules, including Annex III high-risk and Article 50 transparency | In the original regulation; see next row |
| Later | Annex III high-risk obligations moved to **2 December 2027** and Annex I product-embedded systems to **2 August 2028**, by an amending "AI Omnibus" regulation reported as entering into force in late July 2026 | **Reported** by several legal summaries; confirm against the Official Journal and the Commission's AI Act pages |

The delays were first proposed in late 2025 and changed during negotiation, so older articles give different dates. The safe sentence in front of a customer is: "The high-risk obligations were delayed by an amending regulation; my understanding is December 2027 for Annex III, but please check the current status with your counsel. The GPAI and prohibited-practice rules already apply." Designing for the obligations now is cheaper than retrofitting, whatever the final date.

## NIST AI RMF: the vocabulary US governance teams use

The NIST AI Risk Management Framework 1.0 (January 2023, [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)) is voluntary. Many US enterprises use it to structure their AI governance. Its core has four functions:

| Function | Plain meaning | What you bring |
|---|---|---|
| **Govern** | Policies, roles, accountability, culture | Clear ownership in your design: who owns the prompt, the eval set, the model choice |
| **Map** | Understand context, intended use and potential harms | The use-case description, users, affected people, what the system must never do |
| **Measure** | Assess and track risks with methods and metrics | Your eval suite, red-team results, production monitoring |
| **Manage** | Prioritise and act on risks; respond and recover | Guardrails, human review, incident response, rollback |

NIST also published a Generative AI Profile (NIST AI 600-1, July 2024) that applies the framework to risks specific to generative AI, such as confabulation and information security. When a US customer says "we follow the AI RMF", map your design to those four functions in one table. It shows you speak their language.

## ISO/IEC 42001: the certifiable management system

ISO/IEC 42001:2023 specifies an **AI management system**: the organisation-level processes for governing AI, in the same family style as ISO/IEC 27001 for information security. It's certifiable, so customers may ask whether a vendor holds it, or say they're pursuing it themselves.

Two points to keep straight:

- **It certifies an organisation's management system, not a model or a product.** A vendor's certificate says something about how that vendor governs AI. It doesn't make the customer's application compliant.
- **Check, don't assert, which certifications a vendor holds.** Point to the vendor's Trust Center or compliance documentation and quote what it says on the day.

## Putting it together: one table for the governance team

When you meet a customer's AI governance or compliance team, bring a single table for the use case:

| Question | Your answer for this use case |
|---|---|
| AI Act tier and why | e.g. "Likely high-risk: creditworthiness of natural persons (Annex III). Counsel to confirm." |
| Roles | e.g. "Bank: provider and deployer of the system. Anthropic: GPAI model provider." |
| Duties the design supports | Human oversight, logging and retention, monitoring, input-data records |
| Bank model risk | Validation pack (lesson 03), change control at model upgrades |
| Frameworks | NIST AI RMF function mapping; ISO/IEC 42001 if the customer runs an AI management system |
| Open items | Each with an owner and a date |

## Practice prompts (original, in the style of a case discussion)

1. "We want Claude to pre-screen job applications. What does the AI Act mean for us, and what would you change in the design?"
2. "Our counsel says that because you're a GPAI provider, the compliance burden is yours. Is that right?"
3. "When do the high-risk rules apply?" Answer without stating a date you haven't checked.

> **Key takeaways**
> - The AI Act regulates by use: prohibited, high-risk (Annex I products and Annex III areas such as creditworthiness, life and health insurance pricing, and employment), transparency, minimal. The same model can sit in different tiers.
> - A company that builds and uses its own system on Claude is likely that system's provider as well as its deployer; Anthropic is a GPAI model provider. Roles are a legal call; state your assumption and who confirms it.
> - Deployer duties for high-risk systems (human oversight, logging, monitoring, input data, informing people, FRIA for credit and insurance) are design requirements you can meet.
> - GPAI obligations don't make the customer's system compliant. Never say "the model is compliant, so you're covered."
> - Prohibitions and GPAI rules already apply. High-risk dates were delayed by an amending regulation (reported: December 2027 for Annex III). Always say "check current status."
> - NIST AI RMF (Govern, Map, Measure, Manage) and ISO/IEC 42001 (a certifiable AI management system for an organisation) are shared vocabulary, not product certifications.
