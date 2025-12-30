"""
Compare Greedy vs Exact Solver Results

Runs both greedy and exact solvers on the same dataset and compares:
- Solution sizes
- Selected players
- Runtime
- Approximation ratio
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import build_player_franchise_pairs
from src.franchise_mapper import load_franchise_mapping
from src.solver_exact import exact_set_cover
from src.solver_greedy import greedy_set_cover


def format_player_name(player_id, player_info):
    """Format player name for display."""
    name_first = player_info[player_id].get("nameFirst", "")
    name_last = player_info[player_id].get("nameLast", "")
    return f"{name_first} {name_last}".strip() or player_id


def main():
    data_dir = Path(__file__).parent.parent / "data"
    appearances_csv = data_dir / "Appearances.csv"
    teams_csv = data_dir / "Teams.csv"
    people_csv = data_dir / "People.csv"

    if not all([appearances_csv.exists(), teams_csv.exists(), people_csv.exists()]):
        print("Error: Data files not found")
        print("Please run scripts/download_data.py first")
        sys.exit(1)

    print("Loading data...")
    mapping = load_franchise_mapping(str(teams_csv))

    player_pairs, player_info, all_pairs = build_player_franchise_pairs(
        str(appearances_csv), str(teams_csv), str(people_csv), mapping, min_games=1
    )

    print("\n" + "=" * 80)
    print("SOLVER COMPARISON: Greedy vs Exact ILP")
    print("=" * 80)
    print(f"Dataset: {len(player_pairs)} players, {len(all_pairs)} franchise pairs")
    print()

    # Run Greedy Solver
    print("-" * 80)
    print("Running GREEDY solver...")
    print("-" * 80)
    greedy_start = time.time()
    greedy_selected, greedy_stats = greedy_set_cover(
        player_pairs, all_pairs, player_info, verbose=False
    )
    greedy_time = time.time() - greedy_start

    print(f"✓ Greedy complete in {greedy_time:.2f} seconds")
    print(f"  Solution size: {len(greedy_selected)} players")
    print()

    # Run Exact Solver
    print("-" * 80)
    print("Running EXACT ILP solver...")
    print("-" * 80)
    exact_start = time.time()
    exact_selected, exact_stats = exact_set_cover(
        player_pairs, all_pairs, player_info, verbose=False, time_limit=300
    )
    exact_time = time.time() - exact_start

    print(f"✓ Exact complete in {exact_time:.2f} seconds")
    print(f"  Solution size: {len(exact_selected)} players")
    print(f"  Status: {exact_stats['status']}")
    print()

    # Comparison
    print("=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    print()

    print(f"Greedy Solution:  {len(greedy_selected)} players in {greedy_time:.2f}s")
    print(f"Exact Solution:   {len(exact_selected)} players in {exact_time:.2f}s")
    print()

    improvement = len(greedy_selected) - len(exact_selected)
    improvement_pct = (improvement / len(greedy_selected)) * 100

    if improvement > 0:
        print("✅ Exact solver found BETTER solution!")
        print(
            f"   Improvement: {improvement} players ({improvement_pct:.1f}% reduction)"
        )
    elif improvement < 0:
        print("⚠️  Exact solver found worse solution (unexpected!)")
    else:
        print("✓ Both solvers found same solution size")

    print()

    # Approximation Ratio
    if len(exact_selected) > 0:
        approximation_ratio = len(greedy_selected) / len(exact_selected)
        print(f"Approximation Ratio: {approximation_ratio:.4f}")
        print(f"  (Greedy is {approximation_ratio:.2f}x the optimal solution)")
        print()

    # Speed Comparison
    speedup = greedy_time / exact_time
    if speedup > 1:
        print(f"Speed: Greedy is {speedup:.1f}x faster than Exact")
    else:
        print(f"Speed: Exact is {1 / speedup:.1f}x faster than Greedy")
    print()

    # Player Differences
    greedy_set = set(greedy_selected)
    exact_set = set(exact_selected)

    common = greedy_set & exact_set
    greedy_only = greedy_set - exact_set
    exact_only = exact_set - greedy_set

    print("-" * 80)
    print("PLAYER OVERLAP")
    print("-" * 80)
    print(f"Common to both:     {len(common)} players")
    print(f"Greedy only:        {len(greedy_only)} players")
    print(f"Exact only:         {len(exact_only)} players")
    print()

    if greedy_only:
        print("Players in GREEDY but not EXACT:")
        for player_id in sorted(greedy_only):
            name = format_player_name(player_id, player_info)
            franchises = len(set(f for pair in player_pairs[player_id] for f in pair))
            pairs_count = len(player_pairs[player_id])
            print(
                f"  - {name:30s} ({franchises:2d} franchises, {pairs_count:3d} pairs)"
            )
        print()

    if exact_only:
        print("Players in EXACT but not GREEDY:")
        for player_id in sorted(exact_only):
            name = format_player_name(player_id, player_info)
            franchises = len(set(f for pair in player_pairs[player_id] for f in pair))
            pairs_count = len(player_pairs[player_id])
            print(
                f"  - {name:30s} ({franchises:2d} franchises, {pairs_count:3d} pairs)"
            )
        print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"The optimal minimum set size is: {len(exact_selected)} players")
    print(f"Greedy approximation is: {len(greedy_selected)} players")
    print(
        f"Approximation ratio: {approximation_ratio:.4f} ({approximation_ratio:.1%} of optimal)"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
