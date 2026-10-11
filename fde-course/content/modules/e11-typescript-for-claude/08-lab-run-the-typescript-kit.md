---
title: "Lab: Run the TypeScript Kit on Your Machine"
type: written
minutes: 60
sections:
  - key: setup
    label: Setup and test run
    prompt: "Your Node version, the installed @anthropic-ai/sdk version, and the pasted summary lines from npm test and npm run typecheck. If anything failed, what it was and how you fixed it."
    words: [40, 200]
  - key: realcall
    label: One real tool-loop call
    prompt: "Paste the JSON the loop printed for one real question (status, tool calls, usage) and the model and effort it ran at. Work out the cost of that call from the usage and the model's prices, counting thinking as output. Note the request id if you logged it."
    words: [60, 220]
  - key: experiment
    label: One experiment
    prompt: "Change one thing and run the same question again: effort (low vs medium), the model (Haiku 5.5 vs Sonnet 5.5), or a second identical call to check cache_read_input_tokens. Paste both results and say what changed and why."
    words: [80, 250]
  - key: extension
    label: Extend the kit
    prompt: "Do one: (a) add a vitest test of your own (paste it and its result), (b) port the hand-written MCP server to @modelcontextprotocol/sdk and show tools/list and one tools/call working, or (c) wire the chat route into a Next.js app and paste what you saw when you closed the tab mid-answer."
    words: [80, 300]
  - key: lessons
    label: What you'd tell a customer
    prompt: "Two or three things you learned running this that you'd tell a customer's TypeScript team, in plain words."
    words: [40, 140]
rubric:
  - name: Real evidence, honestly reported
    points: 30
    lookFor: "Pastes actual command output (test summary, typecheck, the loop's JSON with usage) rather than describing it. Reports failures honestly and how they were fixed. Results are internally consistent (for example, output tokens larger than the visible text suggests, because thinking is counted)."
  - name: Correct cost and token reasoning
    points: 25
    lookFor: "Computes the call's cost from usage with the right model prices (for example Haiku 5.5 $0.10 input and $0.50 output per million for prompts up to 100K tokens; cache reads priced separately), counts thinking as output, and states the effort used."
  - name: A controlled experiment
    points: 20
    lookFor: "Changes exactly one variable, runs the same question, compares the numbers (output tokens, latency, cost, cache reads) and explains the difference correctly: lower effort means less thinking, a second identical call should show cache_read_input_tokens when the prefix is long enough to cache, and so on. Notes when a single run is too noisy to conclude much."
  - name: A working extension
    points: 15
    lookFor: "Shows a passing test of their own, or an SDK-based MCP server answering tools/list and tools/call (logging to stderr), or evidence that closing the tab aborted the upstream stream. The pasted code uses real SDK APIs."
  - name: Clear customer takeaways
    points: 10
    lookFor: "Two or three specific, accurate lessons (for example: set effort explicitly because defaults differ by model; narrow content blocks by type; abort the stream on disconnect; keep the key server-side; verify caching with usage fields) in plain language."
passScore: 70
graderNotes: |
  The learner ran capstone-kit/typescript on their own machine. You can't verify their output, so judge plausibility and consistency: usage numbers should be plausible for a short support question (hundreds to a few thousand input tokens; output tokens include thinking); costs must follow from the numbers given. Do not penalise a learner who couldn't make a real call (no API key) if they say so plainly and complete the test run, the typecheck and an extension; cap 'Real evidence, honestly reported' at 18 and 'A controlled experiment' at 10 in that case, unless the experiment uses the tests or a fake client sensibly. Mark down invented or obviously copied output, costs that ignore thinking tokens, wrong model prices, and claims that the browser course ran the TypeScript. A prompt shorter than the minimum cacheable length (512 tokens on current models) won't produce cache reads; reward a learner who notices and explains that rather than claiming a cache hit.
anchors:
  - label: weak
    expect: [0, 45]
    answer: "I ran the kit and everything worked. The tests passed. The real call returned the order status. It was cheap. I changed the effort and it was faster. I would tell customers TypeScript is good for Claude."
  - label: strong
    expect: [75, 100]
    answer: "Setup: Node 22.11, @anthropic-ai/sdk 0.128.0. npm test: 'Test Files 3 passed (3), Tests 9 passed (9)'. npm run typecheck: no output, exit 0. First run failed with a missing key; exported ANTHROPIC_API_KEY in my shell, not in a file. Real call: npm run loop -- \"Where is my order QF-1002?\" printed {\"status\":\"ok\",\"text\":\"QF-1002 shipped and should arrive on 2026-10-08.\",\"toolCalls\":[\"get_order\"],\"usage\":{\"input\":1874,\"output\":212,\"cacheRead\":0}} on claude-haiku-5-5 at effort low (the kit's default). Cost: 1,874 x $0.10 + 212 x $0.50 per million = $0.000187 + $0.000106 = about $0.0003. The 212 output tokens include thinking: the visible answer is about 15 tokens. Experiment: same question at effort medium: usage input 1,874, output 498, one tool call, same answer. Output more than doubled, so cost rose to about $0.0004, with no quality gain on this easy question; one run each, so I'd want 20 runs before quoting a ratio. cacheRead stayed 0 on a repeat run: the system prompt plus tools are under the 512-token minimum, so nothing is cached, which is expected. Extension (b): ported the MCP server to @modelcontextprotocol/sdk with registerTool and a Zod shape; piping initialize, notifications/initialized, tools/list and tools/call returned the get_order tool and {\"order_id\":\"QF-1002\",...}; a bad order_id returned isError true with an input validation message; logs go to console.error. Customer takeaways: set effort explicitly, because thinking is billed as output and defaults differ by model; narrow content blocks by type, never content[0].text; check cache hits with usage fields, because short prompts silently don't cache."
---

This is the hands-on part of the module. You'll run real TypeScript, on your own machine, with your own API key. The browser course can't run TypeScript, so you paste your results here and the grader reads them against the rubric.

## What's in the kit

`capstone-kit/typescript/` is a small Node project. Its README has the current file list and commands. At the time of writing it contains:

- **A streaming chat route** in the shape of a Next.js App Router `POST` handler. It streams text deltas, reports a refusal or `max_tokens` mid-stream, and aborts upstream when the client disconnects.
- **A manual tool loop** that handles every stop reason, keeps history append-only and sets `effort` explicitly.
- **A minimal MCP server** over stdio, written by hand so you can see the JSON-RPC. Lesson 04 shows the official-SDK version.
- **Tools** with `strict: true` and an executor that validates input and refuses writes without approval.
- **vitest tests** with fake clients: no key and no network needed.

If the README and this list disagree, follow the README.

## Steps

1. **Copy the kit** somewhere outside the course repository and `cd` into `typescript/`.
2. **Install and test.** Run `npm install`, then `npm test` and `npm run typecheck`. No API key is needed for these.
3. **Make one real call.** Export `ANTHROPIC_API_KEY` in your shell, then run the loop with a question, as the README shows. On Haiku 5.5 at low effort a short question costs a fraction of a cent. Keep the key out of files you might commit.
4. **Run one experiment.** Change exactly one variable and run the same question again.
5. **Extend the kit** with one of the three options in the form.

If you don't have an API key, do steps 1, 2 and 5 (options a or b need no key), and say so in the form. You can still pass.

## Cost check before you run

Every real call costs money. Look at what the loop sets before running it: the model, `max_tokens` and `effort`. Thinking tokens are billed as output and count toward `max_tokens`. A cheap model at low effort keeps a dozen runs well under a dollar. Running at `max` effort on a bigger model does not.
