"""
Quote-to-order pipeline - ADK 2.0 graph-based Workflow.

Graph topology (sequential chain):

    START --> qto_validation_agent --> bsp_extraction_agent

Migration notes (ADK 1.x SequentialAgent -> ADK 2.0 Workflow):
- root agent is now a `Workflow` with an `edges` graph instead of a
  SequentialAgent with sub_agents.
- LLM agents used as graph nodes MUST run in "single_turn" mode
  ("task" mode is disabled inside graph workflows in ADK Python 2.0).
- Data still flows through session state: the GCS tool writes
  opportunity_data / tech_spec_files / template_date, the validator
  writes validation_report, and the extractor reads them via
  {state_key?} instruction templating.
- Requires: pip install -U "google-adk>=2.0.0"
  (ADK 2.0 sessions are NOT readable by ADK 1.x < 1.28)
"""

from google.adk import Agent, Workflow
from google import genai
import google.oauth2.id_token
from google.cloud import aiplatform
from google.genai.types import HttpOptions
from google.adk.models import Gemini

from .config import PROJECT_ID, REGION, LLM_PROXY_ENDPOINT
from .prompts import VALIDATION_PROMPT, EXTRACTION_PROMPT
from .models import BSPOrderTemplate
from .tools import (
    get_opportunity_data,
    lookup_bsp_company,
    lookup_bsp_location,
    save_validation_status,
    get_validation_status,
)

# Product Code Navigator lives in the sibling subAgent package:
#   vf_quote_to_order_agent_configured/subAgent/product_code_agent/agent.py
# and exposes a module-level ADK Agent named `product_code_agent`.
# From Agent/agent.py that is the relative import ..subAgent.product_code_agent.agent
from ..subAgent.product_code_agent.agent import product_code_agent

_HAS_PRODUCT_CODE_AGENT = product_code_agent is not None
print(f"[agent] product_code_agent imported: {getattr(product_code_agent, 'name', None)}")

aiplatform.init(project=PROJECT_ID, location=REGION)

api_endpoint = f"{LLM_PROXY_ENDPOINT}/google-llm"
id_creds = google.oauth2.id_token.fetch_id_token_credentials(LLM_PROXY_ENDPOINT)

client = genai.Client(
    vertexai=True,
    location=REGION,
    project=PROJECT_ID,
    credentials=id_creds,
    http_options=HttpOptions(base_url=api_endpoint, api_version="v1beta1"),
)

gemini_model = Gemini(model="gemini-2.5-pro")
gemini_model.api_client = client


## Node 0: retrieve the opportunity documents from GCS FIRST, so both the
##         validation agent and the product code navigator start with the
##         documents (incl. tech spec) already in shared session state. This
##         removes the race where a parallel branch runs before docs exist.
retrieval_agent = Agent(
    model=gemini_model,
    name="qto_retrieval_agent",
    mode="single_turn",
    description="Fetches the opportunity's parsed documents from GCS into state.",
    instruction=(
        "You are given an opportunity id. Call the tool `get_opportunity_data` "
        "with exactly that id to load the opportunity's documents into session "
        "state. Then reply with a one-line confirmation of the matched folder "
        "and the tech spec / VBOP filenames. Do not do any validation or "
        "extraction - only retrieve."
    ),
    tools=[get_opportunity_data],
    output_key="retrieval_summary",
)


## Node 1: retrieve the opportunity folder from GCS and run all
##         quote-to-order validation checks (Y/N JSON report).
validation_agent = Agent(
    model=gemini_model,
    name="qto_validation_agent",
    mode="single_turn",  # required for LLM agents used as graph nodes
    description=(
        "Retrieves parsed documents for an opportunity id from GCS and runs "
        "the Vodafone quote-to-order validation checklist."
    ),
    instruction=VALIDATION_PROMPT,
    tools=[
        get_opportunity_data,
        lookup_bsp_company,
        lookup_bsp_location,
        save_validation_status,
        get_validation_status,
    ],
    output_key="validation_report",
)

## Node 2: fill the BSP order template from the retrieved documents
##         (tech spec first), schema-enforced output.
bsp_extraction_agent = Agent(
    model=gemini_model,
    name="bsp_extraction_agent",
    mode="single_turn",
    description="Fills the BSP order template from the opportunity documents.",
    instruction=EXTRACTION_PROMPT,
    # NOTE: intentionally NO output_schema. A Pydantic output_schema this size
    # (20+ header fields + a line_items array of 8-field objects, all with long
    # descriptions) compiles into a constrained-decoding state machine that the
    # serving layer rejects with "schema produces constraint that has too many
    # states". Instead the prompt specifies the exact JSON, and the API parses
    # and validates it against BSPOrderTemplate after the fact.
    output_key="bsp_order",
)

## ADK 2.0 graph workflow.
## Validation and the Product Code Navigator run IN PARALLEL from START.
## The extraction agent waits for BOTH (a join), so by the time it fills the
## order rows, the validation report AND the resolved product codes are ready.
## Failed validation checks never block extraction - the edges are
## unconditional.
if _HAS_PRODUCT_CODE_AGENT and product_code_agent is not None:
    # Make sure the navigator's result is addressable by the extractor.
    if not getattr(product_code_agent, "output_key", None):
        try:
            product_code_agent.output_key = "resolved_product_codes"
        except Exception:  # noqa: BLE001
            pass

    root_agent = Workflow(
        name="root_agent",
        description=(
            "Quote-to-order pipeline: fetch opportunity documents from GCS, "
            "then run validation checks and resolve product codes in parallel, "
            "then fill the BSP order template using the resolved codes."
        ),
        edges=[
            # retrieve documents FIRST so both parallel branches have the tech spec
            ("START", retrieval_agent, validation_agent),
            ("START", retrieval_agent, product_code_agent),
            # join: extraction runs after BOTH parallel branches complete
            (validation_agent, bsp_extraction_agent),
            (product_code_agent, bsp_extraction_agent),
        ],
    )
else:
    # Fallback: retrieval -> validation -> extraction if navigator isn't present.
    root_agent = Workflow(
        name="root_agent",
        description=(
            "Quote-to-order pipeline: fetch opportunity documents from GCS, "
            "run validation checks, then fill the BSP order template."
        ),
        edges=[
            ("START", retrieval_agent, validation_agent),
            (validation_agent, bsp_extraction_agent),
        ],
    )
