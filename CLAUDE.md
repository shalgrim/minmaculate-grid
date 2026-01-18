# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Minmaculate Grid Solver finds the minimum set of baseball players needed to cover all possible MLB franchise pair combinations for Immaculate Grid gameplay. This is a Set Cover Problem (NP-complete) solved using both greedy and ILP (Integer Linear Programming) approaches.

## Commands

### Setup
```bash
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
```

### Download Data
```bash
python scripts/download_data.py  # Downloads Lahman database to data/
```

### Populate Database
```bash
python scripts/populate_database.py           # Full run with exact solver (~9 min)
python scripts/populate_database.py --skip-exact  # Skip ILP solver (fast)
```

### Franchise-Constrained Solver
```bash
python scripts/solve_for_franchise.py MIN              # Find MIN-constrained solution
python scripts/solve_for_franchise.py NYY --greedy     # Greedy only (fast)
python scripts/solve_for_franchise.py MIN --output results/min_solution.md
```

### Run Tests
```bash
pytest                              # Run all tests
pytest tests/test_api.py -v         # Run single test file
pytest -k test_greedy_basic         # Run single test by name
```

### Linting
```bash
ruff check src/ tests/ web/
black --check src/ tests/ web/
mypy src/
```

### Run Web Server
```bash
uvicorn web.api:app --reload --port 8000
```

## Architecture

### Core Modules (src/)

- **franchise_mapper.py**: Maps historical teamIDs to current franchIDs (e.g., Brooklyn Dodgers → LAD). Uses Lahman's Teams.csv franchID column.

- **data_processor.py**: Processes Lahman CSVs to build `player_pairs` (playerID → set of franchise pair tuples), `player_info` (biographical data), `all_possible_pairs` (435 C(30,2) combinations), and `player_franchises` (playerID → set of franchises). Also provides `filter_players_by_franchise()` for constrained solving.

- **solver_greedy.py**: Greedy approximation - iteratively selects player covering most uncovered pairs. Fast (~0.1s), returns 21 players.

- **solver_exact.py**: ILP solver using PuLP/CBC - minimizes Σx_i subject to each pair covered by ≥1 player. Supports partial coverage (filters uncoverable pairs). Slow (~9 min), returns optimal 19 players.

- **database.py**: SQLite persistence with tables: `players`, `franchise_pairs`, `solutions`, `solution_players`, `player_coverage`, `player_franchises`. Uses row_factory for dict-style access.

### Web Layer (web/)

- **api.py**: FastAPI application with REST endpoints. Serves static frontend at `/`. Key endpoints: `/api/solutions`, `/api/players/{id}`, `/api/pairs/{f1}/{f2}`, `/api/coverage-matrix`.

### Data Flow

1. `download_data.py` → Lahman CSVs in `data/`
2. `populate_database.py` → Calls `franchise_mapper` + `data_processor` → runs solvers → stores in `minmaculate.db`
3. `web/api.py` → queries SQLite via `Database` class → serves JSON to frontend

### Key Data Structures

- **player_pairs**: `Dict[str, Set[Tuple[str, str]]]` - playerID to set of franchise pair tuples (sorted alphabetically)
- **player_franchises**: `Dict[str, Set[str]]` - playerID to set of franchise IDs they played for
- **all_possible_pairs**: `Set[Tuple[str, str]]` - all 435 combinations of 30 current MLB franchises
- Franchise pairs stored as sorted tuples: `("ARI", "ATL")` not `("ATL", "ARI")`

### Franchise-Constrained Solving

The `solve_for_franchise.py` script finds the minimum players who ALL played for a specific franchise:
1. Filters `player_pairs` to only players from target franchise
2. Checks coverage feasibility (some pairs may be uncoverable)
3. Runs greedy and/or exact solver on filtered players
4. Exact solver handles partial coverage by optimizing only coverable pairs
