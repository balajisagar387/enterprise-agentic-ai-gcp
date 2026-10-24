#!/usr/bin/env bash
# ==============================================================================
# Enterprise ADK + MCP Cloud Run Deployment Automation Script
# ==============================================================================
set -euo pipefail

echo "==> [1/4] Verifying Google Cloud configuration..."
PROJECT_ID=$(gcloud config get-value project)
REGION=$(gcloud compute project-info describe --format="value(commonInstanceMetadata.items[google-compute-default-region])")
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Project ID:      $PROJECT_ID"
echo "Project Number:  $PROJECT_NUMBER"
echo "Region:          $REGION"
echo "Service Account: $SERVICE_ACCOUNT"

echo "==> [2/4] Ensuring IAM Role bindings..."
# Allow compute service account to call private MCP Cloud Run service
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.invoker" \
  --quiet

# Allow compute service account to invoke Vertex AI Platform LLMs
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user" \
  --quiet

echo "==> [3/4] Deploying Agent container to Cloud Run via ADK CLI..."
cd "$(dirname "$0")/../zoo_guide_agent"
source .env || true

adk deploy cloud_run \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --service_name=zoo-tour-guide \
  --with_ui \
  .

echo "==> [4/4] Setting environment variables and labels on Cloud Run service..."
gcloud run services update zoo-tour-guide \
  --region="$REGION" \
  --update-labels=dev-tutorial=codelab-adk,managed-by=adk-cli \
  --set-env-vars="MODEL=${MODEL},MCP_SERVER_URL=${MCP_SERVER_URL},GOOGLE_CLOUD_LOCATION=global"

SERVICE_URL=$(gcloud run services describe zoo-tour-guide --region="$REGION" --format="value(status.url)")
echo "=============================================================================="
echo " Deployment Complete! Live Service URL:"
echo " $SERVICE_URL"
echo "=============================================================================="
