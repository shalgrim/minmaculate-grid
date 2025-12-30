"""
Greedy Set Cover Solver

Implements a greedy approximation algorithm for the minimum set cover problem.
Repeatedly selects the player covering the most uncovered franchise pairs.
"""

from typing import Dict, List, Set, Tuple


def greedy_set_cover(
    player_pairs: Dict[str, Set[Tuple[str, str]]],
    all_possible_pairs: Set[Tuple[str, str]],
    player_info: Dict[str, Dict],
    verbose: bool = True,
) -> Tuple[List[str], Dict]:
    """
    Greedy algorithm to find minimal player set.

    Algorithm:
        1. Start with all pairs uncovered
        2. While uncovered pairs exist:
            a. Select player covering most uncovered pairs
            b. Mark their pairs as covered
        3. Return selected players

    Args:
        player_pairs: {playerID: set of franchise pairs}
        all_possible_pairs: set of all possible franchise pairs
        player_info: {playerID: player details}
        verbose: Print progress

    Returns:
        tuple of:
        - list of selected playerIDs
        - dict with statistics (iterations, coverage per player, etc.)

    Time Complexity:
        O(n × m) where n = number of players, m = number of iterations

    Example:
        >>> selected, stats = greedy_set_cover(player_pairs, all_pairs, player_info)
        >>> len(selected)  # Number of players needed
        42
    """
    if verbose:
        print()
        print("=" * 60)
        print("Greedy Set Cover Solver")
        print("=" * 60)
        print(f"Total pairs to cover: {len(all_possible_pairs)}")
        print(f"Total players available: {len(player_pairs)}")
        print()

    uncovered_pairs = all_possible_pairs.copy()
    selected_players = []

    stats = {
        "iterations": [],
        "players_selected": [],
        "pairs_covered_per_iteration": [],
        "runtime": 0,  # Will be set by caller
    }

    iteration = 0

    while uncovered_pairs:
        iteration += 1

        # Find player covering most uncovered pairs
        best_player = None
        best_coverage = 0
        best_covered_pairs = set()

        for player_id, pairs in player_pairs.items():
            if player_id in selected_players:
                continue

            # Count uncovered pairs this player covers
            newly_covered = pairs & uncovered_pairs

            if len(newly_covered) > best_coverage:
                best_coverage = len(newly_covered)
                best_player = player_id
                best_covered_pairs = newly_covered

        # If no player can cover any remaining pairs, we're done
        if best_player is None or best_coverage == 0:
            if verbose:
                print()
                print("⚠️  Warning: Cannot cover all pairs!")
                print(f"   {len(uncovered_pairs)} pairs remain uncovered")
            break

        # Select this player
        selected_players.append(best_player)
        uncovered_pairs -= best_covered_pairs

        # Track statistics
        stats["iterations"].append(iteration)
        stats["players_selected"].append(best_player)
        stats["pairs_covered_per_iteration"].append(len(best_covered_pairs))

        if verbose:
            name_first = player_info[best_player].get("nameFirst", "")
            name_last = player_info[best_player].get("nameLast", "")
            player_name = f"{name_first} {name_last}".strip() or best_player

            print(
                f"Iteration {iteration:3d}: Selected {player_name:30s} "
                f"(covers {best_coverage:3d} pairs, "
                f"{len(uncovered_pairs):3d} remaining)"
            )

    if verbose:
        print()
        print("=" * 60)
        print("✅ Greedy solution complete!")
        print(f"   Players selected: {len(selected_players)}")
        print(
            f"   Pairs covered: {len(all_possible_pairs) - len(uncovered_pairs)}/{len(all_possible_pairs)}"
        )
        if uncovered_pairs:
            print(f"   ⚠️  Uncovered pairs: {len(uncovered_pairs)}")
        print("=" * 60)
        print()

    return selected_players, stats


def analyze_greedy_solution(
    selected_players: List[str],
    player_pairs: Dict[str, Set[Tuple[str, str]]],
    player_info: Dict[str, Dict],
    all_possible_pairs: Set[Tuple[str, str]],
) -> Dict:
    """
    Analyze greedy solution quality.

    Args:
        selected_players: List of selected playerIDs
        player_pairs: Player→pairs mapping
        player_info: Player info dictionary
        all_possible_pairs: All possible pairs

    Returns:
        Dictionary with analysis metrics
    """
    # Calculate coverage
    covered_pairs = set()
    for player_id in selected_players:
        covered_pairs.update(player_pairs[player_id])

    uncovered_pairs = all_possible_pairs - covered_pairs

    # Find player contributions
    contributions = []
    for player_id in selected_players:
        name_first = player_info[player_id].get("nameFirst", "")
        name_last = player_info[player_id].get("nameLast", "")
        player_name = f"{name_first} {name_last}".strip()

        contributions.append(
            {
                "player_id": player_id,
                "player_name": player_name,
                "pairs_covered": len(player_pairs[player_id]),
                "total_franchises": len(
                    set(f for pair in player_pairs[player_id] for f in pair)
                ),
            }
        )

    return {
        "num_players": len(selected_players),
        "total_pairs": len(all_possible_pairs),
        "covered_pairs": len(covered_pairs),
        "uncovered_pairs": len(uncovered_pairs),
        "coverage_percentage": (len(covered_pairs) / len(all_possible_pairs)) * 100,
        "contributions": contributions,
    }


# For debugging/exploration
if __name__ == "__main__":
    import sys
    import time
    from pathlib import Path

    from src.data_processor import build_player_franchise_pairs
    from src.franchise_mapper import load_franchise_mapping

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

    print("\nRunning greedy solver...")
    start_time = time.time()
    selected_players, stats = greedy_set_cover(
        player_pairs, all_pairs, player_info, verbose=True
    )
    runtime = time.time() - start_time

    stats["runtime"] = runtime

    print("\nAnalyzing solution...")
    analysis = analyze_greedy_solution(
        selected_players, player_pairs, player_info, all_pairs
    )

    print("\n" + "=" * 60)
    print("Final Results")
    print("=" * 60)
    print(f"Players in solution: {analysis['num_players']}")
    print(f"Runtime: {runtime:.2f} seconds")
    print(
        f"Coverage: {analysis['covered_pairs']}/{analysis['total_pairs']} pairs ({analysis['coverage_percentage']:.2f}%)"
    )

    if analysis["uncovered_pairs"] > 0:
        print(f"⚠️  WARNING: {analysis['uncovered_pairs']} pairs not covered!")

    print("\nTop 10 players by franchise coverage:")
    sorted_contributions = sorted(
        analysis["contributions"], key=lambda x: x["pairs_covered"], reverse=True
    )

    for i, contrib in enumerate(sorted_contributions[:10], 1):
        print(
            f"{i:2d}. {contrib['player_name']:30s} "
            f"({contrib['total_franchises']:2d} franchises, "
            f"{contrib['pairs_covered']:3d} pairs)"
        )
