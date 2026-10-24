import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.cloud import bigquery

load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
DATASET_ID = "pool_data"
client = bigquery.Client(project=PROJECT_ID)

# ---------------------------------------------------------
# Database Helper Functions
# ---------------------------------------------------------

def read_table(table_name: str, email: str):
    """Retrieves one customer record by customer_email."""
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    WHERE customer_email = @email
    LIMIT 1;
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = list(query_job.result())
    if not results:
        return None
    row = dict(results[0].items())
    for k, v in row.items():
        if hasattr(v, "isoformat"):
            row[k] = v.isoformat()
    return row


def read_table_all(table_name: str):
    """Retrieves all customer records from a specified table."""
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`;
    """
    query_job = client.query(query)
    rows = []
    for row in query_job.result():
        row_dict = dict(row.items())
        for k, v in row_dict.items():
            if hasattr(v, "isoformat"):
                row_dict[k] = v.isoformat()
        rows.append(row_dict)
    return rows


def write_to_table(table_name: str, row: dict):
    """Inserts a customer record into a specified table."""
    columns = list(row.keys())
    values = [row[col] for col in columns]
    param_names = [f"p_{i}" for i in range(len(columns))]

    col_clause = ", ".join(columns)
    val_clause = ", ".join([f"@{p}" for p in param_names])

    query = f"""
    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{table_name}` ({col_clause})
    VALUES ({val_clause});
    """
    params = [
        bigquery.ScalarQueryParameter(param_names[i], "STRING", str(values[i]))
        for i in range(len(columns))
    ]
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return "Success"
    except Exception as e:
        return f"Error: {e}"


def delete_from_table(table_name: str, email: str):
    """Deletes records from the specified table for the customer email."""
    query = f"""
    DELETE FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
    WHERE customer_email = @email;
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email),
        ]
    )
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return "Success"
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------
# Deterministic Runtime Guardrails & State Machine
# ---------------------------------------------------------

def check_transaction(from_table: str, to_table: str) -> bool:
    """Validates whether a business workflow transition is permitted.

    Valid transitions include:
    - pool_estimates -> accepted_with_deposit
    - pool_estimates -> denied_estimates
    - accepted_with_deposit -> scheduled_installations
    - scheduled_installations -> completed_pools
    - completed_pools -> paid_and_closed
    """
    valid_transitions = {
        ("pool_estimates", "accepted_with_deposit"),
        ("pool_estimates", "denied_estimates"),
        ("accepted_with_deposit", "scheduled_installations"),
        ("scheduled_installations", "completed_pools"),
        ("completed_pools", "paid_and_closed"),
    }
    return (from_table, to_table) in valid_transitions


def perform_consistent_transaction(from_table: str, to_table: str, customer_email: str) -> bool:
    """Safely transitions a customer record between tables with zero data loss.

    Executes in a safe Read -> Insert -> Verify -> Delete sequence:
    1. Read source record by customer email
    2. Abort if source record does not exist
    3. Insert record into destination table
    4. Abort if insert fails
    5. Delete original record only after write is confirmed
    """
    row = read_table(from_table, customer_email)
    if row is None:
        return False
    result = write_to_table(to_table, row)
    if result != "Success":
        return False
    delete_from_table(from_table, customer_email)
    return True


# ---------------------------------------------------------
# Google ADK Agent Definition
# ---------------------------------------------------------

root_agent = Agent(
    name="cymbal_pools_agent",
    model=os.environ.get("MODEL", "gemini-3.5-flash"),
    description="Customer lifecycle management agent for Cymbal Pools operating over BigQuery datasets.",
    instruction="""You are a customer lifecycle management agent for Cymbal Pools.

The tables you have available are:
- pool_estimates: Contains all pool estimates
- accepted_with_deposit: Contains all pool estimates that have been accepted and have a deposit
- denied_estimates: Estimates that have been denied by the customer and will not proceed.
- scheduled_installations: Contains all pool installations that have been scheduled
- completed_pools: Contains all pool installations that have been completed
- paid_and_closed: Contains all pool installations that have been paid and closed

Rules of operation:
1. Use read_table_all or read_table to inspect customer data.
2. ALWAYS use check_transaction to check if a transition between two tables is valid BEFORE performing any record movements. If not valid, inform the user immediately and do not proceed.
3. Use perform_consistent_transaction when you need to read a table, insert a row into another table, and delete the original row.
4. Never attempt to manually delete records without an approved transition.
""",
    tools=[
        read_table,
        read_table_all,
        check_transaction,
        perform_consistent_transaction,
    ],
)
