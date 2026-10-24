# Architecture Deep-Dive: Enterprise ADK & MCP Serverless Agent

This document provides a comprehensive technical overview of the multi-agent system architecture built using the **Google Agent Development Kit (ADK)**, the **Model Context Protocol (MCP)**, and **Google Cloud Run**.

---

## 1. Architectural Philosophy: Separation of Concerns

A classic anti-pattern in generative AI development is tightly coupling **LLM reasoning logic** with **data retrieval and internal tool execution**. 

In this architecture, we strictly decouple the **Reasoning Layer** from the **Tooling Layer**:

```mermaid
flowchart LR
    subgraph Client["Client Interface"]
        UI["ADK Developer UI / Streaming Chat"]
    end

    subgraph Reasoning["Reasoning Layer (Google ADK)"]
        direction TB
        Agent["Tour Guide Agent Service\n(Cloud Run)"]
        Gemini["Gemini Enterprise Model\n(Vertex AI)"]
        Agent <--> Gemini
    end

    subgraph Tooling["Tooling & Data Layer"]
        direction TB
        MCP["Zoo Private MCP Server\n(Cloud Run / Microservice)"]
        Wiki["External Public Web API\n(LangChain Wikipedia)"]
    end

    UI <--> Agent
    Agent -- "Secure RPC (Bearer ID Token)" --> MCP
    Agent -- "HTTP REST" --> Wiki
```

### Key Advantages of This Separation:
1. **Independent Lifecycle & Governance**: Tool APIs (MCP servers) can be maintained, upgraded, and monitored by domain/database engineering teams without touching prompt logic or agent code.
2. **Standardized Protocol**: MCP establishes a vendor-neutral protocol for exposing tools, schemas, and prompts to LLMs.
3. **Zero-Trust Security Boundary**: The LLM agent does not have direct access to database credentials or internal VPC storage. It only interacts with the MCP server over authenticated and authorized endpoints.

---

## 2. Multi-Agent Orchestration Flow

The solution leverages ADK's `SequentialAgent` and specialized roles to handle conversational flow, data gathering, and user presentation deterministically.

```mermaid
sequenceDiagram
    autonumber
    actor User as Zoo Visitor
    participant Greeter as Greeter Agent (Root)
    participant State as ToolContext.state (Memory)
    participant Researcher as Comprehensive Researcher
    participant MCP as Private Zoo MCP Server
    participant Wiki as Wikipedia Tool
    participant Formatter as Response Formatter Agent

    User->>Greeter: "Where are the lions and what do they eat in the wild?"
    Greeter->>State: add_prompt_to_state(PROMPT)
    Note over Greeter: Transfers control to SequentialAgent Workflow
    Greeter->>Researcher: Sequential Step 1 (PROMPT)
    
    rect rgb(240, 248, 255)
        Note over Researcher: Analyzes requirement for dual tooling
        Researcher->>MCP: fetch_animal_details(name="lion") [Private Zoo DB]
        MCP-->>Researcher: { enclosure: "Savanna Trail #4", age: 7, names: ["Simba"] }
        Researcher->>Wiki: search(query="Panthera leo diet in wild")
        Wiki-->>Researcher: "Lions in the wild primarily feed on ungulates..."
    end

    Researcher->>State: Store output in research_data
    Researcher->>Formatter: Sequential Step 2 (research_data)
    Note over Formatter: Synthesizes data into friendly tour guide voice
    Formatter-->>User: "Our lions Simba is at Savanna Trail #4! In the wild, lions..."
```

---

## 3. Enterprise Security & IAM Authentication

To connect to private Cloud Run services (such as the Zoo MCP server), the agent cannot use long-lived API keys. Instead, it relies on **Google Cloud Identity and Access Management (IAM)** and short-lived OpenID Connect (OIDC) ID tokens.

### Identity Flow
1. **Cloud Run Identity**: The agent runs under the default Compute Service Account:
   `${PROJECT_NUMBER}-compute@developer.gserviceaccount.com`
2. **MCP Authorization**: The service account is granted `roles/run.invoker` on the MCP server Cloud Run service.
3. **Token Fetching**:
   ```python
   def get_id_token():
       target_url = os.getenv("MCP_SERVER_URL")
       audience = target_url.split('/mcp/')[0]
       request = google.auth.transport.requests.Request()
       return google.oauth2.id_token.fetch_id_token(request, audience)
   ```
4. **Header Injection**: The token is passed as `Authorization: Bearer <ID_TOKEN>` within `MCPToolset(StreamableHTTPConnectionParams(...))`.
5. **Model Access**: The service account is granted `roles/aiplatform.user` to invoke Gemini models on Google Vertex AI.

---

## 4. Serverless Hosting on Google Cloud Run

Deploying with `adk deploy cloud_run` leverages Google Cloud Run's container infrastructure:

| Feature | Enterprise Benefit |
| :--- | :--- |
| **0-to-N Autoscaling** | Scales to zero when no visitors are chatting ($0 compute cost). Rapidly scales horizontally when thousands of visitors arrive. |
| **Streaming UI** | ADK builds in a token-streaming developer UI (`--with_ui`) with zero frontend setup required. |
| **Stateless Container** | Ephemeral containers prevent cross-session memory leaks; session memory is managed in `ToolContext.state`. |
| **Portability** | Standard Docker container packaged by Google Cloud Build into Artifact Registry, executable on any OCI-compliant runtime. |
