"""
FastAPI Web Application for Minmaculate Grid

Provides RESTful API endpoints for querying player data, solutions, and coverage.
Serves the frontend HTML/CSS/JS application.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database

# Create FastAPI app
app = FastAPI(
    title="Minmaculate Grid API",
    description="Baseball player minimum set cover solver",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Database connection
DB_PATH = "minmaculate.db"
db = Database(DB_PATH)


# Pydantic models
class PlayerResponse(BaseModel):
    player_id: str
    name_first: str
    name_last: str
    debut: str
    full_name: str


class FranchisePair(BaseModel):
    id: int
    franchise_1: str
    franchise_2: str


class PlayerDetailResponse(BaseModel):
    player_id: str
    name_first: str
    name_last: str
    debut: str
    full_name: str
    pairs_covered: List[FranchisePair]
    num_pairs: int


class SolutionSummary(BaseModel):
    id: int
    algorithm: str
    num_players: int
    runtime_seconds: float
    coverage_percentage: float
    created_at: str


class SolutionPlayer(BaseModel):
    player_id: str
    name_first: str
    name_last: str
    full_name: str
    rank: int
    num_pairs: int


class SolutionDetailResponse(BaseModel):
    id: int
    algorithm: str
    num_players: int
    runtime_seconds: float
    coverage_percentage: float
    created_at: str
    players: List[SolutionPlayer]


class PairCoverageResponse(BaseModel):
    franchise_1: str
    franchise_2: str
    players: List[PlayerResponse]
    num_players: int


class CoverageMatrixResponse(BaseModel):
    franchises: List[str]
    matrix: List[List[int]]


# API Endpoints


@app.get("/", response_class=FileResponse)
async def root():
    """Serve the main frontend HTML page."""
    html_path = Path(__file__).parent / "static" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(html_path)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        players = db.execute("SELECT COUNT(*) as count FROM players")
        return {
            "status": "healthy",
            "database": "connected",
            "players": players[0]["count"],
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


@app.get("/api/players", response_model=List[PlayerResponse])
async def get_players(limit: int = 100, offset: int = 0):
    """Get list of all players with pagination."""
    players = db.execute(
        """
        SELECT player_id, name_first, name_last, debut
        FROM players
        ORDER BY name_last, name_first
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )

    return [
        PlayerResponse(
            player_id=p["player_id"],
            name_first=p["name_first"],
            name_last=p["name_last"],
            debut=p["debut"],
            full_name=f"{p['name_first']} {p['name_last']}".strip(),
        )
        for p in players
    ]


@app.get("/api/players/{player_id}", response_model=PlayerDetailResponse)
async def get_player_detail(player_id: str):
    """Get player details including all pairs they cover."""
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
        pairs_covered=[
            FranchisePair(
                id=c["id"], franchise_1=c["franchise_1"], franchise_2=c["franchise_2"]
            )
            for c in coverage
        ],
        num_pairs=len(coverage),
    )


@app.get("/api/solutions", response_model=List[SolutionSummary])
async def get_solutions():
    """Get all solutions (greedy, exact, etc.)."""
    solutions = db.execute("SELECT * FROM solutions ORDER BY created_at DESC")

    return [SolutionSummary(**s) for s in solutions]


@app.get("/api/solutions/{solution_id}", response_model=SolutionDetailResponse)
async def get_solution_detail(solution_id: int):
    """Get solution details including all players."""
    solution = db.get_solution(solution_id)
    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")

    players = db.get_solution_players(solution_id)

    # Get coverage count for each player
    player_list = []
    for p in players:
        coverage = db.get_player_coverage(p["player_id"])
        player_list.append(
            SolutionPlayer(
                player_id=p["player_id"],
                name_first=p["name_first"],
                name_last=p["name_last"],
                full_name=f"{p['name_first']} {p['name_last']}".strip(),
                rank=p["rank"],
                num_pairs=len(coverage),
            )
        )

    return SolutionDetailResponse(
        id=solution["id"],
        algorithm=solution["algorithm"],
        num_players=solution["num_players"],
        runtime_seconds=solution["runtime_seconds"],
        coverage_percentage=solution["coverage_percentage"],
        created_at=solution["created_at"],
        players=player_list,
    )


@app.get("/api/pairs", response_model=List[FranchisePair])
async def get_pairs():
    """Get all 435 franchise pairs."""
    pairs = db.get_all_franchise_pairs()
    return [FranchisePair(**p) for p in pairs]


@app.get("/api/pairs/{franchise1}/{franchise2}", response_model=PairCoverageResponse)
async def get_pair_coverage(franchise1: str, franchise2: str):
    """Get all players who played for both franchises."""
    # Ensure sorted order
    f1, f2 = sorted([franchise1.upper(), franchise2.upper()])

    pair_id = db.get_franchise_pair_id(f1, f2)
    if not pair_id:
        raise HTTPException(status_code=404, detail="Franchise pair not found")

    players = db.get_players_covering_pair(pair_id)

    return PairCoverageResponse(
        franchise_1=f1,
        franchise_2=f2,
        players=[
            PlayerResponse(
                player_id=p["player_id"],
                name_first=p["name_first"],
                name_last=p["name_last"],
                debut=p["debut"],
                full_name=f"{p['name_first']} {p['name_last']}".strip(),
            )
            for p in players
        ],
        num_players=len(players),
    )


@app.get("/api/coverage-matrix", response_model=CoverageMatrixResponse)
async def get_coverage_matrix():
    """Get 30×30 heatmap data showing number of players per pair."""
    # Get all franchises
    pairs = db.get_all_franchise_pairs()

    # Extract unique franchises
    franchises = set()
    for pair in pairs:
        franchises.add(pair["franchise_1"])
        franchises.add(pair["franchise_2"])

    franchises = sorted(franchises)
    n = len(franchises)

    # Create franchise index mapping
    fran_to_idx = {f: i for i, f in enumerate(franchises)}

    # Initialize matrix
    matrix = [[0 for _ in range(n)] for _ in range(n)]

    # Fill matrix with player counts
    for pair in pairs:
        f1_idx = fran_to_idx[pair["franchise_1"]]
        f2_idx = fran_to_idx[pair["franchise_2"]]

        # Get player count for this pair
        players = db.get_players_covering_pair(pair["id"])
        count = len(players)

        # Matrix is symmetric
        matrix[f1_idx][f2_idx] = count
        matrix[f2_idx][f1_idx] = count

    return CoverageMatrixResponse(franchises=franchises, matrix=matrix)
