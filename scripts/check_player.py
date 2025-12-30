#!/usr/bin/env python3
"""
Quick utility to check a player's franchise coverage and greedy solution overlap.

Usage:
    python scripts/check_player.py "Todd Zeile"
    python scripts/check_player.py "Jesse Orosco"
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import build_player_franchise_pairs, get_player_name
from src.franchise_mapper import load_franchise_mapping
from src.solver_greedy import greedy_set_cover


def check_player(search_name: str):
    """Check a specific player's stats and overlap with greedy solution."""
    data_dir = Path(__file__).parent.parent / "data"

    print("Loading data...")
    mapping = load_franchise_mapping(str(data_dir / "Teams.csv"))
    player_pairs, player_info, all_pairs = build_player_franchise_pairs(
        str(data_dir / "Appearances.csv"),
        str(data_dir / "Teams.csv"),
        str(data_dir / "People.csv"),
        mapping,
        min_games=1,
    )

    # Search for player
    print(f"\nSearching for '{search_name}'...")
    matches = []
    for pid, info in player_info.items():
        name = get_player_name(pid, player_info)
        if search_name.lower() in name.lower():
            matches.append((pid, name))

    if not matches:
        print(f"❌ No players found matching '{search_name}'")
        return

    if len(matches) > 1:
        print(f"\n⚠️  Found {len(matches)} players:")
        for pid, name in matches:
            print(f"  - {name} ({pid})")
        print("\nShowing results for first match:")
        print()

    player_id, player_name = matches[0]

    # Get player's stats
    franchises = set()
    for pair in player_pairs[player_id]:
        franchises.add(pair[0])
        franchises.add(pair[1])

    print("=" * 70)
    print(f"Player: {player_name}")
    print("=" * 70)
    print(f"Franchises played for: {len(franchises)}")
    print(f"Franchise pairs covered: {len(player_pairs[player_id])}")
    print(f"Franchises: {', '.join(sorted(franchises))}")
    print()

    # Run greedy solver (quickly, silently)
    print("Running greedy solver to check overlap...")
    greedy_solution, _ = greedy_set_cover(
        player_pairs, all_pairs, player_info, verbose=False
    )

    # Check if player is in solution
    if player_id in greedy_solution:
        rank = greedy_solution.index(player_id) + 1
        print(
            f"✅ Player IS in greedy solution (rank #{rank} of {len(greedy_solution)})"
        )
    else:
        print("❌ Player NOT in greedy solution")

    print()
    print("Overlap Analysis:")
    print("-" * 70)

    # Check overlap with greedy solution
    player_covered_pairs = player_pairs[player_id]
    covered_by_greedy = set()

    for i, pid in enumerate(greedy_solution[:10], 1):  # Check first 10
        covered_by_greedy.update(player_pairs[pid])
        overlap = player_covered_pairs & covered_by_greedy
        remaining = player_covered_pairs - covered_by_greedy

        greedy_player_name = get_player_name(pid, player_info)

        print(f"After selecting {greedy_player_name} (#{i}):")
        print(
            f"  {player_name}'s pairs covered: {len(overlap)}/{len(player_covered_pairs)} "
            f"({len(overlap) / len(player_covered_pairs) * 100:.1f}%)"
        )
        print(f"  Unique pairs remaining: {len(remaining)}")

        if len(remaining) == 0:
            print(f"  ⚠️ All of {player_name}'s pairs covered by iteration {i}!")
            break
        print()

    # Final stats
    final_overlap = player_covered_pairs & covered_by_greedy
    final_remaining = player_covered_pairs - covered_by_greedy

    print("-" * 70)
    print("After first 10 greedy players:")
    print(f"  Pairs already covered: {len(final_overlap)}/{len(player_covered_pairs)}")
    print(f"  Unique value if added: {len(final_remaining)} pairs")
    print()

    if len(final_remaining) > 0:
        print(f"💡 {player_name} could still add {len(final_remaining)} unique pairs!")
    else:
        print(
            f"💡 {player_name}'s entire franchise combination is redundant "
            f"with the greedy solution"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_player.py 'Player Name'")
        print()
        print("Examples:")
        print("  python scripts/check_player.py 'Todd Zeile'")
        print("  python scripts/check_player.py 'Jesse Orosco'")
        print("  python scripts/check_player.py 'Kenny Lofton'")
        sys.exit(1)

    search_name = " ".join(sys.argv[1:])
    check_player(search_name)
