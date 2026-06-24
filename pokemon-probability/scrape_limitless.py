#!/usr/bin/env python3
"""
Limitless TCG Scraper - Extracts all Pokemon card data
Source: https://limitlesstcg.com/cards
Data: Card names, numbers, set codes, prices (USD/EUR), rarity, images
"""
import re
import json
import csv
import time
import urllib.request
import urllib.error

OUTPUT_DIR = "/Users/calvinchu/Desktop/mimo/pokemon-probability"

# All set codes from the Limitless cards page
SET_CODES = [
    # Mega Evolution
    "CRI", "POR", "ASC", "PFL", "MEG", "MEE", "MEP",
    # Scarlet & Violet
    "BLK", "WHT", "DRI", "JTG", "PRE", "SSP", "SCR", "SFA", "TWM",
    "TEF", "PAF", "PAR", "MEW", "OBF", "PAL", "SVI", "SVE", "SVP",
    # Sword & Shield
    "CRZ", "SIT", "LOR", "PGO", "ASR", "BRS", "FST", "CEL", "EVS",
    "CRE", "BST", "SHF", "VIV", "CPA", "DAA", "RCL", "SSH", "SP",
    # Sun & Moon
    "CEC", "HIF", "UNM", "UNB", "DET", "TEU", "LOT", "DRM", "CES",
    "FLI", "UPR", "CIN", "SLG", "BUS", "GRI", "SUM", "SMP",
    # XY
    "EVO", "STS", "FCO", "GEN", "BKP", "BKT", "AOR", "ROS", "DCR",
    "PRC", "PHF", "FFI", "FLF", "XY", "KSS", "XYP",
    # Black & White
    "LTR", "PLB", "PLF", "PLS", "BCR", "DRV", "DRX", "DEX", "NXD",
    "NVI", "EPO", "BLW", "BWP",
    # HeartGold & SoulSilver
    "CL", "TM", "UD", "UL", "HS", "HSP",
    # Diamond & Pearl / Platinum
    "RM", "AR", "SV", "RR", "P9", "PL", "SF", "P8", "LA", "MD",
    "P7", "GE", "SW", "P6", "MT", "DP", "DPP",
    # EX
    "P5", "PK", "DF", "CG", "P4", "HP", "P3", "LM", "DS", "UF",
    "P2", "EM", "UG", "TRR", "FRLG", "DK", "SS", "RS", "TL",
    "HL", "EX", "GR", "FL", "DX",
    # Neo
    "N4", "N3", "N2", "N1", "SI",
    # Base / Gym / E-Card / LC
    "BS", "JU", "FO", "TR", "G1", "G2", "EC1", "EC2", "EC3", "LC",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url, retries=3, delay=2):
    """Fetch URL with retries and rate limiting."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    return None


def parse_set_page(html, set_code):
    """Parse a set page to extract card data."""
    cards = []

    # Pattern: Card images with links to card detail pages
    # Format: /cards/SET_CODE/NUMBER
    card_pattern = r'/cards/' + re.escape(set_code) + r'/(\d+)'
    card_numbers = re.findall(card_pattern, html)
    card_numbers = sorted(set(int(n) for n in card_numbers))

    # Extract set name and date from page header
    set_name_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    set_name = set_name_match.group(1).strip() if set_name_match else set_code

    date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{2,4})', html)
    release_date = date_match.group(1) if date_match else ""

    # Extract total set value
    usd_match = re.search(r'\$([0-9,]+\.?\d*)', html)
    eur_match = re.search(r'([0-9,]+\.?\d*)€', html)
    total_usd = usd_match.group(1).replace(",", "") if usd_match else "0"
    total_eur = eur_match.group(1).replace(",", "") if eur_match else "0"

    # Card count from page
    count_match = re.search(r'(\d+)\s+Cards', html)
    card_count = int(count_match.group(1)) if count_match else len(card_numbers)

    # Extract card names from alt text or title attributes
    # Pattern: alt="CardName" or title="CardName (Set Number)"
    name_pattern = r'(?:alt|title)="([^"]*(?:' + re.escape(set_code) + r')[^"]*)"'
    names_raw = re.findall(name_pattern, html)

    # Better pattern: extract from card links with text
    card_link_pattern = r'/cards/' + re.escape(set_code) + r'/(\d+)"[^>]*>([^<]*)</a>'
    card_links = re.findall(card_link_pattern, html)

    # Extract prices from card entries
    # Price pattern near card links
    price_pattern = r'/cards/' + re.escape(set_code) + r'/(\d+)[^"]*"[^>]*>.*?\$([0-9,]+\.?\d*)'
    prices_raw = re.findall(price_pattern, html, re.DOTALL)

    for num in card_numbers:
        card = {
            "set_code": set_code,
            "set_name": set_name,
            "number": num,
            "card_id": f"{set_code}-{num:03d}",
            "image_url": f"https://limitlesstcg.nyc3.cdn.digitaloceanspaces.com/tpci/{set_code}/{set_code}_{num:03d}_R_EN_SM.png",
            "detail_url": f"https://limitlesstcg.com/cards/{set_code}/{num}",
        }

        # Try to find name for this card number
        for link_num, link_name in card_links:
            if int(link_num) == num and link_name.strip():
                card["name"] = link_name.strip()
                break
        else:
            card["name"] = f"Card {num}"

        # Try to find price
        for price_num, price_val in prices_raw:
            if int(price_num) == num:
                card["price_usd"] = float(price_val.replace(",", ""))
                break
        else:
            card["price_usd"] = 0.0

        cards.append(card)

    return {
        "set_code": set_code,
        "set_name": set_name,
        "release_date": release_date,
        "card_count": card_count,
        "total_usd": float(total_usd),
        "total_eur": float(total_eur),
        "cards": cards,
    }


def scrape_set(set_code, delay=2):
    """Scrape a single set from Limitless TCG."""
    url = f"https://limitlesstcg.com/cards/{set_code}"
    print(f"  Fetching {set_code}...", end=" ", flush=True)

    html = fetch(url)
    if not html:
        print("FAILED")
        return None

    data = parse_set_page(html, set_code)
    print(f"{len(data['cards'])} cards (${data['total_usd']:,.2f})")
    time.sleep(delay)
    return data


def scrape_all_sets(max_sets=None):
    """Scrape all sets from Limitless TCG."""
    all_data = []
    sets_to_scrape = SET_CODES[:max_sets] if max_sets else SET_CODES

    print(f"Scraping {len(sets_to_scrape)} sets from Limitless TCG...")
    print(f"Rate limit: 2s delay between requests\n")

    for i, code in enumerate(sets_to_scrape):
        print(f"[{i+1}/{len(sets_to_scrape)}]", end=" ")
        data = scrape_set(code)
        if data:
            all_data.append(data)

    return all_data


def save_results(all_data):
    """Save scraped data to CSV and JSON."""
    # Save full JSON
    json_path = f"{OUTPUT_DIR}/limitless_cards.json"
    with open(json_path, "w") as f:
        json.dump(all_data, f, indent=2)
    print(f"\nSaved full data to limitless_cards.json")

    # Save sets CSV
    sets_path = f"{OUTPUT_DIR}/limitless_sets.csv"
    with open(sets_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "set_code", "set_name", "release_date", "card_count",
            "total_usd", "total_eur"
        ])
        writer.writeheader()
        for s in all_data:
            writer.writerow({
                "set_code": s["set_code"],
                "set_name": s["set_name"],
                "release_date": s["release_date"],
                "card_count": s["card_count"],
                "total_usd": s["total_usd"],
                "total_eur": s["total_eur"],
            })
    print(f"Saved {len(all_data)} sets to limitless_sets.csv")

    # Save cards CSV
    all_cards = []
    for s in all_data:
        for c in s["cards"]:
            all_cards.append(c)

    cards_path = f"{OUTPUT_DIR}/limitless_cards.csv"
    with open(cards_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "set_code", "set_name", "number", "card_id", "name",
            "price_usd", "image_url", "detail_url"
        ])
        writer.writeheader()
        writer.writerows(all_cards)
    print(f"Saved {len(all_cards)} cards to limitless_cards.csv")


if __name__ == "__main__":
    print("=" * 60)
    print("Limitless TCG Scraper")
    print("Source: https://limitlesstcg.com/cards")
    print("=" * 60)

    # Scrape first 10 sets as demo (full run takes ~6 min)
    all_data = scrape_all_sets(max_sets=10)

    if all_data:
        save_results(all_data)

        # Summary
        total_cards = sum(len(s["cards"]) for s in all_data)
        total_value = sum(s["total_usd"] for s in all_data)
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Sets scraped: {len(all_data)}")
        print(f"Total cards: {total_cards}")
        print(f"Total set value: ${total_value:,.2f}")
        print(f"\nTop sets by value:")
        for s in sorted(all_data, key=lambda x: x["total_usd"], reverse=True)[:5]:
            print(f"  {s['set_name']}: ${s['total_usd']:,.2f} ({len(s['cards'])} cards)")
