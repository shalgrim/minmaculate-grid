# Implementation Plan: Database Population & Web Interface

## Overview

Complete 4 tasks:
1. **Run comparison script** - Execute existing solver comparison to get results
2. **Update status file** - Document exact solver and database completion with metrics
3. **Create database population script** - Populate SQLite with all player data and solutions
4. **Build full web interface** - FastAPI backend + frontend with visualizations

## Implementation Order

### Phase 1: Data & Documentation (Tasks 1-2)

#### Task 1: Run Comparison Script
```bash
cd /Users/scotthalgrim/repos/minmaculate-grid
python scripts/compare_solvers.py
```

**Capture metrics**:
- Solution sizes (greedy vs exact)
- Runtimes
- Approximation ratio
- Coverage percentages
- Player overlap counts

#### Task 2: Update Status File

**File**: `claude-status.md`

**Changes**:
- Move exact solver and database from "Future Enhancements" to "Completed"
- Add new "Solver Comparison Results" section with metrics from Task 1
- Update project statistics

### Phase 2: Database Population (Task 3)

#### Create: `scripts/populate_database.py`

**Purpose**: Populate SQLite database with all players, pairs, coverage, and solutions

**Key functions**:
1. Parse arguments (--db-path, --skip-exact, --time-limit)
2. Load data using existing `data_processor` and `franchise_mapper`
3. Populate `players` table (~19,947 players)
4. Populate `franchise_pairs` table (435 pairs)
5. Populate `player_coverage` table (which pairs each player covers)
6. Run greedy solver and save to `solutions` table
7. Run exact ILP solver and save to `solutions` table (unless --skip-exact)
8. Display summary with database stats

**Pattern to follow**: `scripts/download_data.py` (docstring, path setup, verbose output)

**Dependencies**: Uses existing `src/database.py` class

### Phase 3: Web Backend (Task 4A)

#### Create: `web/api.py`

**FastAPI application with 9 endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve frontend HTML |
| `/api/health` | GET | Health check |
| `/api/players` | GET | List players (paginated) |
| `/api/players/{player_id}` | GET | Player details + coverage |
| `/api/solutions` | GET | List all solutions |
| `/api/solutions/{id}` | GET | Solution details + players |
| `/api/pairs` | GET | All 435 franchise pairs |
| `/api/pairs/{f1}/{f2}` | GET | Players covering specific pair |
| `/api/coverage-matrix` | GET | 30×30 heatmap data |

**Key setup**:
- Import Database class from `src/database.py`
- Enable CORS middleware
- Mount static files from `web/static/`
- Define Pydantic response models
- Database instance: `db = Database("minmaculate.db")`

**Response models** (Pydantic):
- PlayerResponse
- PlayerDetailResponse
- SolutionSummary
- SolutionDetailResponse
- FranchisePair
- PairCoverageResponse
- CoverageMatrixResponse

### Phase 4: Web Frontend (Task 4B)

#### Create: `web/static/index.html`

**Sections**:
1. Solutions comparison table
2. Solution detail view with player list
3. Interactive 30×30 coverage heatmap
4. Player search
5. Pair lookup tool

**Dependencies**:
- Bootstrap 5 for UI
- Plotly.js for heatmap (better than Chart.js for matrix visualization)

#### Create: `web/static/css/style.css`

**Styling**:
- Clean, professional design
- Baseball-themed colors
- Responsive layout
- Card-based UI components

#### Create: `web/static/js/app.js`

**Key functions**:
- `init()` - Load initial data
- `loadSolutions()` - Fetch and display solutions comparison
- `loadSolutionDetail(id)` - Show specific solution players
- `loadCoverageHeatmap()` - Render 30×30 matrix with Plotly
- `searchPlayers(query)` - Search with debouncing
- `lookupPair(f1, f2)` - Find players for franchise pair

**Architecture**: Vanilla JavaScript with async/await

### Phase 5: Testing (Task 4C)

#### Create: `tests/test_api.py`

**Test classes** (following pytest pattern):
- `TestAPIHealth` - Health check endpoint
- `TestPlayersEndpoints` - Player listing and detail endpoints
- `TestSolutionsEndpoints` - Solution endpoints
- `TestPairsEndpoints` - Pair coverage endpoints
- `TestCoverageMatrix` - Matrix endpoint

**Pattern**: Use `TestClient` from FastAPI with temporary database fixtures

## Critical Files

### Files to Create (6 new files)

1. `scripts/populate_database.py` - Database population script
2. `web/api.py` - FastAPI backend
3. `web/static/index.html` - Frontend HTML
4. `web/static/css/style.css` - Styles
5. `web/static/js/app.js` - Frontend logic
6. `tests/test_api.py` - API tests

### Files to Modify (2 files)

1. `claude-status.md` - Add comparison results section
2. `README.md` - Add web interface documentation

### Files to Reference

- `src/database.py` - Database class and schema (already complete)
- `scripts/compare_solvers.py` - Solver comparison pattern
- `scripts/download_data.py` - Script structure pattern
- `tests/test_database.py` - Testing pattern

## Key Implementation Details

### Database Population Script Structure

```python
#!/usr/bin/env python3
"""Populate SQLite Database with Players and Solutions"""

import argparse
from pathlib import Path
from src.database import Database
from src.data_processor import build_player_franchise_pairs
from src.franchise_mapper import load_franchise_mapping
from src.solver_greedy import greedy_set_cover
from src.solver_exact import exact_set_cover

def main():
    # 1. Parse arguments
    # 2. Load data from CSVs
    # 3. Initialize database
    # 4. Populate players table
    # 5. Populate franchise_pairs table (create pair_id_map)
    # 6. Populate player_coverage table
    # 7. Run greedy solver, save solution
    # 8. Run exact solver, save solution (unless --skip-exact)
    # 9. Print summary
```

### API Endpoint Example

```python
@app.get("/api/players/{player_id}", response_model=PlayerDetailResponse)
async def get_player_detail(player_id: str):
    player = db.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    coverage = db.get_player_coverage(player_id)

    return PlayerDetailResponse(
        player_id=player["player_id"],
        name_first=player["name_first"],
        name_last=player["name_last"],
        debut=player["debut"],
        full_name=f"{player['name_first']} {player['name_last']}".strip(),
        pairs_covered=[FranchisePair(**c) for c in coverage],
        num_pairs=len(coverage)
    )
```

### Frontend Heatmap (Plotly.js)

```javascript
async function loadCoverageHeatmap() {
    const data = await fetchAPI('/coverage-matrix');

    const heatmapData = [{
        z: data.matrix,
        x: data.franchises,
        y: data.franchises,
        type: 'heatmap',
        colorscale: 'Blues'
    }];

    Plotly.newPlot('coverageHeatmap', heatmapData, {
        title: 'Player Coverage by Franchise Pair',
        xaxis: { title: 'Franchise' },
        yaxis: { title: 'Franchise' }
    });
}
```

## Execution Checklist

- [ ] Run `python scripts/compare_solvers.py` and capture output
- [ ] Update `claude-status.md` with comparison results
- [ ] Create `scripts/populate_database.py`
- [ ] Run population script: `python scripts/populate_database.py`
- [ ] Verify database created: `minmaculate.db` should exist
- [ ] Create `web/api.py` with all 9 endpoints
- [ ] Create frontend files (HTML, CSS, JS)
- [ ] Create `tests/test_api.py`
- [ ] Run tests: `pytest tests/test_api.py -v`
- [ ] Start server: `uvicorn web.api:app --reload`
- [ ] Test web interface in browser at http://localhost:8000
- [ ] Update README.md with usage instructions

## Dependencies

**Already installed**:
- fastapi, uvicorn, pydantic (web framework)
- pandas, pulp (data processing and optimization)
- pytest (testing)

**May need to add**:
- httpx (for TestClient if not already installed)
- pytest-asyncio (for async tests if not already installed)

## Expected Runtime

- Comparison script: 5-10 minutes (exact solver)
- Database population: 5-10 minutes (exact solver)
- Web development: 2-3 hours
- Testing: 30 minutes

Total: ~4 hours

## Success Criteria

✅ Comparison script runs successfully and shows greedy vs exact results
✅ Status file updated with accurate metrics
✅ Database populated with all players, pairs, coverage, and solutions
✅ API endpoints return correct data
✅ All tests pass
✅ Web interface loads and displays data correctly
✅ Heatmap visualization works
✅ Player search and pair lookup function properly
