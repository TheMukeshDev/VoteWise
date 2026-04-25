"""
Tests for API smoke tests across all pages.
"""



class TestHomepage:
    """Smoke tests for homepage."""

    def test_homepage_loads(self, client):
        """Test homepage loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data

    def test_homepage_has_title(self, client):
        """Test homepage has correct title."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"VoteWise" in response.data

    def test_homepage_has_navbar(self, client):
        """Test homepage has navbar elements."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"navbar" in response.data.lower() or b"nav" in response.data.lower()

    def test_homepage_has_hero(self, client):
        """Test homepage has hero section."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"hero" in response.data.lower() or b"Understand" in response.data


class TestVoterDashboard:
    """Smoke tests for voter dashboard."""

