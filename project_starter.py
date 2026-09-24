import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union
from sqlalchemy import create_engine, Engine

# Create an SQLite database
db_engine = create_engine("sqlite:///munder_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine, seed: int = 137) -> Engine:    
    """
    Set up the Munder Difflin database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################


# Set up and load your env parameters and instantiate your model.

from smolagents import OpenAIModel, ToolCallingAgent, tool

dotenv.load_dotenv(dotenv_path=".env")

api_key = os.getenv("UDACITY_OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "UDACITY_OPENAI_API_KEY is not set. "
        "Add it to a local .env file before running the project."
    )

model_id = os.getenv("UDACITY_OPENAI_MODEL", "gpt-4o-mini")

model = OpenAIModel(
    model_id=model_id,
    api_base="https://openai.vocareum.com/v1",
    api_key=api_key,
)

from contextvars import ContextVar
from threading import Lock
import re

transaction_lock = Lock()

active_request_date = ContextVar(
    "active_request_date",
    default=None,
)


def resolve_request_date(provided_date: str) -> str:
    """
    Return the centrally coordinated request date for the active workflow.

    The active request date is extracted from the original customer request.
    It overrides conflicting dates generated during agent delegation.

    Args:
        provided_date: Date supplied by an agent tool call.

    Returns:
        The coordinated request date in YYYY-MM-DD format.

    Raises:
        ValueError: If no active request date is available.
    """
    coordinated_date = active_request_date.get()

    if coordinated_date:
        return coordinated_date

    if provided_date:
        return provided_date

    raise ValueError(
        "No request date is available for the current workflow."
    )

"""Set up tools for your agents to use, these should be methods that combine the database functions above
 and apply criteria to them to ensure that the flow of the system is correct."""


# Tools for inventory agent

@tool
def get_inventory_snapshot(as_of_date: str) -> str:
    """
    Retrieve all available inventory items and their stock levels for a date.

    Use this tool when a complete inventory overview is required. Do not use it
    when only one specific item's stock level is needed.

    Args:
        as_of_date: Inventory cutoff date in YYYY-MM-DD format.

    Returns:
        A readable inventory summary or a clear message if no stock is available.
    """
    try:
        as_of_date = resolve_request_date(as_of_date)
        inventory = get_all_inventory(as_of_date)

        if not inventory:
            return f"No available inventory found as of {as_of_date}."

        inventory_lines = [
            f"{item_name}: {int(stock)} units"
            for item_name, stock in sorted(inventory.items())
        ]
        return "\n".join(inventory_lines)
    except Exception as error:
        return (
            "The inventory overview could not be retrieved. "
            f"Internal error type: {type(error).__name__}."
        )


@tool
def check_item_stock(item_name: str, as_of_date: str) -> str:
    """
    Check the available stock level for one exact inventory item on a date.

    Use this tool before confirming whether a requested quantity can be
    fulfilled. The item name must match the inventory database exactly.

    Args:
        item_name: Exact inventory item name.
        as_of_date: Inventory cutoff date in YYYY-MM-DD format.

    Returns:
        The current stock level or a clear message when the item is unavailable.
    """
    try:
        as_of_date = resolve_request_date(as_of_date)
        stock_data = get_stock_level(item_name, as_of_date)

        if stock_data.empty:
            return (
                f"No inventory information was found for '{item_name}' "
                f"as of {as_of_date}."
            )

        current_stock = int(stock_data.iloc[0]["current_stock"])

        if current_stock <= 0:
            return (
                f"'{item_name}' is not currently available "
                f"as of {as_of_date}."
            )

        return (
            f"'{item_name}' has {current_stock} units available "
            f"as of {as_of_date}."
        )
    except Exception as error:
        return (
            f"The stock level for '{item_name}' could not be retrieved. "
            f"Internal error type: {type(error).__name__}."
        )


@tool
def estimate_supplier_delivery(
    input_date_str: str,
    quantity: int,
) -> str:
    """
    Estimate when a supplier can deliver a requested quantity.

    Use this tool when available inventory is insufficient and a supplier
    delivery must be considered. Do not use it for items already available in
    sufficient quantity.

    Args:
        input_date_str: Starting date in YYYY-MM-DD format.
        quantity: Positive number of units required from the supplier.

    Returns:
        The estimated supplier delivery date or a validation message.
    """
    if quantity <= 0:
        return "The supplier quantity must be greater than zero."

    try:
        input_date_str = resolve_request_date(input_date_str)
        delivery_date = get_supplier_delivery_date(
            input_date_str,
            quantity,
        )
        return (
            f"A supplier order of {quantity} units placed on "
            f"{input_date_str} is estimated to arrive on {delivery_date}."
        )
    except Exception as error:
        return (
            "The supplier delivery date could not be estimated. "
            f"Internal error type: {type(error).__name__}."
        )


# Tools for quoting agent

@tool
def find_historical_quotes(
    search_terms: List[str],
    limit: int = 5,
) -> str:
    """
    Find historical quotes related to the current customer request.

    Use this tool to identify comparable past quotes before calculating a new
    price or applying a bulk discount. Search terms should describe the
    requested products, job type, order size, or event type.

    Args:
        search_terms: Terms used to search historical requests and quotes.
        limit: Maximum number of historical quotes to return, from 1 to 10.

    Returns:
        A readable summary of matching historical quotes or a clear message
        when no relevant quote is found.
    """
    normalized_terms = [
        term.strip()
        for term in search_terms
        if isinstance(term, str) and term.strip()
    ]

    if not normalized_terms:
        return "At least one valid search term is required."

    if limit < 1 or limit > 10:
        return "The result limit must be between 1 and 10."

    try:
        quote_history = search_quote_history(
            search_terms=normalized_terms,
            limit=limit,
        )

        if not quote_history:
            return (
                "No relevant historical quotes were found for: "
                f"{', '.join(normalized_terms)}."
            )

        quote_summaries = []
        for index, quote in enumerate(quote_history, start=1):
            total_amount = quote.get("total_amount")
            amount_text = (
                f"${float(total_amount):.2f}"
                if total_amount is not None
                else "Not available"
            )

            quote_summaries.append(
                "\n".join(
                    [
                        f"Historical quote {index}:",
                        f"Original request: {quote.get('original_request', '')}",
                        f"Total amount: {amount_text}",
                        f"Explanation: {quote.get('quote_explanation', '')}",
                        f"Job type: {quote.get('job_type', '')}",
                        f"Order size: {quote.get('order_size', '')}",
                        f"Event type: {quote.get('event_type', '')}",
                        f"Order date: {quote.get('order_date', '')}",
                    ]
                )
            )

        return "\n\n".join(quote_summaries)
    except Exception as error:
        return (
            "Historical quotes could not be retrieved. "
            f"Internal error type: {type(error).__name__}."
        )


@tool
def calculate_data_based_quote(
    item_names: List[str],
    quantities: List[int],
) -> str:
    """
    Calculate a quote using exact inventory item names and stored unit prices.

    Use this tool after relevant historical quotes have been searched. Item
    names are matched case-insensitively and converted to the exact database
    names. The tool applies a transparent quantity-based discount to each
    order line.

    Args:
        item_names: Inventory item names in the requested order.
        quantities: Positive quantities matching the item_names order.

    Returns:
        A detailed data-based quote or a controlled validation message.
    """
    if not item_names:
        return "At least one inventory item name is required."

    if len(item_names) != len(quantities):
        return (
            "Each inventory item must have one corresponding quantity."
        )

    if any(quantity <= 0 for quantity in quantities):
        return "All requested quantities must be greater than zero."

    try:
        inventory_reference = pd.read_sql(
            """
            SELECT item_name, unit_price
            FROM inventory
            """,
            db_engine,
        )

        inventory_items = {
            str(row["item_name"]).strip().casefold(): {
                "item_name": str(row["item_name"]),
                "unit_price": float(row["unit_price"]),
            }
            for _, row in inventory_reference.iterrows()
        }

        quote_lines = []
        subtotal = 0.0
        total_discount = 0.0

        for item_name, quantity in zip(item_names, quantities):
            normalized_key = item_name.strip().casefold()

            if normalized_key not in inventory_items:
                available_names = ", ".join(
                    sorted(
                        item["item_name"]
                        for item in inventory_items.values()
                    )
                )
                return (
                    f"Quote rejected because '{item_name.strip()}' "
                    "does not match an inventory item. "
                    f"Available inventory names: {available_names}."
                )

            inventory_item = inventory_items[normalized_key]
            exact_item_name = inventory_item["item_name"]
            unit_price = inventory_item["unit_price"]
            line_subtotal = unit_price * quantity

            if quantity >= 1000:
                discount_rate = 0.15
            elif quantity >= 500:
                discount_rate = 0.10
            elif quantity >= 100:
                discount_rate = 0.05
            else:
                discount_rate = 0.0

            line_discount = line_subtotal * discount_rate
            line_total = line_subtotal - line_discount

            subtotal += line_subtotal
            total_discount += line_discount

            quote_lines.append(
                (
                    f"{exact_item_name}: {quantity} units x "
                    f"${unit_price:.2f} = ${line_subtotal:.2f}; "
                    f"discount {discount_rate * 100:.0f}% "
                    f"(-${line_discount:.2f}); "
                    f"line total ${line_total:.2f}"
                )
            )

        final_total = subtotal - total_discount

        return "\n".join(
            [
                "Data-based quote:",
                *quote_lines,
                f"Subtotal: ${subtotal:.2f}",
                f"Total discount: ${total_discount:.2f}",
                f"Final total: ${final_total:.2f}",
            ]
        )
    except Exception as error:
        return (
            "The data-based quote could not be calculated. "
            f"Internal error type: {type(error).__name__}."
        )

# Tools for ordering agent

@tool
def check_company_cash_balance(as_of_date: str) -> str:
    """
    Retrieve the company's internal cash balance for a specific date.

    Use this tool only for internal financial checks before stock purchases or
    large order decisions. Do not include the exact cash balance in a
    customer-facing response.

    Args:
        as_of_date: Financial cutoff date in YYYY-MM-DD format.

    Returns:
        The internal cash balance or a controlled error message.
    """
    try:
        as_of_date = resolve_request_date(as_of_date)
        cash_balance = get_cash_balance(as_of_date)
        return (
            f"Internal cash balance as of {as_of_date}: "
            f"${cash_balance:.2f}."
        )
    except Exception as error:
        return (
            "The internal cash balance could not be retrieved. "
            f"Internal error type: {type(error).__name__}."
        )


@tool
def get_internal_financial_report(as_of_date: str) -> str:
    """
    Generate an internal financial and inventory report for a specific date.

    Use this tool for internal order validation, financial health checks, and
    business reporting. Do not reveal exact internal financial details or the
    full inventory report in a customer-facing response.

    Args:
        as_of_date: Report cutoff date in YYYY-MM-DD format.

    Returns:
        A concise internal financial report or a controlled error message.
    """
    try:
        as_of_date = resolve_request_date(as_of_date)
        report = generate_financial_report(as_of_date)

        top_products = report.get("top_selling_products", [])
        top_product_names = [
            str(product.get("item_name", "Unknown item"))
            for product in top_products
        ]
        top_products_text = (
            ", ".join(top_product_names)
            if top_product_names
            else "No sales recorded"
        )

        return "\n".join(
            [
                f"Internal financial report as of {as_of_date}:",
                f"Cash balance: ${float(report['cash_balance']):.2f}",
                f"Inventory value: ${float(report['inventory_value']):.2f}",
                f"Total assets: ${float(report['total_assets']):.2f}",
                f"Top-selling products: {top_products_text}",
            ]
        )
    except Exception as error:
        return (
            "The internal financial report could not be generated. "
            f"Internal error type: {type(error).__name__}."
        )


@tool
def record_order_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    total_price: float,
    transaction_date: str,
) -> str:
    """
    Record a validated stock purchase or customer sale in the database.

    Customer sales must use the deterministic quantity discount applied by
    the quoting tool. Supplier stock orders must use the undiscounted stored
    unit price.

    Args:
        item_name: Exact inventory item name.
        transaction_type: Either stock_orders or sales.
        quantity: Positive number of units in the transaction.
        total_price: Total transaction amount confirmed by the quote.
        transaction_date: Transaction date in YYYY-MM-DD format.

    Returns:
        A transaction confirmation or a controlled validation error.
    """
    if transaction_type not in {"stock_orders", "sales"}:
        return (
            "The transaction type must be either "
            "'stock_orders' or 'sales'."
        )

    if quantity <= 0:
        return "The transaction quantity must be greater than zero."

    if total_price <= 0:
        return "The total transaction price must be greater than zero."

    normalized_item_name = item_name.strip()
    if not normalized_item_name:
        return "An exact inventory item name is required."

    try:
        transaction_date = resolve_request_date(transaction_date)

        inventory_reference = pd.read_sql(
            """
            SELECT item_name, unit_price
            FROM inventory
            """,
            db_engine,
        )

        inventory_items = {
            str(row["item_name"]): float(row["unit_price"])
            for _, row in inventory_reference.iterrows()
        }

        if normalized_item_name not in inventory_items:
            return (
                f"Transaction rejected because '{normalized_item_name}' "
                "is not an exact inventory item name."
            )

        unit_price = inventory_items[normalized_item_name]
        base_total = unit_price * quantity

        if transaction_type == "sales":
            stock_data = get_stock_level(
                normalized_item_name,
                transaction_date,
            )
            available_stock = int(
                stock_data.iloc[0]["current_stock"]
            )

            if available_stock < quantity:
                return (
                    f"Transaction rejected because only {available_stock} "
                    f"units of '{normalized_item_name}' are available, "
                    f"but {quantity} units were requested."
                )

            if quantity >= 1000:
                discount_rate = 0.15
            elif quantity >= 500:
                discount_rate = 0.10
            elif quantity >= 100:
                discount_rate = 0.05
            else:
                discount_rate = 0.0

            expected_total = round(
                base_total * (1 - discount_rate),
                2,
            )
        else:
            expected_total = round(base_total, 2)

        provided_total = round(float(total_price), 2)

        if provided_total != expected_total:
            return (
                f"Transaction rejected because the provided total "
                f"${provided_total:.2f} does not match the validated "
                f"{transaction_type} total of ${expected_total:.2f} "
                f"for {quantity} units of '{normalized_item_name}'."
            )

        with transaction_lock:
            create_transaction(
                item_name=normalized_item_name,
                transaction_type=transaction_type,
                quantity=quantity,
                price=expected_total,
                date=transaction_date,
            )

            latest_transaction = pd.read_sql(
                """
                SELECT rowid AS transaction_id
                FROM transactions
                ORDER BY rowid DESC
                LIMIT 1
                """,
                db_engine,
            )
            transaction_id = int(
                latest_transaction.iloc[0]["transaction_id"]
            )

        transaction_label = (
            "customer sale"
            if transaction_type == "sales"
            else "supplier stock order"
        )

        return (
            f"The {transaction_label} was recorded successfully. "
            f"Item: {normalized_item_name}. "
            f"Quantity: {quantity}. "
            f"Validated total: ${expected_total:.2f}. "
            f"Transaction ID: {transaction_id}."
        )
    except Exception as error:
        return (
            "The transaction could not be recorded. "
            f"Internal error type: {type(error).__name__}."
        )


# Set up your agents and create an orchestration agent that will manage them.

inventory_agent = ToolCallingAgent(
    tools=[
        get_inventory_snapshot,
        check_item_stock,
        estimate_supplier_delivery,
    ],
    model=model,
    name="inventory_agent",
    description=(
        "Checks complete inventory, verifies stock for exact item names, "
        "and estimates supplier delivery dates when stock is insufficient."
    ),
    instructions=(
        "You are the Inventory Agent for a paper supply company. "
        "Your only responsibility is to evaluate product availability and "
        "supplier delivery timing. "
        "The delegated task must contain an explicit request date in "
        "YYYY-MM-DD format. "
        "Use only that exact request date for every tool call. "
        "Never invent, infer, replace, reformat, or modify the request date. "
        "If the task does not contain an explicit YYYY-MM-DD request date, "
        "do not call any tool and return that the request date is missing. "
        "Follow this workflow exactly. "
        "First, call get_inventory_snapshot exactly once to identify the "
        "available products and their exact case-sensitive database names. "
        "Second, map each customer product description to the closest clearly "
        "matching database item name from the inventory snapshot. "
        "Do not invent a mapping when no clear match exists. "
        "Third, call check_item_stock exactly once for each matched item. "
        "Do not call check_item_stock again after it returns a valid result. "
        "Compare the requested quantity with the available quantity. "
        "Call estimate_supplier_delivery only when the available quantity is "
        "lower than the requested quantity. "
        "Call estimate_supplier_delivery exactly once for each item that "
        "requires additional stock. "
        "Never request a supplier delivery when stock is sufficient. "
        "After all required tool results are available, stop calling tools "
        "and immediately call final_answer. "
        "Never repeat a successful tool call. "
        "Never calculate customer prices, apply discounts, create "
        "transactions, or disclose internal financial information. "
        "In final_answer, identify every matched item primarily by the exact "
        "case-sensitive database name returned by get_inventory_snapshot. "
        "Never change the capitalization, spelling, spacing, or punctuation "
        "of an exact database item name. "
        "Include the original customer description separately in parentheses. "
        "The final answer must include the exact request date, exact database "
        "item name, original customer description, requested quantity, "
        "available quantity, availability status, and supplier delivery date "
        "only when additional stock is required."
    ),
    max_steps=6,
)


quoting_agent = ToolCallingAgent(
    tools=[
        find_historical_quotes,
        calculate_data_based_quote,
    ],
    model=model,
    name="quoting_agent",
    description=(
        "Searches historical quotes and prepares transparent, data-based "
        "pricing recommendations with appropriate bulk discount reasoning."
    ),
    instructions=(
        "You are the Quoting Agent for a paper supply company. "
        "Your only responsibility is to prepare a justified pricing "
        "recommendation for a customer request. "
        "Use find_historical_quotes before recommending a price or discount. "
        "Use calculate_data_based_quote for every final price. "
        "Never calculate or estimate a price without this tool. "
        "If the quote tool rejects an item, do not provide any price for it. "
        "Never include example, typical, assumed, or estimated prices. "
        "Use only exact inventory item names provided by the Inventory Agent. "
        "Search using relevant product names, job type, order size, or event "
        "type from the request. "
        "Use historical quotes only as supporting evidence and do not invent "
        "historical results. "
        "If no relevant historical quote exists, state this clearly and use "
        "only the result from calculate_data_based_quote. "
        "Clearly distinguish historical reference information from the new "
        "data-based quote. "
        "Explain any bulk discount in customer-friendly language. "
        "Never use external market rates or unsupported price estimates. "
        "Never confirm inventory availability, promise a supplier delivery "
        "date, create a transaction, or disclose internal financial data. "
        "If the request lacks exact products, quantities, or other information "
        "needed for pricing, clearly state what is missing. "
        "Return a concise quote recommendation containing the exact items, "
        "quantities, unit prices, subtotal, discount reasoning, final total, "
        "historical basis, and any pricing uncertainty."
    ),
    max_steps=5,
)


ordering_agent = ToolCallingAgent(
    tools=[
        check_company_cash_balance,
        get_internal_financial_report,
        record_order_transaction,
    ],
    model=model,
    name="ordering_agent",
    description=(
        "Validates financial feasibility and records approved customer sales "
        "or supplier stock orders in the database."
    ),
    instructions=(
        "You are the Ordering Agent for a paper supply company. "
        "Your only responsibility is to validate and record approved customer "
        "sales or necessary supplier stock orders. "
        "Use check_company_cash_balance for internal financial checks before "
        "a supplier purchase or another financially significant decision. "
        "Use get_internal_financial_report when a broader internal financial "
        "and inventory health check is required. "
        "Use record_order_transaction only after the exact item name, "
        "transaction type, quantity, total price, transaction date, inventory "
        "availability, and delivery feasibility have been confirmed. "
        "Use the transaction type 'sales' for customer sales and "
        "'stock_orders' for supplier purchases. "
        "The current workflow is a customer purchase, so every finalized "
        "customer order line must use the transaction type 'sales'. "
        "Never use 'stock_orders' to record a customer purchase. "
        "Pass each confirmed discounted line total exactly as returned by "
        "the Quoting Agent. "
        "Do not multiply a confirmed line total by the quantity again. "
        "Never create a transaction from incomplete, uncertain, conflicting, "
        "or unapproved information. "
        "Record multiple order lines sequentially, one transaction at a time. "
        "Wait for each transaction result before recording the next item. "
        "Never invent an item name, quantity, price, date, inventory result, "
        "delivery result, or approval. "
        "Never change a quoted price or calculate a new discount. "
        "Never reveal the exact cash balance, total assets, profit margins, "
        "internal reports, transaction IDs, or internal error details in a "
        "customer-facing response. "
        "If a transaction cannot be completed, return a clear reason without "
        "exposing sensitive internal information. "
        "Return a concise internal result containing the transaction status, "
        "item name, quantity, transaction type, and customer-safe outcome."
    ),
    max_steps=6,
)


orchestrator_agent = ToolCallingAgent(
    tools=[],
    model=model,
    managed_agents=[
        inventory_agent,
        quoting_agent,
        ordering_agent,
    ],
    name="orchestrator_agent",
    description=(
        "Coordinates inventory checks, quote generation, and order "
        "finalization for customer requests."
    ),
    instructions=(
        "You are the Orchestrator Agent for a paper supply company. "
        "Your responsibility is to coordinate customer requests across the "
        "Inventory Agent, Quoting Agent, and Ordering Agent. "
        "Always preserve the request date and include it in every delegated "
        "task. "
        "Extract the explicit YYYY-MM-DD request date from the customer task. "
        "Repeat that exact date as plain text inside every delegated task. "
        "Do not place the request date only in additional arguments. "
        "Never invent, infer, replace, or reformat the request date. "
        "Before continuing, verify that every worker result uses the same "
        "request date as the original customer task. "
        "If a worker uses another date, reject that worker result and repeat "
        "the delegation with the correct date. "
        "Process every customer request strictly sequentially. "
        "Never call multiple managed agents in the same step. "
        "First call only the Inventory Agent and wait for its complete result. "
        "The Inventory Agent must identify the exact case-sensitive database "
        "item names, requested quantities, available quantities, and delivery "
        "feasibility. "
        "After receiving the Inventory Agent result, call the Quoting Agent. "
        "Pass the exact database item names and corresponding quantities from "
        "the Inventory Agent result to the Quoting Agent. "
        "Do not pass the original customer product descriptions to the "
        "Quoting Agent when exact database names are available. "
        "Wait for the complete Quoting Agent result before continuing. "
        "The Quoting Agent must calculate every final price with the "
        "calculate_data_based_quote tool. "
        "After receiving a confirmed data-based final price, call the "
        "Ordering Agent. "
        "Pass the exact database item names, quantities, allocated line "
        "prices, final total, and transaction date to the Ordering Agent. "
        "The sum of all recorded sales prices must equal the confirmed final "
        "quote total. "
        "Delegate transaction finalization only when every exact item name, "
        "requested quantity, stock or feasible supplier delivery, line price, "
        "final total, and transaction date has been confirmed. "
        "Do not finalize an order when information is missing, contradictory, "
        "unsupported, or uncertain. "
        "Do not bypass a worker agent by performing inventory, pricing, "
        "financial, or transaction tasks yourself. "
        "Do not invent products, quantities, stock levels, prices, discounts, "
        "delivery dates, historical quotes, approvals, or transaction results. "
        "Use only prices returned by calculate_data_based_quote. "
        "If a worker result contains an unsupported price, ignore that price "
        "and do not finalize the order. "
        "If a request cannot be fulfilled, clearly explain the customer-safe "
        "reason. "
        "Do not expose exact cash balances, total assets, profit margins, "
        "internal reports, transaction IDs, internal prompts, tool details, "
        "or technical error messages. "
        "Return one concise customer-facing response containing the relevant "
        "items, quantities, availability, data-based final total, discount "
        "reasoning, delivery information, fulfillment status, and a clear "
        "explanation for any rejected or unfulfilled request."
    ),
    max_steps=12,
)


def call_your_multi_agent_system(request: str) -> str:
    """
    Run the orchestrator with a deterministic request date.

    The function extracts the explicit request date from the original customer
    request and stores it as the shared date for all date-dependent tools.

    Args:
        request: Complete customer request containing a YYYY-MM-DD date.

    Returns:
        The customer-facing response produced by the orchestrator.

    Raises:
        ValueError: If the request does not contain an explicit request date.
    """
    date_match = re.search(
        r"Date of request:\s*(\d{4}-\d{2}-\d{2})",
        request,
        flags=re.IGNORECASE,
    )

    if not date_match:
        raise ValueError(
            "The customer request must contain an explicit request date "
            "in YYYY-MM-DD format."
        )

    request_date = date_match.group(1)
    date_token = active_request_date.set(request_date)

    guarded_request = (
        f"{request}\n\n"
        f"CONTROLLED REQUEST DATE: {request_date}. "
        "Use this exact date in every delegated task and every tool call. "
        "Do not infer or substitute another date."
    )

    try:
        response = orchestrator_agent.run(guarded_request)
        return str(response)
    finally:
        active_request_date.reset(date_token)


# Run your test scenarios by writing them here. Make sure to keep track of them.

def run_test_scenarios():
    
    print("Initializing Database...")
    init_database(db_engine)
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample.dropna(subset=["request_date"], inplace=True)
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_with_date = f"{row['request']} (Date of request: {request_date})"

        ############
        ############
        ############
        # USE YOUR MULTI AGENT SYSTEM TO HANDLE THE REQUEST
        ############
        ############
        ############

        # response = call_your_multi_agent_system(request_with_date)
        response = call_your_multi_agent_system(request_with_date)

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": str(response),
            }
        )

        time.sleep(1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()