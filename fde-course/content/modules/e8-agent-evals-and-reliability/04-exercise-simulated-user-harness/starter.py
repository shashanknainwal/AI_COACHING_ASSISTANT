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
        # TODO: the opening message is the first user turn.
        pass

    def respond(self, agent_text):
        # TODO: Done: -> satisfied; out of patience -> gave_up; otherwise reply (see the rules).
        pass


def run_episode(client, persona, max_agent_turns=8):
    """{"ended", "agent_turns", "transcript", "unknown_questions"}"""
    # TODO
    pass


def check_state(expect):
    """True when every expected field in the sandbox matches."""
    # TODO
    pass


def run_suite(client, scenarios):
    # TODO: reset_db() before each episode, then score the sandbox.
    pass


def summarize(rows):
    # TODO
    pass


# --- Try it out (not graded) ---
rows = run_suite(client, SCENARIOS)
if rows:
    for r in rows:
        print(f"{r['id']:22} ended={r['ended']:10} turns={r['agent_turns']}  success={r['success']}"
              + ("  <- agent claimed success" if r["claimed_but_failed"] else ""))
    print(summarize(rows))
