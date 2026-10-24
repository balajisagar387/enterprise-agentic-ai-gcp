# Autonomous Cloud Operations: AI Agent with Google Cloud Run Remote MCP Server & Human-in-the-Loop Guardrails

[![Google ADK](https://img.shields.io/badge/Google%20ADK-Agent%20Development%20Kit-4285F4?logo=google)](https://google.github.io/adk-docs/)
[![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run%20MCP-blue?logo=google-cloud)](https://cloud.google.com/run)
[![Model Context Protocol](https://img.shields.io/badge/Protocol-Remote%20MCP%20StreamableHTTP-purple)](https://modelcontextprotocol.io/)
[![Safety](https://img.shields.io/badge/Safety-Human--in--the--Loop%20(HITL)-green)]()

> **Enterprise Architecture Showcase**: An autonomous DevOps & Cloud Operations AI Agent built with the **Google Agent Development Kit (ADK)** that interacts directly with Google's managed **Remote Cloud Run MCP Server** (`https://run.googleapis.com/mcp`). Features **Human-in-the-Loop (HITL) tool interception** to enforce explicit administrator confirmation before executing mutating or destructive cloud actions.

---

## 📌 Executive Summary & Business Value

Managing enterprise cloud infrastructure traditionally requires navigating complex consoles, writing Terraform scripts, or running CLI commands. While LLMs can generate infrastructure code, letting an AI agent autonomously execute cloud mutations without guardrails introduces severe operational risks.

This solution demonstrates an **Enterprise-Grade Cloud Operations Agent**:

1. **Google-Managed Remote MCP Server**: Direct integration with Google Cloud's official Cloud Run MCP endpoint (`https://run.googleapis.com/mcp`), enabling agents to discover and execute Cloud Run control-plane operations dynamically.
2. **Human-in-the-Loop (HITL) Guardrails**: A custom toolset interceptor (`CloudRunMcpToolset`) dynamically flags all mutating operations (`create`, `update`, `delete`, `deploy`) with `_require_confirmation = True`, requiring the human administrator to review and click **Confirm** in the ADK UI before changes are committed.
3. **Conversational DevOps**: Natural language cloud management: listing revisions, inspecting container health, deploying serverless microservices, and toggling authentication policies on demand.
4. **Least-Privilege IAM Governance**: Authenticated via dedicated Service Account holding the fine-grained `roles/mcp.toolUser` and `roles/run.developer` roles.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Operator["DevOps Engineer / Administrator"]
        User(["Cloud Operator / Engineer"])
        ADK_Web["ADK Developer Web UI\n(Port 8000 / Token Streaming)"]
        ConfirmModal{{"HITL Confirmation Modal\n(Approve / Reject Action)"}}
    end

    subgraph AgentCore["Agent Reasoning Engine (Python 3.13)"]
        Agent["LlmAgent: CloudRunAgent\n(Gemini 3.5 Flash)"]
        HeaderProvider["cloud_run_header_provider\n(Auto-refreshing Bearer Token)"]
        subgraph ToolsetLayer["Custom Interceptor Layer"]
            Interceptor["CloudRunMcpToolset (McpToolset Subclass)\n• Inspects discovered tools\n• Mutating keyword filter:\n  ['create', 'delete', 'update', 'deploy']"]
        end
    end

    subgraph GoogleMCP["Google Managed Control Plane"]
        RemoteMCP["Google Remote Cloud Run MCP Server\n(https://run.googleapis.com/mcp)"]
        CloudRunAPI["Google Cloud Run Control Plane API\n(Deployments, Revisions, Traffic)"]
    end

    subgraph ManagedResources["Provisioned Workloads"]
        HelloApp["Deployed Workload: hello-test\n(us-docker.pkg.dev/cloudrun/container/hello)"]
    end

    User <--> ADK_Web
    ADK_Web --> Agent
    Agent --> HeaderProvider
    Agent --> Interceptor
    Interceptor -- "Read-only: Execute immediately" --> RemoteMCP
    Interceptor -- "Mutating: Pause for Approval" --> ConfirmModal
    ConfirmModal -- "Approved by User" --> RemoteMCP
    RemoteMCP --> CloudRunAPI
    CloudRunAPI --> HelloApp
```

---

## 🛡️ Human-in-the-Loop (HITL) Tool Interception

To prevent accidental outages, the agent dynamically parses tools exposed by the remote MCP server and classifies them into **Safe (Read-Only)** vs **Mutating (High-Risk)**:

```python
class CloudRunMcpToolset(McpToolset):
    """Dynamically enforces confirmation on mutating tools discovered from MCP server."""
    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> List[BaseTool]:
        tools = await super().get_tools(readonly_context)
        for t in tools:
            mutating_keywords = [
                "delete", "update", "replace", "create", "set", "remove", "run", "deploy"
            ]
            if any(k in t.name.lower() for k in mutating_keywords):
                t._require_confirmation = True  # Pauses execution for user UI confirmation
            else:
                t._require_confirmation = False # Read-only queries execute seamlessly
        return tools
```

---

## 🔄 Autonomous Lifecycle Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Engineer as Cloud Operator
    participant UI as ADK Web UI
    participant Agent as CloudRunAgent (LLM)
    participant Toolset as CloudRunMcpToolset
    participant MCP as Remote Cloud Run MCP
    participant GCP as Cloud Run API

    Engineer->>UI: "Deploy a private Cloud Run service named hello-test..."
    UI->>Agent: Prompt forwarded to Gemini 3.5 Flash
    Agent->>Toolset: Selects tool: 'deploy_service'
    Note over Toolset: Mutating keyword 'deploy' detected!
    Toolset-->>UI: Raises adk_request_confirmation
    UI-->>Engineer: Prompts: "Confirm execution of deploy_service?"
    Engineer->>UI: Clicks "Confirmed" & "Submit"
    UI->>Toolset: Resume execution with approval
    Toolset->>MCP: StreamableHTTP RPC (Bearer Token)
    MCP->>GCP: Deploys container image to us-west1
    GCP-->>MCP: Provisioning complete (Status: 200)
    MCP-->>Agent: Returns Service URL & metadata
    Agent-->>UI: Explains deployment results and gives Service URL
```

---

## 📂 Repository Structure

```text
GCP/multi-agent-systems/cloudrun-remote-mcp-hitl/
├── README.md                           # Master executive and technical showcase
├── crun_agent/
│   ├── __init__.py                     # Package export
│   ├── agent.py                        # ADK LlmAgent with CloudRunMcpToolset HITL logic
│   ├── requirements.txt                # Pinned ADK & MCP dependencies
│   └── .env.example                    # Environment template with Vertex AI configuration
└── docs/
    └── architecture.md                 # Deep-dive: Remote MCP Servers & HITL Safety Patterns
```

---

## 🏢 Business Applications for Enterprise Clients (WeWork)

1. **Self-Service Developer Sandboxes**: Developers can request ephemeral Cloud Run environments in Slack/Teams without requiring GCP Console access; the agent deploys sandbox services and applies strict budget labels.
2. **Autonomous Incident Triage**: On production alerts, the agent inspects revisions, fetches failing container logs via MCP, and suggests rollback revisions subject to human approval.
3. **Automated Traffic Shifting & Canary Deployments**: Safely executing blue-green canary rollouts by instructing the agent to split traffic (e.g., 90/10) with mandatory HITL sign-off.
