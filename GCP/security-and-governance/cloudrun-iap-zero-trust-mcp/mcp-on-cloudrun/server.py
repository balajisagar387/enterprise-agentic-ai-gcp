import os
from fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP(
    name="Products MCP Server",
    description="Retail clothing catalog and inventory management MCP server deployed on Cloud Run."
)

# Product catalog data store
PRODUCTS_DB = [
    {
        "id": "prod-101",
        "name": "Heather Gray Hoodie",
        "category": "Tops",
        "price": 54.99,
        "inventory": 8,
        "sizes": ["S", "M", "L", "XL"],
        "description": "Ultra-soft cotton blend hoodie with kangaroo pocket and brushed fleece interior."
    },
    {
        "id": "prod-102",
        "name": "Classic White Tee",
        "category": "Tops",
        "price": 24.50,
        "inventory": 45,
        "sizes": ["XS", "S", "M", "L", "XL"],
        "description": "100% organic combed ring-spun cotton everyday crewneck t-shirt."
    },
    {
        "id": "prod-103",
        "name": "Vintage Denim Jacket",
        "category": "Outerwear",
        "price": 89.00,
        "inventory": 5,
        "sizes": ["M", "L"],
        "description": "Heavyweight stonewashed indigo denim jacket with brass button accents."
    },
    {
        "id": "prod-104",
        "name": "Slim Chino Pants",
        "category": "Bottoms",
        "price": 64.00,
        "inventory": 22,
        "sizes": ["30x30", "32x32", "34x32", "36x34"],
        "description": "Tailored stretch-twill trousers suitable for business-casual and everyday wear."
    },
    {
        "id": "prod-105",
        "name": "Waterproof Trail Parka",
        "category": "Outerwear",
        "price": 149.99,
        "inventory": 3,
        "sizes": ["S", "M", "L"],
        "description": "Seam-sealed breathable waterproof jacket with adjustable hood and thermal lining."
    }
]

@mcp.tool()
def get_products_by_category(category: str) -> list[dict]:
    """Retrieve all products matching the specified retail category (e.g., Tops, Bottoms, Outerwear)."""
    normalized_category = category.strip().lower()
    return [
        product for product in PRODUCTS_DB
        if product["category"].lower() == normalized_category
    ]

@mcp.tool()
def get_product_details(name: str) -> dict:
    """Retrieve complete specifications, pricing, and stock information for a specific product by name."""
    normalized_name = name.strip().lower()
    for product in PRODUCTS_DB:
        if product["name"].lower() == normalized_name:
            return product
    return {"error": f"Product '{name}' not found in catalog."}

@mcp.tool()
def get_low_inventory_products(threshold: int = 10) -> list[dict]:
    """Find products with inventory counts at or below the given threshold (default: 10 units)."""
    return [
        product for product in PRODUCTS_DB
        if product["inventory"] <= threshold
    ]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Run StreamableHTTP transport on Cloud Run standard port
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
