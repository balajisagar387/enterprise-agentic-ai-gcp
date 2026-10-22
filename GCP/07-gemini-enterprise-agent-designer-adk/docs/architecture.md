# Architecture & Integration Blueprint: Gemini Enterprise with ADK & Agent Designer

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Users["End Users & Operators"]
        Employee(["Cymbal Pools Employee"])
    end

    subgraph GeminiEnterprise["Gemini Enterprise Hub (Cymbal Pools GE)"]
        GE_UI["Gemini Enterprise Web App\n(Central Single Pane of Glass)"]
        AgentDesignerAgent["No-Code Pool Robot Agent\n(Created via Agent Designer)"]
        CustomAgentTile["Custom Agent: Brand Voice Agent\n(Pinned in Navigation)"]
    end

    subgraph SecurityFabric["OAuth 2.0 & Identity Layer"]
        ConsentScreen["OAuth Consent Screen\n(Cymbal Pools Auth - Internal)"]
        OAuthClient["OAuth 2.0 Web Client\n(Gemini Enterprise Client)"]
        TokenAuth["Token Exchange & Auth URI\n(accounts.google.com -> oauth2/token)"]
    end

    subgraph AgentRuntime["Vertex AI Agent Runtime (us-east4)"]
        ReasoningEngine["Reasoning Engine (ADK No-Code YAML)\nCymbal Pools Brand Voice\nModel: Gemini 3.5 Flash"]
        StagingGCS[("Staging Bucket\ngs://qwiklabs-gcp-03-...-bucket")]
    end

    subgraph ExternalServices["Connectors & External Grounding"]
        GoogleSearch["Google Search Grounding Connector"]
    end

    Employee <--> GE_UI
    GE_UI --> AgentDesignerAgent
    AgentDesignerAgent --> GoogleSearch
    GE_UI --> CustomAgentTile
    CustomAgentTile -- "3-Legged OAuth User Delegation" --> ConsentScreen
    ConsentScreen --> OAuthClient
    OAuthClient --> TokenAuth
    TokenAuth --> ReasoningEngine
    ReasoningEngine -. "Deploy Artifacts" .-> StagingGCS
```

---

## 🛡️ Integration & Delegation Standard

### 1. Dual Agent Modalities
- **No-Code Agent Designer**: Built directly within the Gemini Enterprise application for business analysts with instant Google Search grounding.
- **Enterprise ADK YAML Config**: Engineered declaratively via Google ADK (`root_agent.yaml`), deployed to managed Vertex AI Agent Runtime with dedicated compute scaling.

### 2. Zero-Trust User Delegation (OAuth 2.0 Web Client)
Access from Gemini Enterprise to the custom Agent Runtime engine is mediated through a 3-legged OAuth 2.0 authorization code flow:
- Authorized redirect URI: `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html`
- Token endpoint: `https://oauth2.googleapis.com/token`
- Each user authenticates under their corporate identity, guaranteeing audit compliance and isolated execution sessions.
