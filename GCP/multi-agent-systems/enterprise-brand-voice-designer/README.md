# 07. Multi-Agent Ecosystem in Gemini Enterprise: Agent Designer & ADK Agent Runtime

[![Gemini Enterprise](https://img.shields.io/badge/Platform-Gemini%20Enterprise-orange?logo=google)](https://cloud.google.com/gemini)
[![Google ADK](https://img.shields.io/badge/Agent-Google%20ADK%20Config%20YAML-blue?logo=google)](https://google.github.io/adk-docs/)
[![Vertex AI Reasoning Engine](https://img.shields.io/badge/Runtime-Vertex%20AI%20Agent%20Runtime-4285F4?logo=google-cloud)](https://cloud.google.com/vertex-ai)
[![OAuth 2.0 Delegation](https://img.shields.io/badge/Security-OAuth%202.0%20User%20Delegation-34A853?logo=google-cloud)]()

> **Enterprise GenAI Reference Architecture**: Unified enterprise agent hub on **Gemini Enterprise** integrating **No-Code Agent Designer** agents with declarative **ADK Agent Runtime** microservices secured via **3-legged OAuth 2.0 user delegation**.

---

## 📌 Executive Summary & Business Scenario

### The Business Challenge: Cymbal Pools Omnichannel Brand Voice
Cymbal Pools manages hundreds of service technicians, pool maintenance staff, and customer support representatives across the United States. To build brand loyalty, corporate communications requires:
1. Transforming dry, technical service tickets (e.g., equipment delivery, maintenance alerts) into Cymbal Pools' signature **laid-back, surfer-dude brand voice**.
2. Providing operations managers with an instant intelligence tool to research new market innovations in commercial pool robotics grounded in live web data.
3. Centralizing all agent workflows inside a unified enterprise portal (**Gemini Enterprise**) governed by corporate identity and OAuth 2.0 user delegation.

---

## 🏛️ Architecture Overview

```mermaid
flowchart TD
    User(["Enterprise Operator"]) <--> Hub["Gemini Enterprise Hub (Cymbal Pools GE)"]
    
    subgraph HubServices["Integrated Agent Modalities"]
        DesignerAgent["Agent Designer: Pool Robot Analyst\n(Google Search Grounding)"]
        CustomADK["Custom ADK Agent: Brand Voice Agent\n(OAuth 2.0 Authorization)"]
    end

    Hub --> DesignerAgent
    Hub --> CustomADK

    subgraph Backend["Cloud Infrastructure"]
        OAuth["OAuth 2.0 Consent & Web Client\n(https://vertexaisearch.../oauth.html)"]
        Runtime["Vertex AI Agent Runtime (us-east4)\n(Cymbal Pools Brand Voice - Gemini 3.5 Flash)"]
    end

    CustomADK -- "User Token Exchange" --> OAuth
    OAuth --> Runtime
```

---

## 📸 Verification & Validation Artifacts

### 1. Conversational Chat in Gemini Enterprise (Surfer-Dude Brand Voice)
The agent autonomously converted maintenance alerts and customer messaging into the Cymbal Pools laid-back surfer-dude persona with pool puns and hydration reminders:

![Gemini Enterprise Brand Voice Chat](./assets/01-gemini-enterprise-brand-voice-chat.png)

---

## 📂 Directory Layout

```
GCP/multi-agent-systems/enterprise-brand-voice-designer/
├── README.md                                  # Executive summary & system architecture
├── docs/
│   └── architecture.md                        # Deep dive into OAuth delegation & Agent Designer vs ADK
└── adk_brand_agent/
    ├── requirements.txt                       # Runtime dependencies
    ├── construct_auth_uri.py                  # OAuth 2.0 authorization URL builder
    └── brand_voice/
        ├── .env.example                       # Environment configuration template
        └── root_agent.yaml                    # Declarative ADK Agent Config YAML
```

---

## 🚀 Architecture & Verification

Refer to [`docs/architecture.md`](./docs/architecture.md) for full commands, OAuth flow breakdown, and validation prompts.
