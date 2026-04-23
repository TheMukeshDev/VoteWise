"""
FAQ Service for VoteWise AI

Placeholder for FAQ operations.
"""


class FAQService:
    """Mock FAQ service."""

    def get_all(self, category=None, language=None):
        return []

    def get_by_id(self, id):
        return None

    def create(self, **kwargs):
        return {"id": "mock-id", **kwargs}

    def update(self, id, data):
        return {"id": id, **data}

    def delete(self, id):
        return True


faq_service = FAQService()
