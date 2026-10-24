"""Paint Search Agent sub-agent for Cymbal Shops.

Uses Vertex AI Agent Search (VertexAiSearchTool) to query the Cymbal Paint
data store and retrieve product information, pricing, and specifications.
"""
# Copyright (c) Cymbal Shops. All rights reserved.

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool

load_dotenv()

search_agent = Agent(
    name="search_agent",
    model="gemini-2.5-flash",
    description=(
        "Searches the Cymbal Shops paint product catalog using Vertex AI Agent Search. "
        "Returns detailed product information, coverage rates, available colors, and pricing."
    ),
    instruction="""
You are a paint product research specialist. When asked about paint products,
use the search tool to find accurate information from Cymbal Shops' official
paint datasheets. Return complete details including:
- Product name and description
- Available colors
- Coverage rate (sq meters per liter)
- Price per liter
- Special features (e.g., eco-friendly, durability)

Always base your responses on the datasheet content returned by the search tool.
""",
    tools=[
        VertexAiSearchTool(
            data_store_id=os.environ.get("SEARCH_ENGINE_ID", ""),
        )
    ],
)
