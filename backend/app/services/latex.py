"""
LaTeX generation service – ported from notebook cells 10–18, 20–34.

All file I/O uses absolute paths from settings.
"""
from __future__ import annotations

import csv
import os
import subprocess
import tempfile
from typing import Any

from hebrew_numbers import int_to_gematria

from app.config import settings
from app.services import sefaria as sefaria_svc

# Geometry keys whose values come verbatim from settings
_GEOMETRY_KEYS = {"paperheight", "paperwidth", "top", "bottom", "inner", "outer"}


def _num(val, default: float = 0.0) -> float:
    """Convert a value that may be a string like '14pt' or '1.5' to float."""
    try:
        return float(str(val).rstrip("pt").strip())
    except (ValueError, TypeError):
        return float(default)


def _fmt_pt(val: float) -> str:
    """Format a float as a LaTeX pt dimension, using integer notation for whole numbers.

    Examples: 12.0 → '12pt', 14.0 → '14pt', 10.5 → '10.5pt'
    """
    return f"{int(val)}pt" if val == int(val) else f"{val}pt"

# ── Small helpers ─────────────────────────────────────────────────────────────

def pullinput(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return list(f.readlines())


def removeformatting(text: str) -> str:
    """Strip all <tag> HTML markup."""
    while "<" in text and ">" in text:
        loc1 = text.find("<")
        loc2 = text.find(">", loc1) + 1
        text = text.replace(text[loc1:loc2], "")
    return text


def footnoteremove(text: str | None) -> str | None:
    """Remove footnote-marker superscripts; leave inline <i> notes."""
    if text is None:
        return None
    mark_begin = '<sup class="footnote-marker">'
    mark_end = "</sup>"
    while mark_begin in text:
        b = text.find(mark_begin)
        e = text.find(mark_end, b) + len(mark_end)
        text = text[:b] + " " + text[e:]
    text = text.replace('<i class="footnote">', "<i>")
    while "<i data-" in text:
        b = text.find("<i data-")
        e = text.find(">", b + 5) + 1
        text = text[:b] + "<i>" + text[e:]
    text = text.replace("<i></i>", "")
    return text


def parse_perek_title(perek_dict: dict) -> str:
    chap_num = perek_dict["name_en"].replace("Chapter ", "")
    return r"\hebrewnumeral{" + chap_num + r"} " + perek_dict["name_he"]


# ── Commentary extraction ─────────────────────────────────────────────────────

def get_comments(
    i: int,
    j: int,
    commentary: dict[str, Any],
    comment_i: int,
) -> str:
    """Get commentary for chapter i, section j (1-indexed).  Legacy flat path."""
    try:
        chap = commentary["text"][i - 1]
    except IndexError:
        return ""
    if len(chap) < j:
        return ""
    content = chap[j - 1]
    if isinstance(content, list):
        if not content:
            return ""
        content = content[0]
    content = content.replace(r"\par", "")
    content = content.replace("<b>", r"\textrm{\textbf{")
    content = content.replace("</b>", r"}}")
    comment_text = "%\n" + r"\comment" + chr(comment_i + 96) + "{" + content + "}%endcomment"
    if "{}" in comment_text:
        return ""
    return comment_text


def get_comments_json(
    commentary: dict[str, Any],
    chap: int,
    sect: int,
    subsect: int,
    comment_i: int,
) -> str:
    """Get commentary for dict-structured text.  chap/sect/subsect are 0-indexed."""
    try:
        text = commentary["text"][chap][sect]
        if isinstance(text[0], list):
            text = text[subsect]
    except (IndexError, KeyError, TypeError):
        return ""
    if not text:
        return ""
    comment_text = "%\n" + r"\comment" + chr(comment_i + 96) + "{"
    all_blank = True
    for comment in text:
        if not comment:
            continue
        if comment.endswith(" "):
            comment = comment[:-1]
        comment = comment.replace(r"\par", "")
        comment = comment.replace("<b>", r"\textrm{\textbf{")
        comment = comment.replace("</b>", r"}}")
        comment_text += comment
        all_blank = False
    if all_blank or "{}" in comment_text:
        return ""
    comment_text += "}%endcomment"
    return comment_text


# ── Section builders ──────────────────────────────────────────────────────────

def _load_replacements(csv_path: str) -> list[tuple[str, str]]:
    """Load a two-column replacement CSV (Original, LaTeX)."""
    pairs: list[tuple[str, str]] = []
    if not os.path.isfile(csv_path):
        return pairs
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                pairs.append((row[0], row[1]))
    return pairs


def make_section(
    hebrew_text: str,
    english: str | None,
    settings_dict: dict,
    chap_num: int,
    mishna_num: int,
    commentaries: list[dict],
    resources_dir: str,
) -> str:
    hebrew_text = footnoteremove(hebrew_text) or ""
    english = footnoteremove(english)

    for orig, repl in _load_replacements(
        os.path.join(resources_dir, "text_replacements.csv")
    ):
        if orig in hebrew_text:
            hebrew_text = hebrew_text.replace(orig, repl)

    if english:
        for orig, repl in _load_replacements(
            os.path.join(resources_dir, "english_replacements.csv")
        ):
            if orig in english:
                english = english.replace(orig, repl)

    if english:
        english = english.replace("[", "{[").replace("]", "]}")
        output = r"\hebeng{" + hebrew_text + "}{" + english + "}"
        if settings_dict.get("newpage") == 1:
            output += r"\newpage"
    elif settings_dict.get("layout") == "twocol":
        output = hebrew_text
    elif not hebrew_text:
        return ""
    else:
        output = r"\textblock{" + hebrew_text + "}"

    for idx, commentary in enumerate(commentaries, start=1):
        output += get_comments(chap_num, mishna_num, commentary, idx)

    return removeformatting(output)


def make_section_json(
    hebrew_text: dict[str, Any],
    english: dict[str, Any] | None,
    settings_dict: dict,
    commentaries: list[dict],
    chap: int,
    sect: int,
    subsect: int,
    resources_dir: str,
) -> str:
    """Build a single section from dict-structured Sefaria JSON (3-level)."""
    try:
        nodes = hebrew_text["schema"]["nodes"]
        heb_raw = nodes[chap]["chapters"][sect]
        if isinstance(heb_raw, list):
            heb_raw = heb_raw[subsect] if subsect < len(heb_raw) else ""
    except (KeyError, IndexError, TypeError):
        try:
            heb_raw = hebrew_text["text"][chap][sect]
            if isinstance(heb_raw, list):
                heb_raw = heb_raw[subsect] if subsect < len(heb_raw) else ""
        except (IndexError, TypeError):
            heb_raw = ""

    eng_raw: str | None = None
    if english:
        try:
            eng_raw = english["text"][chap][sect]
            if isinstance(eng_raw, list):
                eng_raw = eng_raw[subsect] if subsect < len(eng_raw) else ""
        except (IndexError, TypeError):
            eng_raw = ""

    heb_raw = footnoteremove(str(heb_raw)) or ""
    eng_raw = footnoteremove(str(eng_raw)) if eng_raw else None

    for orig, repl in _load_replacements(
        os.path.join(resources_dir, "text_replacements.csv")
    ):
        if orig in heb_raw:
            heb_raw = heb_raw.replace(orig, repl)

    if eng_raw:
        for orig, repl in _load_replacements(
            os.path.join(resources_dir, "english_replacements.csv")
        ):
            if orig in eng_raw:
                eng_raw = eng_raw.replace(orig, repl)

    if eng_raw:
        eng_raw = eng_raw.replace("[", "{[").replace("]", "]}")
        output = r"\hebeng{" + heb_raw + "}{" + eng_raw + "}"
        if settings_dict.get("newpage") == 1:
            output += r"\newpage"
    elif settings_dict.get("layout") == "twocol":
        output = heb_raw
    elif not heb_raw:
        return ""
    else:
        output = r"\textblock{" + heb_raw + "}"

    for idx, commentary in enumerate(commentaries, start=1):
        output += get_comments_json(commentary, chap, sect, subsect, idx)

    return removeformatting(output)


# ── Body generators ───────────────────────────────────────────────────────────

def make_body_json(
    hebrew_text: dict[str, Any],
    english_text: dict[str, Any] | None,
    settings_dict: dict,
    commentaries: list[dict],
    resources_dir: str,
) -> tuple[str, list[str], str]:
    """
    Generate LaTeX lines for a dict-structured text (3-level: chapter/section/subsection).
    Returns (title_command, output_lines, title).
    """
    output: list[str] = []
    title = hebrew_text["heTitle"]
    title_command = r"\newcommand{\texttitle}{" + title + "}"

    try:
        nodes = hebrew_text["schema"]["nodes"]
    except (KeyError, TypeError):
        nodes = []

    if settings_dict.get("layout") == "twocol" and not english_text:
        output.append(r"\begin{multicols}{2}")

    for chap_i, node in enumerate(nodes):
        chap_title = node.get("heTitle", "")
        if settings_dict.get("newpage") == 1:
            output.append(r"\clearpage")
        output.append(r"\newchap{" + chap_title + "}")

        chapters_data = node.get("chapters", [])
        for sect_i, section in enumerate(chapters_data):
            if isinstance(section, list):
                for subsect_i in range(len(section)):
                    line = make_section_json(
                        hebrew_text, english_text, settings_dict,
                        commentaries, chap_i, sect_i, subsect_i, resources_dir,
                    )
                    if line:
                        output.append(line)
            else:
                line = make_section_json(
                    hebrew_text, english_text, settings_dict,
                    commentaries, chap_i, sect_i, 0, resources_dir,
                )
                if line:
                    output.append(line)

    if settings_dict.get("layout") == "twocol" and not english_text:
        output.append(r"\end{multicols}")
        output.append(r"\newpage")

    return title_command, output, title


def make_body(
    hebrew_text: dict[str, Any],
    english_text: dict[str, Any] | None,
    settings_dict: dict,
    commentaries: list[dict],
    link_list: list[list[str]],
    resources_dir: str,
) -> tuple[str, list[str], str]:
    """
    Generate LaTeX lines for a flat-list-structured text (legacy path).
    Returns (title_command, output_lines, title).
    """
    output: list[str] = []
    chap_num = 1
    mishna_num = 1
    title = hebrew_text["heTitle"]
    title_command = r"\newcommand{\texttitle}{" + title + "}"

    try:
        divisions_en: list[str] = hebrew_text["sectionNames"]
    except KeyError:
        divisions_en = ["Chapter", "Paragraph"]
        hebrew_text["sectionNames"] = divisions_en

    # Normalise dict-structured texts
    if isinstance(hebrew_text["text"], dict):
        hebrew_text["text"] = sefaria_svc.structure_fixer(hebrew_text["text"])
    if english_text and isinstance(english_text["text"], dict):
        english_text["text"] = sefaria_svc.structure_fixer(english_text["text"])

    # Build Hebrew section-name mapping from CSV
    divisions_he: list[str] = []
    section_csv = os.path.join(resources_dir, "section_names.csv")
    if os.path.isfile(section_csv):
        with open(section_csv, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            mapping = {row[0]: row[1] for row in reader if len(row) >= 2}
        for div in divisions_en:
            divisions_he.append(mapping.get(div, div))

    if "Daf" in divisions_en:
        hebrew_text = sefaria_svc.match_chapters(hebrew_text, link_list)

    for perek in hebrew_text["text"]:
        if not any(perek):
            chap_num += 1
            mishna_num = 1
            continue

        if isinstance(perek[0], dict) and "name_he" in perek[0]:
            new_chap_text = r"\newchap{" + parse_perek_title(perek[0]) + "}"
            if new_chap_text not in output:
                output.append(new_chap_text)

        if "Daf" in divisions_en:
            daf = (chap_num + 1) / 2
            if daf == round(daf):
                daftitle = int_to_gematria(round(int(daf)), gershayim=False)
                if settings_dict.get("newpage") == 1:
                    output.append(r"\clearpage")
                output.append(r"\newsection{דף " + daftitle + "}")
        else:
            if settings_dict.get("newpage") == 1:
                output.append(r"\clearpage")
            if divisions_he:
                output.append(
                    r"\newchap{"
                    + divisions_he[0]
                    + " "
                    + int_to_gematria(chap_num, gershayim=False)
                    + "}"
                )

        for par in perek:
            if isinstance(par, dict) and "name_he" in par:
                mishna_num += 1
                continue
            textblock = ""
            while isinstance(par, list):
                par = "".join(par)
            if isinstance(par, str):
                textblock += par + r"\\\vspace{0pt}" + "\n"

            if divisions_en[1:2] in [["Verse"], ["Mishnah"]]:
                textblock = r"\vsnum{" + str(mishna_num) + "}" + textblock

            if english_text and english_text["text"][chap_num - 1] != []:
                try:
                    eng = english_text["text"][chap_num - 1][mishna_num - 1]
                except IndexError:
                    eng = None
            else:
                eng = None

            new_text = make_section(
                textblock, eng, settings_dict, chap_num, mishna_num,
                commentaries, resources_dir,
            )
            if new_text:
                output.append(new_text)
            mishna_num += 1

        chap_num += 1
        mishna_num = 1

    # Wrap in multicols if twocol layout without translation
    if settings_dict.get("layout") == "twocol" and not english_text:
        wrapped: list[str] = []
        in_cols = False
        for i, line in enumerate(output):
            is_section = "newsection" in line or "newchap" in line
            if is_section and in_cols:
                end = "\n" + r"\end{multicols}\newpage" + "\n"
                if wrapped:
                    wrapped[-1] += end
                in_cols = False
            elif not is_section and "renewcommand" not in line and "fancy" not in line:
                if not in_cols:
                    line = r"\begin{multicols}{2}" + "\n" + line
                    in_cols = True
            wrapped.append(line)
        if in_cols:
            wrapped.append(r"\end{multicols}")
            wrapped.append(r"\newpage")
        output = wrapped

    return title_command, output, title


# ── Range filtering ───────────────────────────────────────────────────────────

def range_str(string: str) -> list[int]:
    result: list[int] = []
    for part in string.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            result.extend(range(int(a), int(b) + 1))
        else:
            result.append(int(part))
    return result


def limit_output(lines: list[str], text_settings: dict) -> list[str]:
    if "dafrange" in text_settings and text_settings["dafrange"]:
        start_str, end_str = text_settings["dafrange"].split("-")
        start = int_to_gematria(int(start_str), gershayim=False)
        end = int_to_gematria(int(end_str), gershayim=False)
        collecting = False
        limited: list[str] = []
        for line in lines:
            if not collecting and r"\newsection{דף " + start in line:
                collecting = True
                limited.append(line)
            elif collecting and r"\newsection{דף " + end in line:
                return limited
            elif collecting:
                limited.append(line)
        return limited

    rng = text_settings.get("range", "all")
    if rng == "all" or not rng:
        return lines

    chapters: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if "newchap" in line:
            chapters.append(current)
            current = [line]
        else:
            current.append(line)
    chapters.append(current)

    indices = range_str(rng)
    limited = []
    for idx in indices:
        if idx < len(chapters):
            limited.extend(chapters[idx])
    return limited


# ── Block-comment helpers ─────────────────────────────────────────────────────

def move_comments(lines: list[str], title: str, newpage: int) -> list[str]:
    """Collect inline comments and move them to end-of-perek blocks."""
    collected: list[str] = []
    output: list[str] = []
    for line in lines:
        if r"\comment" in line:
            try:
                cs = line.index(r"\comment") + 10
                ce = line.index("}%endcomment")
                comment = line[cs:ce]
                line = line[:cs - 10] + line[ce + 12:]
                output.append(line)
                collected.append(comment)
            except ValueError:
                output.append(line)
        elif any(k in line for k in (r"\newchap", r"\newsection", r"\addpart")):
            if collected:
                block = r"\blockcomment{" + title + "}{"
                block += r"\\".join(collected) + "\n}%endcomment"
                if newpage == 1:
                    block += r"\newpage"
                output.append(block)
                collected = []
            output.append(line)
        else:
            output.append(line)
    if collected:
        block = r"\blockcomment{" + title + "}{"
        block += r"\\".join(collected) + r"\n}%endcomment"
        if newpage == 1:
            block += r"\newpage"
        output.append(block)
    return output


def block_fix(text: list[str]) -> list[str]:
    for i in range(1, len(text)):
        if r"\blockcomment{" in text[i] and text[i - 1].rstrip("\n") == r"\clearpage}":
            text[i - 1] = "}\n"
        if "}%endcomment" in text[i]:
            text[i] = text[i].replace("}%endcomment", r"}\clearpage %endcomment")
    return text


# ── Per-part format commands ──────────────────────────────────────────────────

def add_part_format(part_i: int, settings_dict: dict) -> list[str]:
    """Return list of LaTeX commands that reset formatting for a new part."""
    output: list[str] = []
    part_settings = settings_dict["texts"][part_i].get("format", {})

    # Ensure format is a plain dict (may be a Pydantic model)
    if hasattr(part_settings, "model_dump"):
        part_settings = {
            k: v for k, v in part_settings.model_dump().items() if v is not None
        }

    def _get(key: str):
        return part_settings.get(key) or settings_dict.get(key)

    # Headers
    headpos = settings_dict.get("headpos", "center")
    if headpos == "center":
        odd_header = r"\fancyhead[CO]{"
        even_header = r"\fancyhead[CE]{"
    else:
        odd_header = r"\fancyhead[RO]{"
        even_header = r"\fancyhead[LE]{"

    _header_map = {
        "title": r"\partname",
        "chapter": r"\chapname",
        "titlechapter": r"\partname\space\textendash\space \chapname",
        "daf": r"\sectname",
        "chapdaf": r"\chapname \space\textendash\space \sectname",
    }
    even_header += _header_map.get(_get("evenhead") or "title", r"\partname") + "}"
    odd_header += _header_map.get(_get("oddhead") or "chapter", r"\chapname") + "}"
    output.append(odd_header)
    output.append(even_header)

    fontsize = _num(_get("fontsize"), 12.0)
    spacing = _num(_get("spacing"), 1.5)
    skip = round(fontsize * spacing, 1)
    engsize = _num(_get("engfontsize"), fontsize)
    output.append(
        r"\renewcommand{\sethebfont}{\fontsize{"
        + _fmt_pt(fontsize)
        + r"}{"
        + _fmt_pt(skip)
        + r"} \selectfont}\sethebfont"
    )
    output.append(
        r"\renewcommand{\setengfont}{\fontsize{"
        + _fmt_pt(engsize)
        + r"}{"
        + _fmt_pt(skip)
        + r"} \selectfont}\setengfont"
    )
    return output


# ── Template formatter ────────────────────────────────────────────────────────

def set_format(template_lines: list[str], settings_dict: dict) -> list[str]:
    """Replace %placeholder comments in template with actual LaTeX commands."""

    output: list[str] = []
    for line in template_lines:
        key = line.rstrip("\n")

        if key in _GEOMETRY_KEYS and key in settings_dict:
            output.append(key + "=" + str(settings_dict[key]) + ",\n")

        elif key == "%setfontsize":
            fs = _num(settings_dict.get("fontsize", 12), 12)
            sp = _num(settings_dict.get("spacing", 1.5), 1.5)
            skip = round(fs * sp, 1)
            output.append(r"\linespread{" + str(sp) + r"}" + "\n")
            output.append(
                r"\fontsize{" + _fmt_pt(fs) + r"}{" + _fmt_pt(skip) + r"}\selectfont" + "\n"
            )

        elif key == "%engfontsize":
            es = _num(settings_dict.get("engfontsize", 10), 10)
            sp = _num(settings_dict.get("spacing", 1.5), 1.5)
            skip = round(es * sp, 1)
            output.append(
                r"\fontsize{" + _fmt_pt(es) + r"}{" + _fmt_pt(skip) + r"}\selectfont" + "\n"
            )

        elif key == "%sethebfont":
            font = settings_dict.get("hebfont", "")
            bold = settings_dict.get("hebboldfont", "")
            if bold:
                cmd = r"\setmainfont[BoldFont=" + bold + r"]{" + font + r"}"
            else:
                cmd = r"\setmainfont{" + font + r"}"
            output.append(cmd + "\n")

        elif key == "%setcommentfont":
            cf = settings_dict.get("commentfont") or settings_dict.get("hebfont", "")
            output.append(r"\setsansfont{" + cf + r"}" + "\n")

        elif key == "%setengfont":
            ef = settings_dict.get("engfont", "")
            output.append(r"\newfontfamily\englishfont{" + ef + r"}" + "\n")

        elif key == "%setparskip":
            output.append(
                r"\setlength{\parskip}{" + str(settings_dict.get("parskip", "6pt")) + r"}" + "\n"
            )

        elif key == "%pagenumber":
            loc = settings_dict.get("pagenumloc", "bottom")
            use_heb = settings_dict.get("pagenumheb", 0)
            page_cmd = r"\hebrewnumeral{\thepage}" if use_heb else r"\thepage"
            if loc == "bottom":
                output.append(r"\fancyfoot[C]{" + page_cmd + r"}" + "\n")
            elif loc == "topouter":
                output.append(r"\fancyhead[LO,RE]{" + page_cmd + r"}" + "\n")
            else:
                output.append(r"\fancyfoot[C]{" + page_cmd + r"}" + "\n")

        elif key == "%header":
            headpos = settings_dict.get("headpos", "center")
            if headpos == "center":
                odd_cmd = r"\fancyhead[CO]{"
                even_cmd = r"\fancyhead[CE]{"
            else:
                odd_cmd = r"\fancyhead[RO]{"
                even_cmd = r"\fancyhead[LE]{"

            _map = {
                "title": r"\texttitle",
                "chapter": r"\chapname",
                "titlechapter": r"\texttitle\space\textendash\space \chapname",
                "daf": r"\sectname",
                "chapdaf": r"\chapname \space\textendash\space \sectname",
            }
            evenhead = settings_dict.get("evenhead", "title")
            oddhead = settings_dict.get("oddhead", "chapter")

            multi = len(settings_dict.get("texts", [])) > 1
            if multi:
                even_cmd += _map.get(evenhead, r"\partname")
                odd_cmd += _map.get(oddhead, r"\chapname")
            else:
                even_cmd += _map.get(evenhead, r"\texttitle")
                odd_cmd += _map.get(oddhead, r"\chapname")

            output.append(even_cmd + r"}" + "\n")
            output.append(odd_cmd + r"}" + "\n")

        elif key == "%chapfontsize":
            cfs = _num(settings_dict.get("chapfontsize", 14), 14)
            sp = _num(settings_dict.get("spacing", 1.5), 1.5)
            skip = round(cfs * sp, 1)
            output.append(
                r"\fontsize{" + _fmt_pt(cfs) + r"}{" + _fmt_pt(skip) + r"}\selectfont" + "\n"
            )

        elif key == "%setcolumnsep":
            output.append(
                r"\setlength{\columnsep}{" + str(settings_dict.get("colsep", "0.25in")) + r"}" + "\n"
            )

        elif key == "%twocolfootnote":
            if settings_dict.get("twocolfootnotes"):
                output.append(r"\usepackage{dblfnote}\DFNalwaysdouble" + "\n")

        else:
            output.append(line if line.endswith("\n") else line + "\n")

    return output


# ── Bibliographic data ────────────────────────────────────────────────────────

def get_bib_info(json_data: dict[str, Any]) -> dict:
    license_str = json_data.get("license", "CC-BY")
    version = json_data.get("versionTitle", "")
    source = json_data.get("versionSource", "")
    he_title = json_data.get("heTitle", "")
    entry = {
        "heTitle": he_title,
        "versionTitle": version,
        "versionSource": source,
        "license": license_str,
    }
    if "Copyright" in license_str:
        entry["NC"] = version
    return entry


def print_source_data(source_list: list[dict]) -> list[str]:
    lines: list[str] = [r"\begin{itemize}"]
    for src in source_list:
        if "NC" in src:
            return ["NC", src["NC"]]
        item = (
            r"\item "
            + src.get("heTitle", "")
            + " – "
            + src.get("versionTitle", "")
            + " ("
            + src.get("license", "")
            + ")"
        )
        lines.append(item)
    lines.append(r"\end{itemize}")
    return lines


# ── Cover ────────────────────────────────────────────────────────────────────

def calc_spine_width(pages: int, settings_dict: dict, resources_dir: str) -> float:
    cover_type = settings_dict.get("covertype", "softcover")
    if cover_type == "softcover":
        return round(pages / 444 + 0.06, 4)
    spine_csv = os.path.join(resources_dir, "spine_width.csv")
    if os.path.isfile(spine_csv):
        with open(spine_csv, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3 and int(row[0]) <= pages <= int(row[1]):
                    return float(row[2])
    return 0.5  # default fallback


def title_to_cover(title_command: str) -> str:
    prefix = r"\newcommand{\texttitle}{"
    inner = title_command[len(prefix):-1]
    words = inner.split()[::-1]
    return " ".join(words)


def make_cover(
    outputpath: str,
    cover_template: list[str],
    title: str,
    settings_dict: dict,
    pages: int,
    resources_dir: str,
) -> None:
    cover_out = outputpath.replace(".tex", "_cover.tex")
    spine = calc_spine_width(pages, settings_dict, resources_dir)
    cover_type = settings_dict.get("covertype", "softcover")

    with open(cover_out, "w", encoding="utf-8") as f:
        for line in cover_template:
            key = line.rstrip("\n")
            if key == "%hebtitle":
                f.write(title)
            elif key == "%backgroundcolor":
                f.write(
                    r"\definecolor{background}{HTML}{"
                    + settings_dict.get("covercolor", "FFFFFF")
                    + "}\n"
                )
            elif key == "%textcolor":
                f.write(
                    r"\definecolor{text}{HTML}{"
                    + settings_dict.get("covertextcolor", "000000")
                    + "}\n"
                )
            elif key == "%height":
                ph = float(settings_dict.get("paperheight", "9in").replace("in", ""))
                h = ph + 1.5 if cover_type == "hardcover" else ph
                f.write("coverheight=" + str(h) + "in,\n")
            elif key == "%width":
                pw = float(settings_dict.get("paperwidth", "6in").replace("in", ""))
                w = pw + 0.75 if cover_type == "hardcover" else pw
                f.write("coverwidth=" + str(w) + "in,\n")
            elif key == "%spinewidth":
                f.write("spinewidth=" + str(spine) + "in,\n")
            elif key == "%bleedwidth":
                f.write("bleedwidth=.125in,\n")
            elif "%spinetextheight" in key:
                h_txt = min(float(spine), 0.375)
                h_in = str(0.85 * h_txt)
                f.write(
                    r"\fontsize{" + h_in + r"in}{" + h_in + r"in}\selectfont"
                )
            elif "%backtext" in key:
                if settings_dict.get("backtext"):
                    f.write(settings_dict["backtext"])
            elif "%sethebfont" in key:
                f.write(r"\setmainfont{" + settings_dict.get("hebfont", "") + r"}")
            elif "%setengfont" in key:
                f.write(r"\newfontfamily\englishfont{" + settings_dict.get("engfont", "") + r"}")
            else:
                f.write(line if line.endswith("\n") else line + "\n")


# ── PDF compilation ───────────────────────────────────────────────────────────

def flip_pdf(pdf_path: str) -> None:
    """Rotate all pages 180° and save as <name>.rotated.pdf."""
    try:
        from pdfrw import PdfReader, PdfWriter
    except ImportError:
        return  # pdfrw not installed; skip rotation

    trailer = PdfReader(pdf_path)
    pages = trailer.pages
    for page in pages:
        current = int(page.inheritable.Rotate or 0)
        page.Rotate = (current + 180) % 360

    out_path = pdf_path.replace(".pdf", ".rotated.pdf")
    writer = PdfWriter(out_path)
    writer.trailer = trailer
    writer.write()


def compile_latex(output_tex: str, settings_dict: dict) -> int:
    """
    Run xelatex twice on *output_tex*, flip the PDF, return page count.
    """
    try:
        from pdfrw import PdfReader
    except ImportError:
        PdfReader = None  # type: ignore

    for _ in range(2):
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", output_tex],
            capture_output=True,
            cwd=os.path.dirname(os.path.abspath(output_tex)),
        )
        if result.returncode != 0:
            raise RuntimeError(
                "xelatex failed:\n" + result.stderr.decode(errors="replace")
            )

    pdf_path = output_tex.replace(".tex", ".pdf")
    flip_pdf(pdf_path)

    pages = 0
    if PdfReader and os.path.isfile(pdf_path):
        pages = len(PdfReader(pdf_path).pages)

    if pages and pages < 24 and settings_dict.get("covertype") == "hardcover":
        raise ValueError(
            "Hardcover books shorter than 24 pages cannot be printed on demand."
        )
    if pages >= 800:
        import warnings
        warnings.warn("PDF output is over 800 pages, which may be too long for POD.")

    return pages


# ── Main orchestration ────────────────────────────────────────────────────────

def writeoutput(
    outputpath: str,
    template: list[str],
    formatting: dict,
    links_dir: str,
    resources_dir: str,
) -> str:
    """
    Core orchestration function (ported from notebook cell 29).
    Fetches texts, generates LaTeX, writes *outputpath*.
    Returns the Hebrew title string for the cover.
    """
    sources: list[dict] = []
    parts: list[dict] = []

    template_with_settings = set_format(template, formatting)
    link_list = sefaria_svc.pull_links(links_dir)

    for text in formatting["texts"]:
        # Defaults
        if "translation" not in text:
            text["translation"] = ""
        if "range" not in text:
            text["range"] = "all"

        part_format: dict = dict(text.get("format") or {})
        # Merge global settings into per-part format (notebook behaviour)
        for k, v in formatting.items():
            if k != "texts" and k not in part_format:
                part_format[k] = v
        if part_format.get("layout") == "twocol":
            part_format["newpage"] = 0

        sefaria_json = sefaria_svc.pull_text(text["link"])
        sources.append(get_bib_info(sefaria_json))

        commentaries: list[dict] = []
        commentary_title = ""
        for commentary_link in (text.get("commentary") or []):
            comments_json = sefaria_svc.pull_text(commentary_link)
            bib = get_bib_info(comments_json)
            commentary_title = bib["heTitle"]
            sources.append(bib)
            commentaries.append(comments_json)

        english_json: dict | None = None
        if text["translation"]:
            english_json = sefaria_svc.pull_text(text["translation"])
            sources.append(get_bib_info(english_json))

        if isinstance(sefaria_json.get("text"), dict):
            sefaria_result = make_body_json(
                sefaria_json, english_json, part_format, commentaries, resources_dir
            )
        else:
            sefaria_result = make_body(
                sefaria_json, english_json, part_format, commentaries, link_list, resources_dir
            )

        content = limit_output(sefaria_result[1], text)

        if part_format.get("commentstyle") == "blocks" and text.get("commentary"):
            content = move_comments(content, commentary_title, formatting.get("newpage", 0))
            if part_format.get("newpage") == 1:
                content = block_fix(content)

        parts.append({"title": sefaria_result[2], "content": content})

    source_listing = print_source_data(sources)
    if source_listing and source_listing[0] == "NC":
        raise PermissionError(
            source_listing[1] + " has a license which does not allow creation of this text."
        )

    title_command = r"\newcommand{\texttitle}{" + formatting.get("titleheb", "") + "}"

    with open(outputpath, "w", encoding="utf-8") as outfile:
        for line in template_with_settings:
            stripped = line.rstrip("\n")
            if stripped == "%title_here":
                outfile.write(title_command + "\n")
            elif stripped == "%license info":
                for item in source_listing:
                    outfile.write(item + "\n")
            elif stripped == "%body_here":
                if len(parts) == 1:
                    for newline in parts[0]["content"]:
                        nl = newline.rstrip(" ")
                        outfile.write(nl + "\n")
                else:
                    for part_num, part in enumerate(parts):
                        outfile.write(
                            r"\addpart{"
                            + part["title"]
                            + r"}\renewcommand{\partname}[1]{"
                            + part["title"]
                            + "}\n"
                        )
                        for pf_line in add_part_format(part_num, formatting):
                            outfile.write(pf_line + "\n")
                        for newline in part["content"]:
                            outfile.write(newline + "\n")
            else:
                outfile.write(line if line.endswith("\n") else line + "\n")

    cover_title = title_to_cover(title_command)
    return formatting.get("title") or cover_title


# ── Public entry point (no live Sefaria calls) ────────────────────────────────

def generate_latex(config: dict) -> str:
    """Generate a complete LaTeX document from a config dict with pre-fetched text.

    Accepts either *nested* format (``config["format"]`` is a dict) or *flat*
    format (format keys at the top level).  Text entries must contain
    pre-fetched ``"he"`` (Hebrew) and optionally ``"text"`` (English) lists.

    Returns the full LaTeX document as a string.

    Raises:
        KeyError          – ``"texts"`` key is missing or empty.
        ValueError        – No format settings are present in the config.
        FileNotFoundError – Template file cannot be found.
    """
    # ── 1. Normalise: merge nested "format" sub-dict, or accept flat layout ──
    fmt = config.get("format")
    if isinstance(fmt, dict):
        book_name: str = config.get("name", "")
        flat: dict = {k: v for k, v in config.items() if k != "format"}
        flat.update(fmt)
    elif any(k in config for k in _GEOMETRY_KEYS | {"hebfont", "engfont", "fontsize"}):
        book_name = config.get("name", "")
        flat = dict(config)
    else:
        raise ValueError(
            "Config must include a 'format' sub-dict or top-level format keys "
            "(paperheight, hebfont, engfont, …)."
        )

    # ── 2. Validate required keys ────────────────────────────────────────────
    texts = flat.get("texts")
    if not texts:
        raise KeyError("'texts' key is required and must be non-empty in config")

    # ── 3. Resolve resources directory (with dev/test fallback) ─────────────
    resources_dir: str = settings.resources_dir
    if not os.path.isdir(resources_dir):
        _here = os.path.dirname(os.path.abspath(__file__))
        _candidate = os.path.normpath(
            os.path.join(_here, "..", "..", "..", "resources")
        )
        if os.path.isdir(_candidate):
            resources_dir = _candidate

    template_path = os.path.join(resources_dir, "input.tex")
    template_lines = pullinput(template_path)  # FileNotFoundError propagates naturally
    template_with_settings = set_format(template_lines, flat)

    # ── 4. Generate body for each text entry ─────────────────────────────────
    parts: list[dict] = []
    for text_entry in texts:
        # Ensure defaults that make_body expects
        if "translation" not in text_entry:
            text_entry = dict(text_entry, translation="")
        if "range" not in text_entry:
            text_entry = dict(text_entry, range="all")

        # Build per-part format by merging global settings (mirrors writeoutput)
        per_part_fmt: dict = dict(text_entry.get("format") or {})
        if hasattr(per_part_fmt, "model_dump"):
            per_part_fmt = {k: v for k, v in per_part_fmt.model_dump().items() if v is not None}
        for k, v in flat.items():
            if k != "texts" and k not in per_part_fmt:
                per_part_fmt[k] = v
        if per_part_fmt.get("layout") == "twocol":
            per_part_fmt["newpage"] = 0

        # Build synthetic Sefaria-style JSON from pre-fetched data
        raw_he = text_entry.get("he") or []
        raw_en = text_entry.get("text") or []
        link = text_entry.get("link", "Untitled")

        # make_body expects a list-of-lists (chapters → verses)
        if raw_he and not isinstance(raw_he[0], list):
            he_chapters = [raw_he]
        else:
            he_chapters = list(raw_he)

        sefaria_json: dict = {
            "heTitle": link,
            "title": link,
            "text": he_chapters,
            "sectionNames": ["Chapter", "Verse"],
        }

        english_json: dict | None = None
        if raw_en:
            en_chapters = [raw_en] if not isinstance(raw_en[0], list) else list(raw_en)
            english_json = {
                "heTitle": link,
                "title": link,
                "text": en_chapters,
                "sectionNames": ["Chapter", "Verse"],
            }

        sefaria_result = make_body(
            sefaria_json,
            english_json,
            per_part_fmt,
            [],          # no live commentary fetching
            [],          # no link_list
            resources_dir,
        )

        # Pre-fetched content is already scoped to the requested range,
        # so we skip chapter-index filtering (pass "range": "all").
        limit_entry = {**text_entry, "range": "all"}
        content = limit_output(sefaria_result[1], limit_entry)
        parts.append({"title": sefaria_result[2], "content": content})

    # ── 5. Assemble output by substituting template markers ──────────────────
    title_command = r"\newcommand{\texttitle}{" + flat.get("titleheb", "") + "}"
    backtext: str = flat.get("backtext", "")

    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".tex", delete=False, encoding="utf-8"
        ) as tmp:
            tmp_path = tmp.name
            for line in template_with_settings:
                stripped = line.rstrip("\n")
                if stripped == "%title_here":
                    if book_name:
                        tmp.write("% " + book_name + "\n")
                    tmp.write(title_command + "\n")
                    if backtext:
                        tmp.write(r"\newcommand{\backtext}{" + backtext + "}" + "\n")
                elif stripped == "%license info":
                    tmp.write("% license info\n")
                elif stripped == "%body_here":
                    if len(parts) == 1:
                        for nl in parts[0]["content"]:
                            tmp.write(nl.rstrip(" ") + "\n")
                    else:
                        for part_num, part in enumerate(parts):
                            tmp.write(
                                r"\addpart{"
                                + part["title"]
                                + r"}\renewcommand{\partname}[1]{"
                                + part["title"]
                                + "}\n"
                            )
                            for pf_line in add_part_format(part_num, flat):
                                tmp.write(pf_line + "\n")
                            for nl in part["content"]:
                                tmp.write(nl + "\n")
                else:
                    tmp.write(line if line.endswith("\n") else line + "\n")

        with open(tmp_path, encoding="utf-8") as f:
            return f.read()
    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
