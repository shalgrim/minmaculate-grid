#!/usr/bin/env python3
"""
Populate SQLite Database with Players and Solutions

Loads all player data from Lahman CSV files, runs both greedy and exact
solvers, and saves all results to the SQLite database.

Usage:
    python scripts/populate_database.py
    python scripts/populate_database.py --db-path custom.db
    python scripts/populate_database.py --skip-exact  # Skip slow exact solver
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import build_player_franchise_pairs
from src.database import Database
from src.franchise_mapper import load_franchise_mapping
from src.solver_exact import exact_set_cover
from src.solver_greedy import greedy_set_cover


def main():
    """Populate database with all players, pairs, coverage, and solutions."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Populate database with players and solutions"
    )
    parser.add_argument(
        "--db-path", default="minmaculate.db", help="Database file path"
    )
    parser.add_argument("--skip-exact", action="store_true", help="Skip exact solver")
    parser.add_argument(
        "--time-limit", type=int, default=300, help="Exact solver time limit (seconds)"
    )
    args = parser.parse_args()

    print()
    print("=" * 80)
    print("MINMACULATE GRID DATABASE POPULATION")
    print("=" * 80)
    print()

    # Check data files
    data_dir = Path(__file__).parent.parent / "data"
    appearances_csv = data_dir / "Appearances.csv"
    teams_csv = data_dir / "Teams.csv"
    people_csv = data_dir / "People.csv"

    if not all([appearances_csv.exists(), teams_csv.exists(), people_csv.exists()]):
        print("❌ Error: Data files not found")
        print("   Please run scripts/download_data.py first")
        sys.exit(1)

    # Load data
    print("Loading data...")
    mapping = load_franchise_mapping(str(teams_csv))

    player_pairs, player_info, all_pairs, player_franchises = (
        build_player_franchise_pairs(
            str(appearances_csv), str(teams_csv), str(people_csv), mapping, min_games=1
        )
    )

    print()
    print("✓ Data loaded:")
    print(f"  Players: {len(player_info):,}")
    print(f"  Franchise pairs: {len(all_pairs)}")
    print()

    # Initialize database
    print("-" * 80)
    print("INITIALIZING DATABASE")
    print("-" * 80)

    db = Database(args.db_path)
    print(f"✓ Database created: {args.db_path}")
    print()

    # Populate players table
    print("-" * 80)
    print("POPULATING PLAYERS TABLE")
    print("-" * 80)

    for i, (player_id, info) in enumerate(player_info.items(), 1):
        name_first = info.get("nameFirst", "")
        name_last = info.get("nameLast", "")
        debut = info.get("debut", "")

        db.insert_player(player_id, name_first, name_last, debut)

        if i % 1000 == 0:
            print(f"  Processed {i:,}/{len(player_info):,} players...")

    print(f"✓ Inserted {len(player_info):,} players")
    print()

    # Populate franchise pairs table
    print("-" * 80)
    print("POPULATING FRANCHISE PAIRS TABLE")
    print("-" * 80)

    pair_id_map = {}
    for pair in sorted(all_pairs):
        pair_id = db.insert_franchise_pair(pair[0], pair[1])
        pair_id_map[pair] = pair_id

    print(f"✓ Inserted {len(all_pairs)} franchise pairs")
    print()

    # Populate player coverage table
    print("-" * 80)
    print("POPULATING PLAYER COVERAGE TABLE")
    print("-" * 80)

    total_coverage_entries = 0
    for i, (player_id, pairs) in enumerate(player_pairs.items(), 1):
        for pair in pairs:
            db.add_player_coverage(player_id, pair_id_map[pair])
            total_coverage_entries += 1

        if i % 1000 == 0:
            print(f"  Processed {i:,}/{len(player_pairs):,} players...")

    print(f"✓ Inserted {total_coverage_entries:,} coverage entries")
    print()

    # Populate player franchises table
    print("-" * 80)
    print("POPULATING PLAYER FRANCHISES TABLE")
    print("-" * 80)

    total_franchise_entries = 0
    for i, (player_id, franchises) in enumerate(player_franchises.items(), 1):
        for franchise_id in franchises:
            db.add_player_franchise(player_id, franchise_id)
            total_franchise_entries += 1

        if i % 1000 == 0:
            print(f"  Processed {i:,}/{len(player_franchises):,} players...")

    print(f"✓ Inserted {total_franchise_entries:,} player-franchise entries")
    print()

    # Run greedy solver
    print("-" * 80)
    print("RUNNING GREEDY SOLVER")
    print("-" * 80)

    start_time = time.time()
    greedy_selected, greedy_stats = greedy_set_cover(
        player_pairs, all_pairs, player_info, verbose=False
    )
    greedy_runtime = time.time() - start_time

    # Calculate coverage
    covered_pairs = set()
    for pid in greedy_selected:
        covered_pairs.update(player_pairs[pid])

    coverage_pct = (len(covered_pairs) / len(all_pairs)) * 100

    print(f"✓ Greedy complete in {greedy_runtime:.2f} seconds")
    print(f"  Solution: {len(greedy_selected)} players")
    print(
        f"  Coverage: {len(covered_pairs)}/{len(all_pairs)} pairs ({coverage_pct:.1f}%)"
    )

    # Save to database
    solution_id = db.save_solution(
        algorithm="greedy",
        player_ids=greedy_selected,
        num_players=len(greedy_selected),
        runtime=greedy_runtime,
        coverage=coverage_pct,
    )

    print(f"✓ Saved greedy solution (ID: {solution_id})")
    print()

    # Run exact solver (unless skipped)
    if not args.skip_exact:
        print("-" * 80)
        print("RUNNING EXACT ILP SOLVER")
        print("-" * 80)
        print(f"Time limit: {args.time_limit} seconds")
        print()

        start_time = time.time()
        exact_selected, exact_stats = exact_set_cover(
            player_pairs,
            all_pairs,
            player_info,
            verbose=False,
            time_limit=args.time_limit,
        )
        exact_runtime = time.time() - start_time

        if exact_stats["status"] in ["Optimal", "Feasible"]:
            print(f"✓ Exact complete in {exact_runtime:.2f} seconds")
            print(f"  Solution: {len(exact_selected)} players")
            print(f"  Status: {exact_stats['status']}")
            print(
                f"  Coverage: {exact_stats['pairs_covered']}/{exact_stats['total_pairs']} pairs ({exact_stats['coverage_percentage']:.1f}%)"
            )

            # Save to database
            solution_id = db.save_solution(
                algorithm="exact",
                player_ids=exact_selected,
                num_players=len(exact_selected),
                runtime=exact_runtime,
                coverage=exact_stats["coverage_percentage"],
            )

            print(f"✓ Saved exact solution (ID: {solution_id})")
        else:
            print(f"❌ Exact solver failed: {exact_stats['status']}")

        print()
    else:
        print("-" * 80)
        print("SKIPPING EXACT SOLVER (--skip-exact flag)")
        print("-" * 80)
        print()

    # Summary
    print("=" * 80)
    print("DATABASE POPULATION COMPLETE")
    print("=" * 80)
    print(f"Database: {args.db_path}")
    print(f"Players: {len(player_info):,}")
    print(f"Franchise pairs: {len(all_pairs)}")
    print(f"Coverage entries: {total_coverage_entries:,}")
    print(f"Player-franchise entries: {total_franchise_entries:,}")
    print(f"Solutions saved: {1 if args.skip_exact else 2}")
    print()
    print("You can now start the web interface:")
    print("  uvicorn web.api:app --reload")
    print("=" * 80)

    db.close()


if __name__ == "__main__":
    main()
