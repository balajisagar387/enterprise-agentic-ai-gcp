---
name: winter-storm-triage
description: Standard operating procedures for handling customer orders delayed due to severe winter storms, verifying order and loyalty details, issuing tier-based compensation, and drafting customer communications.
---

# Winter Storm Triage Standard Operating Procedure

This skill dictates standard operating procedures for resolving customer inquiries and orders delayed due to severe winter storms.

## Workflow Procedures

### Step 1: Verify Order and Loyalty Information
1. Use the `get_order_status` tool with the given `order_id` to check the order status, delay reason, and associated `customer_id`. Verify that the package is delayed due to winter storms.
2. Use the `get_customer_loyalty_info` tool with the retrieved `customer_id` to determine the customer's loyalty tier (`PLATINUM`, `GOLD`, `SILVER`, or `MEMBER`).

### Step 2: Determine Compensation Based on Loyalty Tier
Apply compensation credit and shipping upgrades based on the customer's loyalty tier:

- **Platinum**: $100 credit, Next-Day Air shipping upgrade
- **Gold**: $50 credit, Next-Day Air shipping upgrade
- **Silver**: $25 credit, 3-Day Select shipping upgrade
- **Member**: $10 credit, Priority Shipping upgrade

### Step 3: Issue Disruption Compensation
Call the `issue_disruption_compensation` tool to apply the compensation:
- `customer_id`: The customer's ID (e.g., `CUST-7742`)
- `compensation_amount`: Credit amount corresponding to the tier (`$100`, `$50`, `$25`, or `$10`)
- `shipping_upgrade`: Shipping upgrade corresponding to the tier (`Next-Day Air`, `3-Day Select`, or `Priority Shipping`)

### Step 4: Draft Empathetic Customer Response
Draft an empathetic and clear customer response detailing the resolution:
- Acknowledge and apologize for the delay caused by the severe winter storm.
- Detail the compensation credit applied to their account.
- Specify the complimentary shipping upgrade provided for their shipment.
- Express appreciation for their patience and continued loyalty to Cymbal Direct.
