"""Simple database connection wrapper for Brazilian funds database.

For full schema documentation, see README.md in this directory.
"""

from pathlib import Path

import duckdb


class BRFundsDBAdapter:
    """Simple wrapper for connecting to the Brazilian funds database."""

    def __init__(self, db_path: str = "src/infrastructure/database/br_funds.db"):
        """Initialize the database adapter.

        Args:
            db_path: Path to the DuckDB database file
        """
        self.db_path = db_path
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found at {db_path}")

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Create a read-only connection to the database.

        Returns:
            DuckDB connection object
        """
        return duckdb.connect(self.db_path, read_only=True)

    def execute_query(self, query: str, params: dict | None = None) -> list[tuple]:
        """Execute a SQL query and return results.

        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized queries

        Returns:
            List of result tuples
        """
        conn = self.connect()
        if params:
            results = conn.execute(query, params).fetchall()
        else:
            results = conn.execute(query).fetchall()
        conn.close()
        return results
