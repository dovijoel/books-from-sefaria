"""
Unit tests for app.services.book (build_book orchestration)
"""
import pytest
from unittest.mock import MagicMock, patch


# Flat config matching BookConfigCreate.model_dump(exclude={"name","description"})
SAMPLE_CONFIG = {
    "name": "Test Book",
    "texts": [
        {
            "link": "Genesis/Hebrew/Sefaria_Genesis.json",
            "commentary": ["Rashi"],
            "translation": "",
            "range": "all",
            "format": {},
        }
    ],
    "paperheight": "11in",
    "paperwidth": "8.5in",
    "hebfont": "Noto Serif Hebrew",
    "engfont": "Linux Libertine O",
    "commentfont": "Noto Sans Hebrew",
    "top": "0.75in",
    "bottom": "0.75in",
    "inner": "0.75in",
    "outer": "0.75in",
    "fontsize": 12.0,
    "spacing": 1.5,
    "layout": "",
    "twocolfootnotes": 0,
    "newpage": 0,
    "covercolor": "FFFFFF",
    "covertextcolor": "000000",
    "chapfontsize": 14.0,
    "engfontsize": 10.0,
    "parskip": "6pt",
    "colsep": "0.25in",
    "pagenumloc": "bottom",
    "pagenumheb": 0,
    "headpos": "center",
    "evenhead": "title",
    "oddhead": "chapter",
    "commentstyle": "",
    "covertype": "softcover",
    "backtext": "",
    "titleheb": "",
    "title": None,
    "hebboldfont": "",
    "dafrange": None,
}


class TestBuildBook:
    """Tests for build_book(config: dict, job_id: str) -> (str, int)"""

    def test_build_book_returns_pdf_path(self, tmp_path):
        """build_book orchestrates sefaria + latex and returns (pdf_path, page_count)."""
        fake_pdf = str(tmp_path / "job-123.pdf")
        fake_pdf.replace("\\", "/")

        with (
            patch("app.services.sefaria.pull_text_sync") as mock_text,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}"),
            patch("app.services.book.compile_latex", return_value=5),
            patch("builtins.open", create=True),
            patch("os.makedirs"),
        ):
            mock_text.return_value = {"text": [["בְּרֵאשִׁית"]], "heTitle": "בְּרֵאשִׁית"}

            from app.services.book import build_book

            pdf_path, page_count = build_book(SAMPLE_CONFIG, job_id="job-123")

        assert pdf_path.endswith(".pdf")
        assert page_count == 5

    def test_build_book_calls_sefaria_for_each_text(self, tmp_path):
        """Each text entry triggers a pull_text_sync call."""
        config_two_texts = {
            **SAMPLE_CONFIG,
            "texts": [
                {**SAMPLE_CONFIG["texts"][0], "link": "Genesis/Hebrew/text.json"},
                {**SAMPLE_CONFIG["texts"][0], "link": "Exodus/Hebrew/text.json"},
            ],
        }
        with (
            patch("app.services.sefaria.pull_text_sync") as mock_text,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}"),
            patch("app.services.book.compile_latex", return_value=3),
            patch("builtins.open", create=True),
            patch("os.makedirs"),
        ):
            mock_text.return_value = {"text": [], "heTitle": ""}

            from app.services.book import build_book

            build_book(config_two_texts, job_id="job-456")

        assert mock_text.call_count == 2

    def test_build_book_propagates_sefaria_error(self):
        """If Sefaria service raises, build_book propagates the exception."""
        with patch(
            "app.services.sefaria.pull_text_sync",
            side_effect=RuntimeError("Sefaria unavailable"),
        ):
            from app.services.book import build_book

            with pytest.raises(RuntimeError, match="Sefaria unavailable"):
                build_book(SAMPLE_CONFIG, job_id="job-err")

    def test_build_book_propagates_latex_error(self, tmp_path):
        """If LaTeX generation raises, build_book propagates the exception."""
        with (
            patch("app.services.sefaria.pull_text_sync") as mock_text,
            patch(
                "app.services.latex.generate_latex",
                side_effect=ValueError("Bad config"),
            ),
            patch("os.makedirs"),
        ):
            mock_text.return_value = {"text": [], "heTitle": ""}

            from app.services.book import build_book

            with pytest.raises(ValueError, match="Bad config"):
                build_book(SAMPLE_CONFIG, job_id="job-latex-err")

    def test_build_book_propagates_compile_error(self, tmp_path):
        """If PDF compilation fails, build_book propagates the exception."""
        with (
            patch("app.services.sefaria.pull_text_sync") as mock_text,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}"),
            patch(
                "app.services.book.compile_latex",
                side_effect=RuntimeError("xelatex failed"),
            ),
            patch("builtins.open", create=True),
            patch("os.makedirs"),
        ):
            mock_text.return_value = {"text": [], "heTitle": ""}

            from app.services.book import build_book

            with pytest.raises(RuntimeError, match="xelatex failed"):
                build_book(SAMPLE_CONFIG, job_id="job-compile-err")

    def test_build_book_fetches_translation_when_requested(self, tmp_path):
        """Non-empty translation field triggers a second pull_text_sync call."""
        config_with_translation = {
            **SAMPLE_CONFIG,
            "texts": [
                {
                    **SAMPLE_CONFIG["texts"][0],
                    "translation": "Genesis/English/Sefaria_Genesis.json",
                }
            ],
        }
        with (
            patch("app.services.sefaria.pull_text_sync") as mock_text,
            patch("app.services.latex.generate_latex", return_value=r"\documentclass{article}"),
            patch("app.services.book.compile_latex", return_value=2),
            patch("builtins.open", create=True),
            patch("os.makedirs"),
        ):
            mock_text.return_value = {"text": [], "heTitle": ""}

            from app.services.book import build_book

            build_book(config_with_translation, job_id="job-789")

        # One call for Hebrew text + one for English translation
        assert mock_text.call_count == 2
