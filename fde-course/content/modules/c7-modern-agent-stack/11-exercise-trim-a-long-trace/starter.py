import copy
import json


def audit_append_only(prev, new):
    """List every way `new` breaks the append-only rule relative to `prev`. Empty list = safe."""
    # TODO: compare system, tools, and the shared prefix of messages
    return []


def next_request(prev, last_response_content, user_text, new_rule):
    """Request 41: append-only, with the new rule as a system message and server-side clearing."""
    # TODO
    return copy.deepcopy(prev)


EDIT_CHOICES = {
    # Copy every key from CANDIDATE_EDITS and set "use" or "avoid".
}


# --- Try it out (not graded) ---
req = next_request(PREV_REQUEST, LAST_RESPONSE_CONTENT, NEW_USER_TEXT, NEW_RULE)
before, after = seen_tokens(naive_next_request()), seen_tokens(req)
print("Append-only problems:", audit_append_only(PREV_REQUEST, req) or "none")
print(f"Tokens the model reads: {before:,} -> {after:,} ({1 - after / before:.0%} less)")
