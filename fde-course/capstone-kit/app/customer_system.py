"""A fake "customer system": the orders database and help centre of a fictional
online stationery shop (Quillfeather Stationery). It stands in for the system
you would integrate with on a real deployment.

Replace `data/customer_system.json` and `data/kb/` with your own domain. Keep
the read tools read-only and keep a human approval in front of anything that
writes (here: `create_escalation`).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.retrieval import BM25Index, load_corpus

DATA_DIR = Path(__file__).parent / "data"


class CustomerSystem:
    def __init__(self, data_dir: Path = DATA_DIR, today: date | None = None):
        raw = json.loads((data_dir / "customer_system.json").read_text(encoding="utf-8"))
        self.customers: dict = raw["customers"]
        self.orders: dict = raw["orders"]
        self.index = BM25Index(load_corpus(data_dir / "kb"))
        self.escalations: list[dict] = []
        # A fixed "today" keeps evals reproducible. Pass a date to override.
        self.today = today or date(2026, 10, 10)

    # --- read-only tools -------------------------------------------------
    def get_order(self, order_id: str) -> dict:
        order = self.orders.get(order_id.strip().upper())
        if order is None:
            return {"error": f"No order {order_id}. Order numbers look like QF-1234."}
        result = {"order_id": order_id.strip().upper(), **order}
        if order.get("delivered_on"):
            days = (self.today - date.fromisoformat(order["delivered_on"])).days
            result["days_since_delivery"] = days
        return result

    def search_knowledge_base(self, query: str, k: int = 3) -> dict:
        hits = self.index.search(query, k=k)
        return {"results": [{"chunk_id": c.id, "title": c.title, "text": c.text, "score": round(s, 3)}
                            for c, s in hits]}

    # --- write tool (gated) ----------------------------------------------
    def create_escalation(self, order_id: str, reason: str, approved: bool) -> dict:
        """Open a ticket for a human agent. Refuses unless a human approved it."""
        if not approved:
            return {"error": "Escalation not approved by the operator. Tell the customer a person will review it."}
        ticket = {"ticket_id": f"ESC-{len(self.escalations) + 1:03d}", "order_id": order_id, "reason": reason}
        self.escalations.append(ticket)
        return ticket
