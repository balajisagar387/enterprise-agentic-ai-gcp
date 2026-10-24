# Sample Enterprise Queries & Analytical Prompts

This cookbook contains test prompts to run in Gemini Enterprise once the BigQuery MCP Data Store (`byo_bq_mcp`) is connected to the app (`gemini-bq-mcp-app`).

---

## 1. Schema & Table Discovery
Use these prompts to confirm the agent successfully lists tables and inspects schemas:

```text
Which BigQuery tables can I access in project {PROJECT_ID}?
```
```text
Describe the schema and available columns in the sales transactions table.
```

---

## 2. Business Performance & Growth Analysis

### Year-Over-Year (YoY) Growth
```text
What is our Year-Over-Year (YoY) revenue growth across all product categories?
```
*Expected Agent Behavior*: Generates SQL aggregating annual revenue, calculates percentage delta, and outputs an executive summary table.

### Strategic Product Transition
```text
How is our transition into smart-tech and green energy performing?
```
*Expected Agent Behavior*: Filters line items matching smart-tech and green energy SKUs, compares quarterly volume against traditional categories.

---

## 3. Customer & Commercial Strategy

### Customer Targeting
```text
Which customers should I target based on the 2024 data?
```
*Expected Agent Behavior*: Identifies high-value customers with declining frequency or high-margin accounts primed for renewal.

### Average Order Value (AOV)
```text
What is the average order value (AOV) by customer segment?
```

### Geographic Distribution
```text
Which geographic regions are buying the most "Decor" (like large planters)?
```
