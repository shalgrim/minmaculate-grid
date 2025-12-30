"""
Tests for franchise_mapper module.

Following TDD: Write tests first, then implement src/franchise_mapper.py
"""

# Add src to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.franchise_mapper import (
    get_current_franchises,
    get_franchise_for_team,
    load_franchise_mapping,
)

# Test data paths
DATA_DIR = Path(__file__).parent.parent / "data"
TEAMS_CSV = DATA_DIR / "Teams.csv"


class TestLoadFranchiseMapping:
    """Tests for load_franchise_mapping function."""

    def test_load_franchise_mapping_returns_dict(self):
        """Test that franchise mapping returns a dictionary."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

    def test_franchise_mapping_has_brooklyn_dodgers(self):
        """Test BRO maps to LAD (Dodgers franchise)."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        assert "BRO" in mapping
        assert mapping["BRO"] == "LAD"

    def test_franchise_mapping_has_expos_nationals(self):
        """Test MON maps to WSN (Nationals franchise)."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        assert "MON" in mapping
        assert mapping["MON"] == "WSN"

    def test_franchise_mapping_has_current_teams(self):
        """Test modern teamIDs map to their franchises."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        # Modern teams map to their franchise IDs
        assert mapping["NYA"] == "NYY"  # Yankees: teamID → franchID
        assert mapping["BOS"] == "BOS"  # Red Sox: teamID == franchID
        assert mapping["LAN"] == "LAD"  # Dodgers: teamID → franchID

    def test_all_teams_have_franchise_mapping(self):
        """Test no teamID is unmapped."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        # Check that all values are non-empty strings
        for team_id, franchise_id in mapping.items():
            assert isinstance(team_id, str)
            assert isinstance(franchise_id, str)
            assert len(franchise_id) > 0


class TestGetCurrentFranchises:
    """Tests for get_current_franchises function."""

    def test_get_current_franchises_returns_set(self):
        """Test function returns a set."""
        franchises = get_current_franchises(str(TEAMS_CSV))
        assert isinstance(franchises, set)

    def test_get_current_franchises_returns_30(self):
        """Test exactly 30 current franchises."""
        franchises = get_current_franchises(str(TEAMS_CSV))
        assert len(franchises) == 30

    def test_current_franchises_include_known_teams(self):
        """Test current franchises include well-known teams."""
        franchises = get_current_franchises(str(TEAMS_CSV))

        # Check some well-known current franchises
        expected_franchises = {
            "NYY",  # Yankees
            "BOS",  # Red Sox
            "LAD",  # Dodgers
            "SFG",  # Giants
            "CHC",  # Cubs
            "WSN",  # Nationals
            "ANA",  # Angels
            "ARI",  # Diamondbacks
        }

        assert expected_franchises.issubset(franchises)

    def test_current_franchises_exclude_defunct_teams(self):
        """Test defunct franchises are excluded."""
        franchises = get_current_franchises(str(TEAMS_CSV))

        # These franchises no longer exist as separate entities
        defunct_franchises = {
            "BNA",  # Boston Red Stockings (1870s)
            "CNA",  # Chicago White Stockings (1870s)
            "KEK",  # Fort Wayne Kekiongas (1871)
        }

        assert defunct_franchises.isdisjoint(franchises)


class TestGetFranchiseForTeam:
    """Tests for get_franchise_for_team helper function."""

    def test_get_franchise_for_team_with_valid_team(self):
        """Test getting franchise for a valid teamID."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        franchise = get_franchise_for_team("BRO", mapping)
        assert franchise == "LAD"

    def test_get_franchise_for_team_with_modern_team(self):
        """Test getting franchise for modern teamID."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        franchise = get_franchise_for_team("NYA", mapping)  # Yankees teamID
        assert franchise == "NYY"  # Yankees franchID

    def test_get_franchise_for_team_with_invalid_team(self):
        """Test getting franchise for invalid teamID returns None or raises error."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        # Invalid team should return None or raise KeyError
        result = get_franchise_for_team("INVALID", mapping)
        assert result is None


class TestFranchiseConsistency:
    """Integration tests for franchise mapping consistency."""

    def test_brooklyn_and_la_dodgers_same_franchise(self):
        """Test historical Brooklyn and modern LA Dodgers map to same franchise."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        # BRO (Brooklyn) and LAN (LA) both map to LAD franchise
        assert mapping["BRO"] == mapping["LAN"] == "LAD"

    def test_expos_and_nationals_same_franchise(self):
        """Test Expos and Nationals map to same franchise."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        assert mapping["MON"] == mapping["WAS"] == "WSN"

    def test_all_current_teams_map_to_current_franchises(self):
        """Test all current teamIDs map to current franchises."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        current_franchises = get_current_franchises(str(TEAMS_CSV))

        # Get 2024 teams from file
        import pandas as pd

        teams_df = pd.read_csv(TEAMS_CSV)
        teams_2024 = teams_df[teams_df["yearID"] == 2024]["teamID"].unique()

        # All 2024 teams should map to current franchises
        for team_id in teams_2024:
            franchise = mapping.get(team_id)
            assert franchise is not None
            assert franchise in current_franchises
