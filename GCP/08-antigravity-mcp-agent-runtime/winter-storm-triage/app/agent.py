"""Winter Storm Triage Agent Application.
Provides autonomous triage, loyalty tier lookup, and compensation resolution for Cymbal Direct.
"""
# Copyright (c) Cymbal Direct. All rights reserved.

import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from app.cymbal_direct_mcp import (
    get_order_status,
    get_customer_loyalty_info,
    issue_disruption_compensation
)

model_name = os.environ.get("MODEL", "gemini-3.5-flash")

root_agent = LlmAgent(
    name="WinterStormTriageAgent",
    model=Gemini(model=model_name),
    description="Autonomous order triage agent resolving winter storm logistics disruptions for Cymbal Direct.",
    instruction=(
        "You are the Winter Storm Customer Support Specialist for Cymbal Direct.\n\n"
        "Your mission is to assist customers impacted by severe winter storm shipping delays.\n"
        "Follow this standard protocol:\n"
        "1. Check the order status using get_order_status.\n"
        "2. Retrieve the customer loyalty tier using get_customer_loyalty_info.\n"
        "3. Apply compensation based on loyalty tier:\n"
        "   - Platinum: $100 credit, Next-Day Air upgrade\n"
        "   - Gold: $50 credit, Next-Day Air upgrade\n"
        "   - Silver: $25 credit, 3-Day Select upgrade\n"
        "   - Member: $10 credit, Priority Shipping upgrade\n"
        "4. Call issue_disruption_compensation with the credit and shipping upgrade.\n"
        "5. Respond with an empathetic, reassuring message explaining the resolution."
    ),
    tools=[get_order_status, get_customer_loyalty_info, issue_disruption_compensation]
)

app = root_agent
