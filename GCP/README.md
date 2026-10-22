# Google Cloud Platform (GCP) Enterprise AI & Agentic Solutions Portfolio

This directory contains enterprise-grade reference architectures, proof-of-concepts, and deployable implementations built on **Google Cloud Platform (GCP)**, **Vertex AI**, and modern agentic frameworks.

---

## 📂 Implementations & Modules

| Module | Core Technologies | Architecture Pattern | Status |
| :--- | :--- | :--- | :---: |
| [**01-adk-mcp-cloudrun-agent**](./01-adk-mcp-cloudrun-agent) | **Google ADK, Model Context Protocol (MCP), Cloud Run, Vertex AI** | Decoupled Reasoning & Tooling Layer, Multi-Agent Sequential Orchestration, Zero-Trust IAM ID Tokens | ✅ Completed |
| [**02-gemini-enterprise-bigquery-mcp-datastore**](./02-gemini-enterprise-bigquery-mcp-datastore) | **Gemini Enterprise, BigQuery, MCP StreamableHTTP, OAuth 2.0 Delegation** | Zero-ETL Data Warehouse Grounding, Dynamic Action Discovery, User-Delegated Analytics | ✅ Completed |
| [**03-gemini-enterprise-workspace-model-armor**](./03-gemini-enterprise-workspace-model-armor) | **Gemini Enterprise, Model Armor, Workspace RAG, OAuth 2.0, Gemini 3.1 Pro** | Bilateral AI Security Firewall (Prompt Injection / PII Blocker), Multi-Source Workspace Grounding, Zero-Trust User ACLs | ✅ Completed |
| [**secure-access-mcp-cloudrun-iap**](./secure-access-mcp-cloudrun-iap) | **Cloud Run, Identity-Aware Proxy (IAP), FastMCP, OIDC Token Impersonation, VPC Ingress** | Zero-Trust Defense-in-Depth for MCP Tool Servers, Audience Validation, Network Ingress Hardening | ✅ Completed |
| [**cloud-run-remote-mcp-agent**](./cloud-run-remote-mcp-agent) | **Google ADK, Google Remote Cloud Run MCP, Gemini 3.5 Flash, HITL Safety Guardrails** | Autonomous Cloud Infrastructure Management, Dynamic Tool Interception, Human-in-the-Loop Confirmation | 🔄 In Progress |
| [**06-agent-runtime-bigquery-identity**](./06-agent-runtime-bigquery-identity) | **Vertex AI Agent Runtime, BigQuery, Agent Identity, Gemini 2.5 Flash** | Autonomous SQL Data Warehouse Analytics, Zero-Trust Agent Principal Isolation | ✅ Completed |
| [**07-gemini-enterprise-agent-designer-adk**](./07-gemini-enterprise-agent-designer-adk) | **Gemini Enterprise, Agent Designer, ADK Agent Runtime, OAuth 2.0 Delegation** | Multi-Agent Enterprise Portal, Grounded Search & Declarative Brand Voice Microservices | ✅ Completed |
| [**08-antigravity-mcp-agent-runtime**](./08-antigravity-mcp-agent-runtime) | **Antigravity CLI (agy), MCP, FastMCP, Google Agents CLI, Agent Runtime** | Declarative Workspace Rules, Custom Skills, Logistics Triage Microservice | ✅ Completed |

---

## 🎯 Architectural Standards Applied
1. **Decoupled Tooling**: Strict adherence to the Model Context Protocol (MCP) to avoid monolithic agent anti-patterns.
2. **Zero-Trust Cloud IAM**: All service-to-service calls authenticated using short-lived OpenID Connect (OIDC) identity tokens.
3. **Serverless Deployment**: Compute resources deployed to Google Cloud Run with true 0-to-N autoscaling.
4. **Reproducible Infrastructure**: Scripts, pinned dependencies, and comprehensive runbooks included with each module.
