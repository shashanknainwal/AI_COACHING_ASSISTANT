from anthropic import _sim

_SUMMARY = (
    "Stand-up summary (Mar 12). Card operations: the dispute backlog fell from 410 to 290 after the new triage "
    "classifier went live; fraud tickets still route to humans. Branch support: Lakeview reported two ATM outages, "
    "vendor visit booked for Thursday. Risks: overdraft fee complaints rose 12% week over week; Maya will pull "
    "examples for compliance review. Decisions: pilot expands to the mortgage team on Monday. "
    "Action items: Maya, fee complaint examples by Wednesday; Leo, ATM vendor follow-up; Priya, mortgage onboarding plan."
)


def _responder(params):
    return _sim.message(_sim.thinking(""), _sim.text(_SUMMARY))


_sim.set_responder(_responder)
