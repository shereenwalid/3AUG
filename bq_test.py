"""
Standalone BigQuery diagnostic - run this to see the EXACT BigQuery error,
without the agent / UI / model in the way.

    cd q2o_integrated
    python bq_test.py

It prints: which project/dataset it's using, whether auth works, whether the
tables are reachable, and the full error if not.
"""
import os
import sys

BQ_PROJECT = os.getenv("BQ_PROJECT", "vf-ie-aib-prd-iei-cfa-lab")
BQ_DATASET = os.getenv("BQ_DATASET", "vf-ie-datahub.vfie_dh_lake_customer_complex_fixed_s")


def _table(name):
    ds = BQ_DATASET.strip().strip("`")
    return f"`{ds}.{name}`" if "." in ds else f"`{BQ_PROJECT}.{ds}.{name}`"


print("=" * 70)
print(f"BQ_PROJECT = {BQ_PROJECT}")
print(f"BQ_DATASET = {BQ_DATASET}")
print(f"company table -> {_table('TEMP_company')}")
print(f"location table -> {_table('TEMP_location')}")
print("=" * 70)

# 1) library present?
try:
    from google.cloud import bigquery
    print("[1/4] google-cloud-bigquery import: OK")
except Exception as e:
    print(f"[1/4] FAILED to import google-cloud-bigquery: {e}")
    print("      -> pip install google-cloud-bigquery")
    sys.exit(1)

# 2) credentials / client?
try:
    client = bigquery.Client(project=BQ_PROJECT)
    print(f"[2/4] BigQuery client created for project '{client.project}': OK")
except Exception as e:
    print(f"[2/4] FAILED to create client (auth/credentials): {type(e).__name__}: {e}")
    print("      -> check GOOGLE_APPLICATION_CREDENTIALS / workload identity / gcloud auth")
    sys.exit(1)

# 3) can we reach each table? (metadata only, no data scan)
for t in ("TEMP_company", "TEMP_location"):
    fqn = _table(t).strip("`")
    try:
        tbl = client.get_table(fqn)
        print(f"[3/4] get_table {fqn}: OK ({tbl.num_rows} rows, {len(tbl.schema)} cols)")
        print(f"        columns: {[f.name for f in tbl.schema][:12]}")
    except Exception as e:
        print(f"[3/4] FAILED get_table {fqn}: {type(e).__name__}: {e}")

# 4) run a tiny query
try:
    sql = f"SELECT COUNT(*) AS n FROM {_table('TEMP_company')}"
    rows = list(client.query(sql))
    print(f"[4/4] test query on TEMP_company: OK (count={rows[0]['n']})")
except Exception as e:
    print(f"[4/4] FAILED test query: {type(e).__name__}: {e}")

print("=" * 70)
print("Done. Read the first FAILED line above - that's the root cause.")
