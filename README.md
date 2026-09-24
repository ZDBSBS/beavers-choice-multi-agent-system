# Munder Difflin Multi-Agent System Project

Welcome to the starter code repository for the **Munder Difflin Paper Company Multi-Agent System Project**! This repository contains the starter code and tools you will need to design, build, and test a multi-agent system that supports core business operations at a fictional paper manufacturing company.

## Project Context

You’ve been hired as an AI consultant by Munder Difflin Paper Company, a fictional enterprise looking to modernize their workflows. They need a smart, modular **multi-agent system** to automate:

- **Inventory checks** and restocking decisions
- **Quote generation** for incoming sales inquiries
- **Order fulfillment** including supplier logistics and transactions

Your solution must use a maximum of **5 agents** and process inputs and outputs entirely via **text-based communication**.

This project challenges your ability to orchestrate agents using modern Python frameworks like `smolagents`, `pydantic-ai`, or `npcsh`, and combine that with real data tools like `sqlite3`, `pandas`, and LLM prompt engineering.

---

## What’s Included

From the `project.zip` starter archive, you will find:

- `project_starter.py`: The main Python script you will modify to implement your agent system
- `quotes.csv`: Historical quote data used for reference by quoting agents
- `quote_requests.csv`: Incoming customer requests used to build quoting logic
- `quote_requests_sample.csv`: A set of simulated test cases to evaluate your system

---

## Workspace Instructions

All the files have been provided in the VS Code workspace on the Udacity platform. Please install the agent orchestration framework of your choice.

## Local Setup Instructions

### 1. Install Dependencies

Make sure you have Python 3.10 or newer installed.

Install all required packages using the provided `requirements.txt` file:

```bash
python -m pip install -r requirements.txt
```

The completed project uses:

```text
smolagents==1.26.0
```

The framework is already included in `requirements.txt` and does not need to be installed separately.

### 2. Create the `.env` File

Add your OpenAI-compatible API key:

```text
UDACITY_OPENAI_API_KEY=your_openai_key_here
```

An optional model override can be added:

```text
UDACITY_OPENAI_MODEL=gpt-4o-mini
```

This project uses the following OpenAI-compatible proxy:

```text
https://openai.vocareum.com/v1
```

The `.env` file is excluded from Git and must not be committed.

## How to Run the Project

The completed agents are defined in the `"YOUR MULTI AGENT STARTS HERE"` section inside `project_starter.py`.

Run the completed project with:

```bash
python project_starter.py
```

The `run_test_scenarios()` function processes all requests from `quote_requests_sample.csv` chronologically.

The system coordinates inventory checks, generates data-based quotes, validates transactions, processes orders, and saves evaluation checkpoints.

Output includes:

- Agent responses
- Cash and inventory updates
- Final financial report
- A `test_results.csv` file with all interaction results

To retain the complete terminal output:

```bash
set -o pipefail
python -u project_starter.py 2>&1 | tee evaluation_run.log
```

The generated log file is excluded from Git.

---

## Tips for Success

- Start by sketching a **flow diagram** to visualize agent responsibilities and interactions.
- Test individual agent tools before full orchestration.
- Always include **dates** in customer requests when passing data between agents.
- Ensure every quote includes **bulk discounts** and uses past data when available.
- Use the **exact item names** from the database to avoid transaction failures.

---

## Submission Checklist

Make sure to submit the following files:

1. `project_starter.py` with all agent logic
2. `agent_workflow_diagram.png` describing the architecture and data flow
3. `agent_workflow_diagram.drawio` as the editable diagram source
4. `design_notes.txt` containing the reflection report
5. `test_results.csv` containing the complete evaluation results

---

# Completed Project Implementation

## Solution Overview

The starter project has been extended with a complete multi-agent sales workflow using `smolagents`.

The solution coordinates:

- Inventory management
- Product matching
- Quote generation
- Quantity-based discounts
- Supplier delivery assessment
- Sales finalization
- Transaction validation
- Customer-facing responses

The implementation contains four agents and remains within the project constraint of a maximum of five agents:

1. Orchestrator Agent
2. Inventory Agent
3. Quoting Agent
4. Ordering Agent

All agents communicate through text-based tasks and responses.

---

## Multi-Agent Workflow

The system uses sequential orchestration:

```text
Customer Request
        |
        v
Orchestrator Agent
        |
        v
Inventory Agent
        |
        v
Quoting Agent
        |
        v
Ordering Agent
        |
        v
Transaction and Response Verification
        |
        v
Customer-Facing Response
```

Sequential processing ensures that each agent receives validated information from the previous stage.

The Inventory Agent identifies exact database item names and checks availability before pricing begins.

The Quoting Agent calculates a data-based quote before the Ordering Agent records any transaction.

The Ordering Agent records only transactions that pass deterministic validation.

---

## Agent Responsibilities

### Orchestrator Agent

The Orchestrator Agent has the **workflow coordination competence**.

Responsibilities:

- Receives the original customer request
- Extracts and preserves the request date
- Delegates tasks sequentially
- Coordinates the worker agents
- Prevents downstream processing with incomplete information
- Combines validated worker results
- Returns the final customer-facing response

The Orchestrator Agent does not directly use the database helper functions.

### Inventory Agent

The Inventory Agent has the **inventory-management competence**.

Responsibilities:

- Retrieves the available inventory
- Identifies exact database item names
- Maps customer descriptions to available products
- Checks stock for every requested item
- Compares requested and available quantities
- Estimates supplier delivery when stock is insufficient

Assigned tools:

- `get_inventory_snapshot`
- `check_item_stock`
- `estimate_supplier_delivery`

### Quoting Agent

The Quoting Agent has the **pricing and discount competence**.

Responsibilities:

- Searches historical quote data
- Uses validated inventory item names
- Retrieves stored unit prices
- Calculates line subtotals
- Applies deterministic quantity discounts
- Returns the validated final quote total

Assigned tools:

- `find_historical_quotes`
- `calculate_data_based_quote`

### Ordering Agent

The Ordering Agent has the **sales-finalization competence**.

Responsibilities:

- Performs internal financial checks
- Validates exact inventory item names
- Validates quantities and transaction types
- Validates quoted prices and discounts
- Checks available stock
- Records approved customer sales or supplier stock orders
- Rejects inconsistent transaction parameters

Assigned tools:

- `check_company_cash_balance`
- `get_internal_financial_report`
- `record_order_transaction`

---

## Tool and Helper Function Mapping

All seven required helper functions from the starter code are used in agent tool definitions.

| Agent | Tool | Starter Helper Function |
|---|---|---|
| Inventory Agent | `get_inventory_snapshot` | `get_all_inventory` |
| Inventory Agent | `check_item_stock` | `get_stock_level` |
| Inventory Agent | `estimate_supplier_delivery` | `get_supplier_delivery_date` |
| Quoting Agent | `find_historical_quotes` | `search_quote_history` |
| Ordering Agent | `check_company_cash_balance` | `get_cash_balance` |
| Ordering Agent | `get_internal_financial_report` | `generate_financial_report` |
| Ordering Agent | `record_order_transaction` | `create_transaction` |

The additional `calculate_data_based_quote` tool uses unit prices stored in the inventory table.

---

## Request-Date Coordination

The request date is extracted from the original customer request and stored in a shared `ContextVar`:

```text
active_request_date
```

All date-dependent tools use this controlled date.

If an agent provides an incorrect or conflicting date, the original request date overrides it.

The shared context is reset after every processed customer request to prevent state from leaking into later workflows.

---

## Data-Based Pricing

Prices are calculated from unit prices stored in the inventory table.

The system does not use unsupported external market prices.

The deterministic quantity-discount policy is:

| Quantity | Discount |
|---:|---:|
| Below 100 units | 0% |
| 100 to 499 units | 5% |
| 500 to 999 units | 10% |
| 1,000 units or more | 15% |

A quote can include:

- Exact inventory item name
- Requested quantity
- Unit price
- Line subtotal
- Discount rate
- Discount amount
- Discounted line total
- Subtotal
- Total discount
- Final total

Historical quotes are used as supporting information when relevant.

The final transaction price is always validated against the deterministic pricing rules.

---

## Transaction Validation

Before a transaction is stored, the system validates:

- Exact inventory item name
- Supported transaction type
- Positive quantity
- Positive transaction total
- Available stock
- Controlled request date
- Stored unit price
- Applicable discount
- Expected line total

Invalid transactions are rejected without modifying inventory or cash.

A transaction lock serializes database writes and supports unique transaction IDs.

The transaction logic prevents:

- Unsupported product names
- Negative or zero quantities
- Negative or zero prices
- Sales above the available stock
- Incorrect transaction types
- Incorrectly scaled prices
- Prices that do not match the validated quote

---

## Response Verification

The function `build_transaction_verified_response()` reconciles customer-facing responses with the sales actually recorded during the current request.

The verified response uses:

- Recorded item names
- Recorded quantities
- Recorded prices
- Recorded total
- Controlled request date

This prevents inconsistent agent statements from overriding the database state.

If only part of an order is recorded, the response lists the recorded items and explains that unlisted items could not be confirmed under the available inventory, product-matching, pricing, or delivery conditions.

---

## Additional Project Files

The completed project includes:

| File | Purpose |
|---|---|
| `project_starter.py` | Complete multi-agent implementation |
| `requirements.txt` | Python dependencies |
| `quotes.csv` | Historical quote data |
| `quote_requests.csv` | Historical customer requests |
| `quote_requests_sample.csv` | Complete evaluation dataset |
| `test_results.csv` | Complete evaluation results |
| `agent_workflow_diagram.png` | Workflow diagram for submission |
| `agent_workflow_diagram.drawio` | Editable workflow diagram source |
| `design_notes.txt` | Reflection report |
| `.gitignore` | Excludes secrets and local runtime files |

---

## Running the Completed Evaluation

Run the complete evaluation with:

```bash
python project_starter.py
```

The project will:

1. Initialize the SQLite database
2. Load `quote_requests_sample.csv`
3. Process requests chronologically
4. Coordinate all four agents
5. Update cash and inventory
6. Save a checkpoint after every completed request
7. Generate `test_results.csv`
8. Print the final financial report

---

## Evaluation Checkpoints

The evaluation updates `test_results.csv` after every completed request.

This checkpoint mechanism protects completed results if the evaluation process is interrupted.

The result file contains:

- `request_id`
- `request_date`
- `cash_balance`
- `inventory_value`
- `response`

---

## Evaluation Results

The complete `quote_requests_sample.csv` dataset was processed.

Final evaluation summary:

- Total requests processed: **20**
- Requests with cash-balance changes: **9**
- Recorded customer sales: **13**
- Unique sales transaction IDs: **13**
- Total additional recorded revenue: **$1,179.42**
- Final cash balance: **$46,239.12**
- Final inventory value: **$3,655.45**

The evaluation demonstrates that:

- More than three requests changed the cash balance
- More than three requests were successfully or partially fulfilled
- Not all requests were fulfilled
- Unfulfilled items included customer-safe reasons

Reasons for unfulfilled requests included:

- Insufficient stock
- Unavailable products
- Ambiguous product descriptions
- Missing exact inventory matches
- Invalid transaction parameters
- Delivery constraints

---

## Verified Successful Example

One verified customer request contained:

- 200 units of `Glossy paper`
- 100 units of `Cardstock`
- 100 units of `Colored paper`

Validated line totals:

```text
Glossy paper: $38.00
Cardstock: $14.25
Colored paper: $9.50
Final total: $61.75
```

The completed workflow produced:

- Three unique customer sales
- A cash increase of `$61.75`
- An inventory reduction of 200 units of Glossy paper
- An inventory reduction of 100 units of Cardstock
- An inventory reduction of 100 units of Colored paper

---

## Security and Privacy

The project protects sensitive information by:

- Loading the API key from `.env`
- Excluding `.env` from Git
- Excluding the SQLite database from Git
- Excluding evaluation logs from Git
- Avoiding API keys in source code
- Preventing customer responses from exposing internal cash balances
- Preventing customer responses from exposing total assets
- Hiding internal prompts and technical error details
- Reconciling final responses with recorded transactions

---

## Workflow Diagram

The workflow diagram is available in two formats:

```text
agent_workflow_diagram.png
agent_workflow_diagram.drawio
```

The PNG file is intended for the project submission.

The `.drawio` file contains the editable diagram source.

The diagram includes:

- All four agents
- Explicit agent responsibilities
- Sequential orchestration
- Data flow between agents
- Tools assigned to each agent
- Helper-function mappings
- Database interactions
- Request-date coordination
- Transaction validation
- Response verification

---

## Reflection Report

The architecture explanation, evaluation discussion, system strengths, limitations, and proposed improvements are documented in:

```text
design_notes.txt
```

---

## Known Limitations

Current limitations include:

- Ambiguous customer descriptions can reduce product-matching accuracy
- Product matching does not use a configurable alias table
- Discount thresholds are defined in Python
- Multiple model calls may be required for one request
- The evaluation output could contain additional structured transaction fields

---

## Potential Improvements

Potential future improvements include:

1. A deterministic product-alias and synonym service
2. Configurable discount policies stored in the database
3. Structured evaluation fields for sold and rejected items
4. Lower-token structured communication between agents
5. Automated regression tests
6. Confidence scoring for product matching
7. A business-advisor agent for operational recommendations

---
