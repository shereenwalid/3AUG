import os
from pathlib import Path

## Load .env from the project root (the folder above Agent/).
## Uses python-dotenv if installed; otherwise falls back to a tiny parser
## so the agent still works without the extra dependency.
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_ENV_FILE)
except ImportError:
    if _ENV_FILE.is_file():
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "vf-ie-aib-prd-iei-cfa-lab")
REGION = os.getenv("GCP_REGION", "europe-west1")
LLM_PROXY_ENDPOINT = os.getenv(
    "LLM_PROXY_ENDPOINT",
    "https://proxy-service-1034231601515.europe-west1.run.app",
)

## Full GCS path to the folder containing one subfolder per opportunity id.
## Examples:
##   gs://vfie-dh-customer-fixed
##   gs://vfie-dh-customer-fixed/parsed/opportunities
GCS_BASE_PATH = os.getenv("GCS_BASE_PATH", "gs://vfie-dh-customer-fixed")


def _parse_gcs_path(path: str) -> tuple[str, str]:
    """Split 'gs://bucket/optional/prefix' into (bucket, prefix)."""
    path = path.strip().removeprefix("gs://").strip("/")
    bucket, _, prefix = path.partition("/")
    return bucket, prefix


GCS_BUCKET_NAME, GCS_BASE_PREFIX = _parse_gcs_path(GCS_BASE_PATH)

# BigQuery (BSP internal validation) - direct access via google-cloud-bigquery
BQ_PROJECT = os.getenv("BQ_PROJECT", "vf-ie-aib-prd-iei-cfa-lab")
BQ_DATASET = os.getenv(
    "BQ_DATASET",
    "vf-ie-datahub.vfie_dh_lake_customer_complex_fixed_s",
)

# ── Input size control (keeps every model request under the proxy cap) ──
# The proxy rejects oversized requests ("Constraint is too tall: N vs max").
# These budgets bound, in characters, how much document content is passed to
# the agents. Tune down if you still hit the cap, up if you have headroom.
# Per-document budget: any single cleaned document is shrunk below this.
MAX_DOC_CHARS = int(os.getenv("MAX_DOC_CHARS", "40000"))
# Total budget across ALL documents handed to an agent in one request.
MAX_TOTAL_DOC_CHARS = int(os.getenv("MAX_TOTAL_DOC_CHARS", "120000"))
# The tech spec is the source of truth - give it a larger share.
MAX_TECHSPEC_CHARS = int(os.getenv("MAX_TECHSPEC_CHARS", "60000"))


# ─────────────────────────────────────────────────────────────────────
# Predefined part codes per order type (CIRCUIT orders).
# When a circuit order's type matches one of these, ALL of its part codes
# must appear as line items on the order - IN ADDITION to the products
# extracted from the tech spec. Source: Fulfilment rows reference table.
# Edit here to correct any code; this is the single source of truth.
# ─────────────────────────────────────────────────────────────────────
PART_CODES_BY_ORDER_TYPE = {
    "DIA": [
        "EMD-DIA-100MB-VF", "EMD-MSAB-FIBRE-100MB-SIRO",
        "R30:F240:S24X7:U60_DIA_C1-1", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "IPVPN": [
        "EMD-IPVPN-1GB-VF", "EMD-MSAB-FIBRE-1GB-SIRO",
        "R30:F240:S24X7:U60_IPVPN_C1-1", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "NGA FTTH Standlone 150": [
        "EMD-NGA-FTTH-IPVPN-UP500MB-EIR", "R30:F240:S24X7:U60_IPVPN_C1-1",
        "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "NGA FTTH Standlone Siro": [
        "EMD-FTTH-IPVPN-SIROLIGHTSTREAM",
    ],
    "NGA FTTC": [
        "EMD-NGA-FTTC-IPVPN-EIR", "R30:F240:S24X7:U60_IPVPN_C1-2",
        "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "NGA FTTH/NBI": [
        "NBI-FTTH-IPVPN-UP500M",
    ],
    "Switch Eth": [
        "EMD-SWETH-500MB-VF", "R30:F240:S24X7:U60_SW-ETH_C1-1",
        "EMD-MSAB-FIBRE-500MB-VF", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "Dedicated Ethernet": [
        "EMD-DEDETH-10GB-VF", "R30:F240:S24X7:U60_DEDETH_C1-1",
        "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "Microwave": [
        "EMD-DIA-100MB-VF", "R30:F240:S24X7:U60_DIA_C1-1",
        "EMD-MSAB-P2PMW-100MB-VF", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "GCN-Tel-1GB": [
        "GCN-Tel-1GB", "R30:F240:S24X7:U60_GCN_1",
        "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "Host Ireland Wireless Uncontended/Contended MW": [
        # NOTE: first code is an either/or in the source: IPVPN 50MB *or* DIA 100MB
        "EMD-IPVPN-50MB-VF / EMD-DIA-100MB-VF", "EMD-MSAB-MW-50MB-HOST",
        "R30:F240:S24X7:U60_IPVPN_C1-2", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "NBI IPVPN": [
        "EMD-IPSEC-IPVPN-SBB(204070325)", "R30:F240:S24X7:U60_IPVPN_C1-2",
        "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "Dedicated Microwave/Uncontended Recurring": [
        "EMD-DIA-100MB-VF", "EMD-MSAB-MW-100MB-HOST",
        "R30:F240:S24X7:U60_DIA_C1-1", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "DSL Standalone": [
        "EMD-ADSL-IPVPN-UP24MB-EIR",
    ],
    "DIA wire only": [
        "DIA W/O 200MB VF", "R30:F240:S24X7:U60_DIA_C1-1",
        "EMD-MSAB-FIBRE-200MB-SIRO", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
    "Backup 4G": [
        "EMD-IPVPN-4G-BACKUP", "R30:F480:S24X7:U120_IPVPN_C1",
    ],
    "Global IPVPN QoS": [
        "R30:F240:S24X7:U60_DIA_C1-1", "ECS-INSTALL", "ECS-InstAndConfigIRL",
    ],
}
