#!/usr/bin/env python3
"""
CHECKPOINT 1: Price Database Index
Merges all scraped pricing data into a single searchable JSON index.
Sources: TCGCollector, Limitless TCG, TCGdex (structure only)
"""
import json
import csv
import os
import re
from pathlib import Path
from collections import defaultdict

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")


def load_tcgcollector_sets():
    """Load TCGCollector set data with market values."""
    path = OUTPUT_DIR / "tcgcollector_sets.csv"
    if not path.exists():
        print("  [SKIP] tcgcollector_sets.csv not found")
        return {}
    
    sets = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get("name", "").strip().lower()
            sets[key] = {
                "name": row.get("name", ""),
                "code": row.get("code", ""),
                "era": row.get("era", ""),
                "cards": int(row.get("cards", 0)),
                "market_value_usd": float(row.get("price", 0)),
                "source": "tcgcollector",
            }
    return sets


def load_limitless_sets():
    """Load Limitless TCG set data with USD/EUR values."""
    path = OUTPUT_DIR / "limitless_sets.csv"
    if not path.exists():
        print("  [SKIP] limitless_sets.csv not found")
        return {}
    
    sets = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get("name", "").strip().lower()
            sets[key] = {
                "name": row.get("name", ""),
                "code": row.get("code", ""),
                "cards": int(row.get("cards", 0)),
                "market_value_usd": float(row.get("usd", 0)),
                "market_value_eur": float(row.get("eur", 0)),
                "release_date": row.get("date", ""),
                "source": "limitless",
            }
    return sets


def load_tcgdex_cards():
    """Load TCGdex card data (structure, no prices)."""
    path = OUTPUT_DIR / "tcgdex_all_cards.json"
    if not path.exists():
        print("  [SKIP] tcgdex_all_cards.json not found")
        return {}
    
    with open(path) as f:
        cards = json.load(f)
    
    # Index by card_id for quick lookup
    index = {}
    for card in cards:
        card_id = card.get("card_id", "")
        if card_id:
            index[card_id] = {
                "set_id": card.get("set_id", ""),
                "set_name": card.get("set_name", ""),
                "local_id": card.get("local_id", ""),
                "name": card.get("name", ""),
                "image": card.get("image", ""),
            }
    return index


def load_psa_data():
    """Load PSA population data."""
    path = OUTPUT_DIR / "psa_population.json"
    if not path.exists():
        print("  [SKIP] psa_population.json not found")
        return {}
    
    with open(path) as f:
        data = json.load(f)
    
    # Index by card name + set
    index = {}
    for key, card in data.items():
        search_key = f"{card.get('card_name', '').lower()}_{card.get('set_name', '').lower()}"
        index[search_key] = card
    return index


def build_card_index(tcgdex_cards, tcgcollector_sets, limitless_sets):
    """Build unified card index with fuzzy search capability."""
    index = {
        "cards": {},      # card_id → card data
        "by_name": {},    # name_lower → [card_ids]
        "by_set": {},     # set_code → [card_ids]
        "sets": {},       # set_key → set data
        "last_updated": "",
    }
    
    # Index sets from both sources
    for key, data in tcgcollector_sets.items():
        index["sets"][key] = data
    for key, data in limitless_sets.items():
        if key not in index["sets"]:
            index["sets"][key] = data
        else:
            # Merge: take the richer data
            for k, v in data.items():
                if k not in index["sets"][key] or index["sets"][key][k] == "":
                    index["sets"][key][k] = v
    
    # Index cards from TCGdex
    for card_id, card in tcgdex_cards.items():
        index["cards"][card_id] = card
        
        # Index by name
        name_lower = card.get("name", "").lower()
        if name_lower not in index["by_name"]:
            index["by_name"][name_lower] = []
        index["by_name"][name_lower].append(card_id)
        
        # Index by set
        set_id = card.get("set_id", "")
        if set_id not in index["by_set"]:
            index["by_set"][set_id] = []
        index["by_set"][set_id].append(card_id)
    
    return index


def fuzzy_search(query, index, limit=10):
    """Fuzzy search cards by name."""
    query_lower = query.lower().strip()
    results = []
    
    # Exact match
    if query_lower in index.get("by_name", {}):
        for card_id in index["by_name"][query_lower]:
            results.append(index["cards"].get(card_id, {}))
    
    # Partial match
    for name, card_ids in index.get("by_name", {}).items():
        if query_lower in name or name in query_lower:
            for card_id in card_ids:
                card = index["cards"].get(card_id, {})
                if card not in results:
                    results.append(card)
    
    return results[:limit]


def save_index(index):
    """Save the unified index to JSON."""
    path = OUTPUT_DIR / "card_index.json"
    with open(path, "w") as f:
        json.dump(index, f, indent=2)
    
    stats = {
        "total_cards": len(index.get("cards", {})),
        "unique_names": len(index.get("by_name", {})),
        "total_sets": len(index.get("sets", {})),
        "indexed_at": index.get("last_updated", ""),
    }
    return stats


def print_summary(stats):
    """Print build summary."""
    print(f"\n{'='*60}")
    print(f"CHECKPOINT 1 COMPLETE: Price Database Index")
    print(f"{'='*60}")
    print(f"  Total cards indexed: {stats['total_cards']:,}")
    print(f"  Unique card names: {stats['unique_names']:,}")
    print(f"  Sets with pricing: {stats['total_sets']}")
    print(f"\n  Files created:")
    print(f"    card_index.json — Unified searchable index")
    print(f"\n  Next: Checkpoint 2 — Value Lookup Engine")


if __name__ == "__main__":
    print("Building Price Database Index...")
    
    # Load all sources
    tcgcollector = load_tcgcollector_sets()
    limitless = load_limitless_sets()
    tcgdex = load_tcgdex_cards()
    
    print(f"  Loaded: {len(tcgcollector)} TCGCollector sets")
    print(f"  Loaded: {len(limitless)} Limitless sets")
    print(f"  Loaded: {len(tcgdex)} TCGdex cards")
    
    # Build unified index
    index = build_card_index(tcgdex, tcgcollector, limitless)
    
    # Add metadata
    from datetime import datetime
    index["last_updated"] = datetime.now().isoformat()
    
    # Save
    stats = save_index(index)
    print_summary(stats)
