---
title: "Five Ways to Buy Claude: Deployment Options Compared"
type: reading
minutes: 22
---

> **By the end of this lesson** you'll be able to explain who operates what on each of the five ways an enterprise can run Claude, name the feature gaps that change an architecture, write the right model ID for each platform, and walk a customer from "we're an AWS shop" to a defensible platform choice.

## How this comes up in the job and the interview

Anthropic's Solutions Architect, Applied AI posting describes pre-sales architecture for large enterprises and fitting Claude into the customer's existing stack (**Official**, job posting). In practice the first architecture question at most large companies is not "which prompt?" but "which cloud contract does this run under, and where does our data go?"

No public candidate account confirms that interviewers ask about specific cloud platforms, so treat this as preparation for the job, and for any case study where the fictional customer has a cloud preference. Practice prompts at the end are original and "in the style of" a case discussion.

A rule for this whole module: platform details change often. Everything below was checked against Anthropic's documentation in October 2026. In front of a customer, you say "as of the current docs" and you re-check before you put it in writing.

## The five options

| | **Claude API** (first-party) | **Claude Platform on AWS** | **Amazon Bedrock** | **Google Cloud Vertex AI** | **Microsoft Foundry** |
|---|---|---|---|---|---|
| Who operates inference | Anthropic | Anthropic, on AWS infrastructure | AWS | Google Cloud | Anthropic (on Azure infrastructure or Anthropic's, per deployment) |
| Data processor for prompts and outputs | Anthropic | Anthropic | AWS | Google Cloud | Anthropic |
| How it's billed | Anthropic directly | AWS Marketplace, in Claude Consumption Units | AWS, as a native service | Google Cloud | Azure Marketplace, in Claude Consumption Units |
| Identity | API keys, Workload Identity Federation | AWS IAM / SigV4, or short-term API keys | AWS IAM (service role, assumed roles), short-term bearer tokens | Google Cloud credentials | Azure API keys or Microsoft Entra ID |
| Model ID for Claude Opus 5.5 | `claude-opus-5-5` | `claude-opus-5-5` | `anthropic.claude-opus-5-5` | `claude-opus-5-5` (in the endpoint URL) | your deployment name (default `claude-opus-5-5`) |
| New features arrive | First | Typically same day as the Claude API | On Bedrock's release schedule | On Google Cloud's schedule | Most features; some only on "Hosted on Anthropic" deployments |

Sources: [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude on Google Cloud](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai), [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

Four details in that table matter more than they look.

**1. "On AWS" means two different things.** Claude Platform on AWS is Anthropic's own platform, reached and billed through an AWS account. Amazon Bedrock is an AWS service that serves Claude. Anthropic's docs put it plainly: on Bedrock, AWS operates the inference stack; on Claude Platform on AWS, Anthropic does. Customers mix these up constantly, and so do candidates. If an AWS customer says "we'll use Claude through AWS," your first clarifying question is "through Bedrock or through Claude Platform on AWS?"

**2. Who processes the data decides whose paperwork applies.** Anthropic's data retention page says that on Bedrock and Google Cloud the cloud provider is the data processor, and points you to their retention and compliance docs. On the Claude API, Claude Platform on AWS and Foundry, Anthropic is the processor. That one fact routes half of the security review (lesson 02).

**3. Foundry has two hosting options, and they aren't interchangeable.** In Foundry you pick "Hosted on Azure" (an Anthropic-operated service running on Azure infrastructure) or "Hosted on Anthropic" (Anthropic infrastructure). For Hosted on Azure, Anthropic's docs say prompts and completions stay within Azure, and only usage metadata and content flagged by Anthropic's safety systems leave Azure for Anthropic. The choice is per deployment. Three details from the Foundry page change what you tell a CISO:

- **Anthropic acts as an "independent processor for Microsoft"**, and Foundry customers are subject to Anthropic's data use terms. Don't describe Anthropic as Microsoft's subprocessor or say "Microsoft's terms only."
- **Model availability depends on the hosting option.** Claude Fable 5.1 is offered only Hosted on Anthropic, so a "prompts stay in Azure" requirement rules it out. Opus 5.5, Sonnet 5.5 and Haiku 5.5 are offered in both.
- **Claude Sonnet 5.5 supports only Global Standard deployments.** The US Data Zone option isn't available for it.

**4. Google's product name moved.** Anthropic's docs now call it "Google Cloud's Agent Platform" (the URL still says vertex-ai). Customers will say Vertex. Use their word, and know both.

## What each platform can and can't do

This is where architectures break. Anthropic's skill reference and platform pages give this picture for the features architects most often depend on (GA unless marked beta):

| Feature | Claude API | Platform on AWS | Bedrock | Vertex AI | Foundry |
|---|---|---|---|---|---|
| Messages, streaming, tool use, PDF input | Yes | Yes | Yes | Yes | Yes |
| Structured outputs (`output_config.format`) | Yes | Yes | Not on the Messages-API endpoint; legacy `InvokeModel` for some models (see below) | Yes | Yes |
| Prompt caching (5 min and 1 h) | Yes | Yes | Yes | Yes | Yes |
| 1M-token context (current models) | Yes | Yes | Yes | Yes | Yes |
| `inference_geo` data-residency parameter | Yes | Yes | No (region set by endpoint) | No (region set by endpoint) | No (deployment type instead) |
| Web search tool | Yes | Yes | No | Yes (basic version) | Yes |
| Web fetch tool | Yes | Yes | No | No | Yes |
| Code execution | Yes | Yes | No | No | Hosted on Anthropic only |
| Agent Skills | Yes | Yes | No | No | Beta, Hosted on Anthropic only |
| MCP connector | Beta | Beta | No | No | Beta |
| Message Batches API | Yes | Yes | No | No | No |
| Files API | Yes | Yes | No | No | Beta, Hosted on Anthropic only |
| Claude Managed Agents | Beta | Beta | No | No | No |
| Fast mode (research preview) | Beta | No | No | No | No |

Three things to say out loud when you show a table like this:

- **Batches is a cost lever.** Anthropic's batch pricing is half the standard rate. A customer with a large overnight document backlog who picks Bedrock, Vertex or Foundry gives that up and must find another way to cut cost.
- **Server-side tools change who runs what.** Without code execution or web fetch on the platform, the customer builds and hosts those tools themselves. That's more engineering, but some security teams prefer it.
- **Bedrock has two integrations, and structured outputs splits along them.** The newer "Claude in Amazon Bedrock" page (the Messages API at `/anthropic/v1/messages`, Opus 4.7 and later) lists structured outputs under "Features not supported." The legacy page (`InvokeModel` and `Converse`) lists structured outputs as supported for the models named in the Bedrock note of the structured-outputs compatibility section. So this isn't a contradiction; it's a version split. If a Bedrock design depends on schema-constrained JSON, say which integration and which model, check the current compatibility note, and plan for validate-and-retry in code if the endpoint you use doesn't support it.

## Where inference runs

Data residency questions come in every enterprise deal. The answer differs by platform.

| Platform | Controls | Price effect |
|---|---|---|
| Claude API | `inference_geo` per request: `"global"` (default) or `"us"`. Workspaces can set `default_inference_geo` and `allowed_inference_geos`. Workspace geo (where data is stored at rest) is currently `"us"` only. | US-only inference is 1.1x on Claude 4.6 and later models |
| Claude Platform on AWS | Same `inference_geo` controls. Workspaces are bound to one AWS region. | 1.1x for US-only |
| Amazon Bedrock | Global endpoint; geographic inference profiles (US, EU, JP, AU); and "In-region only" single-region routing in a few listed regions (in the EU: `eu-north-1` Stockholm and `eu-west-1` Ireland). Frankfurt (`eu-central-1`) is listed as "Global, EU", not in-region. | Regional endpoints carry a 10% premium over global |
| Vertex AI | Global, multi-region (`us`, `eu`) or regional endpoints. Single-region endpoints serve **Claude Sonnet 4.6 and earlier only**; newer models use the global or multi-region endpoints. | Regional and multi-region carry a 10% premium |
| Foundry | Global Standard, or US Data Zone Standard (Hosted on Azure only), which Anthropic's docs describe as equivalent to `inference_geo: "us"`. No EU data zone. Sonnet 5.5 is Global Standard only. | 1.1x for US Data Zone |

Source: [Data residency](https://platform.claude.com/docs/en/manage-claude/data-residency) and the platform pages above.

Read that table for the question a European bank will ask: "Can inference stay in the EU?" On the Claude API today, `inference_geo` offers only `"us"` and `"global"`. Foundry offers Global or US only. Bedrock (the EU inference profile, or in-region routing in Stockholm or Ireland) and Vertex AI (the `eu` multi-region) offer EU options. So an EU-only inference requirement can push the platform choice by itself. Before you promise it, confirm that the exact model they need is offered in that geography; model availability varies by region on both clouds.

Now the sharper question: **"Can inference stay in Germany?"** For current models, no documented option pins inference to Germany alone. Vertex AI's `eu` multi-region routes across EU regions, and its single-region endpoints (such as a German region) serve only Sonnet 4.6 and earlier. Bedrock's Frankfurt region is listed as "Global, EU", so it routes through the EU profile, not Frankfurt only. The honest answer is: "EU-only inference, yes, on Bedrock or Vertex AI. Germany-only for current models, not as a documented option today. Is the requirement really Germany, or the EU? I'll check the current docs and the cloud provider's region list before anything goes in writing."

Also know the limits of the claim. "Inference in the EU" is not the same as "no data ever leaves the EU." Logging, abuse monitoring and support processes have their own rules. Lesson 02 covers how to answer that without overclaiming.

## Quotas, lifecycles and other surprises

- **Quotas live with the platform.** Bedrock's default for Claude is 2 million input tokens per minute; customers can request up to 5 million input and 500,000 output tokens per minute without extra Anthropic approval, and AWS sets requests-per-minute limits. On Claude Platform on AWS, Anthropic manages rate limits.
- **Foundry doesn't return Anthropic's rate-limit headers.** Teams that built backoff around `anthropic-ratelimit-*` headers need Azure monitoring instead.
- **Model retirement dates can differ.** Anthropic's docs say lifecycle dates on Bedrock and Google Cloud are set by the partner and can differ from the Claude API schedule. Foundry follows the Claude API schedule. Put this in the customer's model-upgrade plan.
- **Request size limits differ.** Bedrock limits request payloads to 20 MB and Vertex AI to 30 MB. A document-heavy workload can hit those before the token limit.
- **Access can be gated.** Bedrock sets access criteria per model; some models need approval in the AWS console first. Check this in week one, not the week before launch.

## The code is nearly the same

The Anthropic SDKs support all five platforms. The request body is the Messages API everywhere; the client class, credentials and model ID change. In Python:

```python
import anthropic

# Claude API (first-party)
client = anthropic.Anthropic()                       # model="claude-opus-5-5"

# Claude Platform on AWS: needs AWS_REGION and ANTHROPIC_AWS_WORKSPACE_ID
client = anthropic.AnthropicAWS()                    # model="claude-opus-5-5"

# Amazon Bedrock (Messages API endpoint)
client = anthropic.AnthropicBedrockMantle(aws_region="us-east-1")  # model="anthropic.claude-opus-5-5"

# Google Cloud Vertex AI
client = anthropic.AnthropicVertex(project_id="my-project", region="global")  # model="claude-opus-5-5"

# Microsoft Foundry
client = anthropic.AnthropicFoundry(resource="my-resource")  # model=<deployment name>
```

That's the portability story you can tell a CTO worried about lock-in: the application code is close to portable across platforms, as long as it avoids platform-specific features. Every feature you adopt from the second table narrows where you can move. That's a tradeoff to record in the design, not a reason to avoid features.

## How to choose: a five-question sequence

Ask these in order. Each one can eliminate options.

1. **How must they buy it?** Existing AWS, Google Cloud or Azure agreement, or direct? Procurement often decides before engineering does. Whether a marketplace purchase counts against an existing cloud commitment is a question for the customer's cloud account team; don't assert it.
2. **Who may process the data?** Some customers require that only their cloud provider processes prompts; others are fine with Anthropic as processor. This splits {Bedrock, Vertex AI} from {Claude API, Platform on AWS, Foundry}.
3. **Where must inference run?** US-only, EU-only, or anywhere? Map to the residency table, and confirm model availability per geography.
4. **Which features does the design depend on?** Batches, code execution, Agent Skills, Files API, server-side web tools, Managed Agents. Each one you need removes platforms.
5. **What data-handling arrangement do they need?** Zero data retention, HIPAA, customer-managed keys. These differ by platform (lesson 02).

Then write the answer as a recommendation with reasons and open items, for example:

> **Recommendation:** Claude Platform on AWS. **Why:** billed through their AWS Marketplace account, Anthropic-operated so Batches and code execution are available for the overnight reconciliation job, `inference_geo: "us"` meets their US-only rule (1.1x price). **Rejected:** Bedrock, because the design depends on Batches. **Open items:** confirm ZDR enablement with the Anthropic account team; confirm PrivateLink design with their network team.

## Practice prompts (original, in the style of a case discussion)

1. "We're all-in on Azure, and legal wants prompts to stay inside our cloud. Which Claude deployment would you propose, and what do we give up?"
2. "Our data science team prototyped on the Claude API using the Batches API and code execution. Security now says production must run on Bedrock. What breaks, and what are our options?"
3. "Can you guarantee our inference stays in Germany?" Answer with what's verified, what isn't, and what you'd check.

> **Key takeaways**
> - There are five options. Anthropic operates the Claude API, Claude Platform on AWS and Foundry; AWS operates Bedrock and Google Cloud operates Vertex AI. That decides who the data processor is.
> - Claude Platform on AWS and Amazon Bedrock are different products. Always ask which one.
> - Feature gaps (Batches, code execution, Skills, Files API, server-side web tools, Managed Agents) are the main reason a platform choice breaks an architecture.
> - Residency controls differ: `inference_geo` us/global on Anthropic-operated platforms, endpoints and inference profiles on Bedrock and Vertex AI, deployment types on Foundry (Global or US only, no EU zone). Regional options cost about 10% more. No documented option pins current models to a single country such as Germany.
> - Model IDs differ: bare on the Claude API, Platform on AWS and Vertex AI, `anthropic.`-prefixed on Bedrock, deployment names on Foundry.
> - Choose in order: procurement, processor, residency, features, data-handling arrangement. Write the result as a recommendation with reasons, rejections and open items.
