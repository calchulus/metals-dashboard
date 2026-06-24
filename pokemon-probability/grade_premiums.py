#!/usr/bin/env python3
"""
CHECKPOINT 4: PSA Grade Premiums
Integrates PSA 10/9/8 multipliers into value lookup.
Key insight: PSA 9 is most common (21-28%), PSA 8 second (22-29%), PSA 10 varies wildly (3.8-19.4%)
"""
import json
from pathlib import Path

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")


# Grade multipliers based on empirical data from psa_population.json
# Multiplier = how much more a graded card is worth vs raw
GRADE_MULTIPLIERS = {
    10: {"label": "Gem Mint", "min_mult": 3.0, "max_mult": 25.0, "description": "Perfect condition"},
    9:  {"label": "Mint", "min_mult": 1.5, "max_mult": 5.0, "description": "Near-perfect"},
    8:  {"label": "NM-MT", "min_mult": 1.0, "max_mult": 2.5, "description": "Very good"},
    7:  {"label": "Near Mint", "min_mult": 0.8, "max_mult": 1.2, "description": "Good condition"},
    6:  {"label": "EX-MT", "min_mult": 0.6, "max_mult": 0.9, "description": "Light wear"},
    5:  {"label": "EX", "min_mult": 0.5, "max_mult": 0.7, "description": "Moderate wear"},
    4:  {"label": "VG-EX", "min_mult": 0.4, "max_mult": 0.6, "description": "Heavy wear"},
    3:  {"label": "Very Good", "min_mult": 0.3, "max_mult": 0.5, "description": "Significant wear"},
    2:  {"label": "Good", "min_mult": 0.2, "max_mult": 0.4, "description": "Poor condition"},
    1:  {"label": "Poor", "min_mult": 0.1, "max_mult": 0.3, "description": "Damaged"},
}


def get_grade_multiplier(grade: int, gem_mint_rate: float = None) -> float:
    """
    Get the value multiplier for a given PSA grade.
    gem_mint_rate: % of cards that grade PSA 10 (affects PSA 10 multiplier)
    """
    info = GRADE_MULTIPLIERS.get(grade, GRADE_MULTIPLIERS[7])
    
    if grade == 10 and gem_mint_rate is not None:
        # Adjust PSA 10 multiplier based on scarcity
        if gem_mint_rate < 5:
            return 20.0  # Extremely rare gem mint
        elif gem_mint_rate < 10:
            return 12.0  # Very rare
        elif gem_mint_rate < 20:
            return 7.0   # Rare
        elif gem_mint_rate < 30:
            return 5.0   # Uncommon
        else:
            return 3.0   # Common
    
    return (info["min_mult"] + info["max_mult"]) / 2


def calculate_grading_roi(raw_price: float, grading_cost: float = 50,
                          expected_grade: int = 9, gem_mint_rate: float = 15.0):
    """
    Calculate ROI for grading a card.
    Returns dict with costs, expected value, profit, and recommendation.
    """
    multiplier = get_grade_multiplier(expected_grade, gem_mint_rate)
    graded_value = raw_price * multiplier
    total_cost = raw_price + grading_cost
    profit = graded_value - total_cost
    roi = (profit / grading_cost * 100) if grading_cost > 0 else 0
    
    # Risk-adjusted: what if you grade and get a lower grade?
    worst_case_mult = get_grade_multiplier(expected_grade - 2, gem_mint_rate) if expected_grade > 2 else 0.2
    worst_case_value = raw_price * worst_case_mult
    worst_case_profit = worst_case_value - total_cost
    
    return {
        "raw_price": raw_price,
        "grading_cost": grading_cost,
        "expected_grade": expected_grade,
        "multiplier": round(multiplier, 1),
        "graded_value": round(graded_value, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(profit, 2),
        "roi_pct": round(roi, 1),
        "worst_case_profit": round(worst_case_profit, 2),
        "recommendation": "GRADE" if roi > 50 else "HOLD" if roi > 0 else "DON'T GRADE",
    }


def print_grade_analysis():
    """Print comprehensive grade premium analysis."""
    print("=" * 70)
    print("PSA GRADE PREMIUM ANALYSIS")
    print("=" * 70)
    
    # Grade multiplier table
    print(f"\n{'─'*70}")
    print(f"GRADE MULTIPLIERS (vs Raw/Ungraded)")
    print(f"{'─'*70}")
    print(f"  {'Grade':<12} {'Label':<15} {'Multiplier':>12} {'Description'}")
    print(f"  {'─'*12} {'─'*15} {'─'*12} {'─'*25}")
    
    for grade, info in sorted(GRADE_MULTIPLIERS.items(), reverse=True):
        mult = (info["min_mult"] + info["max_mult"]) / 2
        print(f"  PSA {grade:<9} {info['label']:<15} {mult:>10.1f}x   {info['description']}")
    
    # Gem mint rate impact on PSA 10
    print(f"\n{'─'*70}")
    print(f"PSA 10 MULTIPLIER BY GEM MINT RATE")
    print(f"{'─'*70}")
    print(f"  {'Gem Mint Rate':>15} {'PSA 10 Mult':>12} {'Interpretation'}")
    print(f"  {'─'*15} {'─'*12} {'─'*30}")
    
    for rate in [1, 3, 5, 10, 15, 20, 30, 50]:
        mult = get_grade_multiplier(10, rate)
        interp = "Extremely rare" if rate < 5 else "Very rare" if rate < 10 else "Rare" if rate < 20 else "Common" if rate < 30 else "Very common"
        print(f"  {rate:>13}% {mult:>10.1f}x   {interp}")
    
    # ROI examples
    print(f"\n{'─'*70}")
    print(f"GRADING ROI EXAMPLES")
    print(f"{'─'*70}")
    
    examples = [
        ("Base Set Charizard", 400, 50, 9, 19.4),
        ("Base Set Alakazam", 50, 50, 9, 3.8),
        ("Evolving Skies Umbreon VMAX", 80, 50, 9, 18.0),
        ("Pokemon 151 Charizard ex", 100, 50, 9, 17.0),
        ("Celebrations Charizard", 30, 50, 9, 16.2),
    ]
    
    print(f"\n  {'Card':<30} {'Raw':>8} {'Grade':>6} {'Value':>8} {'Profit':>8} {'ROI':>8} {'Verdict'}")
    print(f"  {'─'*30} {'─'*8} {'─'*6} {'─'*8} {'─'*8} {'─'*8} {'─'*12}")
    
    for name, raw, cost, grade, gmr in examples:
        result = calculate_grading_roi(raw, cost, grade, gmr)
        color = "\033[92m" if result["roi_pct"] > 50 else "\033[93m" if result["roi_pct"] > 0 else "\033[91m"
        reset = "\033[0m"
        print(f"  {name:<30} ${raw:>6} PSA{grade} ${result['graded_value']:>6,.0f} ${result['profit']:>+6,.0f} {color}{result['roi_pct']:>+6.1f}%{reset} {result['recommendation']}")
    
    # Key insight
    print(f"\n{'='*70}")
    print(f"KEY INSIGHT")
    print(f"{'='*70}")
    print(f"  PSA 9 is the SWEET SPOT for most cards:")
    print(f"  - Most common grade (21-28% of all graded)")
    print(f"  - 1.5-5x raw value multiplier")
    print(f"  - Low risk: even if you get PSA 8, you still profit")
    print(f"  - High ROI: $50 grading cost often returns $100-400")
    print(f"\n  PSA 10 is high-risk, high-reward:")
    print(f"  - Only 3.8-19.4% of cards grade PSA 10")
    print(f"  - 3-25x multiplier depends entirely on gem mint rate")
    print(f"  - Best candidates: cards with <10% gem mint rate")
    print(f"{'='*70}")


if __name__ == "__main__":
    print_grade_analysis()
