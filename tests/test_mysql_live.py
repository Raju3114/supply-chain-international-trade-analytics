"""
test_mysql_live.py
------------------
Automated test suite verifying the live MySQL server database connection,
table schemas, row counts, and analytical query execution.

Author: Antigravity & Senior Data Analyst Mentor
"""

import pymysql
import pytest

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_DB = "supply_chain_dw"
EXPECTED_FACT_ROWS = 180519

@pytest.fixture(scope="module")
def mysql_connection():
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        yield conn
        conn.close()
    except Exception as e:
        pytest.skip(f"Live MySQL server not reachable: {e}")

def test_mysql_server_connection(mysql_connection):
    """Verify live connection to MySQL server."""
    with mysql_connection.cursor() as cur:
        cur.execute("SELECT VERSION() AS ver;")
        res = cur.fetchone()
        assert res is not None, "Failed to query MySQL version!"
        print(f"\nConnected to live MySQL engine version: {res['ver']}")

def test_mysql_tables_exist(mysql_connection):
    """Verify all 6 Star Schema tables exist in MySQL database."""
    with mysql_connection.cursor() as cur:
        cur.execute("SHOW TABLES;")
        tables = [list(r.values())[0] for r in cur.fetchall()]
        expected_tables = [
            "dim_customer_geo", "dim_date", "dim_order_destination",
            "dim_product", "dim_shipping_mode", "fact_shipments"
        ]
        for tbl in expected_tables:
            assert tbl in tables, f"Missing table in MySQL: {tbl}"

def test_mysql_fact_row_count(mysql_connection):
    """Verify fact_shipments in MySQL matches 180,519 rows exactly."""
    with mysql_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM fact_shipments;")
        res = cur.fetchone()
        assert res['total'] == EXPECTED_FACT_ROWS, f"Row count mismatch in MySQL: {res['total']} vs {EXPECTED_FACT_ROWS}"

def test_mysql_analytical_query(mysql_connection):
    """Verify analytical aggregation query on live MySQL server."""
    with mysql_connection.cursor() as cur:
        cur.execute("""
            SELECT 
                COUNT(*) AS total_items,
                SUM(is_late) AS late_items,
                ROUND(SUM(is_late) * 100.0 / COUNT(*), 2) AS late_pct
            FROM fact_shipments;
        """)
        res = cur.fetchone()
        assert res['total_items'] == EXPECTED_FACT_ROWS
        assert res['late_items'] == 98977
        assert float(res['late_pct']) == 54.83
