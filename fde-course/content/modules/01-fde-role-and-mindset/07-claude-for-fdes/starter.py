import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    system="You are a concise assistant for a forward deployed engineer.",
    messages=[
        {"role": "user", "content": "Give me three questions to ask in a discovery call."}
    ],
)

print("Blocks:", [b.type for b in response.content])
print("Stop reason:", response.stop_reason)
print("Usage:", response.usage.input_tokens, "in /", response.usage.output_tokens, "out")
print()

for block in response.content:
    if block.type == "text":
        print(block.text)
