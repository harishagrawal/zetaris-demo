import os
import jaydebeapi
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. Zetaris Connection Configuration
# ==========================================
ZETARIS_HOST = os.getenv("ZETARIS_HOST", "localhost")
ZETARIS_PORT = os.getenv("ZETARIS_PORT", "10000")
ZETARIS_USER = os.getenv("ZETARIS_USER", "admin")
ZETARIS_PASS = os.getenv("ZETARIS_PASS", "adminpassword")

# Update this path to the location of your downloaded Zetaris JDBC JAR
JAR_FILE_PATH = os.getenv("ZETARIS_JAR_PATH", "./zetaris-lightning-jdbc.jar")
DRIVER_CLASS = "com.zetaris.jdbc.LightningDriver"
JDBC_URL = f"jdbc:zetaris:lightning@{ZETARIS_HOST}:{ZETARIS_PORT}"

# ==========================================
# 2. Query the Virtualized Semantic View
# ==========================================
QUERY = """
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
    exposure_index,
    timestamp
FROM virtual_fraud_alerts
ORDER BY exposure_index DESC
"""

print(f"Connecting to Zetaris virtual engine at {JDBC_URL}...")

conn = jaydebeapi.connect(
    DRIVER_CLASS,
    JDBC_URL,
    [ZETARIS_USER, ZETARIS_PASS],
    JAR_FILE_PATH
)

try:
    cursor = conn.cursor()
    cursor.execute(QUERY)
    columns = [col[0].lower() for col in cursor.description]
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=columns)
finally:
    cursor.close()
    conn.close()

# Convert types for charting
df['amount'] = pd.to_numeric(df['amount'])
df['risk_score'] = pd.to_numeric(df['risk_score'])
df['exposure_index'] = pd.to_numeric(df['exposure_index'])

print(f"Retrieved {len(df)} flagged transactions from virtual layer.")
print(df[['transaction_id', 'jurisdiction_name', 'amount', 'risk_score', 'exposure_index']])

# ==========================================
# 3. Dual-Panel Visualization
# ==========================================
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Subplot 1: Bubble Plot (Amount vs. Risk Score, size scaled to Exposure Index)
scatter = sns.scatterplot(
    data=df,
    x="risk_score",
    y="amount",
    size="exposure_index",
    hue="jurisdiction_name",
    palette="Set2",
    sizes=(100, 1000),
    alpha=0.8,
    legend="brief",
    ax=axes[0]
)

# Label top risk outliers
for _, row in df.iterrows():
    if row['exposure_index'] > 5000:
        axes[0].annotate(
            f"{row['transaction_id']}\n({row['jurisdiction_name']})",
            xy=(row['risk_score'], row['amount']),
            xytext=(row['risk_score'] + 0.015, row['amount'] + 400),
            fontsize=8,
            weight='semibold'
        )

axes[0].set_title("Transaction Amount vs. Country Risk Score", fontsize=12, pad=10)
axes[0].set_xlabel("FATF / Regulatory Risk Score (0 - 1.0)")
axes[0].set_ylabel("Transaction Amount (USD)")

# Subplot 2: Total Exposure Volume aggregated by Jurisdiction
jurisdiction_summary = (
    df.groupby('jurisdiction_name')['exposure_index']
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

sns.barplot(
    data=jurisdiction_summary,
    x="exposure_index",
    y="jurisdiction_name",
    palette="Reds_r",
    ax=axes[1]
)
axes[1].set_title("Total Risk Exposure Index by Jurisdiction", fontsize=12, pad=10)
axes[1].set_xlabel("Aggregated Exposure Index")
axes[1].set_ylabel("Jurisdiction")

plt.tight_layout()
plt.savefig("zetaris_fraud_risk_exposure.png", dpi=300)
print("Saved visualization as 'zetaris_fraud_risk_exposure.png'")
plt.show()