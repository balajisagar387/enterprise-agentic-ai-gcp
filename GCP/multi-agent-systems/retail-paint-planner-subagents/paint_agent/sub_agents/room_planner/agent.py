"""Room Planner sub-agent for Cymbal Shops Paint Agent.

Collects room dimensions, openings (doors and windows), and paint coats,
then delegates to coverage_calculator sub-agent to compute surface area,
liters required, bucket count, and estimated cost.
"""
# Copyright (c) Cymbal Shops. All rights reserved.

import os
from google.adk.agents import Agent
from paint_agent.sub_agents.coverage_calculator.agent import coverage_calculator_agent

room_planner_agent = Agent(
    name="room_planner",
    model=os.environ.get("MODEL", "gemini-2.5-flash"),
    description=(
        "Collects room names, dimensions, doors, windows, and color preferences, "
        "and coordinates with coverage_calculator to calculate required paint volume and cost."
    ),
    instruction="""You are a home renovation and room planning specialist for Cymbal Shops.

The customer has selected:
- Product: {SELECTED_PAINT?}
- Coverage Rate: {COVERAGE_RATE?} sq meters per liter
- Price per 2.5L Bucket: €{PRICE?}

Your goal is to guide the customer through planning their paint project room-by-room:
1. Ask how many rooms they want to paint and their names (e.g., 'living room', 'office', 'baby room').
2. For each room, confirm the chosen color (from the selected product line).
3. Request the room dimensions: length, width, ceiling height, number of standard doors, and number of standard windows.
4. Confirm the number of coats (standard recommendation is 2 coats).
5. Delegate to coverage_calculator to compute the total square meters of wall surface area, liters needed, number of 2.5L buckets (rounded up), and total estimated cost.
6. Present a clean, itemized breakdown for each room and a final total project summary.
""",
    sub_agents=[
        coverage_calculator_agent,
    ],
)
