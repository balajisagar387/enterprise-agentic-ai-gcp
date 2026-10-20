# Lab Execution Notes & Troubleshooting Guide

> **Project**: Deploying an ADK Agent Service with Remote MCP Server to Google Cloud Run  
> **Directory**: `GCP/01-adk-mcp-cloudrun-agent/`  
> **Target Audience**: Client Reviewers & Engineering Team  
> **Status**: Completed Reference

---

## 📋 Cloud Shell Execution Checklist

| Step | Lab Task | Command / Action | Status | Notes / Gotchas |
| :---: | :--- | :--- | :---: | :--- |
| **1** | Enable APIs | `gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com compute.googleapis.com` | Verified | Required before deploying or compiling containers. |
| **2** | Install ADK | `pip3 install -r requirements.txt --user` | Verified | Ensure `~/.local/bin` is added to `$PATH`. |
| **3** | Set Environment | Export `PROJECT_ID`, `REGION`, `PROJECT_NUMBER`, `SERVICE_ACCOUNT` | Verified | If Cloud Shell reconnects or times out, re-run exports. |
| **4** | IAM Roles Binding | `roles/run.invoker` & `roles/aiplatform.user` | Verified | IAM propagation can take 15–30 seconds. |
| **5** | ADK Deploy | `adk deploy cloud_run --project=$PROJECT_ID --region=$REGION --service_name=zoo-tour-guide --with_ui .` | Verified | Takes ~5–10 mins to build image and deploy. |
| **6** | Env Var Update | `gcloud run services update zoo-tour-guide --set-env-vars=...` | Verified | Needed to inject `MODEL` and `MCP_SERVER_URL`. |
| **7** | Verification | Open Cloud Run Service URL & test prompts | Verified | Enable Token Streaming in top right corner. |
| **8** | Cleanup | Delete Cloud Run service & Artifact Registry repo | Verified | Avoids lab billing leakage. |

---

## 🛠️ Known Pitfalls & Solutions

### Issue 1: `adk: command not found` after pip install
- **Symptoms**: Running `adk deploy cloud_run` returns `bash: adk: command not found`.
- **Root Cause**: The Python user binary directory (`~/.local/bin`) was not added to the current shell `$PATH`.
- **Solution**:
  ```bash
  export PATH=$PATH:~/.local/bin
  which adk
  ```

---

### Issue 2: Cloud Shell Reconnection resets environment variables
- **Symptoms**: Commands using `$PROJECT_ID`, `$REGION`, or `$SERVICE_ACCOUNT` fail with blank arguments or `NoneType` errors.
- **Root Cause**: Cloud Shell opened a new subshell or refreshed connection, losing non-persistent in-memory exports.
- **Solution**:
  Re-export the variables in one block:
  ```bash
  export PROJECT_ID=$(gcloud config get-value project)
  export REGION=$(gcloud compute project-info describe --format="value(commonInstanceMetadata.items[google-compute-default-region])")
  export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
  export SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  source .env
  ```

---

### Issue 3: Permission Denied (`403 Forbidden`) calling MCP Server
- **Symptoms**: Agent fails during query with an error indicating an inability to contact `https://zoo-mcp-server-...run.app/mcp/`.
- **Root Cause**: Missing `roles/run.invoker` binding for the default compute service account, or incorrect Audience in `fetch_id_token`.
- **Solution**:
  1. Verify the audience strip logic:
     ```python
     audience = target_url.split('/mcp/')[0]
     ```
     The token must be minted for the base Cloud Run root URL (`https://zoo-mcp-server-...run.app`), not the subpath `/mcp/`.
  2. Verify IAM role binding:
     ```bash
     gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:$SERVICE_ACCOUNT" \
       --role="roles/run.invoker"
     ```

---

### Issue 4: Vertex AI Model Invocation Error (`aiplatform.user` missing)
- **Symptoms**: Error message: `GoogleAPICallError: 403 Permission 'aiplatform.endpoints.predict' denied on resource...`
- **Root Cause**: Service account lacks the Agent Platform / Vertex AI permissions.
- **Solution**:
  ```bash
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/aiplatform.user"
  ```
