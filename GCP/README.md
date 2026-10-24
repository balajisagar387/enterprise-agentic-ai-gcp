# Google Cloud Platform (GCP) Enterprise AI & Agentic Solutions Portfolio

This directory contains enterprise-grade reference architectures, proof-of-concepts, and deployable implementations built on **Google Cloud Platform (GCP)**, **Vertex AI**, and modern agentic frameworks. The portfolio is structured across three core architectural pillars:

---

## 🏛️ Architecture Pillars & Modules

### 🛡️ 1. Security & Governance (`security-and-governance/`)
Zero-Trust defense-in-depth, LLM bilateral firewalls, and workload identity federation without service account key leakage.

| Module | Core Technologies | Architecture Pattern | Status |
| :--- | :--- | :--- | :---: |
| [**Model Armor LLM Firewall**](./security-and-governance/model-armor-llm-firewall) | **Gemini Enterprise, Model Armor, Workspace RAG, OAuth 2.0, Gemini 3.1 Pro** | Bilateral AI Security Firewall (Prompt Injection / PII Blocker), Multi-Source Workspace Grounding, Zero-Trust User ACLs | ✅ Complete |
| [**Cloud Run IAP Zero-Trust MCP**](./security-and-governance/cloudrun-iap-zero-trust-mcp) | **Cloud Run, Identity-Aware Proxy (IAP), FastMCP, OIDC Token Impersonation, VPC Ingress** | Zero-Trust Defense-in-Depth for MCP Tool Servers, Audience Validation, Network Ingress Hardening | ✅ Complete |
| [**Agent Identity Workload Federation**](./security-and-governance/agent-identity-workload-federation) | **Vertex AI Agent Runtime, BigQuery, Agent Identity, Gemini 2.5 Flash** | Autonomous SQL Data Warehouse Analytics, Zero-Trust Agent Principal Isolation | ✅ Complete |

---

### 🤖 2. Multi-Agent Systems & Tooling (`multi-agent-systems/`)
Decoupled multi-agent orchestration, remote MCP integrations, and Human-in-the-Loop approval gates.

| Module | Core Technologies | Architecture Pattern | Status |
| :--- | :--- | :--- | :---: |
| [**ADK MCP Cloud Run Orchestration**](./multi-agent-systems/adk-mcp-cloudrun-orchestration) | **Google ADK, Model Context Protocol (MCP), Cloud Run, Vertex AI** | Decoupled Reasoning & Tooling Layer, Multi-Agent Sequential Orchestration, Zero-Trust IAM ID Tokens | ✅ Complete |
| [**Cloud Run Remote MCP with HITL**](./multi-agent-systems/cloudrun-remote-mcp-hitl) | **Google ADK, Google Remote Cloud Run MCP, Gemini 3.5 Flash, HITL Safety Guardrails** | Autonomous Cloud Infrastructure Management, Dynamic Tool Interception, Human-in-the-Loop Confirmation | 🔄 In Progress |
| [**Retail Paint Planner Sub-Agents**](./multi-agent-systems/retail-paint-planner-subagents) | **Google ADK, Vertex AI Search, Agent Runtime, Chainlit** | Multi-Agent Collaborative Architecture, AgentTool Search Isolation, Session State Persistence | ✅ Complete |
| [**Enterprise Brand Voice Designer**](./multi-agent-systems/enterprise-brand-voice-designer) | **Gemini Enterprise, Agent Designer, ADK Agent Runtime, OAuth 2.0 Delegation** | Multi-Agent Enterprise Portal, Grounded Search & Declarative Brand Voice Microservices | ✅ Complete |

---

### 📊 3. Data Runtime, Analytics & Evaluations (`data-runtime-and-evals/`)
Zero-ETL data grounding, developer automation with Antigravity, and deterministic agent evaluation guardrails.

| Module | Core Technologies | Architecture Pattern | Status |
| :--- | :--- | :--- | :---: |
| [**BigQuery Agent Trajectory Evals & Guardrails**](./data-runtime-and-evals/bigquery-agent-eval-guardrails) | **Google ADK, BigQuery, Gemini 3.5 Flash, Trajectory Evals** | Automated Agent Evaluation, Deterministic State Machine Guardrails, Zero Data Loss | ✅ Complete |
| [**BigQuery MCP Enterprise Analytics**](./data-runtime-and-evals/bigquery-mcp-enterprise-analytics) | **Gemini Enterprise, BigQuery, MCP StreamableHTTP, OAuth 2.0 Delegation** | Zero-ETL Data Warehouse Grounding, Dynamic Action Discovery, User-Delegated Analytics | ✅ Complete |
| [**Antigravity MCP Logistics Runtime**](./data-runtime-and-evals/antigravity-mcp-logistics-runtime) | **Antigravity CLI (agy), MCP, FastMCP, Google Agents CLI, Agent Runtime** | Declarative Workspace Rules, Custom Skills, Logistics Triage Microservice | ✅ Complete |

---

## 🎯 Architectural Standards Applied
1. **Decoupled Tooling**: Strict adherence to the Model Context Protocol (MCP) to avoid monolithic agent anti-patterns.
2. **Zero-Trust Cloud IAM**: All service-to-service calls authenticated using short-lived OpenID Connect (OIDC) identity tokens.
3. **Search Tool Isolation**: Leveraging the `AgentTool` pattern to allow search engines to coexist with custom transactional and state tools.
4. **Deterministic Guardrails**: State machine boundaries implemented in Python rather than relying solely on probabilistic prompt instructions.
5. **Serverless Deployment**: Compute resources deployed to Google Cloud Run and Vertex AI Agent Runtime with true 0-to-N autoscaling.
6. **Reproducible Infrastructure**: Scripts, pinned dependencies, and comprehensive runbooks included with each module.
