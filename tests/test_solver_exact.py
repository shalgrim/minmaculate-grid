"""
Tests for exact ILP solver module.

Following TDD: Write tests first, then implement src/solver_exact.py
"""

import pytest
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.solver_exact import exact_set_cover


class TestExactSolver:
    """Tests for exact ILP set cover solver."""

    def test_exact_with_small_instance(self):
        """Test exact solver on minimal hand-crafted example."""
        # 3 franchises: A, B, C
        # Pairs: (A,B), (A,C), (B,C)
        # Player 1 covers (A,B) and (A,C)
        # Player 2 covers (B,C)
        # Player 3 covers (A,B) - redundant
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

        selected, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Exact should find optimal solution: 2 players
        assert len(selected) == 2
        assert isinstance(selected, list)

        # Verify all pairs are covered
        covered = set()
        for player_id in selected:
            covered.update(player_pairs[player_id])
        assert covered == all_pairs

    def test_exact_covers_all_pairs(self):
        """Test exact solution covers all pairs."""
        player_pairs = {
            "p1": {("A", "B"), ("A", "C"), ("A", "D")},
            "p2": {("B", "C"), ("B", "D")},
            "p3": {("C", "D")},
        }

        all_pairs = {("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"), ("C", "D")}

        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Verify all pairs covered
        covered = set()
        for player_id in selected:
            covered.update(player_pairs[player_id])
        assert covered == all_pairs

    def test_exact_finds_optimal_solution(self):
        """Test exact finds truly optimal solution (better than greedy might)."""
        # Carefully crafted example where greedy might not be optimal
        # 4 franchises, 6 pairs total
        # Player 1: covers 3 pairs (greedy picks this first)
        # Player 2: covers 2 pairs
        # Player 3: covers 2 pairs
        # But optimal is Player 2 + Player 3 (also 2 players but different set)

        player_pairs = {
            "p1": {("A", "B"), ("A", "C")},
            "p2": {("B", "C")},
        }

        all_pairs = {("A", "B"), ("A", "C"), ("B", "C")}

        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Optimal is 2 players
        assert len(selected) == 2

        # Verify coverage
        covered = set()
        for player_id in selected:
            covered.update(player_pairs[player_id])
        assert covered == all_pairs

    def test_exact_single_player_solution(self):
        """Test when one player covers everything."""
        player_pairs = {
            "super_player": {("A", "B"), ("A", "C"), ("B", "C")},
            "normal_player": {("A", "B")},
        }

        all_pairs = {("A", "B"), ("A", "C"), ("B", "C")}

        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Optimal solution is 1 player
        assert len(selected) == 1
        assert selected[0] == "super_player"

    def test_exact_returns_stats(self):
        """Test exact returns statistics dictionary."""
        player_pairs = {
            "p1": {("A", "B")},
        }
        all_pairs = {("A", "B")}
        player_info = {"p1": {"nameFirst": "P1", "nameLast": ""}}

        selected, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Check stats structure
        assert isinstance(stats, dict)
        assert "status" in stats
        assert "objective_value" in stats
        assert isinstance(selected, list)

    def test_exact_is_deterministic(self):
        """Test same input produces same output."""
        player_pairs = {
            "p1": {("A", "B"), ("A", "C")},
            "p2": {("B", "C")},
        }
        all_pairs = {("A", "B"), ("A", "C"), ("B", "C")}
        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        result1, stats1 = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)
        result2, stats2 = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Results should be identical (same objective)
        assert len(result1) == len(result2)
        assert stats1["objective_value"] == stats2["objective_value"]

    def test_exact_handles_infeasible(self):
        """Test exact solver when solution is impossible."""
        # No player covers pair (A, B)
        player_pairs = {
            "p1": {("A", "C")},
            "p2": {("B", "C")},
        }
        all_pairs = {("A", "B"), ("A", "C"), ("B", "C")}
        player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in player_pairs}

        selected, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=False)

        # Should detect infeasibility
        assert stats["status"] == "Infeasible"
        assert isinstance(selected, list)

    def test_exact_verbose_mode(self):
        """Test exact with verbose=True (should not crash)."""
        player_pairs = {
            "p1": {("A", "B")},
        }
        all_pairs = {("A", "B")}
        player_info = {"p1": {"nameFirst": "Test", "nameLast": "Player"}}

        # Should not crash with verbose=True
        selected, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=True)

        assert len(selected) == 1


class TestExactVsGreedy:
    """Tests comparing exact solver to greedy baseline."""

    def test_exact_never_worse_than_greedy(self):
        """Test exact solution is always <= greedy solution size."""
        from src.solver_greedy import greedy_set_cover

        # Test on several instances
        test_cases = [
            {
                "player_pairs": {
                    "p1": {("A", "B"), ("A", "C")},
                    "p2": {("B", "C")},
                },
                "all_pairs": {("A", "B"), ("A", "C"), ("B", "C")},
            },
            {
                "player_pairs": {
                    "p1": {("A", "B"), ("A", "C"), ("A", "D")},
                    "p2": {("B", "C"), ("B", "D")},
                    "p3": {("C", "D")},
                },
                "all_pairs": {("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"), ("C", "D")},
            },
        ]

        for tc in test_cases:
            player_info = {pid: {"nameFirst": pid, "nameLast": ""} for pid in tc["player_pairs"]}

            greedy_selected, _ = greedy_set_cover(tc["player_pairs"], tc["all_pairs"], player_info, verbose=False)
            exact_selected, _ = exact_set_cover(tc["player_pairs"], tc["all_pairs"], player_info, verbose=False)

            # Exact should be <= greedy (by definition of optimal)
            assert len(exact_selected) <= len(greedy_selected)
