# 06. BigQuery-Enabled Agent on Agent Runtime with Agent Identity

[![Vertex AI Reasoning Engine](https://img.shields.io/badge/Runtime-Vertex%20AI%20Agent%20Runtime-4285F4?logo=google-cloud)](https://cloud.google.com/vertex-ai)
[![BigQuery](https://img.shields.io/badge/Data%20Warehouse-Google%20BigQuery-669DF6?logo=google-cloud)](https://cloud.google.com/bigquery)
[![Agent Identity](https://img.shields.io/badge/Security-Dedicated%20Agent%20Identity-34A853?logo=google-cloud)]()
[![Gemini 2.5 Flash](https://img.shields.io/badge/Model-Gemini%202.5%20Flash-orange)]()

> **Enterprise Financial Intelligence Reference Architecture**: Production implementation of an autonomous SQL-enabled AI agent deployed to **Vertex AI Agent Runtime (Reasoning Engine)** utilizing cryptographically isolated **Agent Identity** to securely query enterprise supplier invoices stored in **Google BigQuery**.

---

## 📌 Executive Summary & Business Scenario

### The Business Challenge: Cymbal Pools Supplier Operations
Cymbal Pools, a national provider of commercial and residential pool services, processes thousands of supplier invoices across regional distribution centers. Finance teams face delays tracking payment statuses, identifying unapproved invoices, and projecting 30-day cash flow requirements.

### The Solution
Instead of providing users with raw database access or building brittle custom dashboards:
1. A domain-specific **BigQuery Invoice Agent** is deployed to managed **Agent Runtime**.
2. **Dedicated Agent Identity (`types.IdentityType.AGENT_IDENTITY`)** provisions a unique principal identifier (`principal://agents.global.org-...`), enforcing absolute zero-trust isolation from developer credentials and compute engines.
3. Natural language questions are translated into optimized BigQuery SQL, executed under strict IAM controls (`roles/bigquery.dataEditor`, `roles/bigquery.user`).

---

## 🏛️ Architecture Overview

```mermaid
flowchart LR
    User(["Finance Analyst"]) <--> Playground["Deployments Playground\n(Agent Platform Web UI)"]
    Playground <--> Runtime["Vertex AI Agent Runtime\n(BigQuery Invoice Agent)"]
    Runtime -- "Agent Identity" --> IAM["Cloud IAM Role Bindings\n(Data Editor & User)"]
    IAM --> BQ[("BigQuery Invoices Table\n(Cymbal Pools DWH)")]
```

---

## 📸 Verification & Validation Artifacts

### 1. BigQuery Autonomous SQL Execution in Agent Runtime
The agent autonomously inspected the Cymbal Pools invoices dataset, generated standard SQL, and executed query jobs authenticated under its dedicated Agent Principal identity:

![Playground SQL Execution Success](./assets/01-playground-sql-execution-success.png)

### 2. Conversational Financial Intelligence Output
The agent synthesized monthly invoice totals ($7,672.85 for April 2026) and identified all outstanding unpaid supplier invoices:

![Playground Invoice Synthesis Output](./assets/02-playground-invoice-synthesis-output.png)

---

## 📂 Directory Layout

```
06-agent-runtime-bigquery-identity/
├── README.md                                  # Executive summary and architecture overview
├── lab_notes.md                               # Step-by-step reproduction playbook & query matrix
├── docs/
│   └── architecture.md                        # Deep dive on Agent Identity vs traditional Service Accounts
└── bigquery_agent_installer/
    ├── requirements.txt                       # Runtime and client dependencies
    ├── deploy.py                              # Deployment automation using Agent Identity
    └── bigquery_agent/
        ├── __init__.py
        ├── .env.example                       # Environment configuration template
        └── agent.py                           # ADK Agent definition with BigQuery toolset
```

---

## 🚀 Quickstart & Reproduction

Refer to the complete runbook in [`lab_notes.md`](./lab_notes.md) for full commands, IAM bindings, and validation queries.
