# Real-model labs

Four labs that repeat in-course exercises against the real model, on your own key. The browser course uses a simulator that never calls a real model; these labs are where you see real variance, refusals, latency and cost.

| Lab | Question it answers | Approx. cost | Paste into C8 lesson |
|---|---|---|---|
| `lab1_prompt_iteration` | Did my prompt change help, or is it noise? | under $0.15 | Lab 1 Report |
| `lab2_retrieval_eval` | Does the right document reach the model? | under $0.05 | Lab 2 Report |
| `lab3_judge_calibration` | Can I trust my LLM judge? | about $0.15 to $0.50 | Lab 3 Report |
| `lab4_classifier_eval` | Which model, at what cost, and how often does it refuse? | about $0.05 to $0.35 | Lab 4 Report |

All four together should cost well under $2. Every script meters spend and stops at `CAPSTONE_BUDGET_USD` (default $1.00 per script run).

Run every lab from the kit root, for example `python -m labs.lab1_prompt_iteration.run --prompt labs/lab1_prompt_iteration/prompt_v1.txt`. Results land in `results/` (git-ignored). Fill in each lab's `RESULTS_TEMPLATE.md` and paste it into the matching written lesson in module C8. The grader rewards honest numbers with counts, intervals and a word on variance, not high scores.

The ticket data and help-centre articles describe Quillfeather Stationery, a fictional shop.
