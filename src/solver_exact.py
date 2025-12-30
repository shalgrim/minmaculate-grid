"""
Exact ILP Set Cover Solver

Implements an exact Integer Linear Programming solution for the minimum set cover problem.
Uses PuLP to formulate and solve the optimization problem.

Formulation:
    Minimize: Σ x_i  (sum of selected players)
    Subject to: For each pair p, Σ(x_i where player i covers pair p) >= 1
    Where: x_i ∈ {0, 1} (binary decision variable for each player)
"""

from typing import Dict, Set, Tuple, List
import pulp


def exact_set_cover(
    player_pairs: Dict[str, Set[Tuple[str, str]]],
    all_possible_pairs: Set[Tuple[str, str]],
    player_info: Dict[str, Dict],
    verbose: bool = True,
    time_limit: int = 300
) -> Tuple[List[str], Dict]:
    """
    Exact ILP algorithm to find optimal player set.

    Uses Integer Linear Programming to find the provably optimal solution
    to the set cover problem.

    Args:
        player_pairs: {playerID: set of franchise pairs}
        all_possible_pairs: set of all possible franchise pairs
        player_info: {playerID: player details}
        verbose: Print progress
        time_limit: Maximum solver time in seconds (default 300)

    Returns:
        tuple of:
        - list of selected playerIDs
        - dict with statistics (status, objective_value, solve_time, etc.)

    Example:
        >>> selected, stats = exact_set_cover(player_pairs, all_pairs, player_info)
        >>> len(selected)  # Optimal number of players
        21
        >>> stats['status']
        'Optimal'
    """
    if verbose:
        print()
        print("=" * 60)
        print("Exact ILP Set Cover Solver")
        print("=" * 60)
        print(f"Total pairs to cover: {len(all_possible_pairs)}")
        print(f"Total players available: {len(player_pairs)}")
        print()

    # Check for infeasibility: are there any pairs that no player covers?
    uncoverable_pairs = []
    for pair in all_possible_pairs:
        if not any(pair in pairs for pairs in player_pairs.values()):
            uncoverable_pairs.append(pair)

    if uncoverable_pairs:
        if verbose:
            print(f"❌ Problem is infeasible!")
            print(f"   {len(uncoverable_pairs)} pairs cannot be covered by any player:")
            for pair in uncoverable_pairs[:5]:  # Show first 5
                print(f"     {pair}")
            if len(uncoverable_pairs) > 5:
                print(f"     ... and {len(uncoverable_pairs) - 5} more")
            print()

        return [], {
            "status": "Infeasible",
            "objective_value": None,
            "num_players": 0,
            "pairs_covered": 0,
            "total_pairs": len(all_possible_pairs),
            "coverage_percentage": 0.0,
        }

    # Create the optimization problem
    prob = pulp.LpProblem("MinimalSetCover", pulp.LpMinimize)

    # Decision variables: x[player_id] = 1 if player is selected, 0 otherwise
    player_vars = {
        player_id: pulp.LpVariable(f"x_{player_id}", cat=pulp.LpBinary)
        for player_id in player_pairs.keys()
    }

    # Objective function: minimize number of players selected
    prob += pulp.lpSum(player_vars.values()), "TotalPlayers"

    # Constraints: each pair must be covered by at least one selected player
    for pair in all_possible_pairs:
        # Find all players who cover this pair
        players_covering_pair = [
            player_vars[player_id]
            for player_id, pairs in player_pairs.items()
            if pair in pairs
        ]

        # At least one player covering this pair must be selected
        # (We already checked that all pairs are coverable)
        prob += (
            pulp.lpSum(players_covering_pair) >= 1,
            f"Cover_{pair[0]}_{pair[1]}"
        )

    if verbose:
        print("Solving ILP...")
        print(f"Variables: {len(player_vars)}")
        print(f"Constraints: {len(all_possible_pairs)}")
        print()

    # Solve the problem
    solver = pulp.PULP_CBC_CMD(
        msg=1 if verbose else 0,
        timeLimit=time_limit
    )

    prob.solve(solver)

    # Extract results
    status = pulp.LpStatus[prob.status]

    if status == "Optimal" or status == "Feasible":
        # Get selected players
        selected_players = [
            player_id
            for player_id, var in player_vars.items()
            if pulp.value(var) == 1
        ]

        # Calculate coverage
        covered_pairs = set()
        for player_id in selected_players:
            covered_pairs.update(player_pairs[player_id])

        if verbose:
            print("=" * 60)
            print(f"✅ Solution found: {status}")
            print(f"   Players selected: {len(selected_players)}")
            print(f"   Pairs covered: {len(covered_pairs)}/{len(all_possible_pairs)}")
            print(f"   Objective value: {pulp.value(prob.objective)}")
            print("=" * 60)
            print()

            # Print selected players
            print("Selected players:")
            for i, player_id in enumerate(selected_players, 1):
                name_first = player_info[player_id].get("nameFirst", "")
                name_last = player_info[player_id].get("nameLast", "")
                player_name = f"{name_first} {name_last}".strip() or player_id

                franchises = len(set(f for pair in player_pairs[player_id] for f in pair))
                pairs_count = len(player_pairs[player_id])

                print(f"{i:3d}. {player_name:30s} "
                      f"({franchises:2d} franchises, {pairs_count:3d} pairs)")
            print()

        stats = {
            "status": status,
            "objective_value": pulp.value(prob.objective),
            "num_players": len(selected_players),
            "pairs_covered": len(covered_pairs),
            "total_pairs": len(all_possible_pairs),
            "coverage_percentage": (len(covered_pairs) / len(all_possible_pairs)) * 100,
        }

    else:
        # Problem is infeasible or unbounded
        selected_players = []

        if verbose:
            print("=" * 60)
            print(f"❌ Solution status: {status}")
            print("=" * 60)
            print()

        stats = {
            "status": status,
            "objective_value": None,
            "num_players": 0,
            "pairs_covered": 0,
            "total_pairs": len(all_possible_pairs),
            "coverage_percentage": 0.0,
        }

    return selected_players, stats


# For debugging/exploration
if __name__ == "__main__":
    import sys
    import time
    from pathlib import Path
    from src.franchise_mapper import load_franchise_mapping
    from src.data_processor import build_player_franchise_pairs

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
        str(appearances_csv),
        str(teams_csv),
        str(people_csv),
        mapping,
        min_games=1
    )

    print(f"\nRunning exact ILP solver on full dataset...")
    print(f"This may take several minutes...")
    print()

    start_time = time.time()
    selected_players, stats = exact_set_cover(player_pairs, all_pairs, player_info, verbose=True)
    runtime = time.time() - start_time

    print("\n" + "=" * 60)
    print("Final Results")
    print("=" * 60)
    print(f"Status: {stats['status']}")
    print(f"Players in solution: {stats['num_players']}")
    print(f"Runtime: {runtime:.2f} seconds")
    print(f"Coverage: {stats['pairs_covered']}/{stats['total_pairs']} pairs ({stats['coverage_percentage']:.2f}%)")
    print("=" * 60)
