#!/usr/bin/env python3
"""
TCGdex API Scraper - Complete Pokemon TCG Database
API: https://tcgdex.dev | Base: https://api.tcgdex.net/v2/en
"""
import json
import csv
import time
import urllib.request
import urllib.error

BASE = "https://api.tcgdex.net/v2/en"
OUTPUT_DIR = "/Users/calvinchu/Desktop/mimo/pokemon-probability"

def api_get(path, retries=3):
    url = f"{BASE}{path}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PokemonTCGScraper/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
    return None


def scrape_all_sets():
    """Fetch complete set list."""
    print("Fetching all sets...")
    data = api_get("/sets")
    if not data:
        print("Failed to fetch sets")
        return []
    print(f"Found {len(data)} sets")
    return data


def scrape_set_cards(set_id):
    """Fetch all cards in a set."""
    data = api_get(f"/sets/{set_id}")
    if not data or "cards" not in data:
        return []
    return data["cards"]


def scrape_card_detail(card_id):
    """Fetch detailed card info."""
    return api_get(f"/cards/{card_id}")


def scrape_all():
    """Main scraping pipeline."""
    # 1. Get all sets
    sets = scrape_all_sets()
    if not sets:
        return

    # Save sets
    sets_file = f"{OUTPUT_DIR}/tcgdex_sets.json"
    with open(sets_file, "w") as f:
        json.dump(sets, f, indent=2)
    print(f"Saved {len(sets)} sets to tcgdex_sets.json")

    # Save sets CSV
    with open(f"{OUTPUT_DIR}/tcgdex_sets.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "total_cards", "official_cards", "logo", "symbol"])
        writer.writeheader()
        for s in sets:
            card_count = s.get("cardCount", {})
            writer.writerow({
                "id": s.get("id", ""),
                "name": s.get("name", ""),
                "total_cards": card_count.get("total", 0),
                "official_cards": card_count.get("official", 0),
                "logo": s.get("logo", ""),
                "symbol": s.get("symbol", ""),
            })
    print(f"Saved sets CSV")

    # 2. Get cards for each set (sample first 10 sets for demo)
    all_cards = []
    sets_to_scrape = sets[:10]  # First 10 sets for demo

    print(f"\nScraping cards for {len(sets_to_scrape)} sets (rate-limited)...")
    for i, s in enumerate(sets_to_scrape):
        set_id = s["id"]
        set_name = s["name"]
        print(f"  [{i+1}/{len(sets_to_scrape)}] {set_name}...", end=" ", flush=True)

        cards = scrape_set_cards(set_id)
        if cards:
            for c in cards:
                card_data = {
                    "set_id": set_id,
                    "set_name": set_name,
                    "card_id": c.get("id", ""),
                    "local_id": c.get("localId", ""),
                    "name": c.get("name", ""),
                    "image": c.get("image", ""),
                    "illustrator": c.get("illustrator", ""),
                    "category": c.get("category", ""),
                    "supertype": c.get("supertype", ""),
                    "hp": c.get("hp", ""),
                    "types": ",".join(c.get("types", [])) if isinstance(c.get("types"), list) else c.get("types", ""),
                    "stage": c.get("stage", ""),
                    "evolvesFrom": c.get("evolvesFrom", ""),
                    "artist": c.get("artist", ""),
                    "rarity": c.get("rarity", ""),
                    "illustration": c.get("illustration", ""),
                }
                # TCGdex doesn't include prices in basic card list
                # Prices would need to come from another source
                all_cards.append(card_data)
            print(f"{len(cards)} cards")
        else:
            print("no cards")

        time.sleep(0.5)  # Rate limit

    # Save cards
    if all_cards:
        cards_file = f"{OUTPUT_DIR}/tcgdex_cards.json"
        with open(cards_file, "w") as f:
            json.dump(all_cards, f, indent=2)

        with open(f"{OUTPUT_DIR}/tcgdex_cards.csv", "w", newline="") as f:
            fields = ["set_id", "set_name", "card_id", "local_id", "name", "category", "supertype",
                      "hp", "types", "stage", "evolvesFrom", "rarity", "illustrator", "image"]
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_cards)
        print(f"\nSaved {len(all_cards)} cards to tcgdex_cards.json/csv")


def get_card_detail_sample(card_id):
    """Get full detail for a single card (has more fields)."""
    data = api_get(f"/cards/{card_id}")
    if not data:
        return None
    return {
        "id": data.get("id", ""),
        "name": data.get("name", ""),
        "category": data.get("category", ""),
        "supertype": data.get("supertype", ""),
        "hp": data.get("hp", ""),
        "types": data.get("types", []),
        "stage": data.get("stage", ""),
        "evolvesFrom": data.get("evolvesFrom", ""),
        "attacks": data.get("attacks", []),
        "weaknesses": data.get("weaknesses", []),
        "resistances": data.get("resistances", []),
        "retreatCost": data.get("retreatCost", []),
        "convertedRetreatCost": data.get("convertedRetreatCost", 0),
        "artist": data.get("artist", ""),
        "rarity": data.get("rarity", ""),
        "illustration": data.get("illustration", ""),
        "flavorText": data.get("flavorText", ""),
        "nationalPokedexNumbers": data.get("nationalPokedexNumbers", []),
        "legalities": data.get("legalities", {}),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("TCGdex API Scraper")
    print("API: https://api.tcgdex.net/v2/en")
    print("=" * 60)

    scrape_all()

    # Show a sample card detail
    print("\n" + "=" * 60)
    print("Sample Card Detail (Charizard)")
    print("=" * 60)
    detail = get_card_detail_sample("base1-4")
    if detail:
        for k, v in detail.items():
            if k == "attacks":
                print(f"  {k}: {len(v)} attacks")
            elif k == "weaknesses":
                print(f"  {k}: {v}")
            else:
                print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  tcgdex_sets.json    - All sets (JSON)")
    print(f"  tcgdex_sets.csv     - All sets (CSV)")
    print(f"  tcgdex_cards.json   - Cards (JSON)")
    print(f"  tcgdex_cards.csv    - Cards (CSV)")
