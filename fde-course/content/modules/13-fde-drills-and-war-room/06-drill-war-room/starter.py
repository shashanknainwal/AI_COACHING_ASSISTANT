# War room. The service is in /tmp/relay_incident/service and the logs are in
# /tmp/relay_incident/logs. Read them from here, for example:
#
#   import os
#   for root, dirs, files in os.walk("/tmp/relay_incident"):
#       print(root, files)
#   print(open("/tmp/relay_incident/logs/relay.log").read()[:2000])

LOGS = "/tmp/relay_incident/logs"


# Level 1: return a settings override that stabilises the relay.
def stabilise():
    return {}


# Level 2: fill in from the code and the logs.
ROOT_CAUSE = {
    "file": "",
    "function": "",
    "introduced_in": "",
    "duplicated_events": [],
    "dead_lettered": [],
}


# Level 3
def fixed_idempotency_key(event, attempt):
    pass


def check_idempotency_key(key_fn):
    pass


# Level 4
STATUS_UPDATE = ""
