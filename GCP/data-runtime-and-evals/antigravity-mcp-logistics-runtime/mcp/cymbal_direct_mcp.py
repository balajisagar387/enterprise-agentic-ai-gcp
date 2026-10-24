"""Cymbal Direct Logistics MCP Server.
Provides tools to inspect orders, customer loyalty tiers, and issue disruption compensation.
"""
# Copyright (c) Cymbal Direct. All rights reserved.

from fastmcp import FastMCP
from typing import Dict, Any

mcp = FastMCP("CymbalLogistics")

# Mock database records
ORDERS = {
    "CYM-EC-9921": {
        "order_id": "CYM-EC-9921",
        "customer_id": "CUST-7821",
        "customer_name": "Jordan Smith",
        "item": "Winter Storm Weatherproof Jacket",
        "status": "Delayed: Severe Winter Storm in transit hub",
        "origin": "Denver, CO",
        "destination": "Minneapolis, MN"
    },
    "CYM-EC-1002": {
        "order_id": "CYM-EC-1002",
        "customer_id": "CUST-1044",
        "customer_name": "Taylor Hayes",
        "item": "Thermal Insulated Ski Pants & Boots",
        "status": "Delayed: Severe Winter Storm in transit hub",
        "origin": "Salt Lake City, UT",
        "destination": "Chicago, IL"
    }
}

CUSTOMERS = {
    "CUST-7821": {
        "customer_id": "CUST-7821",
        "name": "Jordan Smith",
        "loyalty_tier": "Gold",
        "membership_years": 4
    },
    "CUST-1044": {
        "customer_id": "CUST-1044",
        "name": "Taylor Hayes",
        "loyalty_tier": "Platinum",
        "membership_years": 7
    }
}

@mcp.tool()
def get_order_status(order_id: str) -> Dict[str, Any]:
    """Retrieves current shipping status, transit notes, and customer ID for an order."""
    if order_id in ORDERS:
        return ORDERS[order_id]
    return {"error": f"Order {order_id} not found in logistics database."}

@mcp.tool()
def get_customer_loyalty_info(customer_id: str) -> Dict[str, Any]:
    """Retrieves customer loyalty tier (Platinum, Gold, Silver, Member) and account details."""
    if customer_id in CUSTOMERS:
        return CUSTOMERS[customer_id]
    return {"error": f"Customer {customer_id} not found."}

@mcp.tool()
def issue_disruption_compensation(customer_id: str, credit_amount: float, shipping_upgrade: str) -> Dict[str, Any]:
    """Issues credit refund to customer account and applies express shipping upgrade."""
    return {
        "status": "SUCCESS",
        "customer_id": customer_id,
        "credit_applied": f"${credit_amount:.2f}",
        "shipping_upgrade": shipping_upgrade,
        "message": f"Successfully credited ${credit_amount:.2f} and upgraded shipping to '{shipping_upgrade}'."
    }

if __name__ == "__main__":
    mcp.run()
