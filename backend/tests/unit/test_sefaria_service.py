"""
Unit tests for app.services.sefaria
TODO: implement when backend/app/services/sefaria.py is ready
"""
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# search_texts
# ---------------------------------------------------------------------------

class TestSearchTexts:
    """Tests for search_texts(query: str) -> list[dict]"""

    @pytest.mark.asyncio
    async def test_search_returns_results(self, mock_sefaria_text_response):
        """search_texts constructs correct URL and parses results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Match Sefaria name-completion API format (uses "matches", "key" fields)
        mock_response.json.return_value = {
            "matches": [
                {
                    "key": "Genesis 1",
                    "title": "Genesis",
                    "heTitle": "בראשית",
                    "type": "ref",
                }
            ]
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import search_texts  # TODO: adjust import path

            results = await search_texts("genesis")

        called_url = mock_get.call_args[0][0]
        assert "genesis" in called_url.lower() or "genesis" in str(mock_get.call_args)
        assert len(results) == 1
        assert results[0]["ref"] == "Genesis 1"

    @pytest.mark.asyncio
    async def test_search_empty_query_returns_empty_list(self):
        """Empty or whitespace query returns []."""
        from app.services.sefaria import search_texts

        result = await search_texts("")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_network_error_raises(self):
        """Network failure propagates as a service exception."""
        with patch("httpx.AsyncClient.get", side_effect=httpx.NetworkError("down")):
            from app.services.sefaria import search_texts

            with pytest.raises(Exception):
                await search_texts("genesis")

    @pytest.mark.asyncio
    async def test_search_malformed_response_returns_empty(self):
        """Unexpected API shape is handled gracefully."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {"unexpected_key": []}

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import search_texts

            result = await search_texts("genesis")

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_non_200_response_raises(self):
        """Non-200 HTTP responses raise an exception."""
        mock_response = MagicMock(status_code=500)
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import search_texts

            with pytest.raises(Exception):
                await search_texts("genesis")


# ---------------------------------------------------------------------------
# pull_text
# ---------------------------------------------------------------------------

class TestPullText:
    """Tests for pull_text(ref: str) -> dict"""

    @pytest.mark.asyncio
    async def test_pull_text_returns_parsed_content(self, mock_sefaria_text_response):
        """pull_text fetches and returns structured text data."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = mock_sefaria_text_response

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import pull_text

            result = await pull_text("Genesis 1")

        assert result["ref"] == "Genesis 1"
        assert "text" in result or "he" in result

    @pytest.mark.asyncio
    async def test_pull_text_encodes_ref_in_url(self):
        """Ref with spaces is URL-encoded in the request."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "ref": "Genesis 1:1",
            "text": ["In the beginning"],
            "he": ["בְּרֵאשִׁית"],
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import pull_text

            await pull_text("Genesis 1:1")

        called_url = mock_get.call_args[0][0]
        # Spaces should be encoded as %20 or replaced with underscores per Sefaria convention
        assert " " not in called_url

    @pytest.mark.asyncio
    async def test_pull_text_network_error_raises(self):
        with patch("httpx.AsyncClient.get", side_effect=httpx.NetworkError("down")):
            from app.services.sefaria import pull_text

            with pytest.raises(Exception):
                await pull_text("Genesis 1")

    @pytest.mark.asyncio
    async def test_pull_text_not_found_raises(self):
        mock_response = MagicMock(status_code=404)
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import pull_text

            with pytest.raises(Exception):
                await pull_text("NonExistent 99")


# ---------------------------------------------------------------------------
# pull_links
# ---------------------------------------------------------------------------

class TestPullLinks:
    """Tests for pull_links(ref: str) -> list[dict]"""

    @pytest.mark.asyncio
    async def test_pull_links_parses_csv_response(self):
        """pull_links correctly parses a CSV-style links payload."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = [
            {
                "ref": "Rashi on Genesis 1:1",
                "anchorRef": "Genesis 1:1",
                "type": "commentary",
                "collectiveTitle": {"en": "Rashi", "he": "רש״י"},
            }
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import pull_links

            links = await pull_links("Genesis 1:1")

        assert len(links) == 1
        assert links[0]["ref"] == "Rashi on Genesis 1:1"

    @pytest.mark.asyncio
    async def test_pull_links_empty_result(self):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = []

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import pull_links

            links = await pull_links("Psalms 119:1")

        assert links == []

    @pytest.mark.asyncio
    async def test_pull_links_filters_by_type(self):
        """When a type filter is passed, only matching links are returned."""
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = [
            {"ref": "Rashi on Genesis 1:1", "type": "commentary"},
            {"ref": "Tosafot on Genesis 1:1", "type": "commentary"},
            {"ref": "Some Cross Ref", "type": "reference"},
        ]

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import pull_links

            links = await pull_links("Genesis 1:1", link_type="commentary")

        assert all(l["type"] == "commentary" for l in links)


# ---------------------------------------------------------------------------
# match_comment
# ---------------------------------------------------------------------------

class TestMatchComment:
    """Tests for match_comment(link: dict, text_ref: str) -> bool (pure logic)"""

    def test_matching_link_returns_true(self):
        from app.services.sefaria import match_comment

        link = {"anchorRef": "Genesis 1:1", "ref": "Rashi on Genesis 1:1"}
        assert match_comment(link, "Genesis 1:1") is True

    def test_non_matching_link_returns_false(self):
        from app.services.sefaria import match_comment

        link = {"anchorRef": "Genesis 1:2", "ref": "Rashi on Genesis 1:2"}
        assert match_comment(link, "Genesis 1:1") is False

    def test_case_insensitive_match(self):
        from app.services.sefaria import match_comment

        link = {"anchorRef": "genesis 1:1", "ref": "Rashi on Genesis 1:1"}
        assert match_comment(link, "Genesis 1:1") is True

    def test_missing_anchor_ref_returns_false(self):
        from app.services.sefaria import match_comment

        link = {"ref": "Rashi on Genesis 1:1"}
        assert match_comment(link, "Genesis 1:1") is False


# ---------------------------------------------------------------------------
# get_text_details
# ---------------------------------------------------------------------------

class TestGetTextDetails:
    """Tests for get_text_details(ref: str) -> dict"""

    @pytest.mark.asyncio
    async def test_returns_title_and_categories(self):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "title": "Genesis",
            "heTitle": "בראשית",
            "categories": ["Tanakh", "Torah"],
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            from app.services.sefaria import get_text_details

            details = await get_text_details("Genesis")

        assert details["title"] == "Genesis"
        assert "categories" in details

    @pytest.mark.asyncio
    async def test_network_error_raises(self):
        with patch("httpx.AsyncClient.get", side_effect=httpx.NetworkError("down")):
            from app.services.sefaria import get_text_details

            with pytest.raises(Exception):
                await get_text_details("Genesis")
