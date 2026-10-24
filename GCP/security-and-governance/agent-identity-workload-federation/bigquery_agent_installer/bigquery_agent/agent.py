import os
import logging
from dotenv import load_dotenv

from google.adk.agents.llm_agent import LlmAgent
from google.adk.models import Gemini
from google.cloud import bigquery

# Load environment configuration
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bigquery_invoice_agent")

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
model_name = os.environ.get("MODEL", "gemini-2.5-flash")

# Initialize BigQuery Client
bq_client = bigquery.Client(project=project_id)

def list_tables(dataset_id: str) -> list:
    """Lists all tables present in the specified BigQuery dataset."""
    dataset_ref = bq_client.dataset(dataset_id)
    tables = list(bq_client.list_tables(dataset_ref))
    return [table.table_id for table in tables]

def get_table_schema(dataset_id: str, table_id: str) -> list:
    """Retrieves field names, types, and modes for a specific BigQuery table."""
    table_ref = bq_client.dataset(dataset_id).table(table_id)
    table = bq_client.get_table(table_ref)
    return [{"name": f.name, "type": f.field_type, "mode": f.mode} for f in table.schema]

def execute_sql_query(query: str) -> list:
    """Executes a SQL query against BigQuery and returns rows as dictionaries."""
    logger.info(f"Executing query: {query}")
    query_job = bq_client.query(query)
    results = query_job.result()
    rows = [dict(row) for row in results]
    return rows

client_kwargs = {
    "vertexai": True,
    "project": project_id,
    "location": location,
}

root_agent = LlmAgent(
    name="BigQueryInvoiceAgent",
    model=Gemini(
        model=model_name,
        client_kwargs=client_kwargs
    ),
    description=(
        "An enterprise financial intelligence agent for Cymbal Pools that inspects invoice "
        "schemas, calculates balances, tracks unpaid supplier invoices, and executes analytical SQL."
    ),
    instruction=(
        "You are an enterprise AI data assistant for Cymbal Pools finance team.\n"
        "Your role is to answer questions about supplier invoices stored in BigQuery.\n\n"
        "Guidelines:\n"
        "1. Always inspect the table schema first if the structure is unknown.\n"
        "2. Formulate precise BigQuery SQL queries using standard SQL dialect.\n"
        "3. Accurately filter for unpaid invoices (`payment_status != 'PAID'` or `payment_status = 'UNPAID'`).\n"
        "4. Calculate invoice totals, dates, and vendor statistics accurately.\n"
        "5. Respond in a professional, concise, and structured financial summary format."
    ),
    tools=[list_tables, get_table_schema, execute_sql_query]
)
