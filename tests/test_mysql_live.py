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
    """Verify all 7 tables (Star Schema + Customs extension) exist in MySQL database."""
    with mysql_connection.cursor() as cur:
        cur.execute("SHOW TABLES;")
        tables = [list(r.values())[0] for r in cur.fetchall()]
        expected_tables = [
            "dim_customer_geo", "dim_date", "dim_order_destination",
            "dim_product", "dim_shipping_mode", "fact_shipments",
            "fact_customs_declarations"
        ]
        for tbl in expected_tables:
            assert tbl in tables, f"Missing table in MySQL: {tbl}"

def test_mysql_fact_row_count(mysql_connection):
    """Verify fact_shipments and fact_customs_declarations row counts in MySQL."""
    with mysql_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM fact_shipments;")
        res = cur.fetchone()
        assert res['total'] == EXPECTED_FACT_ROWS, f"Row count mismatch in MySQL: {res['total']} vs {EXPECTED_FACT_ROWS}"
        
        cur.execute("SELECT COUNT(*) AS total_customs FROM fact_customs_declarations;")
        res_c = cur.fetchone()
        assert res_c['total_customs'] == 65752, f"Customs row count mismatch in MySQL: {res_c['total_customs']}"

def test_mysql_analytical_query(mysql_connection):
    """Verify analytical aggregation query on live MySQL server including dual OTD rates."""
    with mysql_connection.cursor() as cur:
        cur.execute("""
            SELECT 
                COUNT(*) AS total_items,
                SUM(is_late) AS late_items,
                ROUND(SUM(is_on_time) * 100.0 / SUM(CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END), 2) AS otd_shipped_pct,
                ROUND(SUM(is_on_time) * 100.0 / COUNT(*), 2) AS otd_total_pct,
                ROUND(SUM(is_late) * 100.0 / COUNT(*), 2) AS late_pct,
                ROUND(AVG(delay_days), 2) AS delay_variance_days
            FROM fact_shipments;
        """)
        res = cur.fetchone()
        assert res['total_items'] == EXPECTED_FACT_ROWS
        assert res['late_items'] == 98977
        assert float(res['otd_shipped_pct']) == 42.71
        assert float(res['otd_total_pct']) == 40.88
        assert float(res['late_pct']) == 54.83
        assert float(res['delay_variance_days']) == 0.57
