import os
import sys
import logging
import google.cloud.logging
from dotenv import load_dotenv

# Add current directory for workspace utilities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

# ==============================================================================
# Setup Logging and Environment
# ==============================================================================
try:
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
except Exception as log_err:
    logging.basicConfig(level=logging.INFO)
    logging.warning(f"Cloud Logging initialization skipped (fallback to standard logging): {log_err}")

load_dotenv()
model_name = os.getenv("MODEL")

# ==============================================================================
# Define Tools
# ==============================================================================

def add_prompt_to_state(
    tool_context: ToolContext,
    prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the agent's short-term shared state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}

# Configuring the MCP Tool to connect to the Zoo MCP server
mcp_server_url = os.getenv("MCP_SERVER_URL")
if not mcp_server_url:
    raise ValueError("The environment variable MCP_SERVER_URL is not set.")

def get_id_token() -> str:
    """Fetches a Google Cloud ID token to authenticate securely with the private MCP server."""
    target_url = os.getenv("MCP_SERVER_URL")
    # Extract the base Cloud Run service URL as the target audience
    audience = target_url.split('/mcp/')[0]
    auth_request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_request, audience)
    return id_token

# Connect to secure private MCP server with Bearer ID Token
mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url,
        headers={
            "Authorization": f"Bearer {get_id_token()}",
        },
    ),
)

# Configuring the Wikipedia Tool for external general domain knowledge
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)

# ==============================================================================
# Define Specialist Agents
# ==============================================================================

# 1. Researcher Agent
comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=model_name,
    description="The primary researcher that can access both internal zoo data and external knowledge from Wikipedia.",
    instruction="""
    You are a helpful research assistant. Your goal is to fully answer the user's PROMPT.

    You have access to two tools:
    1. A tool for getting specific data about animals AT OUR ZOO (names, ages, locations).
    2. A tool for searching Wikipedia for general knowledge (facts, lifespan, diet, habitat).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both the zoo's database AND Wikipedia, you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary data outputs.

    PROMPT: {{ PROMPT }}
    """,
    tools=[
        mcp_tools,
        wikipedia_tool
    ],
    output_key="research_data"  # Key storing combined findings in shared state
)

# 2. Response Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all information into a friendly, readable response.",
    instruction="""
    You are the friendly voice of the Zoo Tour Guide. Your task is to take the RESEARCH_DATA and present it to the user in a complete and helpful answer.
    - First, present the specific information from the zoo (like names, ages, and where to find them).
    - Then, add the interesting general facts from the research.
    - If some information is missing, just present the information you have.
    - Be conversational and engaging.

    RESEARCH_DATA: {{ research_data }}
    """
)

# ==============================================================================
# Define Workflow Orchestrator (Sequential Agent)
# ==============================================================================

tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="The main workflow for handling a user's request about an animal in ordered sequence.",
    sub_agents=[
        comprehensive_researcher,  # Step 1: Gather all data
        response_formatter,         # Step 2: Format the final response
    ]
)

# ==============================================================================
# Assemble Main Entrypoint (Root Agent)
# ==============================================================================

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Zoo Tour Guide.",
    instruction="""
    - Let the user know you will help them learn about the animals we have in the zoo.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    - After using the tool, transfer control to the 'tour_guide_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow]
)
