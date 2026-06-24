#!/usr/bin/env python3
"""
TCGCollector Complete Scraper
Scrapes: Cards (with rarity/price) + Sets/Boxes (with market value/card count)
Rate-limited: 2s delay between requests
"""
import re
import csv
import time
import urllib.request
import urllib.error

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            print(f"    Retry {attempt+1}: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    return None


# ============================================================
# SETS SCRAPER
# ============================================================
def scrape_sets():
    """Scrape all sets with market prices and card counts."""
    url = "https://www.tcgcollector.com/sets/intl?releaseDateOrder=newToOld&displayAs=list"
    print("Fetching sets list...")
    html = fetch(url)
    if not html:
        print("Failed to fetch sets")
        return []

    sets = []
    # Pattern: Set name, code, release date, market price, card count
    # Format: [Set Name](/sets/ID/slug "Set Name")CODE ... $PRICE ... COUNT/TOTAL
    pattern = r'\[([^\]]+)\]\(/sets/(\d+)/([^"?]+)[^"]*"[^"]*"\)\s*(\w+).*?\$([0-9,]+\.?\d*).*?(\d+)/(\d+)'
    matches = re.findall(pattern, html, re.DOTALL)

    for m in matches:
        name, set_id, slug, code, price, collected, total = m
        sets.append({
            "name": name.strip(),
            "id": set_id,
            "code": code,
            "slug": slug,
            "market_price": float(price.replace(",", "")),
            "cards_collected": int(collected),
            "cards_total": int(total),
            "url": f"https://www.tcgcollector.com/sets/intl/{slug}",
        })

    # Fallback: simpler pattern
    if not sets:
        # Match set links with prices
        link_pattern = r'/sets/(\d+)/([^"?]+)\?[^"]*"[^"]*"[^>]*>([^<]+)</a>\s*(\w+)'
        price_pattern = r'\$([0-9,]+\.?\d*)'
        count_pattern = r'(\d+)/(\d+)'

        links = re.findall(link_pattern, html)
        prices = re.findall(price_pattern, html)
        counts = re.findall(count_pattern, html)

        for i, (set_id, slug, name, code) in enumerate(links):
            sets.append({
                "name": name.strip(),
                "id": set_id,
                "code": code,
                "slug": slug,
                "market_price": float(prices[i].replace(",", "")) if i < len(prices) else 0,
                "cards_total": int(counts[i][1]) if i < len(counts) else 0,
                "url": f"https://www.tcgcollector.com/sets/intl/{slug}",
            })

    print(f"Found {len(sets)} sets")
    return sets


# ============================================================
# CARDS SCRAPER
# ============================================================
def scrape_cards(max_pages=5):
    """Scrape cards with name, set, number, rarity, price."""
    all_cards = []
    seen = set()

    print(f"\nScraping cards (max {max_pages} pages, 120 cards/page)...")
    for page in range(1, max_pages + 1):
        url = f"https://www.tcgcollector.com/cards/intl?releaseDateOrder=newToOld&displayAs=list&page={page}"
        print(f"  Page {page}/{max_pages}...", end=" ", flush=True)

        html = fetch(url)
        if not html:
            print("FAILED")
            continue

        # Parse card rows
        # Pattern: [CardName](/cards/ID/slug "CardName (Set Number/Total)") ... [Set](/sets/...) [CODE] ... NUMBER ... RARITY ... $PRICE
        card_pattern = r'\[([^\]]+)\]\(/cards/(\d+)/([^"]+)"[^"]*"[^"]*"\)'
        set_pattern = r'\[([^\]]+)\]\(/sets/\d+/([^"?]+)[^"]*"[^"]*"\)\s*\[(\w+)\]'
        rarity_pattern = r'alt="(Common|Uncommon|Rare|Double Rare|Illustration Rare|Special Illustration Rare|Ultra Rare|Hyper Rare|Secret Rare|Amazing Rare|Promo|Rare Holo|Rare Holo EX|Rare Prime|Rare Lv.X|Rare LEGEND|Rare Pokémon SP)"'
        price_pattern = r'\$([0-9,]+\.?\d*)'
        number_pattern = r'(\d{3}/\d{3})'

        cards_raw = re.findall(card_pattern, html)
        sets_raw = re.findall(set_pattern, html)
        rarities = re.findall(rarity_pattern, html)
        prices = re.findall(price_pattern, html)
        numbers = re.findall(number_pattern, html)

        new = 0
        for i, (name, card_id, slug) in enumerate(cards_raw):
            key = (name, card_id)
            if key in seen:
                continue
            seen.add(key)

            card = {
                "name": name,
                "card_id": card_id,
                "slug": slug,
            }

            # Match set info
            if i < len(sets_raw):
                card["set_name"] = sets_raw[i][0]
                card["set_code"] = sets_raw[i][2]

            # Match number
            if i < len(numbers):
                card["number"] = numbers[i]

            # Match rarity
            if i < len(rarities):
                card["rarity"] = rarities[i]

            # Match price
            if i < len(prices):
                try:
                    card["price"] = float(prices[i].replace(",", ""))
                except ValueError:
                    card["price"] = 0.0
            else:
                card["price"] = 0.0

            all_cards.append(card)
            new += 1

        print(f"{len(cards_raw)} found, {new} new (total: {len(all_cards)})")
        time.sleep(2)

    return all_cards


# ============================================================
# SAVE FUNCTIONS
# ============================================================
def save_sets_csv(sets, filename="tcgcollector_sets.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "code", "market_price", "cards_total", "url"])
        writer.writeheader()
        for s in sets:
            writer.writerow({
                "name": s["name"],
                "code": s.get("code", ""),
                "market_price": s.get("market_price", 0),
                "cards_total": s.get("cards_total", 0),
                "url": s.get("url", ""),
            })
    print(f"Saved {len(sets)} sets to {filename}")


def save_cards_csv(cards, filename="tcgcollector_cards.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "set_name", "set_code", "number", "rarity", "price"])
        writer.writeheader()
        for c in cards:
            writer.writerow({
                "name": c.get("name", ""),
                "set_name": c.get("set_name", ""),
                "set_code": c.get("set_code", ""),
                "number": c.get("number", ""),
                "rarity": c.get("rarity", ""),
                "price": c.get("price", 0),
            })
    print(f"Saved {len(cards)} cards to {filename}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("TCGCollector Scraper - Cards + Sets/Boxes")
    print("=" * 60)

    # 1. Scrape sets (single page, all sets visible)
    sets = scrape_sets()
    save_sets_csv(sets)

    # 2. Scrape cards (paginated, rate-limited)
    cards = scrape_cards(max_pages=10)
    save_cards_csv(cards)

    # Summary
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Sets scraped: {len(sets)}")
    print(f"Cards scraped: {len(cards)}")

    # Rarity breakdown
    rarity_counts = {}
    for c in cards:
        r = c.get("rarity", "Unknown")
        rarity_counts[r] = rarity_counts.get(r, 0) + 1
    print(f"\nRarity breakdown:")
    for r, n in sorted(rarity_counts.items(), key=lambda x: -x[1]):
        print(f"  {r}: {n}")

    # Price stats
    prices = [c.get("price", 0) for c in cards if c.get("price", 0) > 0]
    if prices:
        print(f"\nPrice stats ({len(prices)} cards with price):")
        print(f"  Total value: ${sum(prices):,.2f}")
        print(f"  Average: ${sum(prices)/len(prices):.2f}")
        print(f"  Median: ${sorted(prices)[len(prices)//2]:.2f}")
        print(f"  Max: ${max(prices):.2f}")

    # Top sets by value
    if sets:
        print(f"\nTop 10 sets by market value:")
        for s in sorted(sets, key=lambda x: x.get("market_price", 0), reverse=True)[:10]:
            print(f"  {s['name']}: ${s.get('market_price', 0):,.0f}")
