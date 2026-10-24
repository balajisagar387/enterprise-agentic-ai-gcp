# System Architecture: Multi-Agent Systems on Agent Runtime with Vertex AI Search

## 1. High-Level Orchestration Topology

Enterprise conversational systems frequently require a hybrid mix of **unstructured document search** (product datasheets, catalog manuals) and **deterministic calculations** (surface area, architectural deductions, cost estimates). 

To ensure modularity and avoid prompt bloat, the architecture separates concerns across specialized sub-agents coordinated by a central root agent:

```mermaid
flowchart TD
    subgraph ClientLayer["User & Presentation Layer"]
        User(["Retail Customer"])
        WebUI["Chainlit Conversational Frontend\n(Port 8000 / WebSockets)"]
    end

    subgraph AgentRuntime["Vertex AI Agent Runtime (Reasoning Engine)"]
        subgraph RootAgent["paint_agent (Orchestrator)"]
            StateStore[("Session State Dictionary\n(ToolContext.state)")]
            StateTool["set_session_value()\n(Persists SELECTED_PAINT, COVERAGE_RATE, PRICE)"]
        end

        subgraph SearchBoundary["Search Isolation Layer"]
            WrappedTool["AgentTool(agent=search_agent)\n(Isolates search capability into standard tool)"]
            SearchSub["search_agent\n(Gemini 2.5 Flash)"]
        end

        subgraph CalculationSubtree["Renovation Planning Subtree"]
            RoomPlanner["room_planner (Sub-agent)\n(Collects rooms, colors & dimensions)"]
            CalcAgent["coverage_calculator (Nested Sub-agent)\n(Loads state via {KEY?}, computes m², buckets & cost)"]
        end
    end

    subgraph GCP_Data["GCP Managed Knowledge & Storage"]
        SearchStore[("Vertex AI Agent Search\n(Cymbal Paint Data Store)")]
        GCS_PDF[("Cloud Storage Bucket\n(Cymbal_Shops_Paint_Datasheets.pdf)")]
    end

    User <--> WebUI
    WebUI <--> RootAgent
    RootAgent --> StateTool
    StateTool --> StateStore
    RootAgent --> WrappedTool
    WrappedTool --> SearchSub
    SearchSub --> SearchStore
    SearchStore -.-> GCS_PDF
    RootAgent -- "transfer_to_agent" --> RoomPlanner
    RoomPlanner --> CalcAgent
    StateStore -. "Key Templating ({KEY?})" .-> CalcAgent
```

---

## 2. The `AgentTool` Pattern: Bypassing Tool-Conflict Constraints

### The Problem
Vertex AI and Gemini enforce strict tool validation rules:
> `400 INVALID_ARGUMENT: Multiple tools are supported only when they are all search tools.`

When building multi-agent systems, if an agent registers a search tool (`VertexAiSearchTool`) alongside regular Python function tools, the API call rejects the request. Even having a sub-agent with a search tool can trigger this, as sub-agents introduce an implicit `transfer_to_agent` function tool.

### The Solution: Agent-as-a-Tool Wrapping
Google ADK provides the `AgentTool` class, which encapsulates an entire agent (including its search tool) into a standard, callable function tool from the perspective of the parent agent:

```python
search_tool = AgentTool(
    agent=search_agent,        # Isolated search agent with VertexAiSearchTool
    skip_summarization=False,  # Returns synthesized search findings to root agent
)
```

This pattern isolates the search execution context, allowing the root agent to freely pair search capabilities with arbitrary Python tools (`set_session_value`).

---

## 3. Session State Persistence & Key Templating

Multi-turn dialogues require sharing context across distinct agents without forcing the end user to repeat themselves.

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Root as paint_agent
    participant Search as search_agent
    participant State as ToolContext.state
    participant Planner as room_planner
    participant Calc as coverage_calculator

    User->>Root: "I'd like to use Forever Paint"
    Root->>Search: Query datasheet specifications
    Search-->>Root: 8 m²/L, €40 per 2.5L bucket
    Root->>State: set_session_value("SELECTED_PAINT", "Forever Paint")
    Root->>State: set_session_value("COVERAGE_RATE", "8")
    Root->>State: set_session_value("PRICE", "40")
    Root-->>User: "Confirmed Forever Paint. How many rooms?"
    User->>Planner: "Living room: 5m x 4m x 2.5m, 1 door, 3 windows, 2 coats"
    Planner->>Calc: Delegate coverage computation
    State-->>Calc: Injects {SELECTED_PAINT?}, {COVERAGE_RATE?}, {PRICE?}
    Calc-->>Planner: 77 m² total area, 9.625 L, 4 buckets, €160
    Planner-->>User: Itemized breakdown & cost estimate
```

### ADK Key Templating Syntax: `{KEY?}`
In agent prompt instructions, wrapping state keys in curly braces with a trailing question mark (`{SELECTED_PAINT?}`) achieves two critical behaviors:
1. **Dynamic Runtime Interpolation**: Injects the value from `ToolContext.state` if it exists.
2. **Graceful Fallback**: If the key has not been set yet, the template renders cleanly without crashing the agent.

---

## 4. Managed Agent Runtime Architecture

Deploying via `adk deploy agent_engine` packages the agent code into a **Vertex AI Reasoning Engine** microservice:
- **Serverless & Autoscaling**: Zero-idle compute with automatic scale-to-demand.
- **Enterprise IAM Authentication**: Governed by `roles/aiplatform.user` and `roles/discoveryengine.user`.
- **SDK Connectivity**: Clean Python SDK interaction via `ReasoningEngineClient()`.
