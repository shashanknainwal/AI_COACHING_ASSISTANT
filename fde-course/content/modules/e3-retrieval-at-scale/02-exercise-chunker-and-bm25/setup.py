# Ridgeline Software's on-call runbooks (fictional). Available to your code as RUNBOOKS.
RUNBOOKS = [
    {"id": "RB-01", "title": "Rolling back a deploy",
     "text": "If a deploy raises the error rate above two percent, roll it back. Run ridge deploy rollback with the "
             "release id. The rollback restores the previous container image. Database migrations are reversed only "
             "when the release marked them reversible. Announce the rollback in the incident channel and link the "
             "release notes so the owning team can follow up after the incident closes."},
    {"id": "RB-02", "title": "Error E4012: token expired",
     "text": "Error E4012 means the service account token expired. Tokens last thirty days. Rotate the token with "
             "ridge auth rotate, then restart the worker pool so every worker picks up the new token. If E4012 "
             "persists after rotation, check that the clock on the host is in sync, because a skewed clock makes "
             "fresh tokens look expired."},
    {"id": "RB-03", "title": "Scaling the worker pool",
     "text": "The worker pool scales on queue depth. When the queue holds more than five thousand jobs for ten "
             "minutes, add workers with ridge pool scale. Each worker handles about two hundred jobs a minute. "
             "Scale down slowly: removing a worker drains its jobs first, and draining a busy worker can take "
             "several minutes."},
    {"id": "RB-04", "title": "Database failover",
     "text": "A failover promotes the replica to primary. Failover is automatic when the primary misses three "
             "health checks in a row. After a failover, confirm replication lag on the new replica is under one "
             "second before you close the incident. A manual failover uses ridge db promote and needs approval "
             "from the database owner."},
    {"id": "RB-05", "title": "Certificate renewal",
     "text": "TLS certificates renew automatically fourteen days before they expire. If renewal fails, the expiry "
             "alert fires. An expired token for the DNS provider is the usual cause. Renew by hand with ridge cert "
             "renew and confirm the new expiry date."},
    {"id": "RB-06", "title": "On-call handoff",
     "text": "At handoff, list open incidents, silenced alerts and any rollback still in progress."},
]
