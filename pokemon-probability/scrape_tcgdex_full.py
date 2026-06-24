#!/usr/bin/env python3
"""
TCGdex Full Scraper - Fetches ALL cards from ALL sets
Uses api.tcgdex.net/v2/en which works via webfetch
Rate-limited with exponential backoff
"""
import json
import csv
import time
import ssl
import urllib.request
import urllib.error

OUTPUT_DIR = "/Users/calvinchu/Desktop/mimo/pokemon-probability"
BASE = "https://api.tcgdex.net/v2/en"


def create_ssl_context():
    """Create SSL context that works with various cert stores."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_json(url, retries=5, base_delay=1.0):
    """Fetch JSON with exponential backoff retry."""
    ctx = create_ssl_context()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "PokemonTCGScraper/2.0",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                delay = base_delay * (2 ** attempt)
                print(f"    Rate limited, waiting {delay:.0f}s...")
                time.sleep(delay)
            elif e.code == 404:
                return None
            else:
                time.sleep(base_delay)
        except Exception as e:
            time.sleep(base_delay)
    return None


def fetch_all_sets():
    """Fetch complete set list."""
    print("Fetching all sets...")
    data = fetch_json(f"{BASE}/sets")
    if data:
        print(f"Found {len(data)} sets")
    return data or []


def fetch_set_cards(set_id):
    """Fetch all cards in a set."""
    data = fetch_json(f"{BASE}/sets/{set_id}")
    if data and "cards" in data:
        return data["cards"], data
    return [], {}


def fetch_card_detail(card_id):
    """Fetch detailed card info (attacks, weaknesses, etc.)."""
    return fetch_json(f"{BASE}/cards/{card_id}")


def scrape_all(max_sets=None, detail_sample=5):
    """Main scraper pipeline."""
    # 1. Get all sets
    sets = fetch_all_sets()
    if not sets:
        print("Failed to fetch sets")
        return

    # Save sets
    with open(f"{OUTPUT_DIR}/tcgdex_all_sets.json", "w") as f:
        json.dump(sets, f, indent=2)

    sets_to_scrape = sets[:max_sets] if max_sets else sets
    print(f"\nScraping cards for {len(sets_to_scrape)} sets...")

    all_cards = []
    total_expected = sum(s.get("cardCount", {}).get("total", 0) for s in sets_to_scrape)

    for i, s in enumerate(sets_to_scrape):
        set_id = s["id"]
        set_name = s["name"]
        expected = s.get("cardCount", {}).get("total", 0)
        print(f"  [{i+1}/{len(sets_to_scrape)}] {set_name} ({expected} cards)...", end=" ", flush=True)

        cards, set_data = fetch_set_cards(set_id)
        if cards:
            for c in cards:
                card = {
                    "set_id": set_id,
                    "set_name": set_name,
                    "card_id": c.get("id", ""),
                    "local_id": c.get("localId", ""),
                    "name": c.get("name", ""),
                    "image": c.get("image", ""),
                }
                all_cards.append(card)
            print(f"{len(cards)} cards")
        else:
            print("no cards")

        time.sleep(0.3)  # Rate limit

    # 2. Fetch detail for sample cards
    if detail_sample > 0 and all_cards:
        print(f"\nFetching details for {detail_sample} sample cards...")
        sample_ids = [c["card_id"] for c in all_cards[:detail_sample]]
        for cid in sample_ids:
            detail = fetch_card_detail(cid)
            if detail:
                # Merge detail into existing card
                for c in all_cards:
                    if c["card_id"] == cid:
                        c["types"] = detail.get("types", [])
                        c["hp"] = detail.get("hp", "")
                        c["stage"] = detail.get("stage", "")
                        c["evolvesFrom"] = detail.get("evolvesFrom", "")
                        c["rarity"] = detail.get("rarity", "")
                        c["artist"] = detail.get("artist", "")
                        c["attacks"] = [a.get("name", "") for a in detail.get("attacks", [])]
                        c["weaknesses"] = detail.get("weaknesses", [])
                        c["retreatCost"] = detail.get("retreatCost", [])
                        break
            time.sleep(0.5)

    # 3. Save everything
    # JSON
    with open(f"{OUTPUT_DIR}/tcgdex_all_cards.json", "w") as f:
        json.dump(all_cards, f, indent=2)

    # CSV
    fields = ["set_id", "set_name", "card_id", "local_id", "name",
              "types", "hp", "stage", "rarity", "artist", "image"]
    with open(f"{OUTPUT_DIR}/tcgdex_all_cards.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_cards)

    # Summary
    total_cards = len(all_cards)
    sets_with_cards = len(set(c["set_id"] for c in all_cards))
    unique_names = len(set(c["name"] for c in all_cards))

    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Sets scraped: {sets_with_cards}")
    print(f"Total cards: {total_cards}")
    print(f"Unique card names: {unique_names}")
    print(f"Expected total: {total_expected}")
    print(f"\nFiles saved:")
    print(f"  tcgdex_all_sets.json     - {len(sets)} sets")
    print(f"  tcgdex_all_cards.json    - {total_cards} cards (JSON)")
    print(f"  tcgdex_all_cards.csv     - {total_cards} cards (CSV)")


if __name__ == "__main__":
    print("=" * 60)
    print("TCGdex Full Scraper")
    print("API: api.tcgdex.net/v2/en")
    print("=" * 60)
    print()

    # Scrape all sets (no limit)
    scrape_all(max_sets=None, detail_sample=10)
