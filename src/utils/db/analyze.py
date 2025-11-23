"""Generate comprehensive database analysis report."""

import duckdb
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree


console = Console()


def analyze_database(db_path: str = "docs/br_funds.db"):
    """Generate comprehensive database analysis."""
    conn = duckdb.connect(db_path, read_only=True)

    console.print(Panel.fit("[bold cyan]🔍 DuckDB Database Analysis Report[/bold cyan]"))

    # 1. Database Overview
    console.print("\n[bold cyan]═══ DATABASE OVERVIEW ═══[/bold cyan]\n")
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]

    overview_table = Table(title="Tables Summary", show_lines=True)
    overview_table.add_column("Table", style="cyan", no_wrap=True)
    overview_table.add_column("Rows", justify="right", style="green")
    overview_table.add_column("Columns", justify="right", style="yellow")

    total_rows = 0
    for table_name in table_names:
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
        total_rows += count
        overview_table.add_row(table_name, f"{count:,}", str(len(cols)))

    console.print(overview_table)
    console.print(f"\n[yellow]Total Rows Across All Tables:[/yellow] {total_rows:,}\n")

    # 2. Table Relationships
    console.print("\n[bold cyan]═══ SCHEMA RELATIONSHIPS ═══[/bold cyan]\n")

    tree = Tree("📊 [bold]Database Schema[/bold]")

    for table_name in table_names:
        schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        table_node = tree.add(f"[green]{table_name}[/green] ({count:,} rows)")

        # Categorize columns
        id_cols = []
        fk_cols = []
        regular_cols = []

        for col in schema:
            col_name = col[0]
            col_type = col[1]

            if col_name.endswith("_id"):
                if "fund_id" in col_name and table_name != "funds":
                    fk_cols.append((col_name, "funds", col_type))
                elif "asset_id" in col_name and table_name != "assets":
                    fk_cols.append((col_name, "assets", col_type))
                elif "position_id" in col_name:
                    id_cols.append((col_name, col_type))
                elif "snapshot_id" in col_name:
                    id_cols.append((col_name, col_type))
                else:
                    id_cols.append((col_name, col_type))
            else:
                regular_cols.append((col_name, col_type))

        # Add categorized columns
        if id_cols:
            id_node = table_node.add("[cyan]🔑 Primary Keys[/cyan]")
            for col_name, col_type in id_cols[:3]:  # Show first 3
                id_node.add(f"{col_name}: {col_type}")

        if fk_cols:
            fk_node = table_node.add("[yellow]🔗 Foreign Keys[/yellow]")
            for col_name, ref_table, col_type in fk_cols:
                fk_node.add(f"{col_name} → {ref_table}")

        if regular_cols:
            cols_node = table_node.add(f"[magenta]📝 Columns ({len(regular_cols)})[/magenta]")
            for col_name, col_type in regular_cols[:5]:  # Show first 5
                cols_node.add(f"{col_name}: {col_type}")
            if len(regular_cols) > 5:
                cols_node.add(f"... and {len(regular_cols) - 5} more")

    console.print(tree)

    # 3. Data Quality Insights
    console.print("\n[bold cyan]═══ DATA QUALITY INSIGHTS ═══[/bold cyan]\n")

    # Analyze funds table
    console.print("[bold]Funds Table Analysis:[/bold]")
    funds_status = conn.execute(
        "SELECT status, COUNT(*) as count FROM funds GROUP BY status ORDER BY count DESC"
    ).fetchall()

    status_table = Table(title="Fund Status Distribution")
    status_table.add_column("Status", style="cyan")
    status_table.add_column("Count", justify="right", style="green")
    status_table.add_column("Percentage", justify="right", style="yellow")

    total_funds = sum(row[1] for row in funds_status)
    for status, count in funds_status[:5]:
        pct = (count / total_funds) * 100
        status_table.add_row(status or "NULL", f"{count:,}", f"{pct:.1f}%")

    console.print(status_table)

    # Analyze time range
    console.print("\n[bold]Data Time Range:[/bold]")
    time_table = Table()
    time_table.add_column("Table", style="cyan")
    time_table.add_column("Earliest Date", style="green")
    time_table.add_column("Latest Date", style="yellow")

    for table_name in ["fund_snapshots", "fund_performance_indicators", "positions"]:
        try:
            min_date = conn.execute(
                f"SELECT MIN(timestamp) FROM {table_name}"
            ).fetchone()[0]
            max_date = conn.execute(
                f"SELECT MAX(timestamp) FROM {table_name}"
            ).fetchone()[0]
            time_table.add_row(table_name, min_date or "N/A", max_date or "N/A")
        except Exception:
            pass

    console.print(time_table)

    # 4. Sample Queries
    console.print("\n[bold cyan]═══ USEFUL SAMPLE QUERIES ═══[/bold cyan]\n")

    queries = [
        (
            "Count funds by type",
            "SELECT fund_type, COUNT(*) as count FROM funds GROUP BY fund_type ORDER BY count DESC LIMIT 5",
        ),
        (
            "Top 10 funds by NAV",
            "SELECT legal_name, net_asset_value FROM funds WHERE net_asset_value IS NOT NULL ORDER BY net_asset_value.value DESC LIMIT 10",
        ),
        (
            "Recent fund snapshots",
            "SELECT fund_id, timestamp, share_price FROM fund_snapshots ORDER BY timestamp DESC LIMIT 5",
        ),
        (
            "Asset class distribution",
            "SELECT asset_class, COUNT(*) as count FROM assets GROUP BY asset_class ORDER BY count DESC LIMIT 5",
        ),
    ]

    for title, query in queries:
        console.print(f"\n[bold yellow]📊 {title}:[/bold yellow]")
        console.print(f"[dim]{query}[/dim]\n")
        try:
            result = conn.execute(query).fetchdf()
            console.print(result.to_string(index=False))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    conn.close()


if __name__ == "__main__":
    analyze_database()
