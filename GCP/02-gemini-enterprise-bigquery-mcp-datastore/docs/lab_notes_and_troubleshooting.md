# Lab 2 Execution Notes & Troubleshooting Guide

> **Lab**: Use a Custom MCP Server Data Store in Gemini Enterprise  
> **Target Service**: BigQuery MCP Server (`https://bigquery.googleapis.com/mcp`)  
> **Status**: Active Troubleshooting

---

## 🚨 Active Incident Log

### Incident 1: `Something went wrong while attempting to login: Failed to obtain refresh token.`

- **Occurred at**: Task 2 - Clicked **Verify Auth** in MCP Server Configuration.
- **Error Details**: `Failed to obtain refresh token.`
- **Root Causes**:
  1. **Truncated Client Secret (Exact Culprit Found!)**:
     - Comparing the entered secret vs the OAuth client JSON revealed:
       - Entered: `GOCSPX-DpSViLu1R5W7SFLGbEiyn0jXYr6` (34 chars)
       - Actual JSON: `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` (35 chars - missed trailing `S`)
     - With an invalid client secret, Google's token endpoint rejects the exchange, failing refresh token retrieval.
  2. **PKCE or HTTP Basic Auth Checkboxes Checked**:
     - Google OAuth 2.0 token endpoint expects credentials in the POST request body.
     - **Fix**: **Uncheck** both `Enable PKCE Support` and `Use HTTP Basic Authentication`.
  3. **Missing or Corrupted `access_type=offline` & `prompt=consent`**:
     - Google OAuth **only** returns a refresh token if `access_type=offline` is explicitly passed in the authorization parameters.
     - **Fix**: Verify `Authorization URL Parameters` has **no spaces**:
       ```text
       &access_type=offline&prompt=consent
       ```
  3. **Wrong Google Account in Auth Popup**:
     - The popup might have defaulted to your personal Google email instead of the lab student account.
     - **Fix**: In the auth popup, ensure you select `student-01-...@qwiklabs.net`.
  4. **Redirect URI Mismatch in Task 1**:
     - **Fix**: In Google Auth Platform > OAuth Clients > `bq_custom_mcp`, verify Authorized Redirect URI is exactly:
       ```text
       https://vertexaisearch.cloud.google.com/oauth-redirect
       ```
       (Ensure no trailing slash and no leading/trailing spaces).

---

## Task-by-Task Checkpoint Matrix

| Task | Description | Critical Settings | Status |
| :--- | :--- | :--- | :---: |
| **Task 1** | Create OAuth Client | App Name: `bq_custom_mcp`<br>Redirect URI: `https://vertexaisearch.cloud.google.com/oauth-redirect` | Done |
| **Task 2** | Create Custom MCP Data Store | URL: `https://bigquery.googleapis.com/mcp`<br>Auth URL: `https://accounts.google.com/o/oauth2/auth`<br>Params: `&access_type=offline&prompt=consent`<br>Token: `https://oauth2.googleapis.com/token`<br>Scope: `https://www.googleapis.com/auth/bigquery`<br>PKCE: **OFF**, Basic Auth: **OFF** | In Progress |
| **Task 3** | Connect to Gemini Enterprise App | App Name: `gemini-bq-mcp-app`<br>Region: `Global`<br>Connect: `byo_bq_mcp` | Pending |
| **Task 4** | Run Natural Language Queries | Web App URL -> Authorize Connector -> Execute queries | Pending |
