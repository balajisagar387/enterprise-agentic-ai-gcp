# Architecture Deep-Dive: Zero-Trust Defense-in-Depth for MCP Servers

This document details the multi-layered security engineering implemented to secure **Model Context Protocol (MCP)** tool servers deployed to **Google Cloud Run** using **Identity-Aware Proxy (IAP)**.

---

## 1. The Vulnerability of Unsecured MCP Servers

When AI agents use tools, the tool execution servers (MCP servers) are granted elevated internal privileges (e.g. executing database queries, calling ERP systems, fetching employee records).

If an MCP server is simply deployed to a public URL:
- **Vulnerability 1: Direct Internet Exposure**: Anyone discovering the URL can execute tools and extract sensitive data.
- **Vulnerability 2: Shared Credential Leaks**: Static API keys stored in agent config files can be leaked via prompt injection or committed code.
- **Vulnerability 3: Lack of Non-Repudiation**: Without per-caller identity tokens, audit logs cannot prove which specific user or service agent triggered a given action.

---

## 2. The 4-Layer Defense-in-Depth Architecture

```mermaid
sequenceDiagram
    autonumber
    actor Caller as AI Agent / Test SA
    participant Net as VPC Ingress Layer
    participant IAP as Identity-Aware Proxy (IAP)
    participant IAM as Cloud IAM Policy Engine
    participant CR as Cloud Run Infrastructure
    participant App as FastMCP Application Container

    Caller->>Net: HTTPS POST /mcp (with OIDC Bearer Token)
    Note over Net: Evaluates Ingress Rule (--ingress internal)
    alt From External Public Internet
        Net-->>Caller: 404 Not Found (Traffic Dropped)
    else From Internal VPC or IAP Tunnel
        Net->>IAP: Passes to IAP Gateway
        Note over IAP: 1. Verifies OAuth Client ID signature<br>2. Verifies Audience claim matches IAP Client ID
        IAP->>IAM: Checks roles/iap.httpsResourceAccessor on caller
        alt IAM Access Denied
            IAP-->>Caller: 403 Forbidden
        else IAM Access Granted
            IAP->>CR: Forwards request with IAP Service Agent Identity
            Note over CR: Verifies IAP agent holds roles/run.invoker
            CR->>App: Invokes FastMCP container method (e.g., tools/call)
            App-->>CR: JSON-RPC 2.0 Response
            CR-->>IAP-->>Net-->>Caller: Streamed SSE / JSON Result
        end
    end
```

---

## 3. OIDC Identity Token & Audience Enforcement

Google Cloud IAP enforces strict **Audience Verification**:
- Standard Google OAuth tokens minted without an audience cannot bypass IAP.
- The caller must mint an OpenID Connect (OIDC) token specifying the exact OAuth Client ID:
  ```bash
  TOKEN=$(gcloud auth print-identity-token \
    --impersonate-service-account="${MCP_TEST_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --audiences="$IAP_AUDIENCE" \
    --include-email)
  ```
- **Why Impersonation is Essential**: End users cannot arbitrary mint tokens with custom audiences for arbitrary service accounts. By granting `roles/iam.serviceAccountTokenCreator`, the authorized administrator delegates the right to generate short-lived, targeted tokens without ever handling private keys.

---

## 4. Network Ingress Hardening

Cloud Run supports three ingress levels:
1. `all` (Default): Accessible from any public internet IP.
2. `internal-and-cloud-load-balancing`: Accessible only via Cloud Load Balancing or internal VPC.
3. `internal`: Drops all external internet traffic, answering with `404 Not Found`.

By combining `internal` ingress with IAP:
- Even if an attacker obtains a valid OIDC token with the correct audience, they **cannot reach the endpoint from the public internet**.
- They must originate from within the authorized VPC network or pass through an authenticated private bastion/tunnel.
