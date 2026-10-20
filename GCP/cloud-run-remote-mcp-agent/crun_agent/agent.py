import os
import logging
from typing import Optional, List
import google.cloud.logging
from dotenv import load_dotenv

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.base_tool import BaseTool
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models import Gemini

# Load environment variables from .env file
load_dotenv()

# --- Setup Logging and Environment ---
try:
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
except Exception:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("crun_agent")
logger.setLevel(logging.INFO)

# --- Vertex AI and Client Configuration ---
use_vertexai = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "False").lower() == "true"
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", os.environ.get("LOCATION", "global"))
mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://run.googleapis.com/mcp")

client_kwargs = {}
if use_vertexai:
    client_kwargs["vertexai"] = True
    client_kwargs["project"] = project_id
    client_kwargs["location"] = location

async def cloud_run_header_provider(context: ReadonlyContext):
    """Generates the required Authorization: Bearer header for the remote MCP server using Application Default Credentials."""
    try:
        from google.auth.transport.requests import Request
        import google.auth
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        credentials.refresh(Request())
        token = credentials.token
    except Exception as e:
        raise ValueError(
            f"Could not get OAuth access token.\n"
            f"Please provide credentials by setting GOOGLE_APPLICATION_CREDENTIALS to the path of your Service Account JSON file in your .env file.\n"
            f"Error details: {e}"
        )
    return {"Authorization": f"Bearer {token}"}

class CloudRunMcpToolset(McpToolset):
    """Custom MCP Toolset subclass that intercepts tools discovered from the remote Cloud Run MCP server
    and enforces Human-in-the-Loop (HITL) confirmation for mutating and destructive operations.
    """
    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> List[BaseTool]:
        tools = await super().get_tools(readonly_context)
        for t in tools:
            # Require explicit user confirmation only for mutating actions
            mutating_keywords = [
                "delete", "update", "replace", "create", "set", "remove", "run", "deploy"
            ]
            if any(k in t.name.lower() for k in mutating_keywords):
                t._require_confirmation = True
                logger.info(f"Requiring confirmation for mutating tool: {t.name}")
            else:
                t._require_confirmation = False
        return tools

# Connect to the Google-managed remote Cloud Run MCP server using StreamableHTTP
toolset = CloudRunMcpToolset(
    connection_params=StreamableHTTPConnectionParams(url=mcp_server_url),
    header_provider=cloud_run_header_provider,
)

model = os.environ.get("MODEL")
if not model:
    raise ValueError("MODEL environment variable is required. Please add it to your .env file.")

# Root LLM Agent orchestrating Cloud Run management operations
root_agent = LlmAgent(
    name="CloudRunAgent",
    model=Gemini(
        model=model,
        client_kwargs=client_kwargs if client_kwargs else None
    ),
    description="An enterprise agent that helps you list, deploy, and manage your Google Cloud Run services.",
    instruction=(
        "You are a helpful assistant that helps users manage their Google Cloud Run services "
        "using the provided Cloud Run MCP tools.\n\n"
        "Capabilities:\n"
        "- List Cloud Run services, jobs, and revisions.\n"
        "- Get details about specific services.\n"
        "- Create, update, or delete services and jobs (requires user confirmation in the UI).\n\n"
        "Guidelines:\n"
        "- Always explain what actions you are taking.\n"
        "- Destructive actions (like deleting, creating, or updating) will require explicit confirmation "
        "from the user via the ADK web UI. Inform the user that they need to click 'Approve' or 'Reject' "
        "when a confirmation prompt appears.\n"
        "- If you encounter permission errors or API enablement errors, explain them clearly to the user "
        "and suggest how they can fix them (e.g., enabling the Cloud Run Admin API, granting roles/run.admin)."
    ),
    tools=[toolset]
)
