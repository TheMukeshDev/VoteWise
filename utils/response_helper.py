"""
DEPRECATED: This module is kept for backward compatibility.
Please use utils.response instead.

Migration:
  - from utils.response_helper import success_response, error_response
  - from utils.response import success_response, error_response
"""

from utils.response import success_response, error_response

__all__ = ["success_response", "error_response"]


def format_chat_response(intro, steps=None, tips=None, actions=None):
    """Format a standardized response for the chat assistant."""
    return {
        "intro": intro,
        "steps": steps or [],
        "tips": tips or [],
        "actions": actions or [],
    }
