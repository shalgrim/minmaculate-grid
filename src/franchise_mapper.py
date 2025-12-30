"""
Franchise Mapper Module

Maps teamIDs to franchise IDs, handling historical teams that belong to current franchises.
For example: Brooklyn Dodgers (BRO) → Los Angeles Dodgers (LAD)
"""

from typing import Dict, Optional, Set

import pandas as pd


def load_franchise_mapping(teams_csv: str) -> Dict[str, str]:
    """
    Create teamID → franchID mapping using Teams.csv franchID column.

    The Lahman database includes a franchID column that groups historical
    teams with their current franchises.

    Args:
        teams_csv: Path to Teams.csv file

    Returns:
        dict: {teamID: franchID} for all teams in history

    Example:
        >>> mapping = load_franchise_mapping("data/Teams.csv")
        >>> mapping["BRO"]  # Brooklyn Dodgers
        'LAD'
        >>> mapping["MON"]  # Montreal Expos
        'WSN'
    """
    # Load teams data
    teams_df = pd.read_csv(teams_csv)

    # Create mapping: teamID → franchID
    # Use the most recent franchID for each teamID (in case of changes)
    mapping = {}

    for _, row in teams_df.iterrows():
        team_id = row["teamID"]
        franchise_id = row["franchID"]

        # Always update to most recent mapping
        # (later entries in the file are more recent)
        mapping[team_id] = franchise_id

    return mapping


def get_current_franchises(teams_csv: str, year: int = 2024) -> Set[str]:
    """
    Get set of current MLB franchise IDs.

    Args:
        teams_csv: Path to Teams.csv file
        year: Year to use for determining current franchises (default: 2024)

    Returns:
        set: Set of current franchise IDs (should be 30)

    Example:
        >>> franchises = get_current_franchises("data/Teams.csv")
        >>> len(franchises)
        30
        >>> "NYY" in franchises
        True
    """
    # Load teams data
    teams_df = pd.read_csv(teams_csv)

    # Get franchises that had teams in the specified year
    current_teams = teams_df[teams_df["yearID"] == year]
    current_franchises = set(current_teams["franchID"].unique())

    return current_franchises


def get_franchise_for_team(team_id: str, mapping: Dict[str, str]) -> Optional[str]:
    """
    Get franchise ID for a given team ID.

    Args:
        team_id: Team ID (e.g., "BRO", "NYY")
        mapping: Franchise mapping dictionary from load_franchise_mapping()

    Returns:
        Franchise ID if found, None otherwise

    Example:
        >>> mapping = load_franchise_mapping("data/Teams.csv")
        >>> get_franchise_for_team("BRO", mapping)
        'LAD'
        >>> get_franchise_for_team("INVALID", mapping)
        None
    """
    return mapping.get(team_id, None)


def validate_franchise_count(franchises: Set[str], expected_count: int = 30) -> bool:
    """
    Validate that we have the expected number of current franchises.

    Args:
        franchises: Set of franchise IDs
        expected_count: Expected number of franchises (default: 30 for current MLB)

    Returns:
        True if count matches, False otherwise
    """
    return len(franchises) == expected_count


# For debugging/exploration
if __name__ == "__main__":
    import sys
    from pathlib import Path

    teams_csv = Path(__file__).parent.parent / "data" / "Teams.csv"

    if not teams_csv.exists():
        print(f"Error: {teams_csv} not found")
        print("Please run scripts/download_data.py first")
        sys.exit(1)

    print("Loading franchise mapping...")
    mapping = load_franchise_mapping(str(teams_csv))
    print(f"Loaded {len(mapping)} team→franchise mappings")
    print()

    print("Current franchises:")
    current = get_current_franchises(str(teams_csv))
    print(f"Found {len(current)} current franchises")
    print(sorted(current))
    print()

    # Test some known mappings
    test_teams = [
        ("BRO", "Brooklyn Dodgers"),
        ("LAD", "Los Angeles Dodgers"),
        ("MON", "Montreal Expos"),
        ("WAS", "Washington Nationals"),
        ("NYY", "New York Yankees"),
    ]

    print("Sample mappings:")
    for team_id, team_name in test_teams:
        franchise_id = get_franchise_for_team(team_id, mapping)
        print(f"  {team_id:3s} ({team_name:25s}) → {franchise_id}")
