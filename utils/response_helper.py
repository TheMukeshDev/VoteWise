def format_chat_response(intro, steps=None, tips=None, actions=None):
    """
    Format a standardized response for the chat assistant.
    """
    return {
        "intro": intro,
        "steps": steps or [],
        "tips": tips or [],
        "actions": actions or []
    }

def success_response(data=None, message="Success"):
    """
    Standard successful API response.
    """
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return response

def error_response(message="An error occurred", status_code=400):
    """
    Standard error API response.
    """
    return {"status": "error", "message": message}, status_code
