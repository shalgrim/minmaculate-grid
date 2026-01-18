#!/usr/bin/env python3
"""
Generate Anki Flash Cards for Minmaculate Grid

Generates three TSV files for import into Anki:
1. optimal_players.txt - 19 cards for optimal solution players
2. twins_players.txt - 34 cards for Twins-constrained players
3. pairs.txt - 435 cards for franchise pairs

Usage:
    python scripts/generate_anki_cards.py
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import Database


def parse_player_table(content: str, start_marker: str, end_marker: str) -> Dict[str, List[str]]:
    """
    Parse a markdown table to extract player names and franchises.

    Args:
        content: Full file content
        start_marker: Text that appears before the table
        end_marker: Text that appears after the table (or end of file)

    Returns:
        Dict mapping player name to list of franchises
    """
    players = {}
    lines = content.split("\n")

    # Find start line
    in_section = False
    for line in lines:
        if start_marker in line:
            in_section = True
            continue

        # Check for end marker - but only if it's a standalone line (not part of table)
        if in_section and end_marker and line.strip() == end_marker:
            break

        if not in_section:
            continue

        # Parse table rows: | # | **Player** | Teams | Franchises |
        # Pattern 1 (with bold): | 1 | **Chase Anderson** | 9 | ARI, BOS, ... |
        # Pattern 2 (without bold): | 1 | Luis Ayala | 21 | ATL, BAL, ... |
        match = re.match(
            r"\|\s*\d+\s*\|\s*\*?\*?([^|*]+?)\*?\*?\s*\|\s*\d+\s*\|\s*([^|]+)\s*\|",
            line
        )
        if match:
            player_name = match.group(1).strip()
            franchises_str = match.group(2).strip()
            franchises = [f.strip() for f in franchises_str.split(",")]
            players[player_name] = franchises

    return players


def parse_optimal_players(answers_path: Path) -> Dict[str, List[str]]:
    """Parse the 19 optimal players from answers.md."""
    content = answers_path.read_text()
    return parse_player_table(
        content,
        "## Optimal Solution: 19 Players",
        "---"
    )


def parse_twins_players(min_solution_path: Path) -> Dict[str, List[str]]:
    """Parse the 34 Twins-constrained players from min_solution.md."""
    content = min_solution_path.read_text()
    return parse_player_table(
        content,
        "## Solution Players (EXACT)",
        "## Uncoverable Pairs"
    )


def format_franchises_alphabetical(franchises: List[str]) -> str:
    """Format franchises in alphabetical order."""
    return ", ".join(sorted(franchises))


def format_franchises_twins_first(franchises: List[str]) -> str:
    """Format franchises with MIN first, then others alphabetically."""
    other = sorted(f for f in franchises if f != "MIN")
    return "MIN, " + ", ".join(other)


def get_players_covering_pair(
    db: Database,
    franchise_1: str,
    franchise_2: str,
    solution_player_ids: Set[str]
) -> List[str]:
    """
    Get players from a solution that cover a specific franchise pair.

    Args:
        db: Database connection
        franchise_1: First franchise code
        franchise_2: Second franchise code
        solution_player_ids: Set of player_ids in the solution

    Returns:
        List of player names that cover this pair
    """
    pair_id = db.get_franchise_pair_id(franchise_1, franchise_2)
    if pair_id is None:
        return []

    # Get all players covering this pair
    all_players = db.get_players_covering_pair(pair_id)

    # Filter to solution players and get names
    covering_players = []
    for player in all_players:
        if player["player_id"] in solution_player_ids:
            name = f"{player['name_first']} {player['name_last']}"
            covering_players.append(name)

    return sorted(covering_players)


def get_player_id_mapping(db: Database, player_names: List[str]) -> Dict[str, str]:
    """
    Get player_id for each player name.

    Args:
        db: Database connection
        player_names: List of player names (e.g., "Chase Anderson")

    Returns:
        Dict mapping player name to player_id
    """
    mapping = {}
    all_players = db.get_all_players()

    for player in all_players:
        full_name = f"{player['name_first']} {player['name_last']}"
        if full_name in player_names:
            mapping[full_name] = player["player_id"]

    return mapping


def generate_optimal_player_cards(players: Dict[str, List[str]]) -> str:
    """
    Generate TSV content for optimal player cards.

    Args:
        players: Dict mapping player name to list of franchises

    Returns:
        TSV content with Anki headers
    """
    lines = [
        "#separator:tab",
        "#html:true",
        "#tags:minmaculate optimal player",
        "#deck:Minmaculate Grid::Optimal Players",
        "Front\tBack",
    ]

    for player_name in sorted(players.keys()):
        franchises = format_franchises_alphabetical(players[player_name])
        lines.append(f"{player_name}\t{franchises}")

    return "\n".join(lines) + "\n"


def generate_twins_player_cards(players: Dict[str, List[str]]) -> str:
    """
    Generate TSV content for Twins-constrained player cards.

    Args:
        players: Dict mapping player name to list of franchises

    Returns:
        TSV content with Anki headers
    """
    lines = [
        "#separator:tab",
        "#html:true",
        "#tags:minmaculate twins player",
        "#deck:Minmaculate Grid::Twins Players",
        "Front\tBack",
    ]

    for player_name in sorted(players.keys()):
        franchises = format_franchises_twins_first(players[player_name])
        lines.append(f"{player_name}\t{franchises}")

    return "\n".join(lines) + "\n"


def generate_pair_cards(
    db: Database,
    optimal_player_ids: Set[str],
    twins_player_ids: Set[str]
) -> str:
    """
    Generate TSV content for franchise pair cards.

    Args:
        db: Database connection
        optimal_player_ids: Set of player_ids in optimal solution
        twins_player_ids: Set of player_ids in Twins solution

    Returns:
        TSV content with Anki headers
    """
    lines = [
        "#separator:tab",
        "#html:true",
        "#tags:minmaculate pair",
        "#deck:Minmaculate Grid::Pairs",
        "Front\tBack",
    ]

    # Get all franchise pairs
    pairs = db.get_all_franchise_pairs()

    for pair in pairs:
        f1, f2 = pair["franchise_1"], pair["franchise_2"]
        front = f"{f1} - {f2}"

        # Get covering players from each solution
        optimal_players = get_players_covering_pair(db, f1, f2, optimal_player_ids)
        twins_players = get_players_covering_pair(db, f1, f2, twins_player_ids)

        # Format back with HTML
        optimal_str = ", ".join(optimal_players) if optimal_players else "(none)"
        twins_str = ", ".join(twins_players) if twins_players else "(none)"

        back = f"<b>Optimal:</b> {optimal_str}<br><b>Twins:</b> {twins_str}"
        lines.append(f"{front}\t{back}")

    return "\n".join(lines) + "\n"


def main():
    """Generate all Anki flash card files."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    answers_path = project_root / "answers.md"
    min_solution_path = project_root / "results" / "min_solution.md"
    db_path = project_root / "minmaculate.db"
    output_dir = project_root / "results" / "anki"

    # Validate input files exist
    if not answers_path.exists():
        print(f"Error: {answers_path} not found")
        sys.exit(1)
    if not min_solution_path.exists():
        print(f"Error: {min_solution_path} not found")
        sys.exit(1)
    if not db_path.exists():
        print(f"Error: {db_path} not found")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse player data from markdown files
    print("Parsing player data from markdown files...")
    optimal_players = parse_optimal_players(answers_path)
    twins_players = parse_twins_players(min_solution_path)

    print(f"  Found {len(optimal_players)} optimal players")
    print(f"  Found {len(twins_players)} Twins-constrained players")

    # Connect to database
    print("Connecting to database...")
    db = Database(str(db_path))

    # Get player ID mappings
    print("Mapping player names to IDs...")
    optimal_id_mapping = get_player_id_mapping(db, list(optimal_players.keys()))
    twins_id_mapping = get_player_id_mapping(db, list(twins_players.keys()))

    optimal_player_ids = set(optimal_id_mapping.values())
    twins_player_ids = set(twins_id_mapping.values())

    # Report any players not found in database
    optimal_not_found = set(optimal_players.keys()) - set(optimal_id_mapping.keys())
    twins_not_found = set(twins_players.keys()) - set(twins_id_mapping.keys())

    if optimal_not_found:
        print(f"  Warning: Optimal players not found in DB: {optimal_not_found}")
    if twins_not_found:
        print(f"  Warning: Twins players not found in DB: {twins_not_found}")

    # Generate optimal player cards
    print("Generating optimal player cards...")
    optimal_content = generate_optimal_player_cards(optimal_players)
    optimal_output = output_dir / "optimal_players.txt"
    optimal_output.write_text(optimal_content, encoding="utf-8")
    print(f"  Written to {optimal_output}")

    # Generate twins player cards
    print("Generating Twins player cards...")
    twins_content = generate_twins_player_cards(twins_players)
    twins_output = output_dir / "twins_players.txt"
    twins_output.write_text(twins_content, encoding="utf-8")
    print(f"  Written to {twins_output}")

    # Generate pair cards
    print("Generating pair cards...")
    pairs_content = generate_pair_cards(db, optimal_player_ids, twins_player_ids)
    pairs_output = output_dir / "pairs.txt"
    pairs_output.write_text(pairs_content, encoding="utf-8")
    print(f"  Written to {pairs_output}")

    # Close database
    db.close()

    # Summary
    print("\nSummary:")
    print(f"  optimal_players.txt: {len(optimal_players)} cards")
    print(f"  twins_players.txt: {len(twins_players)} cards")
    print(f"  pairs.txt: 435 cards")
    print("\nDone! Import the .txt files into Anki using File > Import.")


if __name__ == "__main__":
    main()
