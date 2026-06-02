"""
Mock database for the TechStore Plus customer service agent.

This module provides in-memory data for customers, orders, and support tickets.
It is intentionally simple — no ORM, no persistence — so you can focus on the
agent layer rather than data infrastructure.
"""

from datetime import date

# ─── Customers ────────────────────────────────────────────────────────────────

CUSTOMERS: dict[str, dict] = {
    "john.doe@company.com": {
        "id": "CUST-001",
        "email": "john.doe@company.com",
        "name": "John Doe",
        "category": "vip",
        "status": "active",
        "registration_date": "2023-03-15",
    },
    "sarah.smith@company.com": {
        "id": "CUST-002",
        "email": "sarah.smith@company.com",
        "name": "Sarah Smith",
        "category": "regular",
        "status": "active",
        "registration_date": "2024-01-20",
    },
    "emily.brown@company.com": {
        "id": "CUST-003",
        "email": "emily.brown@company.com",
        "name": "Emily Brown",
        "category": "regular",
        "status": "active",
        "registration_date": "2024-06-10",
    },
    "carlos.reyes@email.com": {
        "id": "CUST-004",
        "email": "carlos.reyes@email.com",
        "name": "Carlos Reyes",
        "category": "regular",
        "status": "active",
        "registration_date": "2025-02-28",
    },
    "anna.wilson@business.org": {
        "id": "CUST-005",
        "email": "anna.wilson@business.org",
        "name": "Anna Wilson",
        "category": "vip",
        "status": "active",
        "registration_date": "2022-11-05",
    },
}

# ─── Orders ───────────────────────────────────────────────────────────────────

ORDERS: list[dict] = [
    {
        "id": "ORD-001",
        "order_number": "TEC-2024-001",
        "customer_id": "CUST-001",
        "products": ["ThinkPad X1 Carbon (16GB/512GB)"],
        "status": "in_transit",
        "tracking_number": "UPS-9876543210",
        "estimated_delivery": str(date.today().replace(day=date.today().day + 2)),
        "total_amount": 1349.99,
        "purchase_date": "2024-12-10",
    },
    {
        "id": "ORD-002",
        "order_number": "TEC-2023-089",
        "customer_id": "CUST-001",
        "products": ["Samsung 27\" 4K Monitor", "Logitech MX Keys"],
        "status": "delivered",
        "tracking_number": "FEDEX-1122334455",
        "estimated_delivery": "2023-12-18",
        "total_amount": 689.98,
        "purchase_date": "2023-12-15",
    },
    {
        "id": "ORD-003",
        "order_number": "TEC-2024-045",
        "customer_id": "CUST-002",
        "products": ["iPhone 15 Pro (256GB)"],
        "status": "pending",
        "tracking_number": None,
        "estimated_delivery": None,
        "total_amount": 999.00,
        "purchase_date": "2024-12-20",
    },
    {
        "id": "ORD-004",
        "order_number": "TEC-2024-005",
        "customer_id": "CUST-003",
        "products": ["Apple Mac Mini (M4, 16GB/256GB)"],
        "status": "delivered",
        "tracking_number": "DHL-5566778899",
        "estimated_delivery": "2024-11-28",
        "total_amount": 799.00,
        "purchase_date": "2024-11-20",
    },
    {
        "id": "ORD-005",
        "order_number": "TEC-2025-012",
        "customer_id": "CUST-004",
        "products": ["Asus ROG Strix G16 Gaming Laptop", "HyperX Cloud III Headset"],
        "status": "cancelled",
        "tracking_number": None,
        "estimated_delivery": None,
        "total_amount": 1789.98,
        "purchase_date": "2025-01-05",
    },
    {
        "id": "ORD-006",
        "order_number": "TEC-2025-031",
        "customer_id": "CUST-005",
        "products": ["iPad Pro 13\" (M4)", "Apple Pencil Pro"],
        "status": "in_transit",
        "tracking_number": "UPS-1122334499",
        "estimated_delivery": str(date.today().replace(day=date.today().day + 1)),
        "total_amount": 1298.00,
        "purchase_date": "2025-01-18",
    },
]

# ─── Support Tickets ──────────────────────────────────────────────────────────

TICKETS: list[dict] = [
    {
        "id": "TKT-001",
        "ticket_number": "TICKET-2024-0891",
        "customer_id": "CUST-001",
        "category": "technical_support",
        "priority": "high",
        "status": "open",
        "description": "Laptop keyboard unresponsive after firmware update",
        "created_date": "2024-12-12",
    },
    {
        "id": "TKT-002",
        "ticket_number": "TICKET-2024-0456",
        "customer_id": "CUST-001",
        "category": "billing",
        "priority": "low",
        "status": "resolved",
        "description": "Requested invoice for order TEC-2023-089",
        "created_date": "2023-12-16",
    },
    {
        "id": "TKT-003",
        "ticket_number": "TICKET-2024-0923",
        "customer_id": "CUST-003",
        "category": "technical_support",
        "priority": "high",
        "status": "open",
        "description": "Mac Mini won't power on after initial setup",
        "created_date": "2024-11-29",
    },
    {
        "id": "TKT-004",
        "ticket_number": "TICKET-2025-0041",
        "customer_id": "CUST-004",
        "category": "returns",
        "priority": "medium",
        "status": "pending",
        "description": "Gaming laptop cancelled order — refund not received",
        "created_date": "2025-01-06",
    },
    {
        "id": "TKT-005",
        "ticket_number": "TICKET-2025-0078",
        "customer_id": "CUST-005",
        "category": "product_inquiry",
        "priority": "low",
        "status": "resolved",
        "description": "Compatibility question about Apple Pencil Pro with older iPad",
        "created_date": "2025-01-17",
    },
]


# ─── Query helpers ────────────────────────────────────────────────────────────

class MockCustomerDB:
    """In-memory store with helper methods used by the @tool functions."""

    def get_customer(self, email: str) -> dict | None:
        return CUSTOMERS.get(email.lower())

    def get_order(self, order_number: str) -> dict | None:
        return next((o for o in ORDERS if o["order_number"] == order_number), None)

    def get_orders_for_customer(self, email: str) -> list[dict]:
        customer = self.get_customer(email)
        if not customer:
            return []
        return [o for o in ORDERS if o["customer_id"] == customer["id"]]

    def get_tickets_for_customer(self, email: str) -> list[dict]:
        customer = self.get_customer(email)
        if not customer:
            return []
        return [t for t in TICKETS if t["customer_id"] == customer["id"]]

    def create_ticket(
        self,
        email: str,
        category: str,
        priority: str,
        description: str,
    ) -> dict | None:
        customer = self.get_customer(email)
        if not customer:
            return None
        ticket_id = f"TKT-{len(TICKETS) + 1:03d}"
        ticket_num = f"TICKET-2025-{len(TICKETS) + 100:04d}"
        new_ticket = {
            "id": ticket_id,
            "ticket_number": ticket_num,
            "customer_id": customer["id"],
            "category": category,
            "priority": priority,
            "status": "open",
            "description": description,
            "created_date": str(date.today()),
        }
        TICKETS.append(new_ticket)
        return new_ticket


# Singleton — import and use this in customer_tools.py
db = MockCustomerDB()
