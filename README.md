# Minmaculate Grid Solver

Find the minimum set of baseball players needed to cover all possible MLB franchise pair combinations for Immaculate Grid gameplay.

## Problem Statement

Given 30 current MLB franchises, find the smallest set of players such that for every pair of franchises, at least one player in the set played for both teams.

- **Total franchise pairs**: C(30,2) = 435 combinations
- **Constraint**: Each pair must have ≥1 player who played for both teams
- **Goal**: Minimize the number of players needed
- **Approach**: This is a **Set Cover Problem** (NP-complete), solved using:
  1. **Greedy heuristic** - Fast approximation (near-optimal)
  2. **Exact optimization** - Integer Linear Programming (provably optimal)

## Historical Team Mapping

Historical teams are mapped to their current franchises:
- Brooklyn Dodgers → Los Angeles Dodgers
- Montreal Expos → Washington Nationals
- Seattle Pilots → Milwaukee Brewers
- etc.

## Technology Stack

- **Python 3.11+** with pandas, numpy
- **PuLP** - Integer Linear Programming for exact solver
- **SQLite** - Persistent storage for results
- **FastAPI + Uvicorn** - Async web API with automatic OpenAPI docs
- **Bootstrap 5 + Chart.js** - Frontend visualization

## Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt

# Install dev dependencies (for testing)
uv pip install -r requirements-dev.txt
```

## Usage

### 1. Download Data

```bash
python scripts/download_data.py
```

Downloads the Sean Lahman Baseball Database (2025 edition) into the `data/` directory.

### 2. Populate Database

```bash
# Populate database with all players, pairs, and solutions
python scripts/populate_database.py

# Skip the exact solver (faster, only runs greedy)
python scripts/populate_database.py --skip-exact

# Custom database path
python scripts/populate_database.py --db-path custom.db
```

This script:
- Loads all 19,947 players from the Lahman database
- Creates 435 franchise pairs
- Populates player coverage data (58,163 entries)
- Runs greedy solver (~0.1 seconds)
- Runs exact ILP solver (~9 minutes, can be skipped)
- Saves results to SQLite database

### 3. Compare Solvers

```bash
# Compare greedy vs exact solver performance
python scripts/compare_solvers.py
```

Shows:
- Solution sizes (greedy: 21 players, exact: 19 players)
- Runtime comparison
- Approximation ratio (1.1053)
- Player overlap analysis

### 4. Franchise-Constrained Solver

Find the minimum players who ALL played for a specific franchise:

```bash
# Find MIN-constrained solution (includes Washington Senators history)
python scripts/solve_for_franchise.py MIN

# Run only greedy solver (faster)
python scripts/solve_for_franchise.py NYY --greedy

# Save results to markdown file
python scripts/solve_for_franchise.py MIN --output results/min_solution.md

# Custom time limit for exact solver (default: 600s)
python scripts/solve_for_franchise.py LAD --time-limit 300
```

This finds players who played for the target franchise AND enough other teams to cover all 435 pairs. Some pairs may be uncoverable if no player from that franchise played for both teams in the pair.

**Example**: MIN-constrained solution requires **34 players** (optimal) covering 434/435 pairs. The FLA-STL pair is uncoverable because no Twins/Senators player ever played for both Florida and St. Louis.

### 5. Start Web Interface

```bash
# Start FastAPI server
uvicorn web.api:app --reload --port 8000

# Access the app at:
# - Frontend: http://localhost:8000
# - API docs: http://localhost:8000/docs (automatic Swagger UI)
```

**Web Interface Features:**
- Solutions comparison table (greedy vs exact)
- Interactive player list for each solution
- 30×30 coverage heatmap showing player counts per franchise pair
- Player search and lookup
- Franchise pair lookup (find all players who played for two teams)

### 6. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## Project Structure

```
minmaculate-grid/
├── src/              # Core Python modules
├── tests/            # Unit and integration tests
├── web/              # FastAPI application and frontend
├── scripts/          # CLI scripts
├── data/             # Lahman database CSVs (not in git)
└── results/          # Solution outputs
```

## Results

### Optimal Solution (Exact ILP Solver) 🏆

**Players needed: 19** ✅ **PROVEN OPTIMAL**
**Runtime: ~9.3 minutes (557 seconds)**
**Coverage: 435/435 pairs (100%)**

The exact Integer Linear Programming solver found the **provably optimal minimum solution**:

**Complete Optimal Player List:**
1. Chase Anderson
2. Ken Brett
3. Lew Burdette
4. Bruce Chen
5. Dennis Cook
6. Jose Cruz
7. Octavio Dotel
8. Jose Guillen
9. Billy Hamilton
10. LaTroy Hawkins
11. Rich Hill
12. Edwin Jackson
13. Mike Morgan
14. Lance Parrish
15. Edgar Renteria
16. Fernando Rodney
17. Matt Stairs
18. Anthony Swarzak
19. Ron Villone

**Memorize these 19 players and you'll be able to answer every possible two-team combination in Immaculate Grid!**

### Greedy Solver Solution

**Players needed: 21**
**Runtime: 0.10 seconds**
**Coverage: 435/435 pairs (100%)**

The greedy algorithm provides a fast approximation requiring 21 players:

**Top Players in Greedy Solution:**
1. **Edwin Jackson** - 14 franchises, 91 pairs (21% of all pairs!)
2. **Rich Hill** - 13 franchises, 78 pairs
3. **Ron Villone** - 12 franchises, 66 pairs
4. **Bruce Chen** - 11 franchises, 55 pairs
5. **Octavio Dotel** - 13 franchises, 78 pairs
6. **Royce Clayton** - 11 franchises, 55 pairs
7. **Terry Mulholland** - 11 franchises, 55 pairs
8. **LaTroy Hawkins** - 11 franchises, 55 pairs
9. **Matt Stairs** - 12 franchises, 66 pairs
10. **Jose Guillen** - 10 franchises, 45 pairs

*(See `answers.md` for complete lists with franchise details)*

### Comparison

| Metric | Greedy | Exact (Optimal) |
|--------|--------|-----------------|
| **Solution Size** | 21 players | **19 players** 🏆 |
| **Runtime** | 0.10 seconds | 557.82 seconds (~9.3 min) |
| **Approximation Ratio** | 1.1053 (11% over optimal) | 1.0000 (proven optimal) |
| **Coverage** | 435/435 pairs (100%) | 435/435 pairs (100%) |

**Key Insights:**
- The exact solver found a solution **2 players smaller** than greedy (9.5% improvement)
- Greedy is **5,578x faster** but slightly suboptimal
- **10 players appear in both solutions** (core journeymen like Edwin Jackson, Rich Hill, etc.)
- For memorization purposes, the difference between 19 and 21 players is minimal
- **Mathematical certainty**: 19 is the absolute minimum - no solution with 18 or fewer players exists

## Data Credits

This project uses the **Sean Lahman Baseball Database**.

**Copyright**: 1996-2025 by Sean Lahman (sean@lahman.com)
**License**: [Creative Commons Attribution-ShareAlike 3.0 Unported License](https://creativecommons.org/licenses/by-sa/3.0/)
**Source**: https://sabr.org/lahman-database/

We are deeply grateful to Sean Lahman for making this comprehensive baseball dataset freely available to the public.

## License

MIT License (for our code only; data is CC BY-SA 3.0 as noted above)
