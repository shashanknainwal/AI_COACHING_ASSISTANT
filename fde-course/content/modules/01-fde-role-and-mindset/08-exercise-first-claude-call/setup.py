from anthropic import _sim

_SUMMARY = """Brightline Health kickoff (Mar 2): the goal is to cut referral intake from ~3 days to same-day by automating fax data entry.

- Sponsor: Dana Ruiz (VP Ops). Champion: Priya Nair (Intake Lead).
- Main risk: EHR vendor API approval may take ~6 weeks, so phase 1 uses a human review queue.
- Next two weeks: profile one month of fax referrals; IT to share sandbox credentials by Friday."""


def _responder(params):
    return _sim.message(_sim.thinking(""), _sim.text(_SUMMARY))


_sim.set_responder(_responder)
