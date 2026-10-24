"""Shared session tools for Paint Agent.

Provides utilities for storing and retrieving key-value pairs in ADK session state,
enabling multi-turn state persistence across agent and sub-agent interactions.
"""
# Copyright (c) Cymbal Shops. All rights reserved.

from google.adk.tools.tool_context import ToolContext


def set_session_value(key: str, value: str, tool_context: ToolContext) -> dict:
    """Stores a key-value pair in the ADK session state for use across agents.

    Args:
        key: The state dictionary key to set (e.g., 'SELECTED_PAINT').
        value: The value to store for the given key.
        tool_context: The ADK ToolContext providing access to the session state.

    Returns:
        A dict with a status message confirming the stored value.
    """
    tool_context.state[key] = value
    return {"status": f"stored '{value}' in '{key}'"}
