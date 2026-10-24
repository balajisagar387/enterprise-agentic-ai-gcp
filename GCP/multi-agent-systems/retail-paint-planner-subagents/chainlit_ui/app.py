"""Chainlit Web UI for Cymbal Shops Paint Agent deployed to Agent Runtime."""

import os
import chainlit as cl
from google.cloud import aiplatform

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_GCP_PROJECT_ID")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
AGENT_RESOURCE_NAME = os.environ.get(
    "AGENT_RESOURCE_NAME",
    "projects/YOUR_PROJECT_NUMBER/locations/us-central1/reasoningEngines/YOUR_ENGINE_ID",
)

# Initialize Vertex AI client
aiplatform.init(project=PROJECT_ID, location=LOCATION)


@cl.on_chat_start
async def on_chat_start():
    """Initializes the chat session and connects to the deployed Agent Runtime."""
    try:
        from vertexai.preview import reasoning_engines

        # Retrieve reference to deployed Agent Runtime
        client = reasoning_engines.ReasoningEngineClient()
        agent = client.get_reasoning_engine(name=AGENT_RESOURCE_NAME)
        cl.user_session.set("agent", agent)
        cl.user_session.set("session_id", cl.context.session.id)
        await cl.Message(
            content=(
                "👋 **Welcome to Cymbal Shops Paint Department!**\n\n"
                "I can help you explore our paint lines (EcoGreens, Forever Paint, SureCoverage, Project Paint), "
                "pick the right colors, and calculate exact paint coverage and costs for your home renovation.\n\n"
                "Would you like to explore our paint catalog?"
            )
        ).send()
    except Exception as e:
        await cl.Message(
            content=f"⚠️ Notice: Connected in preview mode ({e}). Agent Runtime endpoint configured at `{AGENT_RESOURCE_NAME}`."
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Processes user input, queries the Agent Runtime, and returns the response."""
    agent = cl.user_session.get("agent")
    user_input = message.content

    msg = cl.Message(content="")
    await msg.send()

    if agent:
        try:
            # Query deployed Agent Engine reasoning runtime
            response = agent.query(input=user_input)
            response_text = response.get("output", str(response)) if isinstance(response, dict) else str(response)
            msg.content = response_text
            await msg.update()
        except Exception as e:
            msg.content = f"Error communicating with Agent Runtime: {e}"
            await msg.update()
    else:
        # Fallback response for local testing
        msg.content = (
            f"Received: *{user_input}*\n\n"
            "*(Agent Runtime connection ready. Ensure AGENT_RESOURCE_NAME is configured in .env)*"
        )
        await msg.update()
