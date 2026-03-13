"""
Integration tests for the Sefaria proxy API  (/api/v1/sefaria)
TODO: implement when backend/app/routers/sefaria.py is ready
"""
import pytest
from unittest.mock import AsyncMock, patch


MOCK_SEARCH_RESULTS = [
    {
        "ref": "Genesis 1",
        "title": "Genesis",
        "heTitle": "בראשית",
        "type": "Torah",
    }
]

MOCK_TEXT_RESPONSE = {
    "ref": "Genesis 1",
    "title": "Genesis",
    "heTitle": "בראשית",
    "text": ["In the beginning God created the heavens and the earth."],
    "he": ["בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ"],
}


# ---------------------------------------------------------------------------
# GET /api/v1/sefaria/search
# ---------------------------------------------------------------------------

class TestSefariaSearch:
    def test_search_returns_200(self, test_client):
        with patch("app.services.sefaria.search_texts", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = MOCK_SEARCH_RESULTS
            response = test_client.get("/api/v1/sefaria/search?q=genesis")

        assert response.status_code == 200

    def test_search_returns_results_list(self, test_client):
        with patch("app.services.sefaria.search_texts", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = MOCK_SEARCH_RESULTS
            response = test_client.get("/api/v1/sefaria/search?q=genesis")

        results = response.json()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_result_shape(self, test_client):
        with patch("app.services.sefaria.search_texts", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = MOCK_SEARCH_RESULTS
            results = test_client.get("/api/v1/sefaria/search?q=genesis").json()

        for result in results:
            assert "ref" in result
            assert "title" in result

    def test_search_missing_query_returns_422(self, test_client):
        """q is required."""
        response = test_client.get("/api/v1/sefaria/search")
        assert response.status_code == 422

    def test_search_empty_query_returns_empty_or_422(self, test_client):
        with patch("app.services.sefaria.search_texts", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []
            response = test_client.get("/api/v1/sefaria/search?q=")

        assert response.status_code in (200, 422)
        if response.status_code == 200:
            assert response.json() == []

    def test_search_passes_query_to_service(self, test_client):
        with patch("app.services.sefaria.search_texts", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = MOCK_SEARCH_RESULTS
            test_client.get("/api/v1/sefaria/search?q=exodus")

        called_with = mock_search.call_args[0][0]
        assert "exodus" in called_with.lower()

    def test_search_service_error_returns_502(self, test_client):
        with patch(
            "app.services.sefaria.search_texts",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Sefaria down"),
        ):
            response = test_client.get("/api/v1/sefaria/search?q=genesis")

        assert response.status_code in (500, 502, 503)


# ---------------------------------------------------------------------------
# GET /api/v1/sefaria/text/{ref}
# ---------------------------------------------------------------------------

class TestGetSefariaText:
    def test_get_text_returns_200(self, test_client):
        with patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text:
            mock_text.return_value = MOCK_TEXT_RESPONSE
            response = test_client.get("/api/v1/sefaria/text/Genesis%201")

        assert response.status_code == 200

    def test_get_text_returns_hebrew_and_english(self, test_client):
        with patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text:
            mock_text.return_value = MOCK_TEXT_RESPONSE
            data = test_client.get("/api/v1/sefaria/text/Genesis%201").json()

        assert "text" in data or "he" in data

    def test_get_text_passes_decoded_ref_to_service(self, test_client):
        with patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text:
            mock_text.return_value = MOCK_TEXT_RESPONSE
            test_client.get("/api/v1/sefaria/text/Genesis%201")

        called_ref = mock_text.call_args[0][0]
        assert "Genesis" in called_ref

    def test_get_text_not_found_returns_404(self, test_client):
        import httpx

        with patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text:
            mock_text.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=MagicMock(status_code=404)
            )
            response = test_client.get("/api/v1/sefaria/text/NonExistentRef999")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/sefaria/links/{ref}
# ---------------------------------------------------------------------------

class TestGetSefariaLinks:
    def test_get_links_returns_200(self, test_client):
        with patch("app.services.sefaria.pull_links", new_callable=AsyncMock) as mock_links:
            mock_links.return_value = [
                {"ref": "Rashi on Genesis 1:1", "type": "commentary"}
            ]
            response = test_client.get("/api/v1/sefaria/links/Genesis%201:1")

        assert response.status_code == 200

    def test_get_links_returns_list(self, test_client):
        with patch("app.services.sefaria.pull_links", new_callable=AsyncMock) as mock_links:
            mock_links.return_value = []
            data = test_client.get("/api/v1/sefaria/links/Psalms%20119").json()

        assert isinstance(data, list)
