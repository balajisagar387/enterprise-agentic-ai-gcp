# Enterprise User Onboarding & Access Control Guide

This guide details how to grant access to individual internal employees and external stakeholders for the branded Gemini Enterprise assistant.

---

## 🏛️ Identity Architecture Overview

Gemini Enterprise enforces enterprise-grade identity boundaries using **Google Cloud Identity / Google Workspace Single Sign-On (SSO)** combined with **Per-User 3-Legged OAuth 2.0 Consent**.

```
  ┌────────────────────────────────────────────────────────────┐
  │                 GOOGLE CLOUD IAM LAYER                     │
  │  Grant `Discovery Engine User` / `IAP Web App User`        │
  └─────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
  ┌────────────────────────────────────────────────────────────┐
  │                 WEB APP AUTHENTICATION                     │
  │  User logs in with Google Identity SSO                     │
  └─────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
  ┌────────────────────────────────────────────────────────────┐
  │                 WORKSPACE OAUTH DELEGATION                 │
  │  User authorizes personal Drive, Mail, Calendar access     │
  │  (Zero cross-user data leakage / Strict ACL enforcement)   │
  └────────────────────────────────────────────────────────────┘
```

---

## 📋 Method 1: Provisioning Corporate Workspace / Cloud Identity Users

For organizations with an existing Google Workspace domain or Cloud Identity tenant:

### Step 1: Assign Cloud IAM Role
1. Open the **Google Cloud Console** > navigate to **IAM & Admin** > **IAM**.
2. Click **Grant Access** (or **Add Principal**).
3. **New Principals:** Enter the user's corporate email (e.g., `advisor@yourcompany.com`) or Google Group.
4. **Assign Roles:**
   * For standard end-users (Chat & Search only):
     * **Role:** `Discovery Engine User` (`roles/discoveryengine.user`)
   * For security & compliance auditors:
     * **Role:** `Discovery Engine Viewer` (`roles/discoveryengine.viewer`)
   * For AI administrators:
     * **Role:** `Discovery Engine Admin` (`roles/discoveryengine.admin`)
5. Click **Save**.

---

## 📋 Method 2: Granting External / Personal Email Access via IAP

If collaborating with an external client stakeholder using a personal `@gmail.com` or partner domain:

### Step 1: Add User to Google Cloud IAM
1. Go to **IAM & Admin** > **IAM** > click **Grant Access**.
2. Enter the external email address.
3. Assign the role: `Discovery Engine User` (`roles/discoveryengine.user`).

### Step 2: Authorize Through Identity-Aware Proxy (IAP)
1. In the Cloud Console, navigate to **Security** > **Identity-Aware Proxy**.
2. Locate the backend service associated with your Gemini Enterprise web app.
3. Click **Add Principal** in the IAP side panel.
4. Enter the email address and select the role:
   * **Role:** `IAP-secured Web App User` (`roles/iap.httpsResourceAccessor`).
5. Click **Save**.

---

## 📱 Method 3: End-User 1-Click Workspace Authorization (Desktop & Mobile)

Once access is granted, send the user the direct Web App URL:
```
https://vertexaisearch.cloud.google.com/global/home/cid/<CLIENT_ID>/...
```

When the user opens the application for the first time:

1. **Sign In:** Log in with their authorized Google account.
2. **Access Settings:** Tap the user profile / avatar at the bottom left (or top left menu on mobile).
3. **Open Personalization:** Select **Personalization / Settings**.
4. **Authorize Connectors:**
   * Click **Authorize** next to **Drive**, **Mail**, and **Calendar**.
   * Approve the Google Workspace OAuth permission prompt.
   * Toggle the sources to **ON**.
5. **Start Querying:** The assistant will now answer queries based on the specific documents, spreadsheets, and emails that the user has permission to view.
