"""Root Paint Agent for Cymbal Shops.

Coordinates conversational paint shopping, catalog search (via AgentTool wrapped search_agent),
session state persistence (via set_session_value), and room-by-room planning (via room_planner).
"""
# Copyright (c) Cymbal Shops. All rights reserved.

import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import AgentTool

from paint_agent.tools import set_session_value
from paint_agent.sub_agents.search_agent.agent import search_agent
from paint_agent.sub_agents.room_planner.agent import room_planner_agent

load_dotenv()

# Bug Fix Architecture Note:
# In Vertex AI / Gemini, combining search tools with non-search tools directly causes:
# "400 INVALID_ARGUMENT: Multiple tools are supported only when they are all search tools."
# Wrapping search_agent inside AgentTool isolates the VertexAiSearchTool execution,
# allowing the root agent to utilize catalog search alongside Python session state tools.
search_tool = AgentTool(
    agent=search_agent,
    skip_summarization=False,
)

root_agent = Agent(
    name="paint_agent",
    model=os.environ.get("MODEL", "gemini-2.5-flash"),
    description=(
        "Cymbal Shops conversational paint expert. Helps users explore paint products, "
        "select colors, save project preferences to session state, and calculate required coverage."
    ),
    instruction="""You are the lead paint and home renovation assistant for Cymbal Shops.

Your workflow:
1. Greet the customer warmly and offer to help them explore Cymbal Shops' official paint products
   (e.g., Project Paint, SureCoverage, EcoGreens, Forever Paint).
2. When the customer asks about paint products or options, use the search_agent tool to retrieve
   accurate product specifications, coverage rates, available colors, and pricing from the indexed datasheets.
3. When the customer selects a paint product:
   a. Store the selected product name in session state using set_session_value(key="SELECTED_PAINT", value=...).
   b. Store the product's coverage rate using set_session_value(key="COVERAGE_RATE", value=...).
   c. Store the product's price per 2.5L bucket using set_session_value(key="PRICE", value=...).
4. Once the product choice is confirmed and saved to state, transfer the customer to the room_planner
   sub-agent to collect room dimensions, colors, and calculate paint requirements.
5. Provide helpful, conversational guidance throughout the renovation planning journey.
""",
    tools=[
        set_session_value,
        search_tool,
    ],
    sub_agents=[
        room_planner_agent,
    ],
)
