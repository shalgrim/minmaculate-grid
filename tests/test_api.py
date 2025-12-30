"""
Tests for FastAPI web API.

Following TDD: Testing all API endpoints with FastAPI TestClient.
"""

import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database

# Import app after path is set
from web.api import app


@pytest.fixture
def test_db():
    """Create a temporary test database with sample data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db_path = Path(tmpdir) / "test.db"

        # Setup test data (disable thread checking for testing)
        db = Database(str(test_db_path), check_same_thread=False)

        # Insert test players
        db.insert_player("test01", "Test", "Player", "2020-01-01")
        db.insert_player("test02", "Another", "Player", "2021-01-01")
        db.insert_player("test03", "Third", "Player", "2022-01-01")

        # Insert franchise pairs
        pair_id_1 = db.insert_franchise_pair("NYY", "BOS")
        pair_id_2 = db.insert_franchise_pair("LAD", "SFG")
        pair_id_3 = db.insert_franchise_pair("NYY", "LAD")

        # Insert player coverage
        db.add_player_coverage("test01", pair_id_1)  # test01 covers NYY-BOS
        db.add_player_coverage("test01", pair_id_3)  # test01 covers NYY-LAD
        db.add_player_coverage("test02", pair_id_2)  # test02 covers LAD-SFG

        # Insert a test solution
        solution_id = db.save_solution(
            algorithm="greedy",
            player_ids=["test01", "test02"],
            num_players=2,
            runtime=0.5,
            coverage=100.0,
        )

        yield db, str(test_db_path)

        db.close()


@pytest.fixture
def client(test_db):
    """Create test client with test database."""
    db, test_db_path = test_db

    # Override the database path in the app
    import web.api

    original_db = web.api.db
    web.api.db = db

    client = TestClient(app)
    yield client

    # Cleanup
    web.api.db = original_db


class TestAPIHealth:
    """Tests for API health and basic functionality."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["players"] >= 3  # We inserted 3 test players

    def test_root_endpoint(self, client):
        """Test root endpoint serves HTML."""
        response = client.get("/")
        # Should serve HTML file
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestPlayersEndpoints:
    """Tests for player-related endpoints."""

    def test_get_players(self, client):
        """Test GET /api/players."""
        response = client.get("/api/players")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least our 3 test players

        # Check structure
        player = data[0]
        assert "player_id" in player
        assert "full_name" in player
        assert "debut" in player

    def test_get_players_pagination(self, client):
        """Test pagination parameters."""
        response = client.get("/api/players?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_player_detail(self, client):
        """Test GET /api/players/{player_id}."""
        response = client.get("/api/players/test01")
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == "test01"
        assert data["name_first"] == "Test"
        assert data["full_name"] == "Test Player"
        assert "pairs_covered" in data
        assert data["num_pairs"] == 2  # test01 covers 2 pairs

    def test_get_nonexistent_player(self, client):
        """Test 404 for nonexistent player."""
        response = client.get("/api/players/invalid")
        assert response.status_code == 404


class TestSolutionsEndpoints:
    """Tests for solution-related endpoints."""

    def test_get_solutions(self, client):
        """Test GET /api/solutions."""
        response = client.get("/api/solutions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least our test solution

        # Check structure
        solution = data[0]
        assert "algorithm" in solution
        assert "num_players" in solution
        assert "runtime_seconds" in solution
        assert "coverage_percentage" in solution

    def test_get_solution_detail(self, client):
        """Test GET /api/solutions/{id}."""
        # Get first solution
        solutions = client.get("/api/solutions").json()
        solution_id = solutions[0]["id"]

        response = client.get(f"/api/solutions/{solution_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["algorithm"] == "greedy"
        assert "players" in data
        assert len(data["players"]) == 2  # Our test solution has 2 players

        # Check player structure
        player = data["players"][0]
        assert "player_id" in player
        assert "full_name" in player
        assert "rank" in player
        assert "num_pairs" in player

    def test_get_nonexistent_solution(self, client):
        """Test 404 for nonexistent solution."""
        response = client.get("/api/solutions/9999")
        assert response.status_code == 404


class TestPairsEndpoints:
    """Tests for franchise pair endpoints."""

    def test_get_all_pairs(self, client):
        """Test GET /api/pairs."""
        response = client.get("/api/pairs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # We inserted 3 pairs

        # Check structure
        pair = data[0]
        assert "id" in pair
        assert "franchise_1" in pair
        assert "franchise_2" in pair

    def test_get_pair_coverage(self, client):
        """Test GET /api/pairs/{f1}/{f2}."""
        response = client.get("/api/pairs/NYY/BOS")
        assert response.status_code == 200
        data = response.json()
        assert data["franchise_1"] == "BOS"  # Sorted
        assert data["franchise_2"] == "NYY"
        assert data["num_players"] >= 1
        assert isinstance(data["players"], list)

    def test_get_pair_coverage_reversed(self, client):
        """Test pair lookup works regardless of order."""
        response = client.get("/api/pairs/BOS/NYY")
        assert response.status_code == 200
        data = response.json()
        assert data["franchise_1"] == "BOS"  # Still sorted
        assert data["franchise_2"] == "NYY"

    def test_get_nonexistent_pair(self, client):
        """Test 404 for nonexistent franchise pair."""
        response = client.get("/api/pairs/INVALID1/INVALID2")
        assert response.status_code == 404


class TestCoverageMatrix:
    """Tests for coverage matrix endpoint."""

    def test_get_coverage_matrix(self, client):
        """Test GET /api/coverage-matrix."""
        response = client.get("/api/coverage-matrix")
        assert response.status_code == 200
        data = response.json()

        assert "franchises" in data
        assert "matrix" in data
        assert isinstance(data["franchises"], list)
        assert isinstance(data["matrix"], list)

        # Matrix should be square
        n = len(data["franchises"])
        assert len(data["matrix"]) == n
        if n > 0:
            assert all(len(row) == n for row in data["matrix"])
