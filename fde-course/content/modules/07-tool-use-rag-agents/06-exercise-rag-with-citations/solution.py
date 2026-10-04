import json
import math
import re
import anthropic
from fde_datasets import brightway

client = anthropic.Anthropic()
MODEL = "claude-opus-5-5"
STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "do", "does", "for", "from", "get",
             "how", "i", "if", "in", "is", "s", "t", "it", "its", "me", "my", "of", "on", "or", "so", "than", "that", "the",
             "their", "they", "this", "to", "was", "we", "what", "when", "will", "with", "you", "your"}
NO_ANSWER = "I couldn't find that in Brightway's help center. A support teammate will follow up."
SYSTEM_PROMPT = """You answer Brightway Retail customer questions using only the help-center documents provided.
- Use only facts from the <documents>. If they don't answer the question, set answerable to false.
- List the id of every document you used in citations.
- Keep the answer to one or two sentences."""


def chunk_articles(articles):
    chunks = []
    for article in articles:
        paragraphs = [p.strip() for p in article["text"].split("\n\n") if p.strip()]
        for i, paragraph in enumerate(paragraphs, 1):
            chunks.append({"id": f"{article['id']}#{i}", "title": article["title"], "text": paragraph})
    return chunks


def tokenize(text):
    tokens = []
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        if word in STOPWORDS:
            continue
        if len(word) > 3 and word.endswith("s"):
            word = word[:-1]
        tokens.append(word)
    return tokens


def build_index(chunks):
    token_sets = [set(tokenize(c["title"] + " " + c["text"])) for c in chunks]
    df = {}
    for tokens in token_sets:
        for t in tokens:
            df[t] = df.get(t, 0) + 1
    n = len(chunks)
    idf = {t: math.log(1 + n / count) for t, count in df.items()}
    return {"chunks": chunks, "tokens": token_sets, "idf": idf}


def search(index, query, k=3):
    terms = set(tokenize(query))
    results = []
    for chunk, tokens in zip(index["chunks"], index["tokens"]):
        score = sum(index["idf"][t] for t in terms & tokens)
        if score > 0:
            results.append(dict(chunk, score=round(score, 3)))
    results.sort(key=lambda r: -r["score"])
    return results[:k]


def build_prompt(question, results):
    lines = ["<documents>"]
    for r in results:
        lines += [f'<document id="{r["id"]}" title="{r["title"]}">', r["text"], "</document>"]
    lines += ["</documents>", "", "<question>", question, "</question>"]
    return "\n".join(lines)


ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "citations": {"type": "array", "items": {"type": "string"}},
        "answerable": {"type": "boolean"},
    },
    "required": ["answer", "citations", "answerable"],
    "additionalProperties": False,
}


def answer(client, index, question):
    results = search(index, question)
    if not results:
        return {"answer": NO_ANSWER, "citations": [], "answerable": False}
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(question, results)}],
        output_config={"format": {"type": "json_schema", "schema": ANSWER_SCHEMA}},
    )
    data = json.loads(next(b.text for b in response.content if b.type == "text"))
    retrieved = {r["id"] for r in results}
    citations = [c for c in data["citations"] if c in retrieved]
    if not data["answerable"] or not citations:
        return {"answer": NO_ANSWER, "citations": [], "answerable": False}
    return {"answer": data["answer"], "citations": citations, "answerable": True}


INDEX = build_index(chunk_articles(brightway.KB_ARTICLES))

# --- Try it out (not graded) ---
for q in ["My order is 6 business days late. What credit do gold members get?",
          "Can I return a sofa?",
          "Do you price match competitors?",
          "What's the weather in Denver?"]:
    print("Q:", q)
    hits = search(INDEX, q)
    if hits:
        print("   retrieved:", ", ".join(f"{h['id']} ({h['score']})" for h in hits))
    result = answer(client, INDEX, q)
    if result:
        print("   A:", result["answer"], result["citations"])
    print()
