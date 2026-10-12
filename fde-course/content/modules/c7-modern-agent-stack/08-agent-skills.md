---
title: "Agent Skills: Packaging Know-How for Progressive Disclosure"
type: reading
minutes: 14
---

> **By the end of this lesson you will be able to:**
> - Describe what a Skill is and the three levels of progressive disclosure.
> - Write a `SKILL.md` whose description makes it load at the right time.
> - Decide what goes in the body, in reference files and in scripts.
> - Say where Skills run and which platforms don't support them.

A Skill packages task-specific instructions and files that Claude loads only when they're relevant. For an FDE it is the cleanest way to turn a repeatable customer pattern (an exception playbook, a report format, a review checklist) into an asset every Claude-based tool can reuse, and to hand that pattern back to the product team.

## Anatomy

A Skill is a folder:

```text
shipment-exceptions/
  SKILL.md            YAML frontmatter (name, description) + Markdown instructions
  references/         detail loaded only when the instructions say so
  scripts/            code the model runs instead of re-deriving rules
```

The frontmatter needs a `name` and a `description`. Anthropic's skill tooling checks that the name is lowercase letters, digits and hyphens (no leading, trailing or double hyphens) and at most 64 characters, and that the description is at most 1,024 characters with no angle brackets. Check the current Skills documentation for the full list of rules before you publish.

## Progressive disclosure: three levels

1. **Metadata** (name and description) sits in context all the time, for every skill. It's small, roughly a hundred words.
2. **The SKILL.md body** loads when the skill triggers. Keep it short; the general guidance is under 500 lines, and shorter is better.
3. **Bundled resources** load only as needed. Reference files are read when the body points to them; scripts can run without their source ever entering context.

This is why the fixed context stays small even with many skills installed: only descriptions are always present.

## The description does the routing

Claude decides whether to consult a skill from its name and description. So the description must say what the skill does *and when to use it*, in the words people actually use. All the "when to use" information belongs here, not in the body, because the body is never read if the skill doesn't trigger. Skills currently tend to under-trigger, so a description can be a little insistent ("Use whenever ... even if the user doesn't say ..."), but tune it against a trigger eval rather than by feel.

## Body, references, scripts

| Put it in | When |
|---|---|
| The body | The steps, in order, and pointers to each reference file with when to read it |
| A reference file | Detail the steps need only sometimes: code tables, thresholds, long procedures. Add a table of contents to large ones |
| A script | Anything deterministic: a rule, a calculation, a format check. The model runs it and gets the same answer every time |

Scripts are the underused part. If the playbook says "escalate damage over EUR 10,000," a script applies that identically on every run; prose invites the model to re-derive and occasionally misapply it.

## Test it like a prompt

A skill has two failure modes, so it needs two evals:

- **Trigger eval:** a fixed set of queries that should load the skill and queries that shouldn't (including ones that belong to a neighbouring skill). Re-run it on every description change.
- **Behaviour eval:** once loaded, does it do the right thing? Run the script and the steps against known cases.

## Where Skills run

The same folder works in several places:

- **Claude Code:** put it under `.claude/skills/<name>/` in a project.
- **The Messages API:** upload it through the Skills API and enable it with the `container` parameter plus the code execution tool. Skills on the Messages API are out of beta.
- **Managed Agents:** attach it to the agent's `skills` list, or load it from a mounted repository's root `.claude/skills` folder. Repository skills are agent instructions, so treat anyone who can commit to that repo as inside your trust boundary.

Agent Skills on the Messages API are **not available on Amazon Bedrock or Google Vertex AI**, and need a Hosted-on-Anthropic deployment on Microsoft Foundry. Confirm the customer's platform before you promise a Skill-based design.

> **Key takeaways**
> - A Skill is a folder: `SKILL.md` (name, description, instructions) plus optional references and scripts.
> - Progressive disclosure: descriptions always loaded, the body on trigger, resources only when needed.
> - The description does the routing: say what the skill does and when to use it.
> - Put steps in the body, detail in reference files, and deterministic rules in scripts.
> - Run a trigger eval and a behaviour eval; Skills on the Messages API aren't on Bedrock or Vertex.
