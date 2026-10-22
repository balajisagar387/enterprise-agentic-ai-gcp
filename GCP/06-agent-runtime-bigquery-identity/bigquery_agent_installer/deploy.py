import os
import vertexai
from vertexai.preview import reasoning_engines
from vertexai.preview.reasoning_engines import types
from bigquery_agent.agent import root_agent

# ==============================================================================
# Challenge Lab GENAI160 Configuration
# ==============================================================================
AGENT_NAME = "BigQuery Invoice Agent"
STAGING_BUCKET_NAME = "gs://qwiklabs-gcp-01-67ce6f14529a-bucket"
MODEL_VERSION = "gemini-2.5-flash"
PROJECT_ID = "qwiklabs-gcp-01-67ce6f14529a"
REGION = "us-central1"

# Task 2 requirement: Deploy using dedicated Agent Identity
IDENTITY_TYPE = types.IdentityType.AGENT_IDENTITY

def main():
    print(f"Initializing Vertex AI for project '{PROJECT_ID}' in '{REGION}'...")
    vertexai.init(
        project=PROJECT_ID,
        location=REGION,
        staging_bucket=STAGING_BUCKET_NAME
    )

    print(f"Deploying agent '{AGENT_NAME}' with identity type '{IDENTITY_TYPE}'...")
    remote_agent = reasoning_engines.ReasoningEngine.create(
        reasoning_engines.LangchainAgent(
            agent=root_agent,
            model_name=MODEL_VERSION,
        ),
        requirements=[
            "google-adk>=0.1.0",
            "google-cloud-bigquery>=3.25.0",
            "google-cloud-aiplatform>=1.60.0",
            "vertexai>=1.60.0",
            "python-dotenv>=1.0.0"
        ],
        display_name=AGENT_NAME,
        description="Autonomous BigQuery Invoice Intelligence Agent for Cymbal Pools",
        identity_type=IDENTITY_TYPE,
    )

    print("\n=======================================================")
    print(" Agent Deployed Successfully to Agent Runtime!")
    print(f" Resource Name: {remote_agent.resource_name}")
    print(f" Display Name:  {AGENT_NAME}")
    print("=======================================================\n")
    print("Next step: Retrieve the Agent Principal ID from the console and grant BigQuery roles.")

if __name__ == "__main__":
    main()
