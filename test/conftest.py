import os
import pytest
import jaydebeapi
import pandas as pd

ZETARIS_HOST = os.getenv("ZETARIS_HOST", "localhost")
ZETARIS_PORT = os.getenv("ZETARIS_PORT", "10000")
ZETARIS_USER = os.getenv("ZETARIS_USER", "admin")
ZETARIS_PASS = os.getenv("ZETARIS_PASS", "adminpassword")
JAR_FILE_PATH = os.getenv("ZETARIS_JAR_PATH", "./zetaris-lightning-jdbc.jar")
DRIVER_CLASS = "com.zetaris.jdbc.LightningDriver"
JDBC_URL = f"jdbc:zetaris:lightning@{ZETARIS_HOST}:{ZETARIS_PORT}"


@pytest.fixture(scope="session")
def db_connection():
    """Initializes and tears down the session-level JDBC connection."""
    conn = jaydebeapi.connect(
        DRIVER_CLASS,
        JDBC_URL,
        [ZETARIS_USER, ZETARIS_PASS],
        JAR_FILE_PATH
    )
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def virtual_view_df(db_connection) -> pd.DataFrame:
    """Executes the query once and returns a pandas DataFrame for assertions."""
    query = """
    SELECT 
        transaction_id,
        masked_account,
        customer_id,
        amount,
        currency,
        merchant_name,
        country_code,
        jurisdiction_name,
        risk_tier,
        risk_score,
        flag_reason,
        exposure_index,
        timestamp
    FROM virtual_fraud_alerts
    """
    cursor = db_connection.cursor()
    try:
        cursor.execute(query)
        columns = [col[0].lower() for col in cursor.description]
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=columns)
        
        # Ensure target numeric columns are cast
        df["amount"] = pd.to_numeric(df["amount"])
        df["risk_score"] = pd.to_numeric(df["risk_score"])
        df["exposure_index"] = pd.to_numeric(df["exposure_index"])
        return df
    finally:
        cursor.close()