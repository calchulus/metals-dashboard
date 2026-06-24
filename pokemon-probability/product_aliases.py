#!/usr/bin/env python3
"""
PRODUCT NAME ALIAS SYSTEM
Same product = many names across languages, regions, abbreviations
Maps: "CBB2C" = "Gem Pack Vol. 2 Eevee" = "Chinese Gem Pack Vol.2" etc.
"""
import json
import re
from pathlib import Path

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")


# ============================================================
# PRODUCT ALIAS DATABASE
# ============================================================
# Each product has a canonical ID and multiple name variants
PRODUCT_ALIASES = {
    # Chinese Gem Pack Series
    "gem_pack_vol1": {
        "canonical": "Pokemon Chinese Gem Pack Vol.1",
        "code": "CBB1C",
        "set_id": "CBB1C",
        "aliases": [
            "Gem Pack Vol.1", "Gem Pack Vol.1 Eevee", "Gem Pack 1",
            "Chinese Gem Pack Vol.1", "Chinese Gem Pack Vol.1 Eevee",
            "CBB1C", "Gem Pack Vol. 1", "Gem Pack Vol. 1 Eevee",
            "Pokemon TCG Simplified Chinese Gem Pack Vol.1",
            "Pokemon TCG Simplified Chinese Gem Pack Vol.1 Eevee",
            "Gem Pack Vol.1 Eevee Booster Box",
            "Chinese Gem Pack Eevee Vol.1",
        ],
        "language": "Chinese Simplified",
        "region": "China",
        "release_date": "2025-01-17",
    },
    "gem_pack_vol2": {
        "canonical": "Pokemon Chinese Gem Pack Vol.2 Eevee",
        "code": "CBB2C",
        "set_id": "CBB2C",
        "aliases": [
            "Gem Pack Vol.2", "Gem Pack Vol.2 Eevee", "Gem Pack 2",
            "Chinese Gem Pack Vol.2", "Chinese Gem Pack Vol.2 Eevee",
            "CBB2C", "Gem Pack Vol. 2", "Gem Pack Vol. 2 Eevee",
            "Pokemon TCG Simplified Chinese Gem Pack Vol.2",
            "Pokemon TCG Simplified Chinese Gem Pack Vol.2 Eevee",
            "Gem Pack Vol.2 Eevee Booster Box",
            "Chinese Gem Pack Eevee Vol.2",
            "Pokemon Chinese Gem Pack Volume 2 CBB2C",
            "Pokemon Chinese Gem Pack Volume 2 CBB2C Booster Factory Sealed Case 20 BOXES BOX",
        ],
        "language": "Chinese Simplified",
        "region": "China",
        "release_date": "2025-05-16",
    },
    "gem_pack_vol3": {
        "canonical": "Pokemon Chinese Gem Pack Vol.3",
        "code": "CBB3C",
        "set_id": "CBB3C",
        "aliases": [
            "Gem Pack Vol.3", "Gem Pack Vol.3 Eevee", "Gem Pack 3",
            "Chinese Gem Pack Vol.3", "Chinese Gem Pack Vol.3 Eevee",
            "CBB3C", "Gem Pack Vol. 3", "Gem Pack Vol. 3 Eevee",
            "Pokemon TCG Simplified Chinese Gem Pack Vol.3",
            "Gem Pack Vol.3 Eevee Booster Box",
        ],
        "language": "Chinese Simplified",
        "region": "China",
        "release_date": "2025-09-26",
    },
    "gem_pack_vol4": {
        "canonical": "Pokemon Chinese Gem Pack Vol.4",
        "code": "CBB4C",
        "set_id": "CBB4C",
        "aliases": [
            "Gem Pack Vol.4", "Gem Pack Vol.4 Eevee", "Gem Pack 4",
            "Chinese Gem Pack Vol.4", "Chinese Gem Pack Vol.4 Eevee",
            "CBB4C", "Gem Pack Vol. 4", "Gem Pack Vol. 4 Eevee",
            "Pokemon TCG Simplified Chinese Gem Pack Vol.4",
            "Gem Pack Vol.4 Eevee Booster Box",
        ],
        "language": "Chinese Simplified",
        "region": "China",
        "release_date": "2026-02-06",
    },
    "gem_pack_vol5": {
        "canonical": "Pokemon Chinese Gem Pack Vol.5",
        "code": "CBB5C",
        "set_id": "CBB5C",
        "aliases": [
            "Gem Pack Vol.5", "Gem Pack Vol.5 Eevee", "Gem Pack 5",
            "Chinese Gem Pack Vol.5", "Chinese Gem Pack Vol.5 Eevee",
            "CBB5C", "Gem Pack Vol. 5", "Gem Pack Vol. 5 Eevee",
            "Pokemon TCG Simplified Chinese Gem Pack Vol.5",
            "Gem Pack Vol.5 Eevee Booster Box",
        ],
        "language": "Chinese Simplified",
        "region": "China",
        "release_date": "2026-04-24",
    },
    
    # English sets (examples)
    "base_set": {
        "canonical": "Pokemon Base Set",
        "code": "BS",
        "set_id": "base1",
        "aliases": [
            "Base Set", "Base Set 1", "Base", "Base Set (1999)",
            "Pokemon Base Set", "Pokemon TCG Base Set", "WOTC Base Set",
            "1st Edition Base Set", "Unlimited Base Set",
            "Base", "BS",
        ],
        "language": "English",
        "region": "International",
        "release_date": "1999-01-09",
    },
    "evolving_skies": {
        "canonical": "Pokemon Evolving Skies",
        "code": "EVS",
        "set_id": "swsh7",
        "aliases": [
            "Evolving Skies", "EVS", "Evolving Skies (Sword & Shield)",
            "Pokemon Evolving Skies", "SWSH07", "Sword & Shield 7",
        ],
        "language": "English",
        "region": "International",
        "release_date": "2021-08-27",
    },
    "prismatic_evolutions": {
        "canonical": "Pokemon Prismatic Evolutions",
        "code": "PRE",
        "set_id": "sv08.5",
        "aliases": [
            "Prismatic Evolutions", "PRE", "Prismatic Evolutions (SV)",
            "Pokemon Prismatic Evolutions", "SV08.5", "SV08.5",
            "Prismatic Evo", "Prismatic",
        ],
        "language": "English",
        "region": "International",
        "release_date": "2025-01-17",
    },
}


class ProductAliasResolver:
    """Resolve product names to canonical IDs."""
    
    def __init__(self):
        # Build reverse index: alias → canonical_id
        self.alias_index = {}
        for prod_id, prod in PRODUCT_ALIASES.items():
            # Add canonical name
            self.alias_index[prod["canonical"].lower()] = prod_id
            self.alias_index[prod["code"].lower()] = prod_id
            # Add all aliases
            for alias in prod["aliases"]:
                self.alias_index[alias.lower()] = prod_id
    
    def resolve(self, query):
        """Resolve a product name to its canonical ID and metadata."""
        query_lower = query.lower().strip()
        
        # Exact match
        if query_lower in self.alias_index:
            prod_id = self.alias_index[query_lower]
            return {"id": prod_id, **PRODUCT_ALIASES[prod_id], "match_type": "exact"}
        
        # Partial match
        for alias, prod_id in self.alias_index.items():
            if query_lower in alias or alias in query_lower:
                return {"id": prod_id, **PRODUCT_ALIASES[prod_id], "match_type": "partial"}
        
        # Fuzzy match (check if any word in query matches)
        query_words = set(query_lower.split())
        best_match = None
        best_score = 0
        for alias, prod_id in self.alias_index.items():
            alias_words = set(alias.split())
            overlap = len(query_words & alias_words)
            if overlap > best_score:
                best_score = overlap
                best_match = prod_id
        
        if best_match and best_score > 0:
            return {"id": best_match, **PRODUCT_ALIASES[best_match], "match_type": "fuzzy"}
        
        return None
    
    def list_products(self):
        """List all known products."""
        return [{"id": k, "canonical": v["canonical"], "code": v["code"], 
                 "aliases": len(v["aliases"])} for k, v in PRODUCT_ALIASES.items()]


if __name__ == "__main__":
    resolver = ProductAliasResolver()
    
    print("=" * 70)
    print("PRODUCT NAME ALIAS SYSTEM")
    print("=" * 70)
    
    # Test various name variations
    test_names = [
        "CBB2C",
        "Gem Pack Vol. 2",
        "Pokemon TCG Simplified Chinese Gem Pack Vol.2",
        "Chinese Gem Pack Vol.2 Eevee",
        "Gem Pack Vol.2 Eevee Booster Box",
        "Pokemon Chinese Gem Pack Volume 2 CBB2C Booster Factory Sealed Case 20 BOXES BOX",
        "Base Set",
        "BS",
        "Pokemon TCG Base Set",
        "Evolving Skies",
        "EVS",
        "Prismatic Evolutions",
    ]
    
    print(f"\n{'Input Query':<60} {'→ Resolved To'}")
    print(f"{'─'*60} {'─'*30}")
    for name in test_names:
        result = resolver.resolve(name)
        if result:
            print(f"  {name:<58} → {result['canonical']}")
        else:
            print(f"  {name:<58} → NOT FOUND")
    
    print(f"\n{'='*70}")
    print(f"Total products: {len(PRODUCT_ALIASES)}")
    print(f"Total aliases: {sum(len(v['aliases']) for v in PRODUCT_ALIASES.values())}")
    print(f"{'='*70}")
