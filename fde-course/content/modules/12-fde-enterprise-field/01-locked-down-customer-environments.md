---
title: "Locked-Down Customer Environments"
type: reading
minutes: 18
---

> **By the end of this lesson you will be able to:**
> - Name the six walls you meet inside an enterprise network and what each one breaks
> - Get an SDK through a TLS-inspecting proxy without turning verification off
> - Choose private connectivity and IAM roles over long-lived keys
> - Plan installs for networks with no internet, and laptops without admin rights
> - Turn the customer's constraints into a platform choice, building on Module 9

Your first morning at **Quarrybank** (a fictional regional bank) goes like this. Sana Iqbal, Director of Platform Engineering, hands you a badge and a login to a virtual desktop. You have no admin rights. `pip install` hangs. A browser works, but every certificate says it was issued by "Quarrybank Root CA". Production runs in an AWS account whose VPC has no internet gateway. Users sign in through the bank's identity provider. And the analytics team wants your classifier inside an enclave with no outbound network at all.

None of this is unusual. It is the normal shape of a regulated customer, and it decides whether your week-six go-live happens. Module 9 lesson 01 gave you the environment checklist, the five ways to reach Claude and the feature-gap table. This lesson goes one level down: what each wall breaks, what you do about it, and how long it takes.

Quarrybank, Sana Iqbal and everyone else in this module are fictional.

## The six walls

| Wall | What breaks | What you do | Typical lead time (ask; don't assume) |
|---|---|---|---|
| **TLS-inspecting proxy** | `CERTIFICATE_VERIFY_FAILED`, 407s, streaming that stalls | Point clients at the proxy and at a CA bundle that includes the corporate root | Days for the CA file; a change ticket for each new outbound host |
| **Private network, no internet gateway** | The SDK can't reach any public endpoint | Private connectivity to the model platform, or an egress path through an approved proxy | Weeks: network team, firewall review, sometimes a new VPC endpoint |
| **IAM roles instead of keys** | Your `.env` with an API key is rejected at review | Use the platform's role-based auth and short-lived credentials | Days to weeks for the role and its policy |
| **SSO and OIDC** | Your demo login page is not allowed | Put the app behind their identity provider and validate its tokens | Weeks: an app registration with their identity team |
| **No-egress or air-gapped installs** | `pip install` and `docker pull` fail | A wheelhouse or internal mirror, hash-pinned, imported through their process | Days per import; plan for several rounds |
| **VDI without admin rights** | You can't install Python, Docker or your editor | Ask for a development VM or sandbox account in week one | Often the longest wait of all |

The lead times are the point. Every row needs a ticket owned by someone at the customer. File them all in week one, in parallel, and track them on the same page as your engineering work. An FDE who discovers the firewall ticket in week five has lost the go-live date before writing a line of the hard code.

## Wall 1: the TLS-inspecting proxy

Most banks and hospitals inspect outbound HTTPS. The proxy terminates your TLS connection, reads the traffic, and opens its own connection to the real server. To your code, the server's certificate now appears to be signed by the customer's own root CA. Python's default trust store doesn't contain that root, so the handshake fails with `CERTIFICATE_VERIFY_FAILED`.

The fix has three parts:

1. **Route through the proxy.** Most tools read `HTTPS_PROXY` and `NO_PROXY` from the environment. The Anthropic Python SDK also takes an explicit HTTP client:

   ```python
   from anthropic import Anthropic, DefaultHttpxClient

   client = Anthropic(http_client=DefaultHttpxClient(proxy="http://proxy.quarrybank.internal:8080"))
   ```

   The SDK documents `DefaultHttpxClient` (and `DefaultAsyncHttpxClient`) for this, rather than a raw HTTP client, so you keep its default timeouts and connection limits.

2. **Trust the corporate root.** Get the root CA certificate from the customer's platform team, then build a bundle that contains the public roots plus theirs. Append it. If you replace the bundle with only their root, every host the proxy doesn't inspect will fail. Pass the bundle to the HTTP client as an SSL context. `DefaultHttpxClient` accepts the underlying client's TLS settings. The exact argument depends on your SDK version (SDK 1.x moved to `httpx2`), so check that library's docs before you ship.

3. **Never turn verification off.** `verify=False` "works" and lets anyone on the path read every prompt and response. It is the kind of line that ends an engagement when a security reviewer finds it.

Two more proxy habits:

- **Test streaming through the proxy, early.** Some inspecting proxies buffer responses or cut long-lived connections. A stream that works on your laptop can arrive all at once, or not at all, behind the proxy. Run a real streamed request through it in week one.
- **Request the allowlist entry by exact host.** For the Claude API that's `api.anthropic.com`. For Claude Platform on AWS the endpoint pattern is `aws-external-anthropic.{region}.api.aws`. A 403 from the proxy usually means the host isn't on its allowlist, not that your key is wrong.

Exercise 03 has you build and check this configuration.

## Wall 2: private networks and IAM roles

Quarrybank's production VPC has no route to the internet. There are two ways out:

- **Private connectivity to the platform.** Module A2 lesson 02 records AWS PrivateLink as supported on Claude Platform on AWS and Azure Virtual Network on Foundry, as of October 2026. For Bedrock, Vertex AI and the Claude API, confirm the current private networking options in that platform's docs before you design around them.
- **An approved egress path.** Traffic leaves through the customer's inspecting proxy to an allowlisted host. Simpler to get approved at some banks, impossible at others.

On authentication, an API key in an environment variable is a long-lived secret. Regulated customers prefer short-lived credentials tied to an identity they already govern:

| Platform | Prefer | Notes |
|---|---|---|
| Claude Platform on AWS | IAM roles with SigV4 signing (`AnthropicAWS()`) | Needs `AWS_REGION` and `ANTHROPIC_AWS_WORKSPACE_ID`; no default region. Short-term API keys last at most 12 hours |
| Amazon Bedrock | IAM roles (`AnthropicBedrock()`) | Model IDs carry an `anthropic.` prefix |
| Claude API | Workload Identity Federation: exchange a short-lived token from AWS, Google Cloud or an OIDC issuer for API access | No static key in the container |
| Vertex AI, Foundry | The cloud's own identity (Google Cloud credentials; Entra ID) | Check each platform's auth page |

The AWS clients read credentials through the standard AWS chain: environment, shared profile, then the role attached to the instance or task. So in production you usually pass nothing at all, and the role does the work. A **403** from Claude Platform on AWS means the request reached the server: check the workspace ID and the IAM actions on the role. A missing region or workspace ID fails before any request is sent.

## Wall 3: SSO and OIDC for your users

Your assistant will have users, and Quarrybank won't let you build a login page. The app sits behind their identity provider (Okta, Entra ID or similar). After sign-in, your backend receives a signed token (a JWT) and must check it before trusting anything inside it:

- **Signature first**, using the key named by the token's `kid` in the provider's published key set (the JWKS). Production tokens are signed with RS256 or ES256, so you verify with the provider's public key. Use a vetted library for this.
- **Then the claims:** `iss` is their issuer, `aud` is your app, `exp` hasn't passed, `nbf` has, with a small allowance for clock skew.
- **Then authorization.** Group claims map to what the user may do. For an agent, that means which **tools** the model may call on this user's behalf. A teller doesn't get the tool that issues refunds just because the model asked for it.

The mistake to avoid is reading `groups` from a token you haven't verified. Exercise 04 makes you do it in the right order.

## Wall 4: no-egress and air-gapped installs

The analytics enclave has no outbound network. Two consequences, and FDEs often miss the second:

1. **Installs.** You bring dependencies in, you don't download them. Build a **wheelhouse** (all wheels for the exact Python version and platform), pin every package with hashes, and import it through the customer's software intake process. Inside, install with no index:

   ```bash
   pip install --no-index --find-links /opt/wheelhouse --require-hashes -r requirements.txt
   ```

   Many customers run an internal mirror (Artifactory, Nexus or similar) that does the same job continuously. Ask which one, and who approves new packages.
2. **Model calls.** A truly air-gapped enclave can't call any hosted model. Either the enclave gets an approved private path to the platform, or the model step runs elsewhere and only results come back in. Say this in week one. "We'll install it in the enclave" sounds like a plan until someone asks how the enclave reaches Claude.

Exercise 05 builds the dependency plan.

## Wall 5: VDI without admin rights

Your laptop may never touch their network. You work in a virtual desktop with a locked image: no Docker, no Python beyond what's installed, copy and paste disabled, sometimes no access to GitHub. What works:

- **Ask for a development VM or sandbox cloud account in week one**, with the tools you need listed by name and version.
- **Keep your own work runnable without admin rights:** pure-Python dependencies where possible, user-level installs, scripts that don't assume Docker.
- **Agree how code moves** between your company's repository and theirs (a mirror, a pull request into their Git server, a reviewed transfer). Never route around it with a personal email or USB stick.

## Turning constraints into a platform choice

Module 9 lesson 01 has the platform table and the feature gaps; don't rebuild it from memory. What changes in a locked-down account is the order of the questions:

1. **Where does the workload run, and what can it reach?** A VPC with only AWS private endpoints narrows you to the AWS options or a proxied path.
2. **Who must be the data processor?** On Bedrock and Vertex AI the cloud provider is; on the Claude API, Claude Platform on AWS and Foundry, Anthropic is (Module A2 lesson 02). Legal often decides this before you arrive.
3. **Which features does the code you've already written use?** Batches, the MCP connector, Agent Skills, code execution and server-side refusal fallbacks are missing on Bedrock and Vertex AI. A prototype built on the Claude API with any of them needs rework before it moves.
4. **Residency.** `inference_geo` exists on the Claude API and Claude Platform on AWS only. On the clouds, the region or deployment type sets it.

The architect track's [platform fit checker](/learn/a2-enterprise-deployment/03-exercise-platform-fit-checker) answers "which platform meets these requirements?" Exercise 02 answers the FDE's version: "this prototype exists; what breaks, in which files, if we move it to their platform?"

> **Key takeaways**
> - Six walls: inspecting proxy, private network, IAM roles, SSO, no-egress installs, locked VDI. File a ticket for each in week one; the lead times decide your dates.
> - Behind an inspecting proxy, route through it and append the corporate root to a CA bundle. Never disable verification. Test streaming through it early.
> - Prefer private connectivity and short-lived, identity-based credentials over API keys in environment variables.
> - Verify a token's signature before reading its claims, then map groups to the tools the agent may call.
> - An air-gapped enclave needs a wheelhouse for installs and an approved path for model calls. Say the second part out loud.
