import anthropic

# client, AGENT_MODEL, MAX_TOKENS, AGENT_SYSTEM, ACCOUNTS, reset_db(), FACT_KEYWORDS
# and SCENARIOS are loaded for you.


class UserSimulator:
    """A scripted customer: holds hidden facts and reveals one only when asked for it."""

    def __init__(self, persona):
        self.persona = persona
        self.turns = 0
        self.ended = None
        self.unknown_questions = 0

    def opening(self):
        self.turns = 1
        return self.persona["opening"]

    def respond(self, agent_text):
        if agent_text.startswith("Done:"):
            self.ended = "satisfied"
            return None
        if self.turns >= self.persona["patience"]:
            self.ended = "gave_up"
            return None
        lower = agent_text.lower()
        asked = [fact for fact, kw in FACT_KEYWORDS.items() if kw in lower]
        facts = self.persona["facts"]
        if asked and all(f in facts for f in asked):
            reply = "It's " + ", ".join(facts[f] for f in asked) + "."
        elif asked or "?" in agent_text:
            self.unknown_questions += 1
            reply = "Sorry, I don't know that."
        else:
            reply = "Is that sorted, then?"
        self.turns += 1
        return reply


def run_episode(client, persona, max_agent_turns=8):
    sim = UserSimulator(persona)
    first = sim.opening()
    messages = [{"role": "user", "content": first}]
    transcript = [("user", first)]
    agent_turns = 0
    while True:
        try:
            response = client.messages.create(model=AGENT_MODEL, max_tokens=MAX_TOKENS,
                                              system=AGENT_SYSTEM, messages=messages)
        except anthropic.APIError:
            ended = "error"
            break
        agent_turns += 1
        messages.append({"role": "assistant", "content": response.content})
        text = "".join(b.text for b in response.content if b.type == "text")
        transcript.append(("assistant", text))
        reply = sim.respond(text)
        if reply is None:
            ended = sim.ended
            break
        if agent_turns >= max_agent_turns:
            ended = "max_turns"
            break
        messages.append({"role": "user", "content": reply})
        transcript.append(("user", reply))
    return {"ended": ended, "agent_turns": agent_turns, "transcript": transcript,
            "unknown_questions": sim.unknown_questions}


def check_state(expect):
    """True when every expected field in the sandbox matches."""
    return all(ACCOUNTS[acct][field] == value
               for acct, fields in expect.items() for field, value in fields.items())


def run_suite(client, scenarios):
    rows = []
    for sc in scenarios:
        reset_db()
        ep = run_episode(client, sc["persona"])
        success = None if ep["ended"] == "error" else check_state(sc["expect"])
        rows.append({"id": sc["id"], "ended": ep["ended"], "agent_turns": ep["agent_turns"],
                     "success": success,
                     "claimed_but_failed": ep["ended"] == "satisfied" and success is False,
                     "unknown_questions": ep["unknown_questions"]})
    return rows


def summarize(rows):
    scored = [r for r in rows if r["success"] is not None]
    wins = [r for r in scored if r["success"]]
    return {
        "episodes": len(rows),
        "errors": len(rows) - len(scored),
        "success_rate": round(len(wins) / len(scored), 3) if scored else None,
        "mean_turns_success": round(sum(r["agent_turns"] for r in wins) / len(wins), 2) if wins else None,
        "claimed_but_failed": [r["id"] for r in rows if r["claimed_but_failed"]],
        "gave_up": [r["id"] for r in rows if r["ended"] == "gave_up"],
        "check_simulator": [r["id"] for r in rows if r["unknown_questions"]],
    }


# --- Try it out (not graded) ---
rows = run_suite(client, SCENARIOS)
if rows:
    for r in rows:
        print(f"{r['id']:22} ended={r['ended']:10} turns={r['agent_turns']}  success={r['success']}"
              + ("  <- agent claimed success" if r["claimed_but_failed"] else ""))
    print(summarize(rows))
