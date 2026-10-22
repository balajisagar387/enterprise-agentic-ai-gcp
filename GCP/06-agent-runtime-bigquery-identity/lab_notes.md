# Lab Execution Notes & Verification Runbook

> **Lab**: Deploy a BigQuery-enabled agent to Agent Runtime with Agent Identity  
> **Lab ID**: GENAI160  
> **Client / Case**: Cymbal Pools Supplier Invoice Intelligence  
> **Target Project**: `qwiklabs-gcp-01-67ce6f14529a` (Region: `us-central1`)  
> **Target Score**: 100%  

---

## 📋 Task-by-Task Execution Checkpoint Matrix

| Task | Objective | Key Commands / Actions | Target Status | Critical Gotchas / Tips |
| :---: | :--- | :--- | :---: | :--- |
| **1** | Environment Setup | Copy bucket assets, export PATH, install requirements, write `.env` | ✅ Verified | Ensure `.env` has `MODEL=gemini-2.5-flash` and `GOOGLE_GENAI_USE_VERTEXAI=TRUE` |
| **2** | Deploy to Agent Runtime | Set `IDENTITY_TYPE=types.IdentityType.AGENT_IDENTITY`, run `python3 deploy.py` | ✅ Verified | Takes 5–10 mins; verify status in Agent Platform > Deployments |
| **3** | IAM Role Assignment | Copy Agent Principal ID, bind `roles/bigquery.dataEditor` & `roles/bigquery.user` | ✅ Verified | Do NOT edit principalSet; bind directly to agent `principal://...` |
| **4** | Playground Verification | Execute 3 natural language queries in Deployments Playground | ✅ Verified | Verify schema output, calculate April 2026 totals ($7,672.85), count 6 unpaid invoices |

---

## 🛠️ Step-by-Step Command Playbook

### Step 1: Enable APIs & Set Up Environment (Cloud Shell)
```bash
# 1. Download installer assets
gcloud storage cp -r gs://qwiklabs-gcp-01-67ce6f14529a-bucket/bigquery_agent_installer .

# 2. Update PATH and install dependencies
export PATH=$PATH:"/home/${USER}/.local/bin"
python3 -m pip install -r bigquery_agent_installer/requirements.txt
gcloud config set project qwiklabs-gcp-01-67ce6f14529a

# 3. Create agent .env configuration
cd ~/bigquery_agent_installer
cat << EOF > bigquery_agent/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-01-67ce6f14529a
GOOGLE_CLOUD_LOCATION=global
MODEL=gemini-2.5-flash
EOF
```

---

### Step 2: Configure & Execute `deploy.py`
In `~/bigquery_agent_installer/deploy.py`, ensure the following parameters are populated:
```python
AGENT_NAME = "BigQuery Invoice Agent"
STAGING_BUCKET_NAME = "gs://qwiklabs-gcp-01-67ce6f14529a-bucket"
MODEL_VERSION = "gemini-2.5-flash"
PROJECT_ID = "qwiklabs-gcp-01-67ce6f14529a"
REGION = "us-central1"
IDENTITY_TYPE = types.IdentityType.AGENT_IDENTITY
```

Run deployment:
```bash
python3 deploy.py
```
*Wait for output confirming Reasoning Engine creation (typically 5–8 minutes).*  
*Click **Check my progress** for Task 2.*

---

### Step 3: Grant IAM Roles to Agent Identity

1. In Google Cloud Console, navigate to **Agent Platform > Agents > Deployments**.
2. Click **BigQuery Invoice Agent**.
3. Copy the **Agent Principal** string:
   `principal://agents.global.org-ORG_ID.system.id.goog/resources/aiplatform/projects/PROJECT_NUMBER/locations/us-central1/reasoningEngines/REASONING_ENGINE_ID`
4. Grant roles in Cloud Shell or via IAM Console:

```bash
export AGENT_PRINCIPAL="<PASTE_AGENT_PRINCIPAL_HERE>"

gcloud projects add-iam-policy-binding qwiklabs-gcp-01-67ce6f14529a \
    --member="$AGENT_PRINCIPAL" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding qwiklabs-gcp-01-67ce6f14529a \
    --member="$AGENT_PRINCIPAL" \
    --role="roles/bigquery.user"
```

*Click **Check my progress** for Task 3.*

---

### Step 4: Validate in Deployments Playground

In **Agent Platform > Agents > Deployments > BigQuery Invoice Agent > Playground**:

#### Query 1: Table Schema
```text
What is the schema of the invoice table?
```
**Expected Output:**
- `invoice_date (DATE)`
- `date_processed (DATE)`
- `invoice_id (STRING)`
- `vendor_name (STRING)`
- `invoice_total (FLOAT)`
- `payment_status (STRING)`

#### Query 2: Aggregate & Filter Unpaid
```text
What was the total sum of the invoice totals that arrived in April 2026? What invoices are not paid?
```
**Expected Output:**
- Total sum for April 2026: **$7,672.85**
- Unpaid invoices listed: `INV-1006`, `INV-1012`, `INV-1008`, `INV-1014`, `INV-1010`, `INV-1004`

#### Query 3: Count Unpaid
```text
What is the total number of unpaid invoices we currently have?
```
**Expected Output:**
- Currently have **6** unpaid invoices.

*Click **Check my progress** for Task 4 to achieve 100%.*
