#!/usr/bin/env python3
"""
CHECKPOINT 5: Generate frontend JS data for value lookup + singles-vs-packs
Exports data as JS constants for embedding in index.html
"""
import json
from pathlib import Path

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")


def load_index():
    path = OUTPUT_DIR / "card_index.json"
    with open(path) as f:
        return json.load(f)


def generate_frontend_data():
    """Generate JS-embeddable data for the frontend."""
    index = load_index()
    
    # Sets with pricing (top 30 by value)
    sets = list(index.get("sets", {}).values())
    sets_with_value = [s for s in sets if s.get("market_value_usd", 0) > 0]
    top_sets = sorted(sets_with_value, key=lambda x: x.get("market_value_usd", 0), reverse=True)[:30]
    
    # Card name index for autocomplete (top 500 most common names)
    name_index = index.get("by_name", {})
    top_names = sorted(name_index.items(), key=lambda x: -len(x[1]))[:500]
    
    # Grade multipliers
    grade_data = {
        10: {"label": "Gem Mint", "mult_range": [3.0, 25.0]},
        9: {"label": "Mint", "mult_range": [1.5, 5.0]},
        8: {"label": "NM-MT", "mult_range": [1.0, 2.5]},
        7: {"label": "Near Mint", "mult_range": [0.8, 1.2]},
    }
    
    output = {
        "sets": [{
            "name": s.get("name", ""),
            "code": s.get("code", ""),
            "cards": s.get("cards", 0),
            "value_usd": s.get("market_value_usd", 0),
            "value_eur": s.get("market_value_eur", 0),
            "era": s.get("era", ""),
        } for s in top_sets],
        "card_names": [name for name, _ in top_names],
        "grade_data": grade_data,
    }
    
    return output


def save_frontend_data():
    data = generate_frontend_data()
    path = OUTPUT_DIR / "frontend_data.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved frontend data: {len(data['sets'])} sets, {len(data['card_names'])} card names")


if __name__ == "__main__":
    save_frontend_data()
