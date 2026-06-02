"""
TechStore Plus — customer service tools for the LangChain agent.

Each function is decorated with @tool so the agent can discover and invoke it
automatically. Tool docstrings serve as the description the LLM reads when
deciding which tool to call — keep them clear and specific.

Stop 3 task: implement the body of each function.
- Import `db` from mock_db and call the appropriate helper method.
- Return a human-readable string; the agent will read this as the tool result.
- Handle missing data gracefully: return a clear message, never raise.
"""

from langchain_core.tools import tool
from src.database.mock_db import db


@tool
def get_customer_info(email: str) -> str:
    """Retrieve the profile for a TechStore Plus customer by email address.

    Returns name, membership category, account status, and registration date.
    Use this tool first when a customer identifies themselves.
    """
    customer = db.get_customer(email)
    if customer is None:
        return f"No account found for {email}."
    return (
        f"Customer profile for {customer['email']}:\n"
        f"- Name: {customer['name']}\n"
        f"- Category: {customer['category']}\n"
        f"- Status: {customer['status']}\n"
        f"- Registration date: {customer['registration_date']}"
    )


@tool
def get_order_status(order_number: str) -> str:
    """Look up the current status of an order by its order number (e.g. TEC-2024-001).

    Returns order status, products ordered, total amount, and purchase date.
    """
    order = db.get_order(order_number)
    if order is None:
        return f"Order {order_number} not found."
    products = ", ".join(order["products"])
    return (
        f"Order {order['order_number']}:\n"
        f"- Status: {order['status']}\n"
        f"- Products: {products}\n"
        f"- Total: ${order['total_amount']:.2f}\n"
        f"- Purchase date: {order['purchase_date']}"
    )


@tool
def get_shipping_tracking(order_number: str) -> str:
    """Get the shipping tracking number and estimated delivery date for an order.

    Returns the carrier tracking number and estimated delivery. If the order
    has not shipped yet or was cancelled, returns the current status instead.
    """
    order = db.get_order(order_number)
    if order is None:
        return f"Order {order_number} not found."
    if order["tracking_number"] is None:
        return (
            f"Order {order['order_number']} has not shipped yet. "
            f"Current status: {order['status']}."
        )
    return (
        f"Shipping for order {order['order_number']}:\n"
        f"- Tracking number: {order['tracking_number']}\n"
        f"- Estimated delivery: {order['estimated_delivery']}\n"
        f"- Current status: {order['status']}"
    )


@tool
def get_customer_orders(email: str) -> str:
    """List all orders placed by a customer, identified by their email address.

    Returns a summary of each order: order number, products, status, and total.
    """
    orders = db.get_orders_for_customer(email)
    if not orders:
        return f"No orders found for {email}."
    lines = [f"Orders for {email}:"]
    for index, order in enumerate(orders, start=1):
        products = ", ".join(order["products"])
        lines.append(
            f"{index}. {order['order_number']} - {products} - "
            f"{order['status']} - ${order['total_amount']:.2f}"
        )
    return "\n".join(lines)


@tool
def get_customer_tickets(email: str) -> str:
    """List all support tickets associated with a customer's email address.

    Returns each ticket's number, category, priority, status, and description.
    """
    tickets = db.get_tickets_for_customer(email)
    if not tickets:
        return f"No support tickets found for {email}."
    lines = [f"Support tickets for {email}:"]
    for index, ticket in enumerate(tickets, start=1):
        lines.append(
            f"{index}. {ticket['ticket_number']} - {ticket['category']} - "
            f"{ticket['priority']} priority - {ticket['status']} - "
            f"{ticket['description']}"
        )
    return "\n".join(lines)


@tool
def create_support_ticket(
    email: str,
    category: str,
    priority: str,
    description: str,
) -> str:
    """Open a new support ticket for a customer.

    Args:
        email: The customer's email address.
        category: One of 'technical_support', 'billing', 'returns', 'product_inquiry',
                  'general_information'.
        priority: One of 'low', 'medium', 'high'.
        description: A brief description of the issue.

    Returns the new ticket number and confirms the category and priority.
    """
    ticket = db.create_ticket(email, category, priority, description)
    if ticket is None:
        return f"Could not create ticket - no account found for {email}."
    return (
        f"Created support ticket {ticket['ticket_number']}:\n"
        f"- Category: {ticket['category']}\n"
        f"- Priority: {ticket['priority']}\n"
        f"- Status: {ticket['status']}\n"
        f"- Description: {ticket['description']}"
    )


# ─── Tool list ────────────────────────────────────────────────────────────────
# Import this in memory_agent.py: from src.components.customer_tools import TOOLS

TOOLS = [
    get_customer_info,
    get_order_status,
    get_shipping_tracking,
    get_customer_orders,
    get_customer_tickets,
    create_support_ticket,
]
