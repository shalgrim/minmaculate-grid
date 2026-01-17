"""
Tests for SQLite database module.

Following TDD: Write tests first, then implement src/database.py
"""

# Add src to path
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database


class TestDatabaseCreation:
    """Tests for database creation and schema."""

    def test_database_creates_file(self):
        """Test database file is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            assert db_path.exists()
            db.close()

    def test_database_has_players_table(self):
        """Test players table exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            # Query to check if table exists
            result = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='players'"
            )
            assert len(result) == 1
            db.close()

    def test_database_has_franchise_pairs_table(self):
        """Test franchise_pairs table exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            result = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='franchise_pairs'"
            )
            assert len(result) == 1
            db.close()

    def test_database_has_solutions_table(self):
        """Test solutions table exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            result = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='solutions'"
            )
            assert len(result) == 1
            db.close()


class TestPlayerOperations:
    """Tests for player CRUD operations."""

    def test_insert_player(self):
        """Test inserting a player."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player(
                player_id="testid",
                name_first="Test",
                name_last="Player",
                debut="2020-01-01",
            )

            players = db.get_all_players()
            assert len(players) == 1
            assert players[0]["player_id"] == "testid"
            db.close()

    def test_get_player_by_id(self):
        """Test retrieving a player by ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "John", "Doe", "2020-01-01")

            player = db.get_player("p1")
            assert player is not None
            assert player["name_first"] == "John"
            assert player["name_last"] == "Doe"
            db.close()

    def test_get_nonexistent_player(self):
        """Test getting player that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            player = db.get_player("nonexistent")
            assert player is None
            db.close()


class TestFranchisePairOperations:
    """Tests for franchise pair operations."""

    def test_insert_franchise_pair(self):
        """Test inserting a franchise pair."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_franchise_pair("NYY", "BOS")

            pairs = db.get_all_franchise_pairs()
            assert len(pairs) == 1
            assert pairs[0]["franchise_1"] == "BOS"  # Should be sorted
            assert pairs[0]["franchise_2"] == "NYY"
            db.close()

    def test_franchise_pair_sorted(self):
        """Test pairs are stored sorted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            # Insert in reverse order
            db.insert_franchise_pair("ZZZ", "AAA")

            pairs = db.get_all_franchise_pairs()
            assert pairs[0]["franchise_1"] == "AAA"
            assert pairs[0]["franchise_2"] == "ZZZ"
            db.close()


class TestSolutionOperations:
    """Tests for solution storage and retrieval."""

    def test_save_solution(self):
        """Test saving a solution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            # Insert test players first
            db.insert_player("p1", "Player", "One", "2020-01-01")
            db.insert_player("p2", "Player", "Two", "2020-01-01")

            # Save solution
            player_ids = ["p1", "p2"]
            solution_id = db.save_solution(
                algorithm="greedy",
                player_ids=player_ids,
                num_players=2,
                runtime=0.1,
                coverage=100.0,
            )

            assert solution_id is not None
            db.close()

    def test_get_solution(self):
        """Test retrieving a solution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")

            solution_id = db.save_solution(
                algorithm="exact",
                player_ids=["p1"],
                num_players=1,
                runtime=5.0,
                coverage=100.0,
            )

            solution = db.get_solution(solution_id)
            assert solution is not None
            assert solution["algorithm"] == "exact"
            assert solution["num_players"] == 1
            db.close()

    def test_get_latest_solution_by_algorithm(self):
        """Test getting most recent solution for an algorithm."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")

            # Save two greedy solutions
            db.save_solution("greedy", ["p1"], 1, 0.1, 100.0)
            db.save_solution("greedy", ["p1"], 1, 0.2, 100.0)

            latest = db.get_latest_solution("greedy")
            assert latest is not None
            assert latest["algorithm"] == "greedy"
            db.close()


class TestPlayerCoverage:
    """Tests for player coverage (which pairs each player covers)."""

    def test_save_player_coverage(self):
        """Test saving which pairs a player covers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")
            db.insert_franchise_pair("NYY", "BOS")

            pair_id = db.get_all_franchise_pairs()[0]["id"]

            db.add_player_coverage("p1", pair_id)

            coverage = db.get_player_coverage("p1")
            assert len(coverage) == 1
            db.close()

    def test_get_players_covering_pair(self):
        """Test finding all players that cover a specific pair."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")
            db.insert_player("p2", "Player", "Two", "2020-01-01")
            db.insert_franchise_pair("NYY", "BOS")

            pair_id = db.get_all_franchise_pairs()[0]["id"]

            db.add_player_coverage("p1", pair_id)
            db.add_player_coverage("p2", pair_id)

            players = db.get_players_covering_pair(pair_id)
            assert len(players) == 2
            db.close()


class TestPlayerFranchises:
    """Tests for player franchise operations."""

    def test_database_has_player_franchises_table(self):
        """Test player_franchises table exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            result = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='player_franchises'"
            )
            assert len(result) == 1
            db.close()

    def test_add_player_franchise(self):
        """Test adding a player-franchise relationship."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")
            db.add_player_franchise("p1", "NYY")

            franchises = db.get_player_franchises("p1")
            assert len(franchises) == 1
            assert franchises[0] == "NYY"
            db.close()

    def test_add_multiple_franchises_for_player(self):
        """Test adding multiple franchises for a player."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")
            db.add_player_franchise("p1", "NYY")
            db.add_player_franchise("p1", "BOS")
            db.add_player_franchise("p1", "LAD")

            franchises = db.get_player_franchises("p1")
            assert len(franchises) == 3
            assert "NYY" in franchises
            assert "BOS" in franchises
            assert "LAD" in franchises
            db.close()

    def test_add_duplicate_franchise_ignored(self):
        """Test that duplicate franchise entries are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")
            db.add_player_franchise("p1", "NYY")
            db.add_player_franchise("p1", "NYY")  # Duplicate

            franchises = db.get_player_franchises("p1")
            assert len(franchises) == 1
            db.close()

    def test_get_players_for_franchise(self):
        """Test getting all players for a franchise."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            db.insert_player("p1", "Player", "One", "2020-01-01")
            db.insert_player("p2", "Player", "Two", "2020-01-01")
            db.insert_player("p3", "Player", "Three", "2020-01-01")

            db.add_player_franchise("p1", "NYY")
            db.add_player_franchise("p2", "NYY")
            db.add_player_franchise("p3", "BOS")

            nyy_players = db.get_players_for_franchise("NYY")
            assert len(nyy_players) == 2
            player_ids = [p["player_id"] for p in nyy_players]
            assert "p1" in player_ids
            assert "p2" in player_ids
            db.close()

    def test_get_players_for_franchise_empty(self):
        """Test getting players for franchise with no players."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            players = db.get_players_for_franchise("NYY")
            assert len(players) == 0
            db.close()

    def test_get_player_franchises_empty(self):
        """Test getting franchises for player with no franchises."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            db = Database(str(db_path))

            franchises = db.get_player_franchises("nonexistent")
            assert len(franchises) == 0
            db.close()
