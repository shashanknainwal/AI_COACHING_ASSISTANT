"""Brightway Retail: customers, orders, shipments and help-center articles (Module 7).

Plain Python data so tools and retrieval code can use it directly. Use `fresh()` to
get an independent copy you can modify (for example, when issuing store credit).
"""

import copy

CUSTOMERS = {
    "C-100": {"name": "Maya Okafor", "email": "maya@example.com", "tier": "gold", "store_credit": 0.0},
    "C-101": {"name": "Ben Ito", "email": "ben@example.com", "tier": "standard", "store_credit": 15.0},
    "C-102": {"name": "Rosa Silva", "email": "rosa@example.com", "tier": "standard", "store_credit": 0.0},
}

ORDERS = {
    "B-1001": {"customer_id": "C-100", "placed_on": "2026-03-01", "status": "shipped", "shipment_id": "SHP-1003",
               "items": [{"sku": "LAMP-02", "name": "Arc floor lamp", "qty": 1, "price": 89.00}], "total": 89.00},
    "B-1002": {"customer_id": "C-101", "placed_on": "2026-03-03", "status": "delivered", "shipment_id": "SHP-1002",
               "items": [{"sku": "MUG-11", "name": "Stoneware mug set", "qty": 2, "price": 24.50}], "total": 49.00},
    "B-1003": {"customer_id": "C-100", "placed_on": "2026-03-05", "status": "processing", "shipment_id": None,
               "items": [{"sku": "SOFA-07", "name": "Linen sofa", "qty": 1, "price": 1249.00}], "total": 1249.00},
    "B-1004": {"customer_id": "C-102", "placed_on": "2026-03-06", "status": "shipped", "shipment_id": "SHP-1007",
               "items": [{"sku": "RUG-03", "name": "Wool rug 5x8", "qty": 1, "price": 310.00}], "total": 310.00},
}

SHIPMENTS = {
    "SHP-1002": {"carrier": "Northwind", "status": "delivered", "eta": "2026-03-06", "last_event": "Delivered, left at front door"},
    "SHP-1003": {"carrier": "Northwind", "status": "exception", "eta": "2026-03-12", "last_event": "Delayed: weather at Denver hub"},
    "SHP-1007": {"carrier": "Northwind", "status": "in_transit", "eta": "2026-03-10", "last_event": "Departed Chicago facility"},
}

KB_ARTICLES = [
    {"id": "KB-01", "title": "Returns policy",
     "text": "You can return most items within 30 days of delivery for a full refund to the original payment method.\n\n"
             "Large furniture such as sofas and tables can be returned within 14 days, and a $49 pickup fee applies.\n\n"
             "Items must be unused and in original packaging. Final-sale items cannot be returned."},
    {"id": "KB-02", "title": "Delayed or late shipments",
     "text": "If a shipment is marked delayed, the carrier usually delivers within 3 business days of the original estimate.\n\n"
             "If an order arrives more than 5 business days late, customers can request a $20 store credit for the inconvenience.\n\n"
             "Gold members receive a $25 store credit instead."},
    {"id": "KB-03", "title": "Damaged items",
     "text": "If an item arrives damaged, send a photo within 7 days of delivery.\n\n"
             "We ship a free replacement, or issue a full refund if the item is out of stock. You don't need to return the damaged item."},
    {"id": "KB-04", "title": "Store credit",
     "text": "Store credit never expires and can be combined with other offers.\n\n"
             "Support agents can issue up to $50 of store credit without approval. Larger amounts need a supervisor's approval."},
    {"id": "KB-05", "title": "Gold membership",
     "text": "Gold membership costs $59 per year and includes free shipping on every order, early access to sales, and larger "
             "late-delivery credits.\n\nMembership renews automatically each year and can be cancelled anytime for a prorated refund."},
    {"id": "KB-06", "title": "Changing or cancelling an order",
     "text": "Orders can be changed or cancelled free of charge while they are still processing.\n\n"
             "Once an order has shipped it can't be cancelled, but it can be returned under the returns policy."},
    {"id": "KB-07", "title": "Price adjustments",
     "text": "If the price of an item drops within 14 days of purchase, we refund the difference as store credit.\n\n"
             "Price adjustments don't apply to clearance items or flash sales."},
    {"id": "KB-08", "title": "Gift cards",
     "text": "Gift cards are delivered by email within an hour and never expire.\n\nGift cards can't be exchanged for cash or used to buy other gift cards."},
]


def fresh():
    """Independent copies of (CUSTOMERS, ORDERS, SHIPMENTS) that you can modify."""
    return copy.deepcopy(CUSTOMERS), copy.deepcopy(ORDERS), copy.deepcopy(SHIPMENTS)
