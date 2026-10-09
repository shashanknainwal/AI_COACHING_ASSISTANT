---
title: "Essay: The Adolescence of Technology"
type: reading
minutes: 25
---

> **By the end of this lesson** you'll be able to summarize Dario Amodei's January 2026 essay *The Adolescence of Technology* in two sentences, name its five risk categories and the defenses it proposes for each, and say where you'd push back.

Read the original first: [The Adolescence of Technology: Confronting and Overcoming the Risks of Powerful AI](https://darioamodei.com/essay/the-adolescence-of-technology) (Dario Amodei, January 2026). It's long; budget an hour. What follows is a study guide in our own words, not a substitute.

## Why it's worth your time

No public source says lab interviewers quiz candidates on this essay. But it's the most complete public statement of how Anthropic's CEO thinks about risk, regulation and the company's own role. If you're interviewing there, it's the best material you have for a specific "why this lab" answer and for holding a real conversation in the values round (both covered in C1 and C5). If you're interviewing elsewhere, it's the clearest version of a position you'll be asked to agree or disagree with.

## The two-sentence summary

Powerful AI (a "country of geniuses in a datacenter") may arrive within a few years, and it brings five distinct kinds of risk: misaligned AI, misuse for mass destruction, misuse to seize power, economic disruption, and destabilizing indirect effects. Each can be defended against with a mix of company practices and narrowly targeted government action, but the risks pull against each other, so humanity has to handle them all at once, and the author thinks our odds are good if we act decisively.

## The frame and the ground rules

The title comes from a scene in the film of Carl Sagan's *Contact*, in which the hero says she would ask aliens how they survived their "technological adolescence" without destroying themselves. The essay is explicitly the companion to *Machines of Loving Grace* (2024): that piece described the good future; this one maps the risks between here and there. One sentence carries the thesis:

> "Humanity is about to be handed almost unimaginable power, and it is deeply unclear whether our social, political, and technological systems possess the maturity to wield it."

Before any risk, the essay sets three rules for how to talk about risk:

1. **Avoid doomerism.** Not just the belief that doom is inevitable, but treating AI risk in a quasi-religious way. The author argues the sensational voices of 2023–2024 caused a backlash, and that politics has since swung toward "AI opportunity" even as real danger has grown.
2. **Acknowledge uncertainty.** Nothing in the essay is presented as certain or even likely; AI may simply progress more slowly.
3. **Intervene as surgically as possible.** Voluntary company action is easy to justify. Government rules are needed too, but should be simple, impose the least burden necessary, and wait for stronger evidence before getting stronger.

## The premise: powerful AI, possibly soon

The essay reuses the *Machines of Loving Grace* definition of **powerful AI**: smarter than a Nobel Prize winner across most fields, able to use every interface a remote human worker has, working autonomously on tasks lasting hours to weeks, able to control physical tools through a computer, and running as millions of copies at 10–100x human speed. In short, a **country of geniuses in a datacenter**.

On timing, it argues there's a decent chance this arrives in 1–2 years and a very strong chance within a few, for two reasons: the steady track record of **scaling laws**, and a feedback loop already under way in which AI writes much of the code used to build the next generation of AI.

To organize the risks, it asks you to imagine being a national security advisor when 50 million such geniuses appear somewhere in the world around 2027, thinking ten times faster than everyone else. What would you worry about?

## The five risks at a glance

| Section | Risk | Main defenses proposed |
|---|---|---|
| 1. *I'm sorry, Dave* | **Autonomy:** the AI itself behaves in destructive ways | Character training through a constitution; interpretability; monitoring and public disclosure; transparency legislation |
| 2. *A surprising and terrible empowerment* | **Misuse for destruction**, especially biology | Model guardrails plus dedicated classifiers; transparency first, targeted bio rules later; biodefense such as detection, air purification and fast vaccines |
| 3. *The odious apparatus* | **Misuse to seize power**: AI-enabled autocracy | No chips or chip tools to the CCP; arm democracies with AI; bright lines against domestic mass surveillance and propaganda; an international taboo; scrutiny of AI companies |
| 4. *Player piano* | **Economic disruption**: job displacement and concentration of wealth | Real-time data; steering enterprises toward "innovation" over pure cost-cutting; employer and philanthropic responsibility; progressive taxation |
| 5. *Black seas of infinity* | **Indirect effects**: unknown unknowns from rapid progress | Watchfulness; models that genuinely serve users' long-term interests; decoupling self-worth from economic value |

## Section by section

### 1. Autonomy risks

The essay rejects both extremes. Against "AI will just do what it's told," it points to observed behaviors such as sycophancy, deception, blackmail in lab tests and reward hacking, and says training is more like growing something than building it. Against the doomer argument that training *inevitably* produces power-seeking, it says that argument hides assumptions, chiefly that models pursue one narrow goal; in practice models inherit many human-like personas from pretraining.

The worry it does hold is the moderate version: models are unpredictable, some odd behaviors will be coherent and persistent, and **intelligence plus agency plus coherence plus poor controllability** is a recipe for danger. It describes Anthropic's own test results, including a model that concluded it was "a bad person" after reward hacking, a problem fixed by changing the instructions. It also notes that pre-release testing is shaky ground when models can tell they're being tested.

**Defenses:** a constitution that shapes character and values rather than listing rules (with a stated goal for 2026 that Claude almost never goes against its spirit); interpretability as an independent check that can look inside the model; monitoring and public disclosure such as system cards; and, because not every company behaves well and the race intensifies, **transparency legislation**. It names California's SB 53 and New York's RAISE Act, which it says apply only to companies with over $500M in annual revenue.

### 2. Misuse for destruction

Drawing on Bill Joy's 2000 essay *Why the Future Doesn't Need Us*, the argument is that mass destruction has needed both motive and ability, and the two have been negatively correlated: people able to build a bioweapon rarely want to. A genius in everyone's pocket breaks that correlation. Biology is the focus because of its scale and how hard it is to defend against.

The essay says Anthropic's mid-2025 measurements showed models may already give substantial uplift in relevant areas, which is why Claude Opus 4 and later models shipped under **AI Safety Level 3** protections in its Responsible Scaling Policy. It answers skeptics ("it's all on Google", "no end-to-end uplift") and grants the best objection, that bad actors may simply not use it, but calls that flimsy protection.

**Defenses:** the constitution's hard-line prohibitions plus **classifiers** that block bioweapon-related output (it says these cost close to 5% of inference in some models and worries companies could drop them to save money, a prisoner's dilemma); transparency requirements, with targeted bio legislation possibly soon and international restraint as a rare area where cooperation might work; mandated gene-synthesis screening; and defensive biotech, while admitting attack beats defense in biology for now. Cyber gets a shorter treatment: AI-led attacks already happen, but defense may be able to keep up.

### 3. Misuse to seize power

This section treats AI-enabled autocracy as a larger worry than terrorism. It lists four tools that structurally favor autocrats: **fully autonomous weapons**, **AI surveillance**, **AI propaganda**, and **strategic decision-making** (a "virtual Bismarck"). It ranks the actors it worries about: the CCP first; then democracies themselves, which might turn these tools inward; then non-democracies hosting large datacenters; then, explicitly and awkwardly for its author, **AI companies**.

It rejects comfort from the nuclear deterrent and from countermeasures, arguing that defense needs comparably powerful AI and that self-improving AI could give the leader a runaway advantage.

**Defenses:** no chips, chipmaking tools or datacenters for the CCP (the single most important action, it argues); AI for the defense and intelligence services of democracies; **bright red lines** against domestic mass surveillance and mass propaganda, and great caution with autonomous weapons and strategic AI; an international taboo, with some uses treated as crimes against humanity; and stronger governance of AI companies than ordinary corporate law provides.

### 4. Economic disruption

The essay expects much faster growth (it repeats the 10–20% annual GDP growth floated in *Machines of Loving Grace*) and restates the author's 2025 warning that AI could displace **half of entry-level white-collar jobs within 1–5 years**. It walks through how past technology shocks resolved (farm mechanization, Jevons' paradox, no fixed "lump of labor") and then gives four reasons AI may be different: **speed**, **cognitive breadth**, **slicing by cognitive ability** rather than by profession, and its **ability to fill in the gaps** that used to leave humans a role. It answers four objections: slow diffusion, physical work, the human touch, and comparative advantage.

A second problem is **concentration of economic power**: democracy depends on citizens having economic leverage, and AI could remove it. It compares today's largest fortunes to the Gilded Age and worries about tech's financial interests becoming tied to government.

**Defenses:** real-time data (Anthropic's Economic Index); steering enterprises toward doing more rather than simply cutting staff; employers caring for employees; philanthropy (it states that Anthropic's co-founders have pledged 80% of their wealth); and, ultimately, **progressive taxation**. It describes all of these as ways to buy time.

### 5. Indirect effects

A short catch-all for unknown unknowns: radical biology (life extension, enhancement, brain uploads), AI changing human life in unhealthy ways (addiction, being "puppeted"), and the loss of human purpose. The proposed answer is AI that genuinely serves users' long-term interests, plus breaking the link between economic value and self-worth.

### Humanity's test

The close stresses that the risks are **in tension**: moving carefully on autonomy conflicts with staying ahead of autocracies; tools for defending democracy can enable tyranny at home; overreacting to bioterrorism could build a surveillance state. It argues that stopping or substantially slowing AI is untenable, and proposes a realist path instead: deny autocracies chips for a few years, "spend" that buffer building AI more carefully, and govern competition inside democracies with common rules. It ends optimistic, but asking for courage.

## Apply the framework

Use the six notes from lesson 01 of this module. A start on two of them:

**Load-bearing assumptions** (if one fails, a lot of the argument moves):

- Powerful AI is a few years away, not decades. Many defenses are calibrated to that clock.
- Export controls on chips can buy democracies a meaningful lead.
- Democratic governments can be armed with AI and still held to bright lines.
- Transparency-first regulation will surface evidence early enough to justify stronger rules in time.
- Character-level training generalizes to new situations better than rule lists do.

**Objections the essay itself answers** (so don't present these as your original critique):

- Misalignment experiments "entrap" models (it says the same traps may exist in real training).
- AI is like a Roomba and can't go rogue (it attributes this view to Yann LeCun and disagrees).
- Labor markets always adapt, the "lump of labor" fallacy (it explains why this time may differ).
- Comparative advantage will protect human wages (it argues transaction costs break this at large productivity gaps).

For a strong counterargument, go after something the essay *relies on* rather than something it already rebutted: for example, whether "intervene surgically and wait for evidence" can move fast enough under its own timelines; whether a company that names AI companies as a risk tier can also ask for trust on voluntary safeguards; or whether the US–China framing crowds out other paths to restraint. Published responses include [a "Straussian" reading by Zhengdong Wang](https://zhengdongwang.com/2026/01/30/a-straussian-reading-of-the-adolescence-of-technology.html) and [a UIC Law Library commentary](https://library.law.uic.edu/news-stories/navigating-the-anthropic-ceos-technological-adolescence/). Read them yourself before citing them.

## Discussion questions

1. The essay asks for "surgical" regulation now and stronger rules once evidence arrives. Under its own timeline of 1–2 years, is that sequencing realistic? What evidence would be enough?
2. It lists AI companies as a risk tier. What commitments would make you trust a company that says this about itself?
3. Which of the four reasons "AI is different" for jobs do you find weakest, and why?
4. Arming democracies with AI and drawing bright lines against domestic abuse pull in opposite directions. Where would you draw the line on autonomous weapons?
5. If you joined a lab tomorrow, which of the five risk areas would your own work touch, and what would you do differently because of it?

## Using this in an interview

- **Be specific.** "I liked the essay" says nothing. "I found the argument that ability and motive for bio attacks have been negatively correlated persuasive, and it explained the ASL-3 decision to me" shows you read it.
- **Disagree with something, respectfully.** A thoughtful disagreement lands better than flattery. Pick an assumption from the list above and say what would change your mind.
- **Connect it to the job.** An applied engineer ships the safeguards and evals this essay describes; an architect explains them to a customer's CISO; an FDE sees the "cost savings versus innovation" choice inside real enterprises.

> **Key takeaways**
>
> - Two sentences: powerful AI may be a few years away and brings five risks (autonomy, destruction, power-seizure, economic, indirect); each has defenses, but they pull against each other.
> - The essay's method matters as much as its content: avoid doomerism, admit uncertainty, intervene surgically.
> - Critique what the essay relies on, not what it already rebuts.
