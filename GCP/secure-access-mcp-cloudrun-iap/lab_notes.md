# Lab Execution Notes & Troubleshooting Guide

> **Lab**: Secure Access to an MCP Server on Cloud Run with IAP  
> **Lab ID**: OCBL492  
> **Directory**: `GCP/secure-access-mcp-cloudrun-iap/`  
> **Target Service**: FastMCP Retail Products Server (`products-mcp-server`)  
> **Status**: Ready for Execution

---

## 📋 Task-by-Task Checkpoint Matrix

| Task | Objective | Key Commands & Actions | Status | Critical Notes / Gotchas |
| :---: | :--- | :--- | :---: | :--- |
| **1** | Environment Setup | Export `PROJECT_ID`, `REGION`, `ZONE`, `PROJECT_NUMBER`, `MCP_SERVER_NAME` | ⏳ Pending | Set default run region: `gcloud config set run/region $REGION` |
| **2** | Deploy MCP to Cloud Run | Download code, `uv add fastmcp==2.12.4`, deploy with `--no-allow-unauthenticated --iap` | ⏳ Pending | Grant `roles/run.invoker` to IAP service agent `service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com` |
| **3** | Implement IAP Config | Create OAuth Client (`MCP Products App`, Web app), configure IAP custom OAuth | ⏳ Pending | Create `mcp-test-sa` and grant `roles/iap.httpsResourceAccessor` |
| **4** | Test with OIDC Token | Mint OIDC token via impersonation (`--audiences="$IAP_AUDIENCE"`), test `tools/list` & `tools/call` | ⏳ Pending | Audience **must** equal the OAuth Client ID |
| **5** | Ingress Restriction | Set `--ingress internal`, verify Cloud Shell gets 404, SSH to `internal-vm` to verify access | ⏳ Pending | Use `gcloud compute ssh internal-vm --tunnel-through-iap` |

---

## 🛠️ Step-by-Step Command Playbook

### Step 1: Initialize Variables & Shell
```bash
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export REGION=$(gcloud compute project-info describe --format="value(commonInstanceMetadata.items[google-compute-default-region])")
export ZONE=$(gcloud compute project-info describe --format="value(commonInstanceMetadata.items[google-compute-default-zone])")
export MCP_SERVER_NAME=products-mcp-server

gcloud config set run/region $REGION
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### Step 2: Download Code & Deploy Cloud Run with IAP
```bash
gcloud storage cp gs://cloud-training/OCBL492/mcp-on-cloudrun.zip ~ && unzip ~/mcp-on-cloudrun.zip && rm -f ~/mcp-on-cloudrun.zip
cd ~/mcp-on-cloudrun

uv init --description "Custom MCP server on Cloud Run" --bare --python 3.13
uv add fastmcp==2.12.4 --no-sync

# Create runtime service account
gcloud iam service-accounts create mcp-server-sa --display-name="MCP Server Service Account"

# Deploy container directly from source with IAP and zero unauthenticated access
gcloud run deploy $MCP_SERVER_NAME \
  --service-account="mcp-server-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --no-allow-unauthenticated \
  --iap \
  --region=$REGION \
  --source=.

# Grant IAP Service Agent permission to invoke Cloud Run
gcloud run services add-iam-policy-binding $MCP_SERVER_NAME \
  --region=$REGION \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Step 3: Configure IAP Custom OAuth & Test Service Account
1. In Cloud Console: **APIs & Services > Credentials** $\rightarrow$ Create OAuth client ID (Web application named `MCP Products App`).
2. Copy **Client ID** and **Client Secret**.
3. Go to **Security > Identity-Aware Proxy** $\rightarrow$ Under Cloud Run Services, find `products-mcp-server` $\rightarrow$ Settings $\rightarrow$ Select **Custom OAuth** $\rightarrow$ Paste Client ID & Secret $\rightarrow$ Save.
4. Set up test identity:
```bash
export MCP_TEST_SA=mcp-test-sa
gcloud iam service-accounts create $MCP_TEST_SA --display-name="MCP TEST SA"

# Grant IAP access permission
gcloud iap web add-iam-policy-binding \
  --resource-type=cloud-run \
  --service=$MCP_SERVER_NAME \
  --region=$REGION \
  --member="serviceAccount:${MCP_TEST_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iap.httpsResourceAccessor"

# Allow your user to impersonate this service account
gcloud iam service-accounts add-iam-policy-binding \
  "${MCP_TEST_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --member="user:$(gcloud config get-value account)" \
  --role="roles/iam.serviceAccountTokenCreator"
```

### Step 4: Test Tool Invocation with Impersonated OIDC Token
```bash
export MCP_SERVER_URL=$(gcloud run services describe $MCP_SERVER_NAME --region=$REGION --format="value(status.url)")
export IAP_AUDIENCE="<YOUR_CLIENT_ID_HERE>"

# Generate token with audience matching IAP OAuth Client ID
TOKEN=$(gcloud auth print-identity-token \
  --impersonate-service-account="${MCP_TEST_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --audiences="$IAP_AUDIENCE" --include-email)

# 1. List tools
curl -X POST "${MCP_SERVER_URL}/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# 2. Call tool get_products_by_category
curl -sS -X POST "${MCP_SERVER_URL}/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_products_by_category", "arguments": {"category": "Tops"}}}' | sed -n 's/^data: //p' | jq .
```

### Step 5: Network Ingress Hardening & Internal VM Verification
```bash
# Block all external ingress
gcloud run services update $MCP_SERVER_NAME --ingress internal

# Verify external Cloud Shell receives HTTP 404 (Expected behavior)
curl -X POST "${MCP_SERVER_URL}/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# SSH into internal VPC VM through IAP tunnel
gcloud compute ssh internal-vm --tunnel-through-iap --zone=$ZONE
```
Inside the VM:
```bash
gcloud auth login
export IAP_AUDIENCE="<YOUR_CLIENT_ID_HERE>"
export MCP_SERVER_NAME=products-mcp-server
export REGION="<REGION>"
export MCP_TEST_SA=mcp-test-sa
export PROJECT_ID=$(gcloud config get-value project)

TOKEN=$(gcloud auth print-identity-token \
  --impersonate-service-account="${MCP_TEST_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --audiences="$IAP_AUDIENCE" --include-email)

export MCP_SERVER_URL=$(gcloud run services describe $MCP_SERVER_NAME --region=$REGION --format="value(status.url)")

# Call get_product_details
curl -sS -X POST "${MCP_SERVER_URL}/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_product_details", "arguments": {"name": "Heather Gray Hoodie"}}}' | sed -n 's/^data: //p' | jq .
```

---

## 🚨 Known Pitfalls & Solutions

### Pitfall 1: 401 Unauthorized or 403 Forbidden on curl
- **Root Cause**: The token audience does not match the OAuth Client ID configured in IAP, or the IAM binding hasn't propagated yet.
- **Fix**: Verify `echo $IAP_AUDIENCE` matches the exact Client ID. Wait 15–30 seconds for `roles/iap.httpsResourceAccessor` to propagate.

### Pitfall 2: Cloud Run Invoker Missing on IAP Service Agent
- **Symptom**: IAP displays `Error: Server Error - The server encountered a temporary error and could not complete your request.`
- **Fix**: Re-apply the binding:
  ```bash
  gcloud run services add-iam-policy-binding $MCP_SERVER_NAME \
    --region=$REGION \
    --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
  ```

---

## 📸 Verified Execution Evidence
*(Paste screenshots here once completed)*
