---
title: "Prompting, RAG, Agents, Fine-Tuning, or No LLM at All"
type: reading
minutes: 20
---

> **By the end of this lesson** you'll be able to place a customer's use case on a ladder of approaches, name the signals that move it up or down, explain why "fine-tune it on our documents" is usually the wrong first step, and say out loud when the right answer is not an LLM.

## How this comes up in interviews

Anthropic's Solutions Architect, Applied AI posting describes pre-sales architecture for large enterprises: fitting Claude into the customer's stack and designing scalable architectures (Official, from the job posting). In practice the first architecture decision is the approach, and customers often arrive having already picked one. Solutions architect interview loops are thinly documented. The accounts that exist describe a case discussion and a presentation (Anecdotal). Either way, expect to be handed a use case and asked "how would you build this, and why not the alternatives?"

The interviewer is listening for three things: you start with the simplest approach that could work, you name what would make you add complexity, and you can say no to a customer's preferred approach without losing them.

## The ladder

Think of the options as rungs. Start at the bottom and climb only when a signal forces you to.

| Rung | What it is | What it's good at | What it costs you |
|---|---|---|---|
| 0. No LLM | Rules, SQL, search, a form, classic ML | Deterministic, cheap, auditable, fast | Brittle on messy language |
| 1. Prompting | One call: instructions, examples, the input | Most language tasks: extract, classify, draft, summarize | Context and prompt upkeep |
| 2. Retrieval (RAG) | Fetch relevant documents, put them in the prompt | Knowledge that is large, private or changes often; citations | A search pipeline to build and evaluate |
| 3. Tools and workflows | The model calls your APIs in fixed steps | Actions, live data, multi-step processes | Integration, permissions, more failure modes |
| 4. Agents | The model decides the steps in a loop | Open-ended tasks where the path isn't known in advance | Cost, latency, compounding errors, testing burden |
| 5. Fine-tuning | Train a model's weights on your examples | Narrow, stable behaviour or format at very high volume | Data prep, training runs, lock-in to one model version |

Anthropic's engineering post [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) makes the same argument for rungs 1 to 4: "we recommend finding the simplest solution possible, and only increasing complexity when needed." It notes that for many applications a single call with retrieval and in-context examples is enough.

Rungs combine. A support assistant is often prompting plus retrieval plus two read-only tools. The ladder is about which complexity you add, and why.

## Signals for each rung

**Stay at rung 0 (no LLM) when:**

- The input is already structured. "Flag invoices over $10,000 from new vendors" is a SQL query.
- The rule fits on one page and rarely changes.
- Every decision must be exactly reproducible and explainable line by line (some regulated decisions).
- You have years of labelled data for a narrow prediction (churn, fraud score) and a classic model already performs well.
- Latency must be in single-digit milliseconds, or the volume is billions of tiny items.

Saying "you don't need an LLM for this part" is one of the most credible things an architect can say. It's also common: most good LLM systems have plenty of plain code around the model.

**Prompting (rung 1) is enough when:**

- Everything the model needs fits in the prompt: the instructions, a few examples and the input.
- The knowledge involved is general, or small and stable enough to paste in.
- You can write down what a good output looks like. If you can't, no rung will save you; go back to discovery.

**Add retrieval (rung 2) when:**

- The knowledge is too big for the prompt, or too costly to send on every call.
- It changes: policies, prices, product catalogues, manuals with monthly revisions.
- Answers need citations a person can check.
- Access differs by user, so the system must only show what this user may see.

With 1M-token context windows on current Claude models, "too big" is a higher bar than it used to be. A 200-page policy manual might simply go in a cached prompt. Retrieval still wins when the corpus is far larger, changes often, or needs per-user access control.

**Add tools or a workflow (rung 3) when:**

- The task needs live data (order status, account balance) or must do something (create a ticket, update a record).
- The steps are known: classify, look up, draft, check. A fixed workflow is easier to test than an agent.

**Use an agent (rung 4) when:**

- The number and order of steps depends on what the model finds along the way: research, debugging, multi-system investigations.
- You can afford the extra cost and latency, and you can test in a sandbox with guardrails. The same Anthropic post warns that agents trade cost and latency for task performance, and that errors can compound.

**Consider fine-tuning (rung 5) only when:**

- You need a narrow, stable behaviour (a house style, a fixed output format, a domain-specific classification) that prompting, examples and structured outputs still can't hit reliably on your eval.
- You have a large set of high-quality input-output examples.
- The behaviour won't change often, so the training cost is amortized.
- You've checked that the model and platform you need actually support it. Availability of fine-tuning differs by model, vendor and cloud platform and changes over time. Confirm with the vendor's current docs before it appears in any proposal.

## The decision table

Use it in discovery. Each row is a question you ask, and what the answer points to.

| Question | If yes | If no |
|---|---|---|
| Can a rule, query or form do it reliably? | Rung 0. Use an LLM only for the messy edges. | Keep going. |
| Does the knowledge fit in a cached prompt and change rarely? | Prompting (rung 1). | Retrieval (rung 2). |
| Must answers cite sources or respect per-user permissions? | Retrieval with citations and access filters. | Retrieval optional. |
| Does it need live data or actions? | Tools (rung 3), with human approval for risky actions. | No tools. |
| Are the steps known in advance? | A fixed workflow. | An agent (rung 4), sandboxed and evaluated. |
| Is the remaining gap a stable style or format at very high volume, with lots of examples? | Evaluate fine-tuning against a strong prompted baseline. | Don't fine-tune. |

## Wrong choices customers push for

Customers arrive with an approach in mind. Your job is to separate the outcome they want from the technique they've heard of.

**"Fine-tune a model on our documents so it knows our business."** This is the most common one. Fine-tuning is a poor way to add facts:

- The knowledge is frozen at training time. When the manual is revised next month, the model is out of date until you retrain.
- It can't cite. Users can't check where an answer came from.
- It doesn't respect permissions. Anything in the training set can come out for any user.
- Removing a fact (a recalled part, a withdrawn policy) means retraining.
- You're tied to one model version. When a better model ships, you start again.

Retrieval fixes all five. What the customer actually wants is "answers grounded in our documents", so lead with that.

**"We need an agent."** Ask what the agent would do step by step. If you can write the steps down, it's a workflow. Workflows are cheaper, faster and easier to test.

**"Use the biggest model for everything."** Model choice is a lever you set per task against an eval, not a statement of seriousness. Lesson 4 covers the order in which to pull cost levers.

**"Let's train our own model."** For almost every enterprise this means years of work and a research team. Ask what problem it would solve that a hosted model with retrieval and good prompts doesn't.

**"Replace the rules engine with AI."** If the rules work, keep them. Put the model where the rules break: free-text fields, exceptions, the "other" bucket.

## How to say no without losing the room

1. **Restate the goal in their words.** "You want technicians to get correct answers from the latest manuals, with the source."
2. **Show the gap.** "Fine-tuning would bake in this month's manuals. Next month's revisions wouldn't be there."
3. **Offer the better path, and keep their option open.** "Let's start with retrieval over the manuals and measure it. If an eval later shows a gap in tone or format that prompting can't close, we'll test fine-tuning against that baseline."
4. **Make it measurable.** Agree the eval and the success threshold before anyone builds anything. Module A4 covers proofs of concept.

## Practice (say it out loud)

Original prompts in the style of a solutions architect case round:

- "A bank wants to flag suspicious wire transfers. Where do LLMs fit, and where don't they?"
- "A retailer's CTO says, 'We'll fine-tune on our product catalogue so the chatbot knows every SKU.' Respond."
- "Walk me through when you'd move a document-processing workflow from a fixed pipeline to an agent."

> **Key takeaways**
>
> - Climb the ladder from the bottom: no LLM, prompting, retrieval, tools and workflows, agents, fine-tuning. Add a rung only when a signal forces it.
> - Knowledge that is large, private, changing or needs citations points to retrieval. Live data and actions point to tools. Unknown step order points to agents.
> - Fine-tuning shapes behaviour; it's a poor way to add facts. Confirm availability for the specific model and platform before proposing it.
> - "Not an LLM" is often the right answer for part of the system, and saying so builds trust.
> - Redirect a customer's technique to their goal, then agree an eval that decides.
