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
    """One chunk per paragraph: {"id": "KB-01#1", "title": ..., "text": ...}."""
    # TODO
    pass


def tokenize(text):
    """Lowercase words and numbers, minus STOPWORDS, with a trailing "s" removed from words longer than 3 letters."""
    # TODO
    pass


def build_index(chunks):
    """{"chunks": chunks, "tokens": [set of tokens per chunk], "idf": {token: log(1 + N / df)}}."""
    # TODO
    pass


def search(index, query, k=3):
    """Top-k chunks with score > 0, highest score first, each a copy of the chunk plus "score"."""
    # TODO
    pass


def build_prompt(question, results):
    """<documents> with one <document id=... title=...> per result, then <question>."""
    # TODO
    pass


# TODO: answer (string), citations (array of strings), answerable (boolean)
ANSWER_SCHEMA = {}


def answer(client, index, question):
    """Retrieve, ask Claude for a structured answer, and keep only valid citations."""
    # TODO
    pass


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
