# Zero-ETL Cross-Silo Fraud & Risk Detector (Zetaris)

A rapid 2-hour prototype demonstrating zero-ETL data virtualization using **Zetaris Query Director**. This project joins high-frequency relational transaction records in an operational SQL database with reference sanctions and risk scores in an external object store/CSV in real-time—without data movement, copying, or traditional pipeline orchestration.

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────┐      ┌──────────────────────────────────┐
│   Operational DB (PostgreSQL)   │      │    Compliance Store (CSV / S3)   │
│  - transactions (OLTP records)  │      │    - risk_entities (FATF / tiers)│
└────────────────┬────────────────┘      └────────────────┬─────────────────┘
                 │                                        │
                 │          [ Zero Data Movement ]        │
                 └───────────────────┬────────────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │    Zetaris Virtual Layer    │
                      │  - Federated ANSI SQL Join  │
                      │  - Predicate Pushdown       │
                      │  - Dynamic PII Masking      │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │   Downstream Consumers      │
                      │  - JDBC / Python (Analytics)│
                      │  - BI Dashboards            │
                      └─────────────────────────────┘
```

---

## 📦 Project Structure

```text
.
├── README.md                  # Project overview, schemas, and execution guide
├── plan.md                    # 2-hour phased execution plan & checklist
├── docker-compose.yml         # Local PostgreSQL and pgAdmin stack
├── init-scripts/
│   └── 01-init.sql            # PostgreSQL DDL and transaction seed data
├── pgadmin-servers.json       # pgAdmin auto-import server connection config
├── data/
│   └── risk_entities.csv      # External sanctions and FATF risk reference file
└── scripts/
    └── query_and_visualize.py # JayDeBeApi client and dual-panel risk chart
```

---

## 🚀 Quick Start

### 1. Launch the Database Stack

Start PostgreSQL and pgAdmin:

```bash
docker compose up -d
```

* **PostgreSQL:** `localhost:5432` (`devdb` / `devuser` / `devpassword`)
* **pgAdmin 4:** `http://localhost:8080` (Login: `admin@example.com` / `adminpassword`)

The transactions table is automatically created and seeded on initial boot via `init-scripts/01-init.sql`.

---

### 2. Prepare Reference Data (`data/risk_entities.csv`)

Ensure `data/risk_entities.csv` contains the sanctions/risk tiers:

```csv
entity_id,country_code,jurisdiction_name,risk_tier,risk_score,fatf_status,flag_reason
RSK-01,CY,Cyprus,High,0.78,Monitored,Offshore shell banking exposure
RSK-02,PA,Panama,Critical,0.92,Increased Monitoring,High corporate opacity index
RSK-03,VG,British Virgin Islands,Critical,0.95,High Risk,Jurisdiction tax haven / trust sanctuary
RSK-04,MT,Malta,Medium,0.65,Standard,Unregulated VASP corridor scrutiny
RSK-05,SG,Singapore,Low,0.20,Compliant,Standard commercial trade hub
RSK-06,US,United States,Low,0.10,Compliant,Standard low-risk corridor
RSK-07,GB,United Kingdom,Low,0.15,Compliant,Standard low-risk corridor
RSK-08,DE,Germany,Low,0.12,Compliant,Standard low-risk corridor
```

---

### 3. Register Sources & Deploy Semantic View in Zetaris

Mount `local_postgres` as `db_ops` and `risk_entities.csv` (or S3 bucket) as `file_compliance`. Then execute the federated view:

```sql
CREATE OR REPLACE VIEW virtual_fraud_alerts AS
SELECT 
    t.transaction_id,
    CONCAT('****-****-', RIGHT(t.account_number, 4)) AS masked_account,
    t.customer_id,
    t.amount,
    t.currency,
    t.merchant_name,
    t.country_code,
    r.jurisdiction_name,
    r.risk_tier,
    r.risk_score,
    r.flag_reason,
    ROUND(t.amount * r.risk_score, 2) AS exposure_index,
    t.timestamp
FROM db_ops.transactions t
INNER JOIN file_compliance.risk_entities r
    ON t.country_code = r.country_code
WHERE r.risk_score >= 0.70
  AND t.amount >= 1000.00;
```

---

### 4. Run Analysis & Visualization

Install Python dependencies:

```bash
pip install jaydebeapi pandas matplotlib seaborn
```

Run the query and visualization script:

```bash
export ZETARIS_HOST="localhost"
export ZETARIS_JAR_PATH="./zetaris-lightning-jdbc.jar"

python scripts/query_and_visualize.py
```

This exports `zetaris_fraud_risk_exposure.png` containing a scatter plot of amount vs. risk score and a total risk exposure bar chart by jurisdiction.