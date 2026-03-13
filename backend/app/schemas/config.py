from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class TextFormatOverride(BaseModel):
    """Per-text format overrides – any subset of the global format fields."""
    hebfont: Optional[str] = None
    fontsize: Optional[float] = None
    spacing: Optional[float] = None
    commentstyle: Optional[str] = None
    commentfont: Optional[str] = None
    oddhead: Optional[str] = None
    evenhead: Optional[str] = None
    newpage: Optional[int] = None
    layout: Optional[str] = None
    engfontsize: Optional[float] = None


class TextEntry(BaseModel):
    link: str = Field(..., description="Sefaria text path, e.g. 'Mishnah_Avot'")
    commentary: list[str] = Field(default_factory=list)
    translation: str = ""
    range: str = "all"
    dafrange: Optional[str] = None
    format: TextFormatOverride = Field(default_factory=TextFormatOverride)


class BookConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = None
    texts: list[TextEntry] = Field(..., min_length=1)
    # Global format settings
    paperheight: str = "9in"
    paperwidth: str = "6in"
    top: str = "0.75in"
    bottom: str = "0.75in"
    inner: str = "0.75in"
    outer: str = "0.75in"
    hebfont: str = "David CLM"
    hebboldfont: str = ""
    engfont: str = "Linux Libertine O"
    commentfont: str = ""
    fontsize: float = 12.0
    spacing: float = 1.5
    engfontsize: float = 10.0
    chapfontsize: float = 14.0
    newpage: int = Field(0, ge=0, le=2)
    layout: str = ""
    twocolfootnotes: int = 0
    parskip: str = "6pt"
    colsep: str = "0.25in"
    pagenumloc: str = "bottom"
    pagenumheb: int = 0
    headpos: str = "center"
    evenhead: str = "title"
    oddhead: str = "chapter"
    commentstyle: str = ""
    covercolor: str = "FFFFFF"
    covertextcolor: str = "000000"
    covertype: str = "softcover"
    backtext: str = ""
    titleheb: str = ""
    title: Optional[str] = None


class BookConfigResponse(BookConfigCreate):
    id: str
    created_at: str
    updated_at: str
    format: dict = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class BookConfigListItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


def config_to_dict(cfg: BookConfigCreate) -> dict:
    """Return the flat dict that the notebook-ported functions expect."""
    return cfg.model_dump(exclude={"name", "description"})
