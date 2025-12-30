"""
Tests for greedy solver module.

Following TDD: Write tests first, then implement src/solver_greedy.py
"""

import pytest
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.solver_greedy import greedy_set_cover


class TestGreedySolver:
    """Tests for greedy set cover algorithm."""

    def test_greedy_with_small_instance(self):
        """Test greedy on minimal hand-crafted example."""
        # 3 franchises: A, B, C
        # Pairs: (A,B), (A,C), (B,C)
        # Player 1 covers (A,B) and (A,C)
        # Player 2 covers (B,C)
        # Player 3 covers (A,B)
        # Optimal solution: {Player 1, Player 2} = 2 players

        player_pairs = {
            "player1": {("A", "B"), ("A", "C")},  # 2 pairs
            "player2": {("B", "C")},              # 1 pair
            "player3": {("A", "B")},              # 1 pair (redundant)
        }

        all_pairs = {("A", "B"), ("A", "C"), ("B", "C")}

        player_info = {
            "player1": {"nameFirst": "P1", "nameLast": "One"},
            "player2": {"nameFirst": "P2", "nameLast": "Two"},
            "player3": {"nameFirst": "P3", "nameLast": "Three"},
        }

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Greedy should select 2 players (optimal)
        assert len(selected) <= 3
        assert isinstance(selected, list)

        # Verify all pairs are covered
        covered = set()
        for player_id in selected:
            covered.update(player_pairs[player_id])
        assert covered == all_pairs

    def test_greedy_covers_all_pairs(self):
        """Test greedy solution covers all pairs."""
        # Simple 4-franchise example
        player_pairs = {
            "p1": {("A", "B"), ("A", "C"), ("A", "D")},
            "p2": {("B", "C"), ("B", "D")},
            "p3": {("C", "D")},
        }

        all_pairs = {("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"), ("C", "D")}

        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Verify all pairs covered
        covered = set()
        for player_id in selected:
            covered.update(player_pairs[player_id])
        assert covered == all_pairs

    def test_greedy_selects_at_least_one_player(self):
        """Test greedy returns non-empty player list."""
        player_pairs = {
            "p1": {("A", "B")},
        }
        all_pairs = {("A", "B")}
        player_info = {"p1": {"nameFirst": "P1", "nameLast": ""}}

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        assert len(selected) >= 1
        assert "p1" in selected

    def test_greedy_is_deterministic(self):
        """Test same input produces same output."""
        player_pairs = {
            "p1": {("A", "B"), ("A", "C")},
            "p2": {("B", "C")},
        }
        all_pairs = {("A", "B"), ("A", "C"), ("B", "C")}
        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        result1, stats1 = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)
        result2, stats2 = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Results should be identical
        assert result1 == result2
        assert stats1["iterations"] == stats2["iterations"]

    def test_greedy_selects_best_player_first(self):
        """Test first player selected covers most pairs."""
        # Player 1 covers 10 pairs, Player 2 covers 1 pair
        player_pairs = {
            "super_player": {("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"), ("B", "C"),
                            ("B", "D"), ("B", "E"), ("C", "D"), ("C", "E"), ("D", "E")},
            "normal_player": {("A", "B")},
        }

        all_pairs = {("A", "B"), ("A", "C"), ("A", "D"), ("A", "E"), ("B", "C"),
                    ("B", "D"), ("B", "E"), ("C", "D"), ("C", "E"), ("D", "E")}

        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # First player should be the one with most coverage
        assert selected[0] == "super_player"
        assert len(selected) == 1  # Only need one player!

    def test_greedy_returns_stats(self):
        """Test greedy returns statistics dictionary."""
        player_pairs = {
            "p1": {("A", "B")},
        }
        all_pairs = {("A", "B")}
        player_info = {"p1": {"nameFirst": "P1", "nameLast": ""}}

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Check stats structure
        assert isinstance(stats, dict)
        assert "iterations" in stats
        assert "players_selected" in stats
        assert "pairs_covered_per_iteration" in stats
        assert isinstance(stats["iterations"], list)
        assert len(stats["iterations"]) == len(selected)

    def test_greedy_handles_no_solution(self):
        """Test greedy when solution is impossible."""
        # No player covers pair (A, B)
        player_pairs = {
            "p1": {("A", "C")},
            "p2": {("B", "C")},
        }
        all_pairs = {("A", "B"), ("A", "C"), ("B", "C")}
        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Should return partial solution
        assert isinstance(selected, list)

        # Check covered pairs
        covered = set()
        for player_id in selected:
            covered.update(player_pairs[player_id])

        # Should cover 2 out of 3 pairs
        assert len(covered) == 2
        assert ("A", "B") not in covered

    def test_greedy_with_tie_breaking(self):
        """Test greedy handles ties (multiple players with same coverage)."""
        # Two players cover same pairs
        player_pairs = {
            "p1": {("A", "B")},
            "p2": {("A", "B")},  # Identical coverage
            "p3": {("C", "D")},
        }
        all_pairs = {("A", "B"), ("C", "D")}
        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Should select 2 players total
        assert len(selected) == 2

        # One of p1 or p2, plus p3
        assert "p3" in selected
        assert ("p1" in selected) or ("p2" in selected)


class TestGreedyPerformance:
    """Performance and edge case tests."""

    def test_greedy_with_empty_player_pairs(self):
        """Test greedy with player who has no pairs."""
        player_pairs = {
            "p1": {("A", "B")},
            "p2": set(),  # No pairs
        }
        all_pairs = {("A", "B")}
        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Should only select p1
        assert selected == ["p1"]

    def test_greedy_verbose_mode(self):
        """Test greedy with verbose=True (should not crash)."""
        player_pairs = {
            "p1": {("A", "B")},
        }
        all_pairs = {("A", "B")}
        player_info = {"p1": {"nameFirst": "Test", "nameLast": "Player"}}

        # Should not crash with verbose=True
        selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info, verbose=True)

        assert len(selected) == 1
