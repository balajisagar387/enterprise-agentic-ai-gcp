# Architecture & Security Blueprint: BigQuery Agent with Agent Identity

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["User & Evaluation Layer"]
        Operator(["Finance Analyst / Operator"])
        Playground["Vertex AI Deployments Playground\n(Agent Platform Web UI)"]
    end

    subgraph SecurityFabric["Zero-Trust Agent Identity & IAM"]
        AgentIdentity["Agent Principal Identity\nprincipal://agents.global.org-.../reasoningEngines/..."]
        BQ_DataEditor["roles/bigquery.dataEditor"]
        BQ_User["roles/bigquery.user"]
    end

    subgraph RuntimeLayer["Vertex AI Agent Runtime (Reasoning Engine)"]
        AgentEngine["BigQuery Invoice Agent\n(Model: Gemini 2.5 Flash)"]
        ToolExecutor["BigQuery Toolset Execution Layer\n(Schema Inspector, SQL Runner)"]
    end

    subgraph StorageLayer["Enterprise Data Warehouse"]
        StagingGCS[("Enterprise Staging Bucket\ngs://enterprise-agentic-artifacts-prod/")]
        BigQueryDWH[("BigQuery Invoices Table\n(Corporate Finance Dataset)")]
    end

    Operator <--> Playground
    Playground <--> AgentEngine
    AgentEngine --> ToolExecutor
    ToolExecutor -- "Authenticates as" --> AgentIdentity
    AgentIdentity -.-> BQ_DataEditor
    AgentIdentity -.-> BQ_User
    BQ_DataEditor --> BigQueryDWH
    BQ_User --> BigQueryDWH
    AgentEngine -. "Deployment Artifacts" .-> StagingGCS
```

---

## 🛡️ Core Security Architecture: Agent Identity

In traditional cloud agent deployments, workloads often rely on default compute service accounts (e.g., Compute Engine default SA) or end-user identity propagation. This introduces significant risks:
1. **Privilege Over-Assignment**: Default service accounts often hold broad `Editor` or `Viewer` permissions across the entire project.
2. **Blast Radius Expansion**: If multiple agents or workloads share one service account, compromising one agent compromises access to unrelated datasets.

### The Agent Identity Pattern
By setting `identity_type = types.IdentityType.AGENT_IDENTITY`, Google Cloud provisions a cryptographically isolated **Agent Principal** tied strictly to the specific Reasoning Engine instance:

$$\text{Principal} = \text{principal://agents.global.org-\textit{ORG\_ID}.system.id.goog/resources/aiplatform/projects/\textit{PROJECT\_NUMBER}/locations/\textit{REGION}/reasoningEngines/\textit{ENGINE\_ID}}$$

### Least-Privilege IAM Enforcement
Only the exact roles required to inspect and query the targeted dataset are granted to this unique identity:
- **`roles/bigquery.dataEditor`**: Grants table read/write capabilities needed to evaluate queries and temporary tables.
- **`roles/bigquery.user`**: Grants permission to run BigQuery query jobs and allocate compute slots.
