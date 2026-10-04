import json
from anthropic import _sim


def _responder(params):
    prompt = str(params["messages"][-1]["content"])
    lines = [l[2:] for l in prompt.split("<headlines>", 1)[1].split("</headlines>", 1)[0].strip().splitlines()]
    # Like real models sometimes do, the draft adds a plausible-sounding number that isn't in the facts.
    hours = lines[1].split(" coordinator")[0]
    low = lambda t: t[0].lower() + t[1:]
    summary = (f"In the Chicago pilot, {low(lines[0])}. {lines[2]}, and {low(lines[3])}. "
               f"Coordinators saved {hours} hours a month (roughly 2,400 hours a year), "
               f"and the project delivers {lines[4]}.")
    return json.dumps({"summary": summary})


_sim.set_responder(_responder)
