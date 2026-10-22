# Lab Execution Notes & Verification Runbook

> **Lab**: Add Agents to Gemini Enterprise  
> **Course**: Add Agents to Gemini Enterprise Learning Path  
> **Target Project**: `qwiklabs-gcp-03-2c267663a806` (Region: `us-east4`)  
> **Student Username**: `student-01-360fe82e7ba0@qwiklabs.net`  
> **Status**: Ready for 100% Score Execution  

---

## 📋 Task-by-Task Checkpoint Matrix

| Task | Objective | Key Actions & Commands | Status | Critical Tips & Notes |
| :---: | :--- | :--- | :---: | :--- |
| **1** | Environment Setup | Copy bucket code, export PATH, install requirements, configure project | ⏳ Pending | `adk_challenge_lab` downloaded into Cloud Shell home |
| **2** | Create & Deploy ADK Agent | `adk create --type=config ...`, edit `root_agent.yaml`, `adk deploy` | ⏳ Pending | Region: `us-east4`, Display Name: `Cymbal Pools Brand Voice` |
| **3** | OAuth Consent & Client | Create Internal consent screen, create Web App client with redirect URI | ⏳ Pending | Redirect URI: `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html` |
| **4** | Deploy Gemini Enterprise | Activate 30-day trial, deploy `Cymbal Pools GE`, enable Chat & Workflow agents | ⏳ Pending | Set Global location, Google Identity provider |
| **5** | Agent Designer Agent | Create pool robot agent via prompt, enable Google Search, ask question | ⏳ Pending | Prompt: `Keep me informed of the meaningful updates...` |
| **6** | Connect ADK Agent to GE | Run `construct_auth_uri.py`, create Custom Agent via Agent Runtime, grant All Users | ⏳ Pending | Use saved Reasoning Engine ID from Task 2 |
| **7** | Chat & Authorize in GE | Pin agent, chat `hello`, click Authorize, request brand voice rewrite | ⏳ Pending | "The part we needed to fix your pool filter has arrived." |

---

## 🛠️ Step-by-Step Command Playbook

### Task 1: Environment Setup & Code Download
In **Cloud Shell**:
```bash
# 1. Copy project resources
gcloud storage cp -r gs://qwiklabs-gcp-03-2c267663a806-bucket/adk_challenge_lab .
cd adk_challenge_lab

# 2. Update PATH and install dependencies
export PATH=$PATH:"/home/${USER}/.local/bin"
python3 -m pip install -r requirements.txt
gcloud config set project qwiklabs-gcp-03-2c267663a806
```

---

### Task 2: Create No-Code Agent & Deploy to Agent Runtime
```bash
# 1. Create agent template using YAML config
adk create \
  --type=config \
  --project qwiklabs-gcp-03-2c267663a806 \
  --region global \
  --model gemini-3.5-flash \
  brand_voice

# 2. Edit brand_voice/root_agent.yaml
cat << 'EOF' > brand_voice/root_agent.yaml
name: brand_voice
model: gemini-3.5-flash
description: Rewrites content into the Cymbal Pools brand voice.
instruction: >
  Rewrite text provided to you into the laid-back tone of a surfer dude. Include pool puns where possible. End each message with a goal of getting outside into the sun and water. Periodically add reminders to stay hydrated and wear sunscreen.
EOF

# 3. Deploy to Agent Runtime (takes 5-8 mins)
adk deploy \
  --display_name "Cymbal Pools Brand Voice" \
  --region us-east4 \
  --staging_bucket gs://qwiklabs-gcp-03-2c267663a806-bucket \
  brand_voice
```
> [!IMPORTANT]
> From the deployment output, copy and save your Reasoning Engine resource name:  
> `projects/PROJECT_NUMBER/locations/us-east4/reasoningEngines/ENGINE_ID`  
> *(Click **Check my progress** for Task 2)*

---

### Task 3: Set up OAuth Consent Screen & Client

1. Navigate to **Google Auth Platform** (or **APIs & Services > OAuth consent screen**).
2. Configure **OAuth Consent Screen**:
   - **App Name**: `Cymbal Pools Auth`
   - **User support email**: `student-01-360fe82e7ba0@qwiklabs.net`
   - **Audience**: `Internal`
   - **Developer contact information**: `student-01-360fe82e7ba0@qwiklabs.net`
   - Save and continue through scopes.
3. Navigate to **Credentials > Create Credentials > OAuth client ID**:
   - **Application type**: `Web application`
   - **Name**: `Gemini Enterprise Client`
   - **Authorized redirect URIs**:
     ```text
     https://vertexaisearch.cloud.google.com/static/oauth/oauth.html
     ```
   - Click **Create**.
4. Copy and save your **Client ID** and **Client Secret**.  
*(Click **Check my progress** for Task 3)*

---

### Task 4: Deploy Gemini Enterprise & Enable Features

1. In the console, search and open **Gemini Enterprise**.
2. Click **Start 30-day free trial** > **Continue**.
3. Deploy application:
   - **Name**: `Cymbal Pools GE`
   - **Location**: `Global`
   - **Company name**: `Cymbal Pools`
   - **Identity Provider**: `Global Google Identity`
4. Once created, in the left navigation settings, enable:
   - ✅ **Chat Agents**
   - ✅ **Workflow Agents**  
*(Click **Check my progress** for Task 4)*

---

### Task 5: Add No-Code Agent with Agent Designer

1. Open the **web preview / live URL** of your deployed `Cymbal Pools GE` app.
2. In the left navigation, click **Agents** > **Agent Designer** (or Create new agent).
3. In the creation prompt, paste:
   ```text
   Keep me informed of the meaningful updates and differences between models in new pool robot innovations.
   ```
4. Verify the default **Google Search** connector is enabled.
5. Save/Create the agent and open a chat with it.
6. Ask the agent:
   ```text
   What is the latest in pool robot technology, and is it a meaningful improvement over last year's robots?
   ```
*(Click **Check my progress** for Task 5)*

---

### Task 6: Connect ADK Agent Deployed to Agent Runtime

1. In Cloud Shell, update `construct_auth_uri.py` with your OAuth Client ID:
   ```bash
   cd ~/adk_challenge_lab
   # Replace YOUR_CLIENT_ID with your actual OAuth Client ID
   sed -i 's/YOUR_CLIENT_ID/<PASTE_YOUR_OAUTH_CLIENT_ID_HERE>/' construct_auth_uri.py
   python3 construct_auth_uri.py
   ```
   *Copy the output URL printed to the terminal.*

2. Return to the Google Cloud Console for **Gemini Enterprise**:
   - Go to **Agents** menu > Add agent > **Custom agent via Agent Runtime**.
3. Configure Authorization:
   - **Authorization name**: `Brand Voice Auth`
   - **Client ID**: `<Your OAuth Client ID>`
   - **Client secret**: `<Your OAuth Client Secret>`
   - **Token URI**: `https://oauth2.googleapis.com/token`
   - **Authorization URI**: `<The URI generated by construct_auth_uri.py>`
4. Configure Agent Settings:
   - **Agent name**: `Brand Voice Agent`
   - **Agent description**: `Rewrites content into the Cymbal Pools brand voice.`
   - **Agent Engine reasoning engine**: `<Your Reasoning Engine resource name from Task 2>`
5. Under Agent Permissions, set access to **All Users**.  
*(Click **Check my progress** for Task 6)*

---

### Task 7: Chat with Agent in Gemini Enterprise

1. In your **Gemini Enterprise** web app tab, refresh the page.
2. Go to **Agents** and click the **three dots (...)** next to **Brand Voice Agent** > select **Pin**.
3. Open chat and type:
   ```text
   hello
   ```
4. A prompt will ask to authorize the agent. Click **Authorize**.
5. Select your student account (`student-01-360fe82e7ba0@qwiklabs.net`) and click **Allow**.
6. Prompt the agent:
   ```text
   Please rewrite in our brand voice: The part we needed to fix your pool filter has arrived.
   ```
   *(The agent will reply in the surfer-dude tone with pool puns and sun/hydration reminders).*  
*(Click **Check my progress** for Task 7 to complete the lab!)*
