#!/usr/bin/env python3
"""
CHECKPOINT 2: Value Lookup Engine
Takes a card name/set/number and returns aggregated value from multiple sources.
"""
import json
import os
from pathlib import Path

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")


def load_index():
    """Load the unified card index."""
    path = OUTPUT_DIR / "card_index.json"
    if not path.exists():
        print("Run build_price_index.py first")
        return None
    with open(path) as f:
        return json.load(f)


class ValueLookup:
    """Multi-source card value lookup engine."""
    
    def __init__(self):
        self.index = load_index()
        if not self.index:
            raise FileNotFoundError("card_index.json not found")
    
    def search(self, query, limit=5):
        """Search cards by name (fuzzy)."""
        query_lower = query.lower().strip()
        results = []
        
        # Exact name match
        for name, card_ids in self.index.get("by_name", {}).items():
            if query_lower == name:
                for cid in card_ids:
                    card = self.index["cards"].get(cid, {})
                    results.append(card)
        
        # Partial match
        if len(results) < limit:
            for name, card_ids in self.index.get("by_name", {}).items():
                if query_lower in name or name in query_lower:
                    for cid in card_ids:
                        card = self.index["cards"].get(cid, {})
                        if card not in results:
                            results.append(card)
        
        return results[:limit]
    
    def get_set_value(self, set_name):
        """Get total market value for a set."""
        set_key = set_name.lower().strip()
        return self.index.get("sets", {}).get(set_key, None)
    
    def get_card_value(self, card_name, set_name=None):
        """Get value for a specific card."""
        results = self.search(card_name)
        if set_name:
            results = [r for r in results if set_name.lower() in r.get("set_name", "").lower()]
        return results[0] if results else None
    
    def get_top_sets(self, n=10):
        """Get top N sets by market value."""
        sets = list(self.index.get("sets", {}).values())
        sets_with_value = [s for s in sets if s.get("market_value_usd", 0) > 0]
        return sorted(sets_with_value, key=lambda x: x.get("market_value_usd", 0), reverse=True)[:n]
    
    def get_set_cards(self, set_code):
        """Get all cards in a set."""
        card_ids = self.index.get("by_set", {}).get(set_code, [])
        return [self.index["cards"].get(cid, {}) for cid in card_ids]


if __name__ == "__main__":
    print("=" * 60)
    print("CHECKPOINT 2: Value Lookup Engine")
    print("=" * 60)
    
    lookup = ValueLookup()
    
    # Demo searches
    demos = ["Charizard", "Umbreon VMAX", "Pikachu", "Mewtwo"]
    
    for query in demos:
        print(f"\nSearch: '{query}'")
        results = lookup.search(query, limit=3)
        for r in results:
            print(f"  → {r.get('name', '?')} ({r.get('set_name', '?')})")
    
    # Top sets
    print(f"\nTop 5 Most Valuable Sets:")
    for s in lookup.get_top_sets(5):
        print(f"  {s.get('name', '?')}: ${s.get('market_value_usd', 0):,.0f}")
    
    print(f"\n{'='*60}")
    print(f"CHECKPOINT 2 COMPLETE")
    print(f"{'='*60}")
