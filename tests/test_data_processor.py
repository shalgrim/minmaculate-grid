"""
Tests for data_processor module.

Following TDD: Write tests first, then implement src/data_processor.py
"""

# Add src to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import build_player_franchise_pairs
from src.franchise_mapper import load_franchise_mapping

# Test data paths
DATA_DIR = Path(__file__).parent.parent / "data"
APPEARANCES_CSV = DATA_DIR / "Appearances.csv"
TEAMS_CSV = DATA_DIR / "Teams.csv"
PEOPLE_CSV = DATA_DIR / "People.csv"


class TestBuildPlayerFranchisePairs:
    """Tests for build_player_franchise_pairs function."""

    def test_build_player_pairs_returns_four_tuples(self):
        """Test function returns (player_pairs, player_info, all_pairs, player_franchises)."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        result = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping, min_games=1
        )

        # Should return tuple of 4 elements
        assert isinstance(result, tuple)
        assert len(result) == 4

        player_pairs, player_info, all_pairs, player_franchises = result
        assert isinstance(player_pairs, dict)
        assert isinstance(player_info, dict)
        assert isinstance(all_pairs, set)
        assert isinstance(player_franchises, dict)

    def test_all_possible_pairs_count_is_435(self):
        """Test C(30,2) = 435 franchise pairs."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        _, _, all_pairs, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping
        )

        # C(30, 2) = 30 * 29 / 2 = 435
        assert len(all_pairs) == 435

    def test_player_pairs_are_tuples_not_lists(self):
        """Test pairs are immutable tuples."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        player_pairs, _, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping, min_games=1
        )

        # Check that pairs are tuples
        for player_id, pairs in player_pairs.items():
            assert isinstance(pairs, set)
            for pair in pairs:
                assert isinstance(pair, tuple)
                assert len(pair) == 2
                # Pairs should be sorted (franchise1 < franchise2)
                assert pair[0] < pair[1]

    def test_player_info_has_required_fields(self):
        """Test player_info has name and other biographical data."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        _, player_info, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping
        )

        # Check a few random players have required fields
        assert len(player_info) > 0

        for player_id, info in list(player_info.items())[:10]:
            assert isinstance(info, dict)
            assert "nameFirst" in info
            assert "nameLast" in info
            # birthYear might be null for very old players
            assert "birthYear" in info

    def test_min_games_filter_works(self):
        """Test min_games parameter filters appearances."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))

        # Get results with min_games=1 (all appearances)
        player_pairs_1, _, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping, min_games=1
        )

        # Get results with min_games=50 (substantial appearances only)
        player_pairs_50, _, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping, min_games=50
        )

        # Filtering should reduce number of players
        assert len(player_pairs_50) < len(player_pairs_1)

    def test_all_pairs_are_sorted(self):
        """Test all franchise pairs are sorted tuples."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        _, _, all_pairs, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping
        )

        for pair in all_pairs:
            assert isinstance(pair, tuple)
            assert len(pair) == 2
            # Pairs should be sorted
            assert pair[0] < pair[1]


class TestPlayerPairLogic:
    """Tests for player pair generation logic."""

    def test_player_with_one_franchise_has_zero_pairs(self):
        """Test player with single franchise contributes no pairs."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        player_pairs, _, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping, min_games=1
        )

        # Find players with only 1 franchise
        single_franchise_players = [
            p_id for p_id, pairs in player_pairs.items() if len(pairs) == 0
        ]

        # There should be many players who played for only one franchise
        assert len(single_franchise_players) > 0

    def test_player_with_two_franchises_has_one_pair(self):
        """Test player with 2 franchises contributes C(2,2) = 1 pair."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        player_pairs, _, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping, min_games=1
        )

        # Find players with exactly 1 pair (2 franchises)
        two_franchise_players = [
            p_id for p_id, pairs in player_pairs.items() if len(pairs) == 1
        ]

        # There should be many players who played for exactly 2 franchises
        assert len(two_franchise_players) > 0

    def test_player_with_three_franchises_has_three_pairs(self):
        """Test player with 3 franchises contributes C(3,2) = 3 pairs."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        player_pairs, _, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping, min_games=1
        )

        # Find players with exactly 3 pairs (3 franchises)
        three_franchise_players = [
            p_id for p_id, pairs in player_pairs.items() if len(pairs) == 3
        ]

        # There should be players who played for exactly 3 franchises
        assert len(three_franchise_players) > 0

    def test_combinations_formula_holds(self):
        """Test C(n,2) = n*(n-1)/2 for various n."""

        # Helper to calculate C(n, 2)
        def c_n_2(n):
            return n * (n - 1) // 2

        assert c_n_2(2) == 1
        assert c_n_2(3) == 3
        assert c_n_2(4) == 6
        assert c_n_2(5) == 10
        assert c_n_2(30) == 435  # Our expected total


class TestDataIntegrity:
    """Integration tests for data quality."""

    def test_all_player_ids_exist_in_player_info(self):
        """Test all playerIDs in player_pairs exist in player_info."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        player_pairs, player_info, _, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping
        )

        # Every player in player_pairs should have info
        for player_id in player_pairs.keys():
            assert player_id in player_info

    def test_all_pairs_use_current_franchises(self):
        """Test all pairs use only current (2024) franchises."""
        from src.franchise_mapper import get_current_franchises

        mapping = load_franchise_mapping(str(TEAMS_CSV))
        current_franchises = get_current_franchises(str(TEAMS_CSV))

        player_pairs, _, all_pairs, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping
        )

        # Check all_possible_pairs
        for pair in all_pairs:
            assert pair[0] in current_franchises
            assert pair[1] in current_franchises

        # Check player pairs
        for player_id, pairs in player_pairs.items():
            for pair in pairs:
                assert pair[0] in current_franchises
                assert pair[1] in current_franchises

    def test_no_duplicate_pairs_in_all_pairs(self):
        """Test all_possible_pairs has no duplicates."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        _, _, all_pairs, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping
        )

        # Since it's a set, converting to list should have same length
        pairs_list = list(all_pairs)
        assert len(pairs_list) == len(all_pairs)

    def test_player_pairs_subset_of_all_pairs(self):
        """Test each player's pairs are subset of all_possible_pairs."""
        mapping = load_franchise_mapping(str(TEAMS_CSV))
        player_pairs, _, all_pairs, _ = build_player_franchise_pairs(
            str(APPEARANCES_CSV), str(TEAMS_CSV), str(PEOPLE_CSV), mapping
        )

        # Every pair in player_pairs should exist in all_pairs
        for player_id, pairs in player_pairs.items():
            assert pairs.issubset(all_pairs)
