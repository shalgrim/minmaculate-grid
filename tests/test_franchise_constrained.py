"""
Tests for franchise-constrained solver functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import filter_players_by_franchise


class TestFilterPlayersByFranchise:
    """Tests for filter_players_by_franchise function."""

    def test_filter_includes_correct_players(self):
        """Test that filter includes only players who played for target franchise."""
        player_pairs = {
            "player1": {("ARI", "ATL"), ("ATL", "BOS")},  # plays for NYY
            "player2": {("LAD", "MIN")},  # plays for NYY
            "player3": {("CHC", "CHW")},  # does NOT play for NYY
        }
        player_franchises = {
            "player1": {"NYY", "BOS", "ATL"},
            "player2": {"NYY", "LAD", "MIN"},
            "player3": {"CHC", "CHW"},
        }

        filtered = filter_players_by_franchise(player_pairs, player_franchises, "NYY")

        assert "player1" in filtered
        assert "player2" in filtered
        assert "player3" not in filtered

    def test_filter_preserves_pairs_for_included_players(self):
        """Test that pairs are preserved for included players."""
        player_pairs = {
            "player1": {("ARI", "ATL"), ("ATL", "BOS")},
            "player2": {("LAD", "MIN")},
        }
        player_franchises = {
            "player1": {"NYY", "BOS"},
            "player2": {"BOS"},
        }

        filtered = filter_players_by_franchise(player_pairs, player_franchises, "NYY")

        assert len(filtered) == 1
        assert "player1" in filtered
        assert filtered["player1"] == {("ARI", "ATL"), ("ATL", "BOS")}

    def test_filter_empty_result_when_no_match(self):
        """Test that filter returns empty dict when no players match."""
        player_pairs = {
            "player1": {("ARI", "ATL")},
            "player2": {("LAD", "MIN")},
        }
        player_franchises = {
            "player1": {"BOS"},
            "player2": {"CHC"},
        }

        filtered = filter_players_by_franchise(player_pairs, player_franchises, "NYY")

        assert len(filtered) == 0

    def test_filter_handles_missing_player_in_franchises(self):
        """Test that filter handles players missing from player_franchises."""
        player_pairs = {
            "player1": {("ARI", "ATL")},
            "player2": {("LAD", "MIN")},
        }
        player_franchises = {
            "player1": {"NYY"},
            # player2 not in player_franchises
        }

        filtered = filter_players_by_franchise(player_pairs, player_franchises, "NYY")

        assert len(filtered) == 1
        assert "player1" in filtered

    def test_filter_with_single_franchise_player(self):
        """Test that player with only target franchise is included."""
        player_pairs = {
            "player1": set(),  # No pairs (only played for one franchise)
        }
        player_franchises = {
            "player1": {"NYY"},
        }

        filtered = filter_players_by_franchise(player_pairs, player_franchises, "NYY")

        assert len(filtered) == 1
        assert "player1" in filtered
        assert filtered["player1"] == set()


class TestFranchiseConstrainedIntegration:
    """Integration tests for franchise-constrained functionality."""

    def test_all_solution_players_played_for_target_franchise(self):
        """Test that all players in filtered set played for target franchise."""
        player_pairs = {
            "p1": {("ARI", "ATL"), ("ATL", "BOS")},
            "p2": {("LAD", "MIN"), ("MIN", "NYY")},
            "p3": {("CHC", "CHW"), ("CHW", "CIN")},
            "p4": {("ARI", "BOS")},
        }
        player_franchises = {
            "p1": {"MIN", "ATL", "BOS"},  # Played for MIN
            "p2": {"LAD", "MIN", "NYY"},  # Played for MIN
            "p3": {"CHC", "CHW", "CIN"},  # Did NOT play for MIN
            "p4": {"ARI", "BOS"},  # Did NOT play for MIN
        }

        filtered = filter_players_by_franchise(player_pairs, player_franchises, "MIN")

        # Verify all players in result played for MIN
        for player_id in filtered:
            assert "MIN" in player_franchises[player_id], (
                f"Player {player_id} did not play for MIN"
            )

    def test_filter_is_case_sensitive(self):
        """Test that franchise matching is case sensitive."""
        player_pairs = {
            "player1": {("ARI", "ATL")},
        }
        player_franchises = {
            "player1": {"NYY"},
        }

        # Lowercase should not match uppercase
        filtered = filter_players_by_franchise(player_pairs, player_franchises, "nyy")

        assert len(filtered) == 0
