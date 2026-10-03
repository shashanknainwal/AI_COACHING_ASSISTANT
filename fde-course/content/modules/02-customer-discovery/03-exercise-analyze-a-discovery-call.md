---
title: "Exercise: Analyze a Discovery Call Transcript"
type: exercise
minutes: 25
hints:
  - "In `parse_transcript`, use `line.partition(\": \")`. If the separator is found, start a new turn `(speaker.strip(), text.strip())`. If not, and there is a previous turn, append the line to that turn's text with a space."
  - "Tuples are immutable. To extend the last turn, replace it: `turns[-1] = (turns[-1][0], turns[-1][1] + \" \" + line)`."
  - "Count words with `len(text.split())`. Add them up separately for the chosen speaker and for everyone."
  - "`re.findall(r\"[^.?!]+\\?\", text)` returns every question in a piece of text, including the question mark. Strip each one."
  - "A question is open if `q.lower().startswith(OPEN_STARTERS)` (startswith accepts a tuple), or if it contains \"walk me through\" or \"tell me about\"."
  - "Split a turn into sentences with `re.split(r\"(?<=[.!?])\\s+\", text)`. A sentence is quantified if `any(ch.isdigit() for ch in sentence)`."
---

Great FDE teams review their own discovery calls the way athletes review game footage. In this exercise you'll build a small call-analysis tool that answers three questions about any transcript:

1. **Did the FDE listen?** Their share of the words should be under about 30%.
2. **Did they ask open questions?** Open questions ("How…", "Walk me through…") surface detail; closed ones ("Do you…?") get yes or no.
3. **What quantified pains came up?** Customer sentences containing numbers are the raw material for a business case.

## The transcript format

Transcripts from meeting tools look like this: one turn per line, `Speaker: text`. Long turns sometimes wrap onto the next line, and wrapped lines have **no** `Speaker: ` prefix.

```text
FDE: Thanks for joining. Could you walk me through how a new claim gets processed today?
Marcus: Sure. Claims come in by email, about 900 a week. An adjuster reads each one
and keys it into ClaimsPro by hand.
FDE: How long does that take per claim?
```

## Your task

Complete four functions.

**1. `parse_transcript(text)`** returns a list of `(speaker, text)` tuples, in order.
- A line containing `": "` starts a new turn. The speaker is everything before the **first** `": "`, and the text is everything after it. Strip both.
- A non-blank line **without** `": "` continues the previous turn: append it to the previous text, separated by one space.
- Skip blank lines.

**2. `talk_ratio(turns, speaker="FDE")`** returns the share of all words spoken by `speaker`, as a float rounded to 2 decimals. Words are separated by whitespace. Return `0.0` if there are no words at all.

**3. `question_counts(turns, speaker="FDE")`** returns `{"open": n, "closed": m}` for the questions asked by `speaker`.
- A question is any run of text ending in `?` (use the regex in the hints).
- It's **open** if, in lowercase, it starts with one of `OPEN_STARTERS`, **or** it contains `"walk me through"` or `"tell me about"`. Everything else is **closed**.

**4. `quantified_pains(turns, speaker="FDE")`** returns the sentences spoken by everyone **except** `speaker` that contain at least one digit, in order, stripped. Split turns into sentences after `.`, `!` or `?` followed by whitespace.

Press **Run** to see the analysis of the sample call with Lumen Insurance, then **Submit**.

> **Why this matters:** You can run this on your own call recordings' transcripts. If your talk ratio is above 0.4 or your questions are mostly closed, you'll know exactly what to practice before your next customer call.
