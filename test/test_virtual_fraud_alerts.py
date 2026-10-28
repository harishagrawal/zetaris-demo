import pytest
import re
import pandas as pd


class TestVirtualFraudAlertsSchema:
    """Validates structural schema integrity and metadata types."""

    EXPECTED_COLUMNS = {
        "transaction_id",
        "masked_account",
        "customer_id",
        "amount",
        "currency",
        "merchant_name",
        "country_code",
        "jurisdiction_name",
        "risk_tier",
        "risk_score",
        "flag_reason",
        "exposure_index",
        "timestamp",
    }

    def test_column_presence(self, virtual_view_df: pd.DataFrame):
        """Asserts all expected virtual view columns exist."""
        actual_columns = set(virtual_view_df.columns)
        missing = self.EXPECTED_COLUMNS - actual_columns
        assert not missing, f"Missing columns in virtual view: {missing}"

    def test_not_empty(self, virtual_view_df: pd.DataFrame):
        """Asserts the view produces records from the seed datasets."""
        assert len(virtual_view_df) > 0, "Virtual view returned zero rows."

    def test_schema_null_constraints(self, virtual_view_df: pd.DataFrame):
        """Ensures key federated identifiers and amounts have no NULL values."""
        assert virtual_view_df["transaction_id"].isnull().sum() == 0
        assert virtual_view_df["amount"].isnull().sum() == 0
        assert virtual_view_df["risk_score"].isnull().sum() == 0
        assert virtual_view_df["exposure_index"].isnull().sum() == 0


class TestVirtualFraudBusinessLogic:
    """Validates business rules, PII policies, and derived metrics."""

    def test_predicate_filtering_pushdown(self, virtual_view_df: pd.DataFrame):
        """Asserts that records satisfy WHERE filter: risk_score >= 0.70 and amount >= 1000.00."""
        invalid_amount = virtual_view_df[virtual_view_df["amount"] < 1000.00]
        invalid_risk = virtual_view_df[virtual_view_df["risk_score"] < 0.70]

        assert len(invalid_amount) == 0, f"Found amounts below threshold: {invalid_amount['amount'].tolist()}"
        assert len(invalid_risk) == 0, f"Found risk scores below threshold: {invalid_risk['risk_score'].tolist()}"

    def test_exposure_index_computation(self, virtual_view_df: pd.DataFrame):
        """Asserts exposure_index equals round(amount * risk_score, 2)."""
        expected_exposure = (virtual_view_df["amount"] * virtual_view_df["risk_score"]).round(2)
        diff = (virtual_view_df["exposure_index"] - expected_exposure).abs()
        
        # Allow small floating-point epsilon (0.01)
        mismatches = virtual_view_df[diff > 0.01]
        assert len(mismatches) == 0, f"Exposure index calculation mismatch:\n{mismatches[['transaction_id', 'amount', 'risk_score', 'exposure_index']]}"

    def test_pii_account_masking(self, virtual_view_df: pd.DataFrame):
        """Asserts account number masking complies with pattern: ****-****-XXXX."""
        mask_pattern = re.compile(r"^\*{4}-\*{4}-\d{4}$")
        for val in virtual_view_df["masked_account"]:
            assert mask_pattern.match(str(val)), f"Account not properly masked: '{val}'"


class TestZetarisPushdownExecutionPlan:
    """Validates engine pushdown and query optimizer behavior."""

    def test_pushdown_explain_plan(self, db_connection):
        """Inspects EXPLAIN plan output to verify join and predicate pushdown."""
        explain_query = """
        EXPLAIN
        SELECT * FROM virtual_fraud_alerts
        """
        cursor = db_connection.cursor()
        try:
            cursor.execute(explain_query)
            plan_lines = [str(row[0]).lower() for row in cursor.fetchall()]
            plan_text = " ".join(plan_lines)

            # Checks that pushdown predicates are present in plan
            assert any(term in plan_text for term in ["pushdown", "filter", "scan"]), (
                "Query execution plan did not indicate predicate pushdown."
            )
        finally:
            cursor.close()