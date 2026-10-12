# Lab 1: Prompt iteration on 30 labelled tickets

**Mirrors:** the in-course prompt exercises in E1 (production prompting). **Paste results into:** C8 lesson "Lab 1 Report: Prompt Iteration on a Real Model".
**Time:** 45 to 60 minutes. **Cost:** about $0.01 to $0.05 per prompt version on Claude Haiku 5.5 at effort low (90 calls). Your `results/*.json` file has the exact figure.

In the browser course, the simulator returns the same answer every time. Here you see what a real model does: the same prompt, run three times, does not give the same 30 labels. Your job is to improve the prompt and tell signal from noise.

## Steps

1. From the kit root, with your venv active and `ANTHROPIC_API_KEY` exported:
   ```bash
   python -m labs.lab1_prompt_iteration.run --prompt labs/lab1_prompt_iteration/prompt_v1.txt
   ```
2. Read the output. Write down, before you change anything: accuracy per run with the interval, the spread across runs, which tickets flipped, and the top confusions.
3. Open `tickets.jsonl` and read the tickets the model got wrong. Six tickets are marked `"ambiguous": true` because reasonable people could label them two ways. Decide for each mistake: is the prompt unclear, is the label debatable, or is the ticket genuinely ambiguous?
4. Copy `prompt_v1.txt` to `prompt_v2.txt` and improve it. Ideas: a one-line definition per category, a rule for each boundary you saw confused (wrong item vs damaged; refund not received vs billing; account takeover), and what to do when two categories fit. Do not paste the 30 tickets into the prompt: that is training on the test set.
5. Run v2 the same way. Compare. Stop after at most three versions.
6. Optional: run v2 with `--effort medium`, or `--model claude-sonnet-5-5`, and see whether accuracy or only cost moves. Sonnet 5.5 is 20 times Haiku 5.5's per-token price.

## What to notice

- With 30 tickets, one ticket is 3.3 points. A 95% interval on 27/30 runs from about 74% to 96%. A "3-point gain" from one run is one ticket and may be noise.
- If most flips are on the ambiguous tickets, your labels need a rule, not your prompt more words.
- A prompt under 512 tokens is not cached (the minimum on current models). Check `cache_read_tokens_total` in the results: it should be 0 here. A long prompt with many examples would cache, and the second run would be cheaper.

## Results template (paste into the course lesson)

See `RESULTS_TEMPLATE.md`.
