import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, patch

# Use SQLite for tests — no PostgreSQL needed in CI
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_client(db_session):
    from app.main import app
    from app.database import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_book_config():
    """Flat-format config matching BookConfigCreate schema."""
    return {
        "name": "Test Book",
        "texts": [
            {
                "link": "Genesis 1",
                "commentary": [],
                "translation": "",
                "range": "all",
            }
        ],
        # Global format fields at top level (not nested under "format")
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
        "fontsize": 12.0,
        "spacing": 1.5,
        "engfontsize": 10.0,
        "parskip": "6pt",
        "layout": "",
        "twocolfootnotes": 0,
        "newpage": 0,
        "pagenumloc": "bottom",
        "pagenumheb": 0,
        "headpos": "",
        "evenhead": "",
        "oddhead": "",
        "chapfontsize": 14.0,
        "covercolor": "1a3a5c",
        "covertextcolor": "ffffff",
        "covertype": "softcover",
        "backtext": "",
        "titleheb": "בראשית",
    }


@pytest.fixture
def mock_sefaria_text_response():
    return {
        "ref": "Genesis 1",
        "title": "Genesis",
        "heTitle": "בראשית",
        "text": ["In the beginning..."],
        "he": ["בְּרֵאשִׁית..."],
    }
