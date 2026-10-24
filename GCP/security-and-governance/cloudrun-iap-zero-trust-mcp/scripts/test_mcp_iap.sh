#!/usr/bin/env bash
# ==============================================================================
# Script to test IAP-secured FastMCP Server on Cloud Run
# ==============================================================================
set -euo pipefail

if [[ -z "${IAP_AUDIENCE:-}" ]]; then
  echo "Error: IAP_AUDIENCE environment variable is not set."
  echo "Usage: export IAP_AUDIENCE='<YOUR_OAUTH_CLIENT_ID>' && ./test_mcp_iap.sh"
  exit 1
fi

PROJECT_ID=$(gcloud config get-value project)
REGION=$(gcloud compute project-info describe --format="value(commonInstanceMetadata.items[google-compute-default-region])")
MCP_SERVER_NAME="${MCP_SERVER_NAME:-products-mcp-server}"
MCP_TEST_SA="${MCP_TEST_SA:-mcp-test-sa}"

echo "==> Fetching Cloud Run Service URL..."
MCP_SERVER_URL=$(gcloud run services describe "$MCP_SERVER_NAME" --region="$REGION" --format="value(status.url)")
echo "Service URL: $MCP_SERVER_URL"

echo "==> Minting OIDC Token with Audience matching IAP Client ID..."
TOKEN=$(gcloud auth print-identity-token \
  --impersonate-service-account="${MCP_TEST_SA}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --audiences="$IAP_AUDIENCE" \
  --include-email)

echo "==> [1/2] Invoking 'tools/list' via FastMCP StreamableHTTP..."
curl -sS -X POST "${MCP_SERVER_URL}/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | jq . || true

echo -e "\n==> [2/2] Invoking 'tools/call' for 'get_products_by_category'..."
curl -sS -X POST "${MCP_SERVER_URL}/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_products_by_category",
      "arguments": { "category": "Tops" }
    }
  }' | sed -n 's/^data: //p' | jq . || true

echo -e "\n=============================================================================="
echo " MCP Tool Invocation Complete!"
echo "=============================================================================="
