#!/usr/bin/env python3
"""
Gem Pack Vol. 2 Eevee Box EV Calculator
Box: 15 packs × 4 cards = 60 cards total
Set: 140 cards (9 Eeveelutions × ~15 cards each)
"""
import json
import math

# Set composition from TCGCollector
SET_SIZE = 140
PACKS_PER_BOX = 15
CARDS_PER_PACK = 4
TOTAL_CARDS = PACKS_PER_BOX * CARDS_PER_PACK  # 60

# Rarity distribution in the set
RARITY_DIST = {
    "Common":       {"count": 36, "pull_rate": 3.0, "packs_per_card": 3.0},
    "Uncommon":     {"count": 36, "pull_rate": 3.0, "packs_per_card": 3.0},
    "Rare":         {"count": 27, "pull_rate": 4.5, "packs_per_card": 4.5},
    "Double Rare":  {"count": 18, "pull_rate": 7.0, "packs_per_card": 7.0},
    "Triple Rare":  {"count": 10, "pull_rate": 12.0, "packs_per_card": 12.0},
}

# Estimated market values (CNY → USD conversion at ~7.2 CNY/USD)
# These are estimates based on comparable Chinese Gem Pack products
# since TCGCollector shows no prices yet for this set
ESTIMATED_PRICES_USD = {
    "Common":       0.10,
    "Uncommon":     0.15,
    "Rare":         0.30,
    "Double Rare":  1.00,
    "Triple Rare":  3.00,
    "V":            2.50,
    "VMAX":         4.00,
}

# Alternative: per-Eeveelution pricing (Umbreon/Umbreon typically premium)
EEVEELUTION_MULTIPLIER = {
    "Eevee":     1.0,
    "Vaporeon":  0.9,
    "Jolteon":   0.9,
    "Flareon":   0.9,
    "Espeon":    1.1,
    "Umbreon":   1.5,  # Umbreon premium
    "Leafeon":   0.9,
    "Glaceon":   0.9,
    "Sylveon":   1.2,
}


def calculate_pack_ev():
    """Calculate expected value of a single pack."""
    ev = 0
    details = []
    
    for rarity, info in RARITY_DIST.items():
        # Probability of getting this rarity in one pack
        p_rarity = info["pull_rate"] / CARDS_PER_PACK
        
        # Average value for this rarity
        avg_price = ESTIMATED_PRICES_USD.get(rarity, 0.10)
        
        # Contribution to EV
        contribution = p_rarity * avg_price
        ev += contribution
        details.append({
            "rarity": rarity,
            "count_in_set": info["count"],
            "pull_rate": f"1 in {info['pull_rate']:.1f} packs",
            "probability_per_pack": f"{p_rarity:.1%}",
            "avg_value": f"${avg_price:.2f}",
            "contribution": f"${contribution:.3f}",
        })
    
    return ev, details


def calculate_box_ev():
    """Calculate expected value of a full box."""
    pack_ev, details = calculate_pack_ev()
    box_ev = pack_ev * PACKS_PER_BOX
    
    # Calculate distribution of rarities in a box
    box_distribution = {}
    for rarity, info in RARITY_DIST.items():
        expected = info["pull_rate"] * PACKS_PER_BOX / CARDS_PER_PACK
        box_distribution[rarity] = expected
    
    return box_ev, box_distribution, details


def calculate_set_completion():
    """Calculate probability of completing set from one box."""
    # Using coupon collector approximation
    cards_per_pack = CARDS_PER_PACK
    total_unique = SET_SIZE
    
    expected_unique = total_unique * (1 - math.exp(-PACKS_PER_BOX * cards_per_pack / total_unique))
    percent_complete = expected_unique / total_unique * 100
    
    return {
        "expected_unique": round(expected_unique, 1),
        "percent_complete": round(percent_complete, 1),
        "packs_for_50pct": math.ceil(total_unique * math.log(2) / cards_per_pack),
        "packs_for_90pct": math.ceil(total_unique * math.log(10) / cards_per_pack),
    }


def print_analysis():
    """Print full box analysis."""
    print("=" * 70)
    print("POKEMON TCG GEM PACK VOL. 2 - EEVEE BOX EV ANALYSIS")
    print("=" * 70)
    
    print(f"\nBox Configuration:")
    print(f"  Packs per box: {PACKS_PER_BOX}")
    print(f"  Cards per pack: {CARDS_PER_PACK}")
    print(f"  Total cards per box: {TOTAL_CARDS}")
    print(f"  Set size: {SET_SIZE} cards")
    
    # Pack EV
    pack_ev, pack_details = calculate_pack_ev()
    print(f"\n{'─'*70}")
    print(f"SINGLE PACK EXPECTED VALUE: ${pack_ev:.2f}")
    print(f"{'─'*70}")
    print(f"\n  {'Rarity':<15} {'In Set':>8} {'1/Pack':>10} {'Prob':>8} {'Value':>8} {'EV':>8}")
    print(f"  {'─'*15} {'─'*8} {'─'*10} {'─'*8} {'─'*8} {'─'*8}")
    for d in pack_details:
        print(f"  {d['rarity']:<15} {d['count_in_set']:>8} {d['pull_rate']:>10} {d['probability_per_pack']:>8} {d['avg_value']:>8} {d['contribution']:>8}")
    
    # Box EV
    box_ev, box_dist, _ = calculate_box_ev()
    print(f"\n{'─'*70}")
    print(f"FULL BOX EXPECTED VALUE: ${box_ev:.2f}")
    print(f"{'─'*70}")
    print(f"\n  Expected rarity distribution in 60 cards:")
    print(f"  {'Rarity':<15} {'Expected Count':>15} {'× Avg Value':>12} {'Total':>10}")
    print(f"  {'─'*15} {'─'*15} {'─'*12} {'─'*10}")
    
    box_total = 0
    for rarity, expected in box_dist.items():
        avg_val = ESTIMATED_PRICES_USD.get(rarity, 0.10)
        total_val = expected * avg_val
        box_total += total_val
        print(f"  {rarity:<15} {expected:>15.2f} ${avg_val:>10.2f} ${total_val:>8.2f}")
    
    print(f"  {'─'*15} {'─'*15} {'─'*12} {'─'*10}")
    print(f"  {'TOTAL':<15} {'':<15} {'':<12} ${box_total:>8.2f}")
    
    # Set completion
    completion = calculate_set_completion()
    print(f"\n{'─'*70}")
    print(f"SET COMPLETION PROBABILITY")
    print(f"{'─'*70}")
    print(f"  Expected unique cards from 1 box: {completion['expected_unique']}/{SET_SIZE} ({completion['percent_complete']}%)")
    print(f"  Packs needed for 50% completion: {completion['packs_for_50pct']}")
    print(f"  Packs needed for 90% completion: {completion['packs_for_90pct']}")
    
    # ROI Analysis
    print(f"\n{'─'*70}")
    print(f"ROI ANALYSIS (assuming box price varies)")
    print(f"{'─'*70}")
    
    box_prices = [30, 40, 50, 60, 70, 80, 100]
    print(f"\n  {'Box Price':>10} {'Pack Price':>12} {'Box EV':>10} {'ROI':>10} {'Verdict'}")
    print(f"  {'─'*10} {'─'*12} {'─'*10} {'─'*10} {'─'*15}")
    
    for price in box_prices:
        pack_price = price / PACKS_PER_BOX
        roi = (box_ev / price - 1) * 100
        verdict = "PROFIT" if roi > 0 else "LOSS" if roi < -10 else "BREAK EVEN"
        color = "\033[92m" if roi > 0 else "\033[91m" if roi < -10 else "\033[93m"
        reset = "\033[0m"
        print(f"  ${price:>8} ${pack_price:>10.2f} ${box_ev:>8.2f} {color}{roi:>8.1f}%{reset} {verdict}")
    
    # Umbreon Premium Analysis
    print(f"\n{'─'*70}")
    print(f"EEVEELUTION PREMIUM ANALYSIS")
    print(f"{'─'*70}")
    print(f"\n  Umbreon/Sylveon typically command premiums:")
    for name, mult in sorted(EEVEELUTION_MULTIPLIER.items(), key=lambda x: -x[1]):
        premium = (mult - 1) * 100
        indicator = "★" if mult > 1.0 else " " if mult == 1.0 else "↓"
        print(f"  {indicator} {name:<12} {mult:.1f}x base price ({premium:+.0f}% premium)")


if __name__ == "__main__":
    print_analysis()
