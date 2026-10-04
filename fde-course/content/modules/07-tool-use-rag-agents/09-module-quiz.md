---
title: "Module 7 Quiz"
type: quiz
minutes: 12
questions:
  - q: "Claude returns stop_reason \"tool_use\" with a lookup_order block. Who runs lookup_order?"
    options:
      - "Anthropic's servers, using the schema you provided"
      - "Claude, inside its sandbox"
      - "Your code, after validating the input"
      - "Nobody; the tool_use block is the final answer"
    answer: 2
    explain: "Claude only asks. Your code decides whether and how to run the tool, which is where validation and permissions live."
  - q: "Which tool description will lead Claude to use the tool most reliably?"
    options:
      - "\"Order tool.\""
      - "\"Looks up orders.\""
      - "\"Returns JSON.\""
      - "\"Look up an order by ID (format B-1234). Call this whenever the customer mentions an order number or asks about an order.\""
    answer: 3
    explain: "Say what it does, the input format, and when to call it. Claude decides whether to use a tool largely from its description."
  - q: "Claude's turn contains two tool_use blocks. How do you send the results back?"
    options:
      - "One user message containing both tool_result blocks, each with its own tool_use_id"
      - "Two separate user messages, one per result"
      - "Only the result of the first tool; Claude will ask again for the second"
      - "Put both results in the system prompt"
    answer: 0
    explain: "The next user message must answer every tool_use id. Splitting results across messages causes a 400 error."
  - q: "lookup_order raises KeyError for an unknown order ID. What should your code send back?"
    options:
      - "Nothing; stop the loop and show a stack trace"
      - "A tool_result with is_error: true and a helpful message such as \"No order found with ID B-9999. Order IDs look like B-1001.\""
      - "A made-up order so the conversation can continue"
      - "An empty string as a normal result"
    answer: 1
    explain: "Return the error to Claude. It can then ask the customer for a corrected ID or explain the problem."
  - q: "You need Claude to use a specific tool on Claude Opus 5.5. What works?"
    options:
      - "tool_choice {\"type\": \"tool\", \"name\": \"lookup_order\"}"
      - "tool_choice {\"type\": \"any\"}"
      - "Remove every other tool and hope"
      - "Ask for it in the prompt and check in code that the call was made"
    answer: 3
    explain: "Opus 5.5 supports only auto and none for tool_choice. Instruct in the prompt and verify the call; use structured outputs if you only need JSON."
  - q: "Why does an agent loop need a maximum step count?"
    options:
      - "The API rejects conversations longer than six turns"
      - "A confused agent can repeat failing calls forever, and every step resends a growing history, which raises cost"
      - "It makes Claude answer faster"
      - "Tools can only be called six times per API key"
    answer: 1
    explain: "Bound steps, tokens and time. Fail clearly or hand off to a human when a limit is hit."
  - q: "Brightway's entire help center is 1,000 tokens. What's the best first design for answering policy questions?"
    options:
      - "Put all the articles in a cached system prompt"
      - "Build an embedding pipeline with a vector database"
      - "Fine-tune a model on the articles"
      - "Build an agent with a search tool"
    answer: 0
    explain: "If the corpus fits comfortably in context, skip retrieval. It's simpler and can't miss the right article. It's also a quality baseline for any later RAG system."
  - q: "A customer searches for \"refund my couch\", but the policy says \"return a sofa\". Keyword search misses it. What helps most?"
    options:
      - "A longer system prompt"
      - "Bigger chunks"
      - "Adding embedding (semantic) search, usually combined with keyword search as a hybrid"
      - "Lowering max_tokens"
    answer: 2
    explain: "Embeddings catch paraphrases and synonyms; keyword search catches exact terms. Hybrid retrieval gets both."
  - q: "Claude's structured answer cites \"KB-09#1\", but retrieval only returned KB-01#1 and KB-01#2. What should your code do?"
    options:
      - "Show the answer; Claude probably knows another article"
      - "Drop the invalid citation, and don't show the answer if no valid citation remains"
      - "Retry until the citation is valid"
      - "Add KB-09 to the help center"
    answer: 1
    explain: "Validate citations against what you actually retrieved. An unsupported answer becomes the honest fallback."
  - q: "Retrieval finds no relevant chunks for a question. What should the system do?"
    options:
      - "Return a fallback answer immediately, without calling Claude, and log the question"
      - "Call Claude anyway with an empty <documents> block"
      - "Call Claude without the grounding instructions"
      - "Pick three random chunks"
    answer: 0
    explain: "There is nothing to ground the answer in, so a call only costs money and risks an invented answer. The log shows which articles are missing."
  - q: "Every request follows the same steps: look up the order, track the shipment, then write a reply. What's the right architecture?"
    options:
      - "An autonomous agent with three tools"
      - "A multi-agent system"
      - "A workflow: your code runs the lookups, then one Claude call writes the reply"
      - "Fine-tuning"
    answer: 2
    explain: "If you can draw it as a flowchart, write it as code. It's cheaper, faster and easier to test than an agent."
  - q: "Your approval service times out while a $90 credit is waiting for approval. What should guarded_execute do?"
    options:
      - "Issue the credit, since most requests are approved"
      - "Retry forever"
      - "Ask Claude whether to proceed"
      - "Treat it as declined (fail closed), tell Claude, and record it in the audit log"
    answer: 3
    explain: "Risky actions need an explicit yes. Errors, missing answers and ambiguous answers all mean no."
  - q: "What is the Model Context Protocol (MCP)?"
    options:
      - "Anthropic's embedding model"
      - "An open standard for exposing tools and data sources as servers that any MCP-compatible client can use"
      - "A prompt format for long documents"
      - "A billing plan for agents"
    answer: 1
    explain: "Build an MCP server once (for example, for Brightway's order system) and many Claude-based applications can use it. The usual tool safety rules still apply."
---

Thirteen questions on tool use, the agent loop, RAG, workflows versus agents, guardrails and MCP. You need **11 out of 13** to pass. You can retry as many times as you like.
