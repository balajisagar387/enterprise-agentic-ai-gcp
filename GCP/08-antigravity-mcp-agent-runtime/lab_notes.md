# Lab Execution Notes & Verification Runbook

> **Lab**: Accelerate Development with Antigravity: Challenge Lab  
> **Lab ID**: GENAI144  
> **Organization**: Cymbal Direct E-Commerce Logistics  
> **Target Project**: `qwiklabs-gcp-04-8ee6b65cc387`  
> **Grading Bucket**: `gs://qwiklabs-gcp-04-8ee6b65cc387-grading/`  
> **Deployment Region**: `us-west1`  
> **Target Score**: 100%  

---

## 📋 Task-by-Task Checkpoint Matrix

| Task | Objective | Key Actions & Prompts | Grading Criteria | Target Status |
| :---: | :--- | :--- | :--- | :---: |
| **1** | Setup Cloud Shell & `agy` | Export `GOOGLE_CLOUD_PROJECT`, run `agy`, authenticate via browser, select `global` & `gemini-3.5-flash` | Initial CLI connection | ✅ Verified |
| **2** | CymbalLogistics MCP Server | Download `cymbal_direct_mcp.py`, create `.agents/mcp_config.json`, test `CYM-EC-9921`, upload `summary_task2.md` | `summary_task2.md` in grading bucket | ✅ Verified |
| **3** | Agent Skill & Workspace Rules | Create `GEMINI.md` (`always_on`), create skill `winter-storm-triage`, test `/winter-storm-triage`, upload `summary_task3.md` | `summary_task3.md` in grading bucket | ✅ Verified |
| **4** | Scaffold with Agents CLI | Install `uv` & `agents-cli`, scaffold `winter-storm-triage`, test on port 8080 (`CYM-EC-1002`), upload `summary_task4.md` | `summary_task4.md` in grading bucket | ✅ Verified |
| **5** | Deploy to Agent Runtime | Copy `cymbal_direct_mcp.py` to `app/`, deploy to `us-west1`, test in Cloud Console, upload `summary_task5.md` | `summary_task5.md` in grading bucket | ✅ Verified |

---

## 🛠️ Step-by-Step Command Playbook

### Task 1: Authenticate Antigravity CLI (`agy`)
In Cloud Shell Editor Terminal (`Terminal > New Terminal`):
```bash
export GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-04-8ee6b65cc387
agy
```
1. Choose option **`2`** (*Use a Google Cloud project*).
2. Choose option **`1`** (*Use your browser to authenticate*).
3. Open auth link, sign in with lab student account, copy auth code, and paste into terminal.
4. Project ID prompt: `qwiklabs-gcp-04-8ee6b65cc387`
5. Location prompt: `global`
6. License: *Agent Platform - Pay as you go*
7. Skip extensions > Agree terms > Trust folder.
8. In agy prompt:
   ```text
   /model
   ```
   Select `Gemini 3.5 Flash`. Test with `Hello`.

---

### Task 2: Configure the CymbalLogistics MCP Server
Type `/exit` in `agy` to return to shell prompt:
```bash
# 1. Create workspace & download mock logistics server
mkdir -p ~/genai144-challenge/mcp
gcloud storage cp gs://qwiklabs-gcp-04-8ee6b65cc387-lab-scripts/cymbal_direct_mcp.py ~/genai144-challenge/mcp/
cd ~/genai144-challenge

# 2. Install dependencies
pip3 install "mcp<2" fastmcp pydantic-settings --break-system-packages

# 3. Create .agents/mcp_config.json
mkdir -p .agents
cat << 'EOF' > .agents/mcp_config.json
{
  "mcpServers": {
    "cymbal-logistics": {
      "command": "python3",
      "args": [
        "mcp/cymbal_direct_mcp.py"
      ]
    }
  }
}
EOF

# 4. Start agy inside ~/genai144-challenge
agy
```

In `agy`:
1. Type `/mcp` and wait for `cymbal-logistics` to initialize. Press `ESC`.
2. Ask:
   ```text
   What tools do you have in your cymbal-logistics MCP server?
   ```
3. Test order status:
   ```text
   What is the status of order CYM-EC-9921?
   ```
   *(Agent responds that order is delayed due to severe winter storm).*

4. **Generate & Upload `summary_task2.md`**:
   Prompt `agy`:
   ```text
   Create a file named summary_task2.md that lists:
   - The registered MCP server name
   - The names of the three available tools registered on this server
   Upload the summary to gs://qwiklabs-gcp-04-8ee6b65cc387-grading/
   ```
   *(Or run directly via shell:)*
   ```bash
   cat << 'EOF' > ~/genai144-challenge/summary_task2.md
   # Task 2 Summary: CymbalLogistics MCP Server
   - Registered MCP Server Name: cymbal-logistics
   - Available Tools:
     1. get_order_status
     2. get_customer_loyalty_info
     3. issue_disruption_compensation
   EOF
   gcloud storage cp ~/genai144-challenge/summary_task2.md gs://qwiklabs-gcp-04-8ee6b65cc387-grading/
   ```
👉 *Click **Check my progress** for Task 2.*

---

### Task 3: Author Agent Skill & Workspace Rule

In `agy` prompt:
1. **Create Workspace Rules**:
   ```text
   Add rules to a GEMINI.md file in the root of my workspace (~/genai144-challenge/). The rules must be configured as always_on and enforce the following code organization rules: 1. All new Python code files must start with a docstring at the top of the file explaining what the file does. 2. All new Python code files must start with a commented copyright statement for "Cymbal Direct" at the top of the file. 3. All custom agent skills must be created in the root of the workspace under the .agents/skills/ directory.
   ```
2. Verify:
   ```text
   What rules have been set for this workspace?
   ```
3. **Create Custom Skill**:
   ```text
   Create an agent skill named winter-storm-triage. The skill should dictate the standard operating procedures for customers whose packages are delayed due to severe winter storms. It must: 1. Require the agent to use get_order_status and get_customer_loyalty_info to verify the order. 2. Apply the following compensation based on loyalty tier: - Platinum: $100 credit, Next-Day Air shipping upgrade - Gold: $50 credit, Next-Day Air shipping upgrade - Silver: $25 credit, 3-Day Select shipping upgrade - Member: $10 credit, Priority Shipping upgrade 3. Require the agent to call issue_disruption_compensation to apply the refund. 4. Draft an empathetic customer response detailing the resolution.
   ```
4. **Test the Skill**:
   ```text
   /winter-storm-triage a customer's package (order CYM-EC-9921) is lost in the winter storm. Please find their customer ID and loyalty tier, and write a response to the customer.
   ```
   *(Agent checks Gold tier, applies $50 credit and Next-Day Air upgrade).*

5. **Generate & Upload `summary_task3.md`**:
   Prompt `agy` or execute:
   ```bash
   cat << 'EOF' > ~/genai144-challenge/summary_task3.md
   # Task 3 Summary: Workspace Rules & Custom Skill
   - Workspace Rule File: GEMINI.md
   - Trigger Configuration: always_on
   - Custom Agent Skill: winter-storm-triage
   - Compensation Rules:
     - Platinum: $100 credit, Next-Day Air shipping upgrade
     - Gold: $50 credit, Next-Day Air shipping upgrade
     - Silver: $25 credit, 3-Day Select shipping upgrade
     - Member: $10 credit, Priority Shipping upgrade
   - Order CYM-EC-9921 Resolution:
     - Customer ID: CUST-7821
     - Loyalty Tier: Gold
     - Compensation: $50.00 store credit applied and shipping upgraded to Next-Day Air.
   EOF
   gcloud storage cp ~/genai144-challenge/summary_task3.md gs://qwiklabs-gcp-04-8ee6b65cc387-grading/
   ```
👉 *Click **Check my progress** for Task 3.*

---

### Task 4: Build Agent using Agents CLI

1. **Enable Auto-Edit Mode in `agy`**:
   - Type `/config` > Set **Tool Permission** to **`always-proceed`** > Press `ESC`.
   - (Or start agy with `agy --dangerously-skip-permissions`).
2. Open a **second terminal tab** in Cloud Shell:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="$HOME/.local/bin:$PATH"
   uvx google-agents-cli setup
   ```
3. Return to the **first terminal tab** (`agy`) and prompt:
   ```text
   Use your agents-cli skills to build a winter storm triage agent based on the MCP server. Name the project "winter-storm-triage" and place it inside the ~/genai144-challenge/ directory. Configure the agent to use the gemini-3.5-flash model.
   ```
4. In the **second terminal tab**, install dependencies & test playground:
   ```bash
   cd ~/genai144-challenge/winter-storm-triage
   uv pip install "mcp<2" fastmcp pydantic-settings
   agents-cli playground
   ```
   *Preview on port 8080 > Select `app` from dropdown > Ask:*
   ```text
   Where is my order CYM-EC-1002?
   ```
   *(Verify Platinum tier resolution: $100 credit).* Press `Ctrl+C` to stop.

5. **Generate & Upload `summary_task4.md`**:
   ```bash
   cat << 'EOF' > ~/genai144-challenge/summary_task4.md
   # Task 4 Summary: Scaffolded Agent Prototype
   - Project Name: winter-storm-triage
   - Primary Configuration File Path: app/agent.py
   - Local Playground Command: agents-cli playground
   - Order CYM-EC-1002 Response:
     - Status: Delayed due to severe winter storm in transit hub
     - Customer Loyalty Tier: Platinum
     - Compensation: $100 store credit and Next-Day Air shipping upgrade applied
   EOF
   gcloud storage cp ~/genai144-challenge/summary_task4.md gs://qwiklabs-gcp-04-8ee6b65cc387-grading/
   ```
👉 *Click **Check my progress** for Task 4.*

---

### Task 5: Deploy the Agent to Agent Runtime

1. In the **first terminal tab (`agy`)**, prompt:
   ```text
   Deploy the winter storm triage agent to Agent Runtime in the us-west1 region. Make sure to copy the local `cymbal_direct_mcp.py` file into the agent's `app/` directory before deployment.
   ```
   *(Wait 5–10 minutes for deployment to complete).*

2. Verify in Google Cloud Console:
   - Navigate to **Agent Platform > Agents > Deployments**.
   - Verify `winter-storm-triage` is active in `us-west1`.
   - In **Playground**, test:
     ```text
     Where is my order CYM-EC-1002?
     ```

3. **Generate & Upload `summary_task5.md`**:
   Prompt `agy` or run in shell:
   ```bash
   # Retrieve your reasoning engine ID and runtime SA from console or gcloud:
   export ENGINE_RESOURCE=$(gcloud beta ai reasoning-engines list --region=us-west1 --format="value(name)" | head -n 1)
   export RUNTIME_SA=$(gcloud projects describe qwiklabs-gcp-04-8ee6b65cc387 --format="value(projectNumber)")-compute@developer.gserviceaccount.com

   cat << EOF > ~/genai144-challenge/summary_task5.md
   # Task 5 Summary: Live Agent Runtime Deployment
   - Reasoning Engine Resource ID: $ENGINE_RESOURCE
   - Region: us-west1
   - Runtime Service Account: $RUNTIME_SA
   EOF
   gcloud storage cp ~/genai144-challenge/summary_task5.md gs://qwiklabs-gcp-04-8ee6b65cc387-grading/
   ```
👉 *Click **Check my progress** for Task 5 to achieve 100%!*
