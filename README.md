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

### Download Data

```bash
python scripts/download_data.py
```

### Run Solvers

```bash
# Run both greedy and exact algorithms
python scripts/run_solver.py --method both

# Run only greedy (fast)
python scripts/run_solver.py --method greedy

# Run exact with custom time limit
python scripts/run_solver.py --method exact --time-limit 7200
```

### Start Web Interface

```bash
# Start FastAPI server
uvicorn web.api:app --reload --port 8000

# Access the app at:
# - Frontend: http://localhost:8000/static/index.html
# - API docs: http://localhost:8000/docs (automatic Swagger UI!)
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
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

(Results will be added after running the solvers)

## Data Credits

This project uses the **Sean Lahman Baseball Database**.

**Copyright**: 1996-2025 by Sean Lahman (sean@lahman.com)
**License**: [Creative Commons Attribution-ShareAlike 3.0 Unported License](https://creativecommons.org/licenses/by-sa/3.0/)
**Source**: https://sabr.org/lahman-database/

We are deeply grateful to Sean Lahman for making this comprehensive baseball dataset freely available to the public.

## License

MIT License (for our code only; data is CC BY-SA 3.0 as noted above)
