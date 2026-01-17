#!/usr/bin/env python3
"""
Franchise-Constrained Solver

Find the minimum set of players who ALL played for a specific franchise
while together covering all 435 franchise pairs.

Usage:
    python scripts/solve_for_franchise.py MIN            # Find MIN-constrained solution
    python scripts/solve_for_franchise.py NYY --greedy   # Greedy only (fast)
    python scripts/solve_for_franchise.py MIN --output results/min_solution.md
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import (
    build_player_franchise_pairs,
    filter_players_by_franchise,
    get_coverage_stats,
    get_player_name,
)
from src.franchise_mapper import get_current_franchises, load_franchise_mapping
from src.solver_exact import exact_set_cover
from src.solver_greedy import greedy_set_cover


def main():
    """Run franchise-constrained solver."""
    parser = argparse.ArgumentParser(
        description="Find minimum set of players from a specific franchise to cover all pairs"
    )
    parser.add_argument(
        "franchise",
        type=str,
        help="Franchise ID (e.g., MIN, NYY, LAD)",
    )
    parser.add_argument(
        "--greedy",
        action="store_true",
        help="Run only greedy solver (faster)",
    )
    parser.add_argument(
        "--exact-only",
        action="store_true",
        help="Run only exact solver",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path for results (markdown)",
    )
    parser.add_argument(
        "--time-limit",
        type=int,
        default=600,
        help="Exact solver time limit in seconds (default: 600)",
    )
    args = parser.parse_args()

    print()
    print("=" * 80)
    print("FRANCHISE-CONSTRAINED SOLVER")
    print("=" * 80)
    print()

    # Check data files
    data_dir = Path(__file__).parent.parent / "data"
    appearances_csv = data_dir / "Appearances.csv"
    teams_csv = data_dir / "Teams.csv"
    people_csv = data_dir / "People.csv"

    if not all([appearances_csv.exists(), teams_csv.exists(), people_csv.exists()]):
        print("Error: Data files not found")
        print("Please run scripts/download_data.py first")
        sys.exit(1)

    # Load current franchises and validate target franchise
    current_franchises = get_current_franchises(str(teams_csv))

    target_franchise = args.franchise.upper()
    if target_franchise not in current_franchises:
        print(f"Error: '{args.franchise}' is not a valid current franchise")
        print()
        print("Valid franchises (30 total):")
        for i, f in enumerate(sorted(current_franchises), 1):
            print(f"  {f}", end="")
            if i % 10 == 0:
                print()
        print()
        sys.exit(1)

    print(f"Target franchise: {target_franchise}")
    print()

    # Load data
    print("Loading data...")
    mapping = load_franchise_mapping(str(teams_csv))

    player_pairs, player_info, all_pairs, player_franchises = (
        build_player_franchise_pairs(
            str(appearances_csv), str(teams_csv), str(people_csv), mapping, min_games=1
        )
    )

    print()

    # Filter to only players from target franchise
    print(f"Filtering players who played for {target_franchise}...")
    filtered_player_pairs = filter_players_by_franchise(
        player_pairs, player_franchises, target_franchise
    )

    # Get stats on filtered players
    total_players = len(filtered_player_pairs)
    players_with_pairs = sum(
        1 for pairs in filtered_player_pairs.values() if len(pairs) > 0
    )

    print(f"  Total players who played for {target_franchise}: {total_players:,}")
    print(f"  Players with 2+ franchises (have pairs): {players_with_pairs:,}")
    print()

    # Check feasibility
    covered_pairs = set()
    for pairs in filtered_player_pairs.values():
        covered_pairs.update(pairs)

    uncovered_pairs = all_pairs - covered_pairs
    coverage_pct = (len(covered_pairs) / len(all_pairs)) * 100

    print(f"Coverage potential:")
    print(
        f"  Pairs coverable: {len(covered_pairs)}/{len(all_pairs)} ({coverage_pct:.1f}%)"
    )

    if uncovered_pairs:
        print()
        print(
            f"WARNING: {len(uncovered_pairs)} pairs CANNOT be covered by {target_franchise} players:"
        )
        print("(These pairs require players who never played for this franchise)")
        print()
        sorted_uncovered = sorted(uncovered_pairs)
        for pair in sorted_uncovered[:20]:
            print(f"  {pair[0]} - {pair[1]}")
        if len(uncovered_pairs) > 20:
            print(f"  ... and {len(uncovered_pairs) - 20} more")
        print()

        if not args.greedy and not args.exact_only:
            print("Solvers will find the best possible coverage.")
        print()

    # Store results
    results = {
        "franchise": target_franchise,
        "total_players": total_players,
        "players_with_pairs": players_with_pairs,
        "coverable_pairs": len(covered_pairs),
        "total_pairs": len(all_pairs),
        "uncovered_pairs": list(sorted(uncovered_pairs)),
        "greedy_solution": None,
        "exact_solution": None,
    }

    # Run greedy solver
    if not args.exact_only:
        print("-" * 80)
        print("RUNNING GREEDY SOLVER")
        print("-" * 80)
        print()

        start_time = time.time()
        greedy_selected, greedy_stats = greedy_set_cover(
            filtered_player_pairs, all_pairs, player_info, verbose=True
        )
        greedy_runtime = time.time() - start_time

        # Calculate actual coverage
        greedy_covered = set()
        for pid in greedy_selected:
            greedy_covered.update(filtered_player_pairs[pid])

        results["greedy_solution"] = {
            "players": greedy_selected,
            "num_players": len(greedy_selected),
            "pairs_covered": len(greedy_covered),
            "runtime": greedy_runtime,
        }

        print()

    # Run exact solver
    if not args.greedy:
        print("-" * 80)
        print("RUNNING EXACT ILP SOLVER")
        print("-" * 80)
        print(f"Time limit: {args.time_limit} seconds")
        print()

        start_time = time.time()
        exact_selected, exact_stats = exact_set_cover(
            filtered_player_pairs,
            all_pairs,
            player_info,
            verbose=True,
            time_limit=args.time_limit,
        )
        exact_runtime = time.time() - start_time

        if exact_stats["status"] in ["Optimal", "Feasible"]:
            results["exact_solution"] = {
                "players": exact_selected,
                "num_players": len(exact_selected),
                "pairs_covered": exact_stats["pairs_covered"],
                "runtime": exact_runtime,
                "status": exact_stats["status"],
            }

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Franchise: {target_franchise}")
    print(f"Eligible players: {total_players:,}")
    print(
        f"Maximum coverage: {len(covered_pairs)}/{len(all_pairs)} pairs ({coverage_pct:.1f}%)"
    )
    print()

    if results["greedy_solution"]:
        gs = results["greedy_solution"]
        print(f"Greedy solution: {gs['num_players']} players")
        print(f"  Pairs covered: {gs['pairs_covered']}/{len(all_pairs)}")
        print(f"  Runtime: {gs['runtime']:.2f} seconds")
        print()

    if results["exact_solution"]:
        es = results["exact_solution"]
        print(f"Exact solution: {es['num_players']} players ({es['status']})")
        print(f"  Pairs covered: {es['pairs_covered']}/{len(all_pairs)}")
        print(f"  Runtime: {es['runtime']:.2f} seconds")
        print()

    # Determine best solution
    best_solution = None
    if results["exact_solution"]:
        best_solution = results["exact_solution"]
        best_type = "exact"
    elif results["greedy_solution"]:
        best_solution = results["greedy_solution"]
        best_type = "greedy"

    if best_solution:
        print("-" * 80)
        print(
            f"BEST SOLUTION ({best_type.upper()}): {best_solution['num_players']} players"
        )
        print("-" * 80)
        print()

        for i, player_id in enumerate(best_solution["players"], 1):
            name = get_player_name(player_id, player_info)
            player_franch = sorted(player_franchises.get(player_id, set()))
            pairs_count = len(filtered_player_pairs.get(player_id, set()))
            print(f"{i:3d}. {name:30s} ({pairs_count:3d} pairs)")
            print(f"     Franchises: {', '.join(player_franch)}")

        print()

    # Write output file if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(f"# {target_franchise}-Constrained Minmaculate Grid Solution\n\n")
            f.write(
                f"Find the minimum set of players who ALL played for **{target_franchise}** "
                f"while together covering all 435 franchise pairs.\n\n"
            )

            f.write("## Summary\n\n")
            f.write(f"- **Target Franchise**: {target_franchise}\n")
            f.write(f"- **Eligible Players**: {total_players:,}\n")
            f.write(
                f"- **Maximum Possible Coverage**: {len(covered_pairs)}/{len(all_pairs)} "
                f"({coverage_pct:.1f}%)\n"
            )

            if uncovered_pairs:
                f.write(f"- **Uncoverable Pairs**: {len(uncovered_pairs)}\n")

            f.write("\n")

            if results["greedy_solution"]:
                gs = results["greedy_solution"]
                f.write("## Greedy Solution\n\n")
                f.write(f"- **Players**: {gs['num_players']}\n")
                f.write(
                    f"- **Pairs Covered**: {gs['pairs_covered']}/{len(all_pairs)}\n"
                )
                f.write(f"- **Runtime**: {gs['runtime']:.2f} seconds\n\n")

            if results["exact_solution"]:
                es = results["exact_solution"]
                f.write("## Exact (ILP) Solution\n\n")
                f.write(f"- **Players**: {es['num_players']}\n")
                f.write(f"- **Status**: {es['status']}\n")
                f.write(
                    f"- **Pairs Covered**: {es['pairs_covered']}/{len(all_pairs)}\n"
                )
                f.write(f"- **Runtime**: {es['runtime']:.2f} seconds\n\n")

            if best_solution:
                f.write(f"## Solution Players ({best_type.upper()})\n\n")
                f.write("| # | Player | Pairs | Franchises |\n")
                f.write("|---|--------|-------|------------|\n")

                for i, player_id in enumerate(best_solution["players"], 1):
                    name = get_player_name(player_id, player_info)
                    player_franch = sorted(player_franchises.get(player_id, set()))
                    pairs_count = len(filtered_player_pairs.get(player_id, set()))
                    f.write(
                        f"| {i} | {name} | {pairs_count} | {', '.join(player_franch)} |\n"
                    )

                f.write("\n")

            if uncovered_pairs:
                f.write("## Uncoverable Pairs\n\n")
                f.write(
                    f"These {len(uncovered_pairs)} pairs cannot be covered by any player "
                    f"who played for {target_franchise}:\n\n"
                )
                for pair in sorted(uncovered_pairs):
                    f.write(f"- {pair[0]} - {pair[1]}\n")
                f.write("\n")

        print(f"Results written to: {output_path}")
        print()

    print("=" * 80)


if __name__ == "__main__":
    main()
