#!/usr/bin/env python3
"""
PSA GRADING OPTION FRAMEWORK
"Option on the option" - Is it worth grading a card?

Core insight: Grading a card is like buying a call option on the card's value.
- You pay a fixed cost (grading fee + shipping)
- You receive a graded card worth raw × multiplier
- The multiplier depends on the grade received
- You don't know the grade in advance (random outcome)

The "option on the option" means:
- The OPTION is: grade the card (fixed cost)
- The UNDERLYING is: the raw card value
- The OUTCOME is: grade 10 (huge payoff) or grade 9 (good) or grade 8+ (loss)
"""
import math
import json


# Grade probabilities (from PSA population data)
# These vary by card but represent typical distributions
GRADE_PROBS = {
    10: 0.12,  # 12% chance of PSA 10
    9: 0.25,   # 25% chance of PSA 9
    8: 0.27,   # 27% chance of PSA 8
    7: 0.19,   # 19% chance of PSA 7
    6: 0.10,   # 10% chance of PSA 6
    5: 0.05,   # 5% chance of PSA 5
    4: 0.015,  # 1.5% chance of PSA 4
    3: 0.005,  # 0.5% chance of PSA 3
    2: 0.002,  # 0.2% chance of PSA 2
    1: 0.001,  # 0.1% chance of PSA 1
}

# Grade multipliers (vs raw/ungraded)
# These vary significantly by card rarity and gem mint rate
def get_multiplier(grade, gem_mint_rate=15.0):
    """Get value multiplier for a given grade."""
    base = {10: 14.0, 9: 3.2, 8: 1.8, 7: 1.0, 6: 0.8, 5: 0.6, 4: 0.5, 3: 0.4, 2: 0.3, 1: 0.2}
    
    if grade == 10:
        # Adjust PSA 10 based on gem mint scarcity
        if gem_mint_rate < 5: return 20.0
        elif gem_mint_rate < 10: return 12.0
        elif gem_mint_rate < 20: return 7.0
        elif gem_mint_rate < 30: return 5.0
        else: return 3.0
    
    return base.get(grade, 1.0)


def grading_option_analysis(raw_price, grading_cost, gem_mint_rate=15.0, custom_probs=None):
    """
    Full option analysis for grading a card.
    
    Returns: Expected value, breakeven, optimal grade, risk metrics
    """
    probs = custom_probs or GRADE_PROBS
    
    # Calculate expected value
    expected_value = 0
    outcomes = []
    for grade, prob in probs.items():
        mult = get_multiplier(grade, gem_mint_rate)
        value = raw_price * mult
        profit = value - grading_cost
        expected_value += prob * value
        outcomes.append({
            "grade": grade,
            "probability": prob,
            "multiplier": mult,
            "value": round(value, 2),
            "profit": round(profit, 2),
        })
    
    # Breakeven analysis
    net_ev = expected_value - grading_cost
    roi = (net_ev / grading_cost * 100) if grading_cost > 0 else 0
    
    # Risk metrics
    best_case = max(o["value"] for o in outcomes)
    worst_case = min(o["value"] for o in outcomes)
    expected_profit = net_ev
    max_loss = grading_cost  # If you grade and it's worthless
    
    # Probability of profit
    profitable_outcomes = sum(o["probability"] for o in outcomes if o["profit"] > 0)
    
    # Sharpe-like ratio: expected profit / std dev of outcomes
    variance = sum(o["probability"] * (o["value"] - expected_value)**2 for o in outcomes)
    std_dev = math.sqrt(variance)
    sharpe = (expected_value - grading_cost) / std_dev if std_dev > 0 else 0
    
    return {
        "raw_price": raw_price,
        "grading_cost": grading_cost,
        "expected_value": round(expected_value, 2),
        "net_ev": round(net_ev, 2),
        "roi_pct": round(roi, 1),
        "best_case": round(best_case, 2),
        "worst_case": round(worst_case, 2),
        "max_loss": grading_cost,
        "profitable_probability": round(profitable_outcomes * 100, 1),
        "sharpe_ratio": round(sharpe, 2),
        "recommendation": "GRADE" if roi > 50 else "MAYBE" if roi > 0 else "DON'T GRADE",
        "outcomes": outcomes,
    }


def print_analysis(raw_price, grading_cost=50, gem_mint_rate=15.0, card_name="Card"):
    """Print full grading option analysis."""
    result = grading_option_analysis(raw_price, grading_cost, gem_mint_rate)
    
    print(f"\n{'='*70}")
    print(f"PSA GRADING OPTION ANALYSIS: {card_name}")
    print(f"{'='*70}")
    print(f"Raw price: ${raw_price:.2f} | Grading cost: ${grading_cost:.2f}")
    print(f"Gem mint rate: {gem_mint_rate}%")
    
    print(f"\n{'─'*70}")
    print(f"GRADE OUTCOMES")
    print(f"{'─'*70}")
    print(f"  {'Grade':<8} {'Prob':>8} {'Mult':>8} {'Value':>10} {'Profit':>10}")
    print(f"  {'─'*8} {'─'*8} {'─'*8} {'─'*10} {'─'*10}")
    
    for o in result["outcomes"]:
        color = "\033[92m" if o["profit"] > 0 else "\033[91m" if o["profit"] < 0 else ""
        reset = "\033[0m"
        print(f"  PSA {o['grade']:<5} {o['probability']:>7.1%} {o['multiplier']:>7.1f}x ${o['value']:>9,.2f} {color}${o['profit']:>+9,.2f}{reset}")
    
    print(f"\n{'─'*70}")
    print(f"OPTION METRICS")
    print(f"{'─'*70}")
    print(f"  Expected value:      ${result['expected_value']:>10,.2f}")
    print(f"  Grading cost:        ${result['grading_cost']:>10,.2f}")
    print(f"  Net EV:              ${result['net_ev']:>10,.2f}")
    print(f"  ROI:                 {result['roi_pct']:>9.1f}%")
    print(f"  Best case (PSA 10):  ${result['best_case']:>10,.2f}")
    print(f"  Worst case (PSA 1):  ${result['worst_case']:>10,.2f}")
    print(f"  Max loss:            ${result['max_loss']:>10,.2f}")
    print(f"  Prob of profit:      {result['profitable_probability']:>9.1f}%")
    print(f"  Risk-adjusted (SR):  {result['sharpe_ratio']:>9.2f}")
    
    print(f"\n{'='*70}")
    print(f"RECOMMENDATION: {result['recommendation']}")
    print(f"{'='*70}")


def compare_cards(cards, grading_cost=50):
    """Compare grading ROI across multiple cards."""
    print(f"\n{'='*70}")
    print(f"GRADING ROI COMPARISON (cost: ${grading_cost}/card)")
    print(f"{'='*70}")
    print(f"\n  {'Card':<30} {'Raw':>8} {'PSA9':>8} {'PSA10':>8} {'ROI':>8} {'Verdict'}")
    print(f"  {'─'*30} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*12}")
    
    for name, raw, gmr in cards:
        result = grading_option_analysis(raw, grading_cost, gmr)
        psa9_val = raw * get_multiplier(9, gmr)
        psa10_val = raw * get_multiplier(10, gmr)
        color = "\033[92m" if result["roi_pct"] > 50 else "\033[93m" if result["roi_pct"] > 0 else "\033[91m"
        reset = "\033[0m"
        print(f"  {name:<30} ${raw:>6} ${psa9_val:>6,.0f} ${psa10_val:>6,.0f} {color}{result['roi_pct']:>+6.1f}%{reset} {result['recommendation']}")


if __name__ == "__main__":
    # Demo with real cards
    print("PSA GRADING OPTION FRAMEWORK")
    print("Is it worth grading? Analyze the option on the option.\n")
    
    # Individual card analysis
    print_analysis(400, 50, 19.4, "Base Set Charizard")
    print_analysis(50, 50, 3.8, "Base Set Alakazam")
    print_analysis(80, 50, 18.0, "Evolving Skies Umbreon VMAX")
    
    # Comparison
    compare_cards([
        ("Base Set Charizard", 400, 19.4),
        ("Base Set Alakazam", 50, 3.8),
        ("Neo Genesis Lugia", 200, 13.1),
        ("Evolving Skies Umbreon VMAX", 80, 18.0),
        ("151 Charizard ex SAR", 100, 17.0),
        ("Celebrations Charizard", 30, 16.2),
    ], grading_cost=50)
