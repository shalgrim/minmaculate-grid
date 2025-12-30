"""
SQLite Database Module

Provides persistent storage for:
- Players and their biographical data
- Franchise pairs (all 435 combinations)
- Solutions (greedy, exact, etc.)
- Player coverage (which pairs each player covers)
"""

import sqlite3
from typing import Dict, List, Optional


class Database:
    """SQLite database interface for minmaculate grid data."""

    def __init__(self, db_path: str):
        """
        Initialize database connection and create schema.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self._create_schema()

    def _create_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                name_first TEXT,
                name_last TEXT,
                debut TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Franchise pairs table (all 435 combinations)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS franchise_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                franchise_1 TEXT NOT NULL,
                franchise_2 TEXT NOT NULL,
                UNIQUE(franchise_1, franchise_2)
            )
        """)

        # Solutions table (stores greedy, exact, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                algorithm TEXT NOT NULL,
                num_players INTEGER NOT NULL,
                runtime_seconds REAL,
                coverage_percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Solution players (many-to-many: solutions <-> players)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solution_players (
                solution_id INTEGER NOT NULL,
                player_id TEXT NOT NULL,
                rank INTEGER,
                FOREIGN KEY (solution_id) REFERENCES solutions(id),
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                PRIMARY KEY (solution_id, player_id)
            )
        """)

        # Player coverage (which pairs each player covers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_coverage (
                player_id TEXT NOT NULL,
                pair_id INTEGER NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (pair_id) REFERENCES franchise_pairs(id),
                PRIMARY KEY (player_id, pair_id)
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_solution_algorithm
            ON solutions(algorithm, created_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_coverage_player
            ON player_coverage(player_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_player_coverage_pair
            ON player_coverage(pair_id)
        """)

        self.conn.commit()

    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        self.conn.close()

    # Player operations

    def insert_player(
        self, player_id: str, name_first: str, name_last: str, debut: str
    ):
        """Insert a player into the database."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO players (player_id, name_first, name_last, debut)
            VALUES (?, ?, ?, ?)
            """,
            (player_id, name_first, name_last, debut),
        )
        self.conn.commit()

    def get_player(self, player_id: str) -> Optional[Dict]:
        """Get a player by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_players(self) -> List[Dict]:
        """Get all players."""
        return self.execute("SELECT * FROM players ORDER BY name_last, name_first")

    # Franchise pair operations

    def insert_franchise_pair(self, franchise_1: str, franchise_2: str) -> int:
        """
        Insert a franchise pair.

        Pairs are stored sorted (franchise_1 < franchise_2).

        Returns:
            The ID of the inserted pair
        """
        # Sort the franchises
        f1, f2 = sorted([franchise_1, franchise_2])

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO franchise_pairs (franchise_1, franchise_2)
            VALUES (?, ?)
            """,
            (f1, f2),
        )
        self.conn.commit()

        # Get the ID
        cursor.execute(
            "SELECT id FROM franchise_pairs WHERE franchise_1 = ? AND franchise_2 = ?",
            (f1, f2),
        )
        return cursor.fetchone()[0]

    def get_all_franchise_pairs(self) -> List[Dict]:
        """Get all franchise pairs."""
        return self.execute(
            "SELECT * FROM franchise_pairs ORDER BY franchise_1, franchise_2"
        )

    def get_franchise_pair_id(
        self, franchise_1: str, franchise_2: str
    ) -> Optional[int]:
        """Get the ID of a franchise pair."""
        f1, f2 = sorted([franchise_1, franchise_2])
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM franchise_pairs WHERE franchise_1 = ? AND franchise_2 = ?",
            (f1, f2),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    # Solution operations

    def save_solution(
        self,
        algorithm: str,
        player_ids: List[str],
        num_players: int,
        runtime: float,
        coverage: float,
    ) -> int:
        """
        Save a solution to the database.

        Args:
            algorithm: Algorithm name (e.g., "greedy", "exact")
            player_ids: List of player IDs in the solution
            num_players: Number of players
            runtime: Runtime in seconds
            coverage: Coverage percentage

        Returns:
            Solution ID
        """
        cursor = self.conn.cursor()

        # Insert solution
        cursor.execute(
            """
            INSERT INTO solutions (algorithm, num_players, runtime_seconds, coverage_percentage)
            VALUES (?, ?, ?, ?)
            """,
            (algorithm, num_players, runtime, coverage),
        )
        solution_id = cursor.lastrowid

        # Insert solution players with rank
        for rank, player_id in enumerate(player_ids, 1):
            cursor.execute(
                """
                INSERT INTO solution_players (solution_id, player_id, rank)
                VALUES (?, ?, ?)
                """,
                (solution_id, player_id, rank),
            )

        self.conn.commit()
        return solution_id

    def get_solution(self, solution_id: int) -> Optional[Dict]:
        """Get a solution by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM solutions WHERE id = ?", (solution_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_latest_solution(self, algorithm: str) -> Optional[Dict]:
        """Get the most recent solution for a given algorithm."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM solutions
            WHERE algorithm = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (algorithm,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_solution_players(self, solution_id: int) -> List[Dict]:
        """Get all players in a solution, ordered by rank."""
        return self.execute(
            """
            SELECT p.*, sp.rank
            FROM solution_players sp
            JOIN players p ON sp.player_id = p.player_id
            WHERE sp.solution_id = ?
            ORDER BY sp.rank
            """,
            (solution_id,),
        )

    # Player coverage operations

    def add_player_coverage(self, player_id: str, pair_id: int):
        """Record that a player covers a specific franchise pair."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO player_coverage (player_id, pair_id)
            VALUES (?, ?)
            """,
            (player_id, pair_id),
        )
        self.conn.commit()

    def get_player_coverage(self, player_id: str) -> List[Dict]:
        """Get all franchise pairs covered by a player."""
        return self.execute(
            """
            SELECT fp.*
            FROM player_coverage pc
            JOIN franchise_pairs fp ON pc.pair_id = fp.id
            WHERE pc.player_id = ?
            ORDER BY fp.franchise_1, fp.franchise_2
            """,
            (player_id,),
        )

    def get_players_covering_pair(self, pair_id: int) -> List[Dict]:
        """Get all players that cover a specific franchise pair."""
        return self.execute(
            """
            SELECT p.*
            FROM player_coverage pc
            JOIN players p ON pc.player_id = p.player_id
            WHERE pc.pair_id = ?
            ORDER BY p.name_last, p.name_first
            """,
            (pair_id,),
        )
