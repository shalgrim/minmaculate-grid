"""
Data Processor Module

Processes Lahman database CSV files to build player→franchise-pairs mapping.
This is the core data processing module for the Minmaculate Grid solver.
"""

from typing import Dict, Set, Tuple
from itertools import combinations
import pandas as pd
from src.franchise_mapper import get_current_franchises


def build_player_franchise_pairs(
    appearances_csv: str,
    teams_csv: str,
    people_csv: str,
    franchise_mapping: Dict[str, str],
    min_games: int = 1
) -> Tuple[Dict[str, Set[Tuple[str, str]]], Dict[str, Dict], Set[Tuple[str, str]]]:
    """
    Build optimization data structures using pandas.

    Args:
        appearances_csv: Path to Appearances.csv
        teams_csv: Path to Teams.csv
        people_csv: Path to People.csv
        franchise_mapping: teamID → franchID mapping from franchise_mapper
        min_games: Minimum games for appearance to count (default: 1)

    Returns:
        tuple containing:
        - player_pairs: {playerID: set of (franchID1, franchID2) tuples}
        - player_info: {playerID: {nameFirst, nameLast, birthYear, ...}}
        - all_possible_pairs: set of all 435 franchise pairs

    Example:
        >>> mapping = load_franchise_mapping("data/Teams.csv")
        >>> player_pairs, player_info, all_pairs = build_player_franchise_pairs(
        ...     "data/Appearances.csv",
        ...     "data/Teams.csv",
        ...     "data/People.csv",
        ...     mapping
        ... )
        >>> len(all_pairs)
        435
    """
    print("Loading data...")

    # 1. Load Appearances.csv
    appearances_df = pd.read_csv(appearances_csv)
    print(f"Loaded {len(appearances_df):,} appearance records")

    # 2. Filter for minimum games
    appearances_df = appearances_df[appearances_df["G_all"] >= min_games]
    print(f"After min_games={min_games} filter: {len(appearances_df):,} records")

    # 3. Map teamID → franchID
    appearances_df["franchID"] = appearances_df["teamID"].map(franchise_mapping)

    # Remove rows where franchise mapping failed
    before_count = len(appearances_df)
    appearances_df = appearances_df[appearances_df["franchID"].notna()]
    after_count = len(appearances_df)
    if before_count != after_count:
        print(f"Warning: Dropped {before_count - after_count} rows with unmapped teams")

    # 4. Get current franchises only
    current_franchises = get_current_franchises(teams_csv)
    appearances_df = appearances_df[appearances_df["franchID"].isin(current_franchises)]
    print(f"After filtering to current franchises: {len(appearances_df):,} records")

    # 5. Group by playerID, get unique franchises per player
    print("Aggregating franchises per player...")
    player_franchises = (
        appearances_df
        .groupby("playerID")["franchID"]
        .apply(lambda x: set(x))
        .to_dict()
    )
    print(f"Found {len(player_franchises):,} unique players")

    # 6. Generate franchise pairs for each player
    print("Generating franchise pairs...")
    player_pairs = {}

    for player_id, franchises in player_franchises.items():
        # Generate all C(n,2) combinations of franchises
        if len(franchises) >= 2:
            pairs = set()
            for fran1, fran2 in combinations(sorted(franchises), 2):
                # Store as sorted tuple (smaller, larger)
                pairs.add((fran1, fran2) if fran1 < fran2 else (fran2, fran1))
            player_pairs[player_id] = pairs
        else:
            # Player only played for one franchise - no pairs
            player_pairs[player_id] = set()

    # Count total pairs
    total_pairs = sum(len(pairs) for pairs in player_pairs.values())
    print(f"Generated {total_pairs:,} total player-pair associations")

    # 7. Load player biographical info
    print("Loading player biographical data...")
    people_df = pd.read_csv(people_csv)

    # Create player_info dictionary
    player_info = {}
    for _, row in people_df.iterrows():
        player_id = row["playerID"]
        if player_id in player_pairs:  # Only include players we care about
            player_info[player_id] = {
                "nameFirst": row.get("nameFirst", ""),
                "nameLast": row.get("nameLast", ""),
                "birthYear": row.get("birthYear"),
                "debut": row.get("debut"),
                "finalGame": row.get("finalGame"),
            }

    print(f"Loaded info for {len(player_info):,} players")

    # 8. Generate all possible franchise pairs C(30,2) = 435
    print("Generating all possible franchise pairs...")
    all_possible_pairs = set()
    current_franchises_list = sorted(current_franchises)

    for fran1, fran2 in combinations(current_franchises_list, 2):
        # Store as sorted tuple
        all_possible_pairs.add((fran1, fran2))

    print(f"Total possible franchise pairs: {len(all_possible_pairs)}")

    # Verify count
    expected_pairs = len(current_franchises) * (len(current_franchises) - 1) // 2
    assert len(all_possible_pairs) == expected_pairs, \
        f"Expected {expected_pairs} pairs, got {len(all_possible_pairs)}"

    print("✅ Data processing complete!")
    return player_pairs, player_info, all_possible_pairs


def get_player_name(player_id: str, player_info: Dict[str, Dict]) -> str:
    """
    Get formatted player name.

    Args:
        player_id: Player ID
        player_info: Player info dictionary

    Returns:
        Formatted name as "First Last"

    Example:
        >>> get_player_name("aaronha01", player_info)
        'Hank Aaron'
    """
    if player_id not in player_info:
        return player_id

    info = player_info[player_id]
    first = info.get("nameFirst", "")
    last = info.get("nameLast", "")

    return f"{first} {last}".strip()


def get_coverage_stats(player_pairs: Dict[str, Set[Tuple[str, str]]],
                      all_possible_pairs: Set[Tuple[str, str]]) -> Dict:
    """
    Calculate coverage statistics.

    Args:
        player_pairs: Player→pairs mapping
        all_possible_pairs: Set of all possible pairs

    Returns:
        Dictionary with coverage stats

    Example:
        >>> stats = get_coverage_stats(player_pairs, all_possible_pairs)
        >>> stats["total_pairs"]
        435
    """
    # Find which pairs are covered by at least one player
    covered_pairs = set()
    for pairs in player_pairs.values():
        covered_pairs.update(pairs)

    uncovered_pairs = all_possible_pairs - covered_pairs

    return {
        "total_pairs": len(all_possible_pairs),
        "covered_pairs": len(covered_pairs),
        "uncovered_pairs": len(uncovered_pairs),
        "coverage_percentage": (len(covered_pairs) / len(all_possible_pairs)) * 100,
        "total_players": len(player_pairs),
        "players_with_pairs": sum(1 for pairs in player_pairs.values() if len(pairs) > 0),
    }


# For debugging/exploration
if __name__ == "__main__":
    import sys
    from pathlib import Path
    from src.franchise_mapper import load_franchise_mapping

    data_dir = Path(__file__).parent.parent / "data"
    appearances_csv = data_dir / "Appearances.csv"
    teams_csv = data_dir / "Teams.csv"
    people_csv = data_dir / "People.csv"

    if not all([appearances_csv.exists(), teams_csv.exists(), people_csv.exists()]):
        print("Error: Data files not found")
        print("Please run scripts/download_data.py first")
        sys.exit(1)

    print("Building franchise mapping...")
    mapping = load_franchise_mapping(str(teams_csv))

    print()
    print("Processing data...")
    player_pairs, player_info, all_pairs = build_player_franchise_pairs(
        str(appearances_csv),
        str(teams_csv),
        str(people_csv),
        mapping,
        min_games=1
    )

    print()
    print("=" * 60)
    print("Coverage Statistics")
    print("=" * 60)
    stats = get_coverage_stats(player_pairs, all_pairs)
    for key, value in stats.items():
        if "percentage" in key:
            print(f"{key:30s}: {value:.2f}%")
        else:
            print(f"{key:30s}: {value:,}")

    print()
    print("Sample players with most franchise pairs:")
    # Find players with most pairs
    top_players = sorted(player_pairs.items(), key=lambda x: len(x[1]), reverse=True)[:10]

    for player_id, pairs in top_players:
        name = get_player_name(player_id, player_info)
        print(f"{name:30s} ({player_id:10s}): {len(pairs):3d} pairs")
