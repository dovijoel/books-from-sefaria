"""
Unit tests for app.services.book (build_book orchestration)
TODO: implement when backend/app/services/book.py is ready
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


SAMPLE_CONFIG = {
    "name": "Test Book",
    "texts": [
        {
            "link": "Genesis 1",
            "commentary": ["Rashi"],
            "translation": "English",
            "range": "1:1-5",
        }
    ],
    "format": {
        "paperheight": "11in",
        "paperwidth": "8.5in",
        "hebfont": "David CLM",
        "engfont": "EB Garamond",
        "top": "0.75in",
        "bottom": "0.75in",
        "inner": "0.75in",
        "outer": "0.75in",
        "fontsize": 12,
        "spacing": "1.5",
        "layout": "",
        "twocolfootnotes": False,
        "newpage": 0,
        "covercolor": "#1a3a5c",
        "covertextcolor": "#ffffff",
    },
}


class TestBuildBook:
    """Tests for build_book(config: dict, job_id: str) -> str (path to PDF)"""

    @pytest.mark.asyncio
    async def test_build_book_returns_pdf_path(self):
        """build_book orchestrates sefaria + latex and returns a PDF path."""
        with (
            patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text,
            patch("app.services.sefaria.pull_links", new_callable=AsyncMock) as mock_links,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}") as mock_latex,
            patch("app.services.book.compile_latex", return_value="/output/job-123.pdf") as mock_compile,
        ):
            mock_text.return_value = {
                "text": ["In the beginning"],
                "he": ["בְּרֵאשִׁית"],
            }
            mock_links.return_value = [
                {"ref": "Rashi on Genesis 1:1", "type": "commentary"}
            ]

            from app.services.book import build_book

            pdf_path = await build_book(SAMPLE_CONFIG, job_id="job-123")

        assert pdf_path.endswith(".pdf")

    @pytest.mark.asyncio
    async def test_build_book_calls_sefaria_for_each_text(self):
        """Each text entry triggers a pull_text call."""
        config_two_texts = {
            **SAMPLE_CONFIG,
            "texts": [
                {**SAMPLE_CONFIG["texts"][0], "link": "Genesis 1"},
                {**SAMPLE_CONFIG["texts"][0], "link": "Exodus 1"},
            ],
        }
        with (
            patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text,
            patch("app.services.sefaria.pull_links", new_callable=AsyncMock) as mock_links,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}"),
            patch("app.services.book.compile_latex", return_value="/output/job-456.pdf"),
        ):
            mock_text.return_value = {"text": [], "he": []}
            mock_links.return_value = []

            from app.services.book import build_book

            await build_book(config_two_texts, job_id="job-456")

        assert mock_text.call_count == 2

    @pytest.mark.asyncio
    async def test_build_book_propagates_sefaria_error(self):
        """If Sefaria service raises, build_book propagates the exception."""
        with patch(
            "app.services.sefaria.pull_text",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Sefaria unavailable"),
        ):
            from app.services.book import build_book

            with pytest.raises(RuntimeError, match="Sefaria unavailable"):
                await build_book(SAMPLE_CONFIG, job_id="job-err")

    @pytest.mark.asyncio
    async def test_build_book_propagates_latex_error(self):
        """If LaTeX generation raises, build_book propagates the exception."""
        with (
            patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text,
            patch("app.services.sefaria.pull_links", new_callable=AsyncMock) as mock_links,
            patch(
                "app.services.latex.generate_latex",
                side_effect=ValueError("Bad config"),
            ),
        ):
            mock_text.return_value = {"text": [], "he": []}
            mock_links.return_value = []

            from app.services.book import build_book

            with pytest.raises(ValueError, match="Bad config"):
                await build_book(SAMPLE_CONFIG, job_id="job-latex-err")

    @pytest.mark.asyncio
    async def test_build_book_propagates_compile_error(self):
        """If PDF compilation fails, build_book propagates the exception."""
        with (
            patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text,
            patch("app.services.sefaria.pull_links", new_callable=AsyncMock) as mock_links,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}"),
            patch(
                "app.services.book.compile_latex",
                side_effect=RuntimeError("pdflatex failed"),
            ),
        ):
            mock_text.return_value = {"text": [], "he": []}
            mock_links.return_value = []

            from app.services.book import build_book

            with pytest.raises(RuntimeError, match="pdflatex failed"):
                await build_book(SAMPLE_CONFIG, job_id="job-compile-err")

    @pytest.mark.asyncio
    async def test_build_book_fetches_commentary_when_requested(self):
        """Commentary refs in text config trigger pull_links."""
        with (
            patch("app.services.sefaria.pull_text", new_callable=AsyncMock) as mock_text,
            patch("app.services.sefaria.pull_links", new_callable=AsyncMock) as mock_links,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}"),
            patch("app.services.book.compile_latex", return_value="/output/job-789.pdf"),
        ):
            mock_text.return_value = {"text": [], "he": []}
            mock_links.return_value = []

            from app.services.book import build_book

            await build_book(SAMPLE_CONFIG, job_id="job-789")

        # Commentary = ["Rashi"] means we need links for that text
        mock_links.assert_called()
