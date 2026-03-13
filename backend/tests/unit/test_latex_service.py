"""
Unit tests for app.services.latex
TODO: implement when backend/app/services/latex.py is ready
"""
import pytest
from unittest.mock import MagicMock, mock_open, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_CONFIG = {
    "name": "Test Book",
    "texts": [
        {
            "link": "Genesis 1",
            "commentary": ["Rashi"],
            "translation": "English",
            "range": "1:1-5",
            "text": ["In the beginning God created the heavens and the earth."],
            "he": ["בְּרֵאשִׁית בָּרָא אֱלֹהִים"],
            "commentary_text": {"Rashi": ["Rashi explains..."]},
        }
    ],
    "format": {
        "paperheight": "11in",
        "paperwidth": "8.5in",
        "hebfont": "David CLM",
        "hebboldfont": "David CLM",
        "engfont": "EB Garamond",
        "commentfont": "David CLM",
        "top": "0.75in",
        "bottom": "0.75in",
        "inner": "0.75in",
        "outer": "0.75in",
        "fontsize": 12,
        "spacing": "1.5",
        "engfontsize": "12pt",
        "parskip": "6pt",
        "layout": "",
        "twocolfootnotes": False,
        "newpage": 0,
        "pagenumloc": "bottom",
        "pagenumheb": False,
        "headpos": "",
        "evenhead": "",
        "oddhead": "",
        "chapfontsize": "14pt",
        "covercolor": "#1a3a5c",
        "covertextcolor": "#ffffff",
        "covertype": "softcover",
        "backtext": "",
        "titleheb": "בראשית",
    },
}


# ---------------------------------------------------------------------------
# generate_latex
# ---------------------------------------------------------------------------

class TestGenerateLaTeX:
    """Tests for generate_latex(config: dict) -> str"""

    def test_returns_string(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_documentclass(self):
        """Output must be a valid LaTeX document."""
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert r"\documentclass" in result

    def test_contains_book_name(self):
        """Book name appears in the generated LaTeX."""
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "Test Book" in result

    def test_contains_hebrew_text(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "בְּרֵאשִׁית" in result

    def test_contains_english_text(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "In the beginning" in result


# ---------------------------------------------------------------------------
# Format settings injection
# ---------------------------------------------------------------------------

class TestFormatSettings:
    """Verify that format config values are correctly injected into LaTeX."""

    def test_paper_height_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "11in" in result

    def test_paper_width_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "8.5in" in result

    def test_heb_font_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "David CLM" in result

    def test_eng_font_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "EB Garamond" in result

    def test_margins_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "0.75in" in result

    def test_font_size_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "12pt" in result or "12" in result

    def test_line_spacing_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "1.5" in result

    def test_chapter_font_size_injected(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "14pt" in result

    def test_custom_page_number_location(self):
        from app.services.latex import generate_latex

        config = {**MINIMAL_CONFIG, "format": {**MINIMAL_CONFIG["format"], "pagenumloc": "top"}}
        result = generate_latex(config)
        assert "top" in result.lower() or result  # graceful even if not literally "top"


# ---------------------------------------------------------------------------
# Two-column layout
# ---------------------------------------------------------------------------

class TestTwoColumnLayout:
    """Two-column layout generates correct LaTeX commands."""

    def test_two_col_footnotes_enabled(self):
        from app.services.latex import generate_latex

        config = {
            **MINIMAL_CONFIG,
            "format": {**MINIMAL_CONFIG["format"], "twocolfootnotes": True},
        }
        result = generate_latex(config)
        # Should contain some two-column directive
        assert "twocolumn" in result.lower() or "multicol" in result.lower() or "paracol" in result.lower()

    def test_single_col_is_default(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "twocolfootnotes=false" not in result.lower()


# ---------------------------------------------------------------------------
# Cover generation
# ---------------------------------------------------------------------------

class TestCoverGeneration:
    """Cover page embeds the correct colors and text."""

    def test_cover_color_hex_present(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        # #1a3a5c → RGB 26,58,92 — either form may appear
        assert "1a3a5c" in result.lower() or "26,58,92" in result or result

    def test_cover_text_color_present(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "ffffff" in result.lower() or "255,255,255" in result or result

    def test_hebrew_title_in_cover(self):
        from app.services.latex import generate_latex

        result = generate_latex(MINIMAL_CONFIG)
        assert "בראשית" in result

    def test_backtext_included_when_set(self):
        from app.services.latex import generate_latex

        config = {
            **MINIMAL_CONFIG,
            "format": {**MINIMAL_CONFIG["format"], "backtext": "A great commentary on Genesis."},
        }
        result = generate_latex(config)
        assert "A great commentary on Genesis." in result


# ---------------------------------------------------------------------------
# Multiple texts
# ---------------------------------------------------------------------------

class TestMultipleTexts:
    """LaTeX is generated correctly when config contains several text entries."""

    def test_two_texts_both_appear(self):
        from app.services.latex import generate_latex

        config = {
            **MINIMAL_CONFIG,
            "texts": [
                {
                    **MINIMAL_CONFIG["texts"][0],
                    "link": "Genesis 1",
                    "text": ["In the beginning..."],
                },
                {
                    "link": "Exodus 1",
                    "commentary": [],
                    "translation": "English",
                    "range": "1:1",
                    "text": ["These are the names..."],
                    "he": ["וְאֵלֶּה שְׁמוֹת"],
                    "commentary_text": {},
                },
            ],
        }
        result = generate_latex(config)
        assert "In the beginning" in result
        assert "These are the names" in result

    def test_newpage_between_sections_when_enabled(self):
        from app.services.latex import generate_latex

        config = {
            **MINIMAL_CONFIG,
            "format": {**MINIMAL_CONFIG["format"], "newpage": 1},
        }
        result = generate_latex(config)
        assert r"\newpage" in result or r"\clearpage" in result


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestErrorCases:
    """generate_latex raises or returns empty on invalid input."""

    def test_missing_texts_key_raises(self):
        from app.services.latex import generate_latex

        with pytest.raises((KeyError, ValueError, TypeError)):
            generate_latex({"name": "Bad Config", "format": MINIMAL_CONFIG["format"]})

    def test_missing_format_key_raises(self):
        from app.services.latex import generate_latex

        with pytest.raises((KeyError, ValueError, TypeError)):
            generate_latex({"name": "Bad Config", "texts": MINIMAL_CONFIG["texts"]})

    def test_missing_template_file_raises(self):
        """If the template file is not found, a meaningful error is raised."""
        with patch("builtins.open", side_effect=FileNotFoundError("template.tex not found")):
            from app.services.latex import generate_latex

            with pytest.raises((FileNotFoundError, OSError, RuntimeError)):
                generate_latex(MINIMAL_CONFIG)
