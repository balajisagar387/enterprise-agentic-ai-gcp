# Lab Execution Notes & Troubleshooting Guide

> **Lab**: Develop an Agent to Interact with the Google Cloud Run Remote MCP Server  
> **Lab ID**: OCBL493  
> **Directory**: `GCP/cloud-run-remote-mcp-agent/`  
> **Target Project**: `qwiklabs-gcp-03-da45b2ebfd08` (Region: `us-west1`)  
> **Status**: Ready for Execution

---

## 📋 Task-by-Task Checkpoint Matrix

| Task | Objective | Key Actions & Commands | Status | Critical Notes / Gotchas |
| :---: | :--- | :--- | :---: | :--- |
| **1** | Environment Setup | Export env vars, create `crun_agent` directory, generate `.env`, `requirements.txt`, `__init.py__` | ⏳ Pending | Verify `.env` has correct model `gemini-3.5-flash` and `MCP_SERVER_URL` |
| **2** | Develop Agent & Roles | Create `agent.py`, activate venv, install requirements, create `crun-agent-sa` & assign 8 IAM roles | ⏳ Pending | Critical role: `roles/mcp.toolUser` is mandatory for invoking Google remote MCP server |
| **3** | Launch ADK Web | `adk web --allow_origins="*"` | ⏳ Pending | Opens local web interface on `http://127.0.0.1:8000` |
| **4** | Test Agent Prompts | List services, autonomously deploy `hello-test`, approve HITL confirmation | ⏳ Pending | Click **Confirmed** & **Submit** on `adk_request_confirmation` |
| **5** | Verify Private & Public | Curl `hello-test` with Bearer ID token (200), instruct agent to remove auth & redeploy | ⏳ Pending | Verify web page renders in browser |

---

## 🛠️ Step-by-Step Command Playbook

### Step 1: Initialize Cloud Shell & Environment Variables
```bash
sudo apt-get update && sudo apt-get --only-upgrade install google-cloud-cli -y

export PROJECT_ID=qwiklabs-gcp-03-da45b2ebfd08
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export REGION=us-west1
export AGENT_SA_NAME=crun-agent-sa
export AGENT_SA=${AGENT_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION
```

### Step 2: Create Python Project Configuration Files
```bash
mkdir -p ~/crun_agent && cd ~/crun_agent

cat <<EOF > .env
MODEL="gemini-3.5-flash"
MCP_SERVER_URL="https://run.googleapis.com/mcp"
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
PROJECT_NUMBER=$PROJECT_NUMBER
GOOGLE_CLOUD_LOCATION=global
GOOGLE_APPLICATION_CREDENTIALS=$HOME/crun_agent/${AGENT_SA_NAME}-key.json
EOF

cat <<EOF > requirements.txt
google-adk
mcp>=1.24,<2
google-auth
requests
google-cloud-logging
python-dotenv
EOF

cat <<EOF > __init.py__
from .agent import root_agent
__all__ = ["root_agent"]
EOF
```

### Step 3: Populate `agent.py` & Install Virtual Environment
```bash
# Verify or edit agent.py in ~/crun_agent/agent.py
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Provision Service Account & Assign Governance Roles
```bash
gcloud iam service-accounts create $AGENT_SA_NAME --display-name="MCP Agent Service Account"

for role in \
  roles/aiplatform.user \
  roles/run.invoker \
  roles/run.developer \
  roles/iam.serviceAccountUser \
  roles/iam.serviceAccountTokenCreator \
  roles/logging.logWriter \
  roles/artifactregistry.reader \
  roles/mcp.toolUser \
; do \
  gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$AGENT_SA" --role="$role" \
  --quiet; \
done

# Create Service Account key matching GOOGLE_APPLICATION_CREDENTIALS path
gcloud iam service-accounts keys create ${AGENT_SA_NAME}-key.json --iam-account=$AGENT_SA
```

### Step 5: Start ADK Web Interface
```bash
cd ~
adk web --allow_origins="*"
```
*Click the `http://127.0.0.1:8000` link in Cloud Shell (or Web Preview on port 8000).*

---

## 💬 ADK Web Conversational Prompts & Execution Guide

In the ADK Web UI, select **`crun_agent`** from the agent dropdown.

### Prompt 1: Initial Discovery
```text
List the services in project qwiklabs-gcp-03-da45b2ebfd08 and region us-west1.
```
> *Tip: If an error or timeout occurs on the first prompt, wait 10–20 seconds for IAM credentials to propagate and re-submit.*

### Prompt 2: Autonomous Service Deployment
```text
Deploy a private Cloud Run service named hello-test from the Docker image us-docker.pkg.dev/cloudrun/container/hello to project qwiklabs-gcp-03-da45b2ebfd08 to the us-west1 region.
```
> **Human-in-the-Loop Action**: The agent will pause and show an `adk_request_confirmation` dialog. Select **Confirmed** and click **Submit**.

### Prompt 3: Verification
```text
Which Cloud Run services are deployed in project qwiklabs-gcp-03-da45b2ebfd08 and in the us-west1 region ?
```
```text
Get the details of the hello-test service.
```

### Prompt 4: Testing Private Access via Terminal
In Cloud Shell (new terminal tab `+`):
```bash
HELLO_TEST_URL=$(gcloud run services describe hello-test --region=us-west1 --format="value(status.url)")
echo "HELLO_TEST_URL=$HELLO_TEST_URL"

# Calling directly via browser returns 403 Forbidden.
# Calling with Bearer Identity token returns 200 OK:
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" $HELLO_TEST_URL
```

### Prompt 5: Autonomous Re-deployment with Public Access
Return to the ADK UI and prompt:
```text
Update the hello-test service in the project qwiklabs-gcp-03-da45b2ebfd08 and region us-west1 to disable authentication and redeploy the service.
```
> **Human-in-the-Loop Action**: Confirm the `adk_request_confirmation` prompt. Once updated, open the Service URL directly in your browser without credentials!

---

## 🚨 Known Pitfalls & Solutions

### Pitfall 1: `Could not get OAuth access token`
- **Cause**: `GOOGLE_APPLICATION_CREDENTIALS` path in `.env` does not point to the generated `${AGENT_SA_NAME}-key.json`.
- **Fix**: Verify file exists: `ls -la ~/crun_agent/crun-agent-sa-key.json`.

### Pitfall 2: `Permission Denied` invoking remote MCP tools
- **Cause**: Missing `roles/mcp.toolUser` or `roles/run.developer` on the service account.
- **Fix**: Re-run the IAM binding loop from Step 4.

### Pitfall 3: ADK UI shows blank or CORS error
- **Cause**: Starting `adk web` without `--allow_origins="*"`.
- **Fix**: Ensure the command is executed with `adk web --allow_origins="*"`.

### Pitfall 4: `FAILED_PRECONDITION: Organization Policy constraint constraints/vertexai.allowedModels violated ... attempting to use a disallowed Gen AI model gemini-3.5-flash`
- **Cause**: The lab manual contained a typo specifying `MODEL="gemini-3.5-flash"`. The Qwiklabs Google Cloud organization policy strictly allows verified models.
  
  ![Vertex AI Allowed Model](./assets/screenshots/vertex_allowed_model_gemini_3_8_flash.png)

- **Verification Command (Discovers Inherited Allowed Models)**:
  Run this command to inspect the exact effective list of allowed Gen AI models inherited from the parent organization:
  ```bash
  gcloud org-policies describe constraints/vertexai.allowedModels --project=$PROJECT_ID --effective
  ```

- **Fix**: Update `MODEL` in `~/crun_agent/.env` to the whitelisted model found in the effective policy (e.g. `gemini-3.8-flash` or `gemini-2.0-flash`):
  ```bash
  sed -i 's/MODEL=.*/MODEL="gemini-3.8-flash"/' ~/crun_agent/.env
  ```
  *(Alternative fallback: `MODEL="gemini-2.0-flash"`)*.
  
  Then restart the ADK web server:
  ```bash
  cd ~
  adk web --allow_origins="*"
  ```
  and re-run the prompt in the ADK Web UI!

### Pitfall 5: `ModuleNotFoundError: Fail to load 'crun_agent.agent' module. No module named 'mcp'`
- **Cause**: `adk web` was started without the Python virtual environment activated (`.venv`), causing it to run on global system Python where `mcp` is not installed.
- **Fix**: Either activate the virtual environment or install dependencies with `--user`:
  ```bash
  pip3 install -r ~/crun_agent/requirements.txt --user
  ```
  Or activate the environment:
  ```bash
  source ~/crun_agent/.venv/bin/activate
  ```
  Then restart `adk web --allow_origins="*"`!
