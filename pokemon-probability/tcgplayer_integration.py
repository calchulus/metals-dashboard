#!/usr/bin/env python3
"""
TCGplayer Integration - Bridges TCGplayer API with Pokemon Probability Framework
Fetches live pricing data for EV calculations and box analysis.
"""
import json
import csv
import os
import time

# Try to import the client, fall back to basic mode
try:
    from tcgplayer_client import TCGplayerClient, TCGplayerError
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False

OUTPUT_DIR = "/Users/calvinchu/Desktop/mimo/pokemon-probability"

# TCGplayer Category IDs (Pokemon TCG)
POKEMON_CATEGORY_ID = 1

# Pokemon set group IDs (major sets)
POKEMON_SETS = {
    "Base Set": {"id": None, "code": "BS"},
    "Jungle": {"id": None, "code": "JU"},
    "Fossil": {"id": None, "code": "FO"},
    "Team Rocket": {"id": None, "code": "TR"},
    "Neo Genesis": {"id": None, "code": "N1"},
    "Evolving Skies": {"id": None, "code": "EVS"},
    "Crown Zenith": {"id": None, "code": "CRZ"},
    "Pokemon 151": {"id": None, "code": "MEW"},
    "Prismatic Evolutions": {"id": None, "code": "PRE"},
    "Destined Rivals": {"id": None, "code": "DRI"},
}


class TCGplayerIntegration:
    """Integration layer for TCGplayer API + probability framework."""

    def __init__(self, bearer_token: str = None):
        if HAS_CLIENT and bearer_token:
            self.client = TCGplayerClient(bearer_token=bearer_token)
        else:
            self.client = None
            print("Note: No bearer token provided. Using public endpoints only.")
            print("Get a token at: https://docs.tcgplayer.com/docs/getting-started")

    def get_all_pokemon_sets(self) -> list:
        """Fetch all Pokemon sets from TCGplayer catalog."""
        if not self.client:
            print("Error: Need bearer token for catalog access")
            return []
        try:
            result = self.client.catalog.get_category_groups(POKEMON_CATEGORY_ID)
            groups = result.get("results", [])
            print(f"Found {len(groups)} Pokemon sets")
            return groups
        except TCGplayerError as e:
            print(f"Error fetching sets: {e}")
            return []

    def get_product_prices(self, product_ids: list) -> list:
        """Fetch market prices for products."""
        if not self.client:
            return []
        try:
            result = self.client.pricing.get_product_prices(product_ids)
            return result.get("results", [])
        except TCGplayerError as e:
            print(f"Error fetching prices: {e}")
            return []

    def get_set_prices(self, group_id: int) -> list:
        """Fetch all product prices for a set."""
        if not self.client:
            return []
        try:
            result = self.client.pricing.get_group_prices([group_id])
            return result.get("results", [])
        except TCGplayerError as e:
            print(f"Error fetching set prices: {e}")
            return []

    def calculate_box_ev(self, set_name: str, box_price: float,
                         group_id: int = None) -> dict:
        """Calculate Expected Value for a booster box."""
        if not group_id:
            print("Need group_id for EV calculation")
            return {}

        prices = self.get_set_prices(group_id)
        if not prices:
            return {}

        total_product_value = sum(p.get("marketPrice", 0) or 0 for p in prices)
        total_low = sum(p.get("lowPrice", 0) or 0 for p in prices)
        total_trend = sum(p.get("approvedTop", 0) or 0 for p in prices)

        return {
            "set_name": set_name,
            "box_price": box_price,
            "total_market_value": round(total_product_value, 2),
            "total_low_value": round(total_low, 2),
            "ev_roi": round((total_product_value / box_price - 1) * 100, 1) if box_price > 0 else 0,
            "product_count": len(prices),
            "cards_above_10": len([p for p in prices if (p.get("marketPrice") or 0) > 10]),
            "cards_above_50": len([p for p in prices if (p.get("marketPrice") or 0) > 50]),
            "cards_above_100": len([p for p in prices if (p.get("marketPrice") or 0) > 100]),
        }

    def export_prices_csv(self, product_ids: list, filename: str = "tcgplayer_prices.csv"):
        """Export product prices to CSV."""
        prices = self.get_product_prices(product_ids)
        if not prices:
            return

        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "productId", "productName", "marketPrice", "lowPrice",
                "midPrice", "highPrice", "subTypeName"
            ])
            writer.writeheader()
            for p in prices:
                writer.writerow({
                    "productId": p.get("productId"),
                    "productName": p.get("productName"),
                    "marketPrice": p.get("marketPrice"),
                    "lowPrice": p.get("lowPrice"),
                    "midPrice": p.get("midPrice"),
                    "highPrice": p.get("highPrice"),
                    "subTypeName": p.get("subTypeName"),
                })
        print(f"Exported {len(prices)} prices to {filename}")

    def get_top_sellers(self, category_id: int = 1, limit: int = 25) -> list:
        """Get top selling Pokemon products."""
        if not self.client:
            return []
        try:
            # Use search with sort by market price descending
            body = {
                "filters": [],
                "sort": {"field": "marketPrice", "order": "DESC"},
                "limit": limit
            }
            result = self.client.catalog.search_category(category_id, body)
            product_ids = result.get("results", [])
            if product_ids:
                return self.client.catalog.get_product(product_ids).get("results", [])
            return []
        except TCGplayerError as e:
            print(f"Error: {e}")
            return []


# ============================================================
# DEMO WITHOUT API KEY (uses public data we already have)
# ============================================================
def demo_ev_analysis():
    """Show EV analysis using data we already scraped."""
    print("=" * 60)
    print("Box EV Analysis (from scraped TCGCollector data)")
    print("=" * 60)

    # Load TCGCollector sets data
    sets_file = os.path.join(OUTPUT_DIR, "tcgcollector_sets.csv")
    if not os.path.exists(sets_file):
        print("Run save_tcgcollector_data.py first")
        return

    with open(sets_file) as f:
        reader = csv.DictReader(f)
        sets = list(reader)

    # Box price estimates (market averages)
    box_prices = {
        "Evolving Skies": 160,
        "Crown Zenith": 110,
        "Pokemon 151": 115,
        "Prismatic Evolutions": 130,
        "Destined Rivals": 115,
        "Journey Together": 110,
        "Surging Sparks": 110,
        "Stellar Crown": 100,
        "Twilight Masquerade": 110,
        "Temporal Forces": 110,
        "Obsidian Flames": 110,
        "Paldea Evolved": 110,
        "Scarlet & Violet": 100,
        "Base Set": 400,
        "Jungle": 300,
        "Fossil": 300,
        "Neo Genesis": 350,
    }

    print(f"\n{'Set':<28} {'Set Value':<12} {'Box Price':<12} {'ROI':<10} {'Verdict'}")
    print(f"{'─'*28} {'─'*12} {'─'*12} {'─'*10} {'─'*15}")

    for s in sets:
        name = s["name"]
        value = float(s.get("price", 0))
        box = box_prices.get(name, 0)
        if box > 0 and value > 0:
            roi = (value / box - 1) * 100
            verdict = "PROFIT" if roi > 0 else "LOSS"
            color = "\033[92m" if roi > 0 else "\033[91m"
            reset = "\033[0m"
            print(f"{name:<28} ${value:>9,.0f}  ${box:>9,.0f}  {color}{roi:>7.1f}%{reset}  {verdict}")

    print(f"\n{'─'*60}")
    print("Note: Set value = sum of individual card market prices")
    print("Actual ROI depends on pull rates and card conditions")


if __name__ == "__main__":
    print("=" * 60)
    print("TCGplayer Integration Module")
    print("=" * 60)

    # Check for API key
    api_key = os.environ.get("TCGPLAYER_API_KEY")

    if api_key:
        print(f"\nFound TCGplayer API key in environment")
        integration = TCGplayerIntegration(bearer_token=api_key)

        # Example: Get top Pokemon products
        print("\nFetching top Pokemon products...")
        top = integration.get_top_sellers(limit=10)
        for p in top[:5]:
            print(f"  {p.get('productName', 'Unknown')}")
    else:
        print("\nNo TCGplayer API key found.")
        print("Set TCGPLAYER_API_KEY environment variable to use live data.")
        print("Get a key at: https://docs.tcgplayer.com/docs/getting-started")

    # Always show EV analysis from scraped data
    print()
    demo_ev_analysis()
