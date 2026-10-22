"""
run_sql_analytics.py
--------------------
Executes all SQL queries from sql/02_analytical_queries.sql against the local
relational database, logs formatted outputs, and validates cross-system consistency.

Author: Antigravity & Senior Data Analyst Mentor
"""

import os
import sqlite3
import pandas as pd
from tabulate import tabulate

DB_PATH = os.path.join("data", "supply_chain_analytics.db")
SQL_FILE = os.path.join("sql", "02_analytical_queries.sql")
OUTPUT_MD = os.path.join("docs", "sql_analytical_results.md")

def execute_queries():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        full_sql = f.read()

    # Split queries by semicolon separator, ignoring comments
    statements = [stmt.strip() for stmt in full_sql.split(";") if stmt.strip()]
    
    query_titles = [
        "Query 1: Shipping Mode SLA Adherence & Average Delay Variance",
        "Query 2: Global Market Delivery Performance & Profitability",
        "Query 3: Top Product Categories by Revenue and Delay Ranking (Window Functions)",
        "Query 4: Monthly Trajectory & 3-Month Moving Average (Window Functions)",
        "Query 5: Order-Level Fulfillment Status Funnel",
        "Query 6: Relational Data Quality Exception Audit",
        "Query 7: Cross-Border Trade Lane Demurrage & Modeled Freight Costs [SIMULATION]"
    ]

    results_md = ["# SQL Analytics: Query Execution & Results\n\n"]
    results_md.append("Database: `data/supply_chain_analytics.db` (Star Schema)\n\n")

    for idx, (title, stmt) in enumerate(zip(query_titles, statements), 1):
        print(f"\n[{idx}/{len(query_titles)}] Executing {title}...")
        try:
            df = pd.read_sql_query(stmt, conn)
            print(tabulate(df.head(10), headers="keys", tablefmt="psql", showindex=False))
            
            results_md.append(f"## {title}\n\n")
            results_md.append("```sql\n" + stmt + "\n```\n\n")
            results_md.append("### Result (First 15 rows):\n\n")
            results_md.append(df.head(15).to_markdown(index=False))
            results_md.append("\n\n")
            
            # Special check for Query 6: Exception count must be 0 for all checks!
            if idx == 6:
                total_exceptions = df["exception_count"].sum()
                assert total_exceptions == 0, f"Integrity violations found in Query 6: {df}"
                print("  -> [PASS] Data Quality Exception Audit: exactly 0 exceptions detected across all checks.")
        except Exception as e:
            print(f"Error executing Query {idx}: {e}")
            raise e

    conn.close()

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.writelines(results_md)
    print(f"\nAll SQL query outputs documented in {OUTPUT_MD}")

if __name__ == "__main__":
    execute_queries()
