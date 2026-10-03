# Scratchpad: this is real Python running in your browser.
# Press Run (or Ctrl/Cmd + Enter).

skills = {
    "Customer discovery": 3,
    "Data wrangling": 2,
    "Integration engineering": 2,
    "LLM application engineering": 1,
    "Production engineering": 2,
    "Communication": 4,
}

# Rate yourself 1-5 on each skill, then run this again.
print("Your FDE skill profile\n")
for skill, level in skills.items():
    print(f"{skill:<30} {'#' * level}{'.' * (5 - level)}  {level}/5")

weakest = min(skills, key=skills.get)
print(f"\nFocus area for this course: {weakest}")
