"""Coverage Calculator sub-agent for Paint Agent.

Computes total paintable surface area for a room based on dimensions,
applying deductions for doors and windows. Uses session state for the
selected paint product, coverage rate, and price per bucket.
"""
# Copyright (c) Cymbal Shops. All rights reserved.

import os
from google.adk.agents import Agent

coverage_calculator_agent = Agent(
    name="coverage_calculator",
    model=os.environ.get("MODEL", "gemini-2.5-flash"),
    description=(
        "Calculates the total paintable surface area for a room, required liters, "
        "2.5L bucket quantities, and total estimated price based on the selected product."
    ),
    instruction="""
You are a paint coverage and pricing calculation expert for Cymbal Shops.

The customer has selected: {SELECTED_PAINT?}
Product coverage rate: {COVERAGE_RATE?} sq meters per liter.
Price per 2.5L bucket: €{PRICE?}

To calculate paint requirements for a room:
1. Compute gross wall area: 2 * (length + width) * height
2. Deduct standard openings:
   - Door deduction: number_of_doors * 1.9 sq meters
   - Window deduction: number_of_windows * 1.4 sq meters
   - Net paintable area (1 coat) = gross wall area - door deductions - window deductions
3. Multiply by number of coats (standard is 2 coats) to get total required coverage area.
4. Calculate liters needed: total coverage area / coverage rate.
5. Calculate buckets: Each bucket contains 2.5 liters. Buckets = ceiling(liters needed / 2.5).
6. Calculate estimated cost: number of buckets * price per bucket.

If COVERAGE_RATE is not available, default to 10 sq meters per liter.
If PRICE is not available, default to €35 per bucket.

Present your calculation clearly, showing:
- Net area per coat and total coverage area
- Total liters needed
- Bucket count (2.5L buckets)
- Total price for the room
""",
)
