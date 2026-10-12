---
title: "Module Quiz: TypeScript for Claude"
type: quiz
minutes: 10
questions:
  - q: "Where does the TypeScript code in this module run?"
    options:
      - "In the course's browser editor, alongside the Python exercises"
      - "On your own machine with Node, for example in the capstone kit"
      - "On a hosted sandbox that the course starts for each learner"
      - "Inside the AI tutor, which executes it and returns the output"
    answer: 1
    explain: "The browser course runs Python only. TypeScript is taught through readings, code-reading questions, written lessons and a local lab that you run with Node."
  - q: "Which way of reading the answer text from a Messages API response is correct in TypeScript?"
    options:
      - "Cast the first block to any and read its text property"
      - "Read response.text, which the SDK fills in for convenience on every call"
      - "JSON.parse the response and read the first content entry"
      - "Filter content with a type guard for text blocks, then join"
    answer: 3
    explain: "Content is a discriminated union and may start with a thinking or tool_use block. Narrow by block.type before reading text."
  - q: "A browser chat UI needs streamed answers from Claude. Where should the client.messages.stream call live?"
    options:
      - "In a server route handler that streams text on to the browser"
      - "In the React component, using a key from a public env variable"
      - "In a service worker so the key is hidden from the page"
      - "In the browser, with the key stored in localStorage after login"
    answer: 0
    explain: "The API key must stay on the server. The browser calls your route, and the route calls Claude and forwards the text."
  - q: "In a streaming route, what does calling stream.abort() from the ReadableStream's cancel() handler achieve?"
    options:
      - "It retries the request on a cheaper model when the user leaves"
      - "It saves the partial answer so the user can resume it later"
      - "It stops generation when the client disconnects, so you stop paying"
      - "It tells the API to refund the tokens already generated"
    answer: 2
    explain: "When the browser goes away, the ReadableStream is cancelled. Aborting the upstream stream stops generation and further billing."
  - q: "Code written for Opus 5 sends tool_choice {type: \"tool\", name: \"get_booking\"}. After moving to claude-opus-5-5, what should it do instead?"
    options:
      - "Send tool_choice {type: \"any\"}, which is still accepted"
      - "Add an assistant prefill that starts the tool call by hand"
      - "Use auto with strict tools, ask for the tool in the prompt, and check for a tool_use"
      - "Set temperature to 0 so the model always picks the same tool"
    answer: 2
    explain: "Forced tool choice (any or tool) returns a 400 on Opus 5.5. Prefill and temperature also return 400s. Steer with the prompt, keep strict: true, and verify the call happened."
  - q: "messages.parse with zodOutputFormat returns parsed_output as null. What's the most sensible first check?"
    options:
      - "The stop_reason, for example a refusal or a max_tokens cut-off"
      - "Whether Zod was installed as a dev dependency instead of a runtime one"
      - "Whether the schema has more than ten fields, the documented limit"
      - "Whether the call used the beta client namespace by mistake"
    answer: 0
    explain: "A refusal or a truncated answer leaves nothing to parse. Log and branch on stop_reason before treating it as a schema problem."
  - q: "Two identical requests with a 3,000-token cached system prompt both show cache_read_input_tokens of 0. Which TypeScript habit is the most likely cause?"
    options:
      - "Using async/await instead of .then() chains for the API call itself"
      - "Typing the messages array as Anthropic.MessageParam[]"
      - "Reading the key from the environment with new Anthropic()"
      - "Interpolating new Date().toISOString() into the system prompt"
    answer: 3
    explain: "Caching is a prefix match. A timestamp in the system prompt changes the bytes on every request, so nothing after it can be read from cache."
  - q: "With @modelcontextprotocol/sdk, why must a stdio MCP server log with console.error rather than console.log?"
    options:
      - "console.log is disabled by the SDK in production builds"
      - "stdout carries the JSON-RPC messages, so stray output corrupts the protocol"
      - "stderr output is shown to the model as part of each tool result"
      - "console.error is the only call that the SDK's logger forwards"
    answer: 1
    explain: "On the stdio transport, stdout is the protocol channel. Logs belong on stderr."
  - q: "In the SDK version tested in lesson 04, what happened when a tools/call request had arguments that failed the tool's Zod schema?"
    options:
      - "The server returned a tool result marked isError with an input validation message"
      - "The handler ran anyway and received the raw, unvalidated arguments"
      - "The server process exited and the client had to restart it"
      - "The server silently dropped the request and sent no reply"
    answer: 0
    explain: "The SDK validated the arguments before the handler ran and returned an isError result explaining the failure, which the model can act on. Behaviour can differ between versions, so test yours."
  - q: "Ada asks whether the TypeScript SDK will retry 429s for her or whether she should add her own retry loop. What's the best answer?"
    options:
      - "Add your own loop that retries every error five times immediately"
      - "The SDK never retries, so wrap every call in a retry library"
      - "The SDK retries 429 and 5xx with backoff, so don't stack another loop on top unless you turn it off"
      - "Retry only 400 errors, since 429s are permanent account limits"
    answer: 2
    explain: "The SDK retries 429 and 5xx errors with exponential backoff by default. Stacked retry layers multiply load during an incident. 400s should never be retried."
---

Ten questions on the TypeScript SDK, streaming routes, tool loops, structured outputs, caching and MCP servers. You need 8 correct to pass.
