# Project Implementation Plan: Zetaris Risk Detector

**Total Budgeted Time:** 120 Minutes (2 Hours)  
**Deliverable:** Live federated semantic risk view joining PostgreSQL and CSV/S3, queried via JDBC and visualized in Python.

---

## Phase Breakdown

### Phase 1: Environment & Source Data Provisioning (0:00 – 0:25)
* [ ] **Local Stack Deployment:** Launch `docker-compose.yml` containing PostgreSQL 16 and pgAdmin.
* [ ] **Schema & Seeding:** Verify automated execution of `01-init.sql` (schema creation and insertion of 10 test records).
* [ ] **External Source Setup:** Create `data/risk_entities.csv` containing country code mappings, FATF statuses, and risk coefficients ($0.10$ to $0.95$).
* [ ] **Verification:** Query local Postgres directly via `psql` to verify row counts.

### Phase 2: Zetaris Virtualization & Semantic Layer (0:25 – 1:00)
* [ ] **Connector Setup (Silo A):** Configure PostgreSQL JDBC data source (`db_ops`) inside Zetaris Query Director.
* [ ] **Connector Setup (Silo B):** Mount the static CSV / S3 object store (`file_compliance`) in Zetaris.
* [ ] **Cross-Silo Query Creation:** Author the federated SQL view `virtual_fraud_alerts` joining `transactions` and `risk_entities` on `country_code`.
* [ ] **Calculated Metrics:** Add calculated field `exposure_index = amount * risk_score`.
* [ ] **Data Governance & Masking:** Apply account number masking (`****-****-XXXX`) directly within the view.
* [ ] **Predicate Pushdown Check:** Verify via `EXPLAIN` that filtering criteria (`risk_score >= 0.70`, `amount >= 1000.00`) are pushed down to the underlying sources.

### Phase 3: Access Control & Governance Validation (1:00 – 1:25)
* [ ] **Role Testing:** Test policy controls against virtual views (e.g., restricted PII visibility for compliance analysts vs. full visibility for admins).
* [ ] **Performance & Caching Check:** Evaluate query execution latency and test Zetaris result set caching.

### Phase 4: Downstream Integration & Analytics (1:25 – 2:00)
* [ ] **JDBC Client Configuration:** Set up Python virtual environment with `jaydebeapi`, `pandas`, `matplotlib`, and `seaborn`.
* [ ] **Driver Integration:** Link the Zetaris Lightning JDBC driver JAR.
* [ ] **Query Execution:** Run `scripts/query_and_visualize.py` against the `virtual_fraud_alerts` view.
* [ ] **Visual Output:** Generate dual-panel chart (`zetaris_fraud_risk_exposure.png`):
  * Amount vs. Country Risk Score bubble plot.
  * Aggregate exposure volume by high-risk jurisdiction.
* [ ] **Final Review:** Wrap up project documentation and commit artifacts.