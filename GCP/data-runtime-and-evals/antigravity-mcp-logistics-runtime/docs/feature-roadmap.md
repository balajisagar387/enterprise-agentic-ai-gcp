# Feature Roadmap & Enhancement Suggestions

> **Module**: Cymbal Direct Winter Storm Triage Agent  
> **Lab Reference**: GENAI144 - Accelerate Development with Antigravity  
> **Status**: Post-MVP — Production Enhancement Planning  

---

## 🗺️ Current Architecture (MVP Baseline)

```
Antigravity CLI → MCP (3 tools) → Agent Runtime (us-west1)
                   get_order_status
                   get_customer_loyalty_info
                   issue_disruption_compensation
```

The current agent handles a **single disruption type** (winter storm) for **manually queried orders** via a **playground chat interface**. The roadmap below evolves this into a fully autonomous, enterprise-grade logistics intelligence platform.

---

## 🚀 Feature Roadmap (Prioritized)

---

### 🟥 Priority 1 — Proactive Disruption Intelligence (High Impact)

#### 1.1 Real-Time Weather Event Feed Integration
**Problem**: The current agent is **reactive** — a customer must reach out first.  
**Solution**: Connect to a live weather API (e.g., NOAA, Tomorrow.io, or Google Maps Weather API) as an additional MCP tool. When a storm is detected at a transit hub, the agent proactively scans all `DELAYED` orders in the affected zip code radius and **automatically issues compensation without waiting for customer contact**.

```python
@mcp.tool()
def get_active_weather_disruptions(region: str) -> dict:
    """Returns active NOAA storm warnings by transit region."""
    ...

@mcp.tool()
def get_orders_in_affected_region(zip_codes: list[str]) -> list:
    """Returns all DELAYED orders in the affected zip code cluster."""
    ...
```

**Business Impact**: Reduces inbound support volume by ~70% during weather events.

---

#### 1.2 Automated Email & SMS Notification
**Problem**: The agent only **drafts** a response — it doesn't actually **send** it.  
**Solution**: Add a `send_customer_notification` MCP tool backed by **SendGrid (Email)** and **Twilio (SMS)**.

```python
@mcp.tool()
def send_customer_notification(
    customer_id: str,
    email: str,
    phone: str,
    channel: str,  # "email" | "sms" | "both"
    message: str
) -> dict:
    """Dispatches resolution notification via email or SMS."""
    ...
```

**Business Impact**: Completes the full resolution loop autonomously — zero human intervention.

---

### 🟧 Priority 2 — Multi-Disruption Type Coverage

#### 2.1 Additional Disruption Type Skills

| Skill Name | Trigger Condition | Unique Compensation Rule |
| :--- | :--- | :--- |
| `hurricane-triage` | Active hurricane zones (FEMA alerts) | 2x standard credit + free reship |
| `port-strike-triage` | Union strike flags on international orders | Refund + domestic substitute offer |
| `flood-damage-triage` | Package confirmed damaged in transit | Full refund + replacement order |
| `carrier-lost-triage` | Status stuck in `LOST` for 72h+ | Full refund + loyalty tier upgrade |

Each skill lives at `.agents/skills/<skill-name>/SKILL.md` following the established workspace rules.

---

#### 2.2 Dynamic Disruption Classifier
**Problem**: Currently the skill is invoked manually (`/winter-storm-triage`).  
**Solution**: Add an intent routing agent that reads the order status and auto-selects the correct triage skill.

```python
@mcp.tool()
def classify_disruption_type(order_id: str) -> dict:
    """Returns the disruption type and recommended triage skill."""
    # Returns: {"disruption_type": "WINTER_STORM", "recommended_skill": "winter-storm-triage"}
    ...
```

---

### 🟨 Priority 3 — Operational Intelligence & Analytics

#### 3.1 BigQuery Integration for Disruption Analytics
Log every compensation event to **BigQuery** and use **Gemini Enterprise** for natural-language analytics:

```python
@mcp.tool()
def log_disruption_event(
    order_id: str,
    customer_id: str,
    disruption_type: str,
    compensation_amount: float,
    loyalty_tier: str,
    region: str
) -> dict:
    """Writes disruption event to BigQuery analytics table."""
    ...
```

**Sample NL Queries**:
- `"How much total compensation did we issue in Q4 2026 due to weather events?"`
- `"Which transit hubs had the highest disruption rate this month?"`

---

#### 3.2 Compensation Budget Guardrails
Add a budget threshold check before issuing compensation. If daily cap is exceeded, escalate to a human supervisor.

```python
@mcp.tool()
def check_compensation_budget_remaining(cost_center: str, date: str) -> dict:
    """Returns remaining daily compensation budget for a cost center."""
    ...
```

---

### 🟦 Priority 4 — Enterprise Security & Compliance

#### 4.1 Agent Identity + Least-Privilege IAM (From Module 06)
Apply `types.IdentityType.AGENT_IDENTITY` to provision a cryptographically isolated Agent Principal, removing dependency on the default compute service account.

#### 4.2 Model Armor Input/Output Guardrails (From Module 03)
- **Input firewall**: Detect prompt injection attacks from malicious customer inputs.
- **Output firewall**: Redact PII (SSN, credit card numbers) accidentally included in logistics records.

#### 4.3 Audit Trail via Cloud Logging
Every tool call emits a structured log entry to **Cloud Logging**:
- Timestamp, Agent Principal ID, customer ID, order ID, compensation amount
- Satisfies SOC 2, PCI-DSS, and GDPR audit requirements.

---

### 🟩 Priority 5 — Multi-Channel Deployment

#### 5.1 Gemini Enterprise Chat Integration (From Module 07)
Register the Agent Runtime endpoint as a **Custom Agent via Agent Runtime** inside Cymbal Direct's Gemini Enterprise hub for internal staff access.

#### 5.2 Customer Portal Webhook via Cloud Run
Deploy a Cloud Run webhook that triggers triage automatically when a customer submits an inquiry form:

```python
@app.post("/triage")
async def triage_order(order_id: str, customer_email: str):
    """Triggered by customer portal on order inquiry submission."""
    response = await agent_runtime_client.query(prompt=f"Triage order {order_id}")
    await send_email(customer_email, response)
    return {"status": "resolved"}
```

#### 5.3 Multi-Language Response Support
Add a post-processing step translating the customer response using **Gemini's multilingual generation** or **Cloud Translation API**.

---

## 📊 Development Priority Matrix

| Feature | Business Impact | Dev Effort | Priority |
| :--- | :---: | :---: | :---: |
| Proactive weather feed integration | ⭐⭐⭐⭐⭐ | Medium | 🟥 P1 |
| Automated email/SMS notification | ⭐⭐⭐⭐⭐ | Low | 🟥 P1 |
| Additional disruption type skills | ⭐⭐⭐⭐ | Low | 🟧 P2 |
| Dynamic disruption classifier | ⭐⭐⭐⭐ | Medium | 🟧 P2 |
| BigQuery disruption analytics | ⭐⭐⭐⭐ | Medium | 🟨 P3 |
| Compensation budget guardrails | ⭐⭐⭐ | Low | 🟨 P3 |
| Agent Identity + Model Armor | ⭐⭐⭐⭐⭐ | Low | 🟦 P4 |
| Audit trail via Cloud Logging | ⭐⭐⭐⭐ | Low | 🟦 P4 |
| Gemini Enterprise integration | ⭐⭐⭐ | Low | 🟩 P5 |
| Customer portal webhook | ⭐⭐⭐⭐ | High | 🟩 P5 |
| Multi-language response support | ⭐⭐⭐ | Low | 🟩 P5 |

---

## 🔗 Cross-Module Portfolio Synergies

| Integration | Source Module | Enhancement |
| :--- | :--- | :--- |
| BigQuery analytics reporting | [Agent Identity Federation](../../security-and-governance/agent-identity-workload-federation/) | Disruption event logging & NL analytics |
| Gemini Enterprise portal access | [Enterprise Brand Voice Designer](../../multi-agent-systems/enterprise-brand-voice-designer/) | Internal staff agent chat interface |
| Model Armor security layer | [Model Armor LLM Firewall](../../security-and-governance/model-armor-llm-firewall/) | Input/output PII & jailbreak protection |
| IAP-secured MCP toolserver | [Cloud Run IAP Zero-Trust MCP](../../security-and-governance/cloudrun-iap-zero-trust-mcp/) | Production-grade MCP hosting with zero-trust |
