---
title: "Module Quiz: Multimodal, Streaming and Scale"
type: quiz
minutes: 12
questions:
  - q: "A customer sends 4032 x 3024 phone photos to Claude Sonnet 5.5. Roughly how many visual tokens does each photo cost?"
    options:
      - "About 15,500, one token per 28 x 28 patch of the original"
      - "At most 4,784, because it is downscaled to the tier's limits"
      - "1,568, the standard-tier maximum for any image"
      - "It depends only on the JPEG file size in bytes"
    answer: 1
    explain: "Images are downscaled to fit the model's long-edge and visual-token limits before patches are counted. On Claude 4.7 and later the cap is 4,784 tokens, so a 12 MP photo hits the cap."
  - q: "Why can't native citations point into a phone photo of a purchase order?"
    options:
      - "Citations are only available on the Claude API, not for images"
      - "Photos must be uploaded through the Files API to be citable"
      - "Citations need output_config.format to locate the text"
      - "Only text can be cited, and a photo has no extractable text"
    answer: 3
    explain: "The Citations API cites text only. Image citations aren't supported, so photos and scanned PDFs without a text layer can't be cited; you verify those another way or abstain."
  - q: "You enable citations on your policy documents and also set output_config.format with a JSON schema. What happens?"
    options:
      - "The API returns a 400 error"
      - "Citations are silently dropped from the JSON"
      - "The JSON gets a citations field added automatically"
      - "It works, but cited_text counts as output tokens"
    answer: 0
    explain: "Citations interleave pointers with text blocks, which can't satisfy a strict schema, so the combination is rejected. Split the work into two calls or validate your own quote fields."
  - q: "Which statement about native citations is guaranteed by the API?"
    options:
      - "Every sentence in the answer carries at least one citation"
      - "The cited passage logically entails the claim it supports"
      - "Each pointer refers to a document you sent, and cited_text is extracted from it"
      - "Citations work on every document even if only one has them enabled"
    answer: 2
    explain: "Pointers are guaranteed valid and the quoted text is extracted rather than generated. Uncited claims can still appear, support isn't proven, and citations must be enabled on all documents or none."
  - q: "A stream ends with a message_delta whose stop_reason is refusal, after some text was already shown. What should the UI do?"
    options:
      - "Keep the partial text and append the refusal explanation"
      - "Discard the partial text and show a refusal message instead"
      - "Send a user message asking the model to continue"
      - "Retry the same request on the same model until it completes"
    answer: 1
    explain: "The docs say to treat partial output before a refusal as incomplete and discard it. Continuation is for errors and drops; for refusals, change the request or use a fallback model."
  - q: "Where should you stop the clock when measuring time to first token for a chat UI?"
    options:
      - "At the first text_delta that contains non-empty text"
      - "At message_start, when the response headers arrive"
      - "At the first content_block_start of any block type"
      - "At the first ping event, since it proves the connection is alive"
    answer: 0
    explain: "Users experience the first visible word. On thinking models the stream opens with a thinking block whose text is empty by default, so earlier events would hide the real wait."
  - q: "How should you handle input_json_delta events for a tool_use block?"
    options:
      - "Parse each fragment as JSON and merge the resulting objects"
      - "Use only the last fragment, which carries the complete input"
      - "Ignore them; the full input arrives in content_block_start"
      - "Concatenate the strings and parse once at content_block_stop"
    answer: 3
    explain: "Fragments are pieces of one JSON string and can split anywhere, even inside a key. Accumulate and parse at the block's stop, and don't run a tool if the message ended with max_tokens."
  - q: "An async pool sleeps for the retry-after period while still holding its semaphore slot. What's the effect?"
    options:
      - "The SDK detects it and releases the slot automatically"
      - "Nothing changes, because sleeping tasks use no rate limit"
      - "Healthy requests wait for a slot that's doing no work"
      - "The server extends the retry-after period for that client"
    answer: 2
    explain: "While a task sleeps inside the semaphore, a request that could run is blocked. Hold the slot only around the API call and wait outside it."
  - q: "A customer accesses Claude only through Amazon Bedrock and wants a 2-million-ticket backfill at the lowest cost. What do you tell them about Message Batches?"
    options:
      - "It isn't available on Bedrock, so plan an async pool at standard prices"
      - "Batches work on Bedrock but results take up to 72 hours"
      - "Bedrock gives the same 50% discount through the Files API"
      - "Batches work everywhere, but only with Claude Haiku models"
    answer: 0
    explain: "Message Batches runs on the Claude API and Claude Platform on AWS, not on Bedrock, Vertex or Foundry. That can halve or double a cost estimate, so raise it early."
  - q: "Two logged requests compare equal as Python dicts, yet the second one misses the cache. What's a likely cause?"
    options:
      - "The cache_control marker moved to a later message"
      - "A tool schema was rebuilt with its keys in a different order"
      - "The second request appended a new user turn at the end"
      - "The second request used a lower max_tokens value"
    answer: 1
    explain: "Dict equality ignores key order, but the cache matches the serialized bytes in tools, system, messages order. A moved marker or an appended turn doesn't break the shared prefix."
---
