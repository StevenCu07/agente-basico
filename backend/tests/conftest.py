import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    db_file = tmp_path / "aulabot_test.db"
    os.environ["DB_PATH"] = str(db_file)
    os.environ["LLM_MODE"] = "mock"
    app = create_app()
    return TestClient(app)

