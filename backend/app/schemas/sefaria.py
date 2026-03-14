from pydantic import BaseModel


class NameSearchResult(BaseModel):
    ref: str
    title: str
    heTitle: str
    type: str


class TextResolveResult(BaseModel):
    ref: str
    link: str
    heTitle: str
    title: str


class TextInfo(BaseModel):
    ref: str
    heTitle: str
    title: str
    categories: list[str]
    sectionNames: list[str]


class TextVersion(BaseModel):
    language: str
    versionTitle: str
    versionSource: str
    languageFamilyName: str


class CommentaryOption(BaseModel):
    title: str
    heTitle: str
