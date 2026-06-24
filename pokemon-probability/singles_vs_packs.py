#!/usr/bin/env python3
"""
CHECKPOINT 3: Singles vs Packs Arbitrage Calculator
Answers: "Given you want card X, should you buy packs or singles?"

The no-arbitrage condition: Pack EV ≈ Sum of singles prices
In practice, there's always a spread due to:
  - Chase card premiums (singles cost more than their pack share)
  - Set completion value (packs give you bulk you don't want)
  - Risk aversion (guaranteed cost vs probabilistic outcome)
  - Liquidity (commons are worthless, singles are instant)
"""
import json
import math
from pathlib import Path

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")


class SinglesVsPacks:
    """
    Decision engine: Buy singles or buy packs?
    
    Given you want specific cards from a set, this calculates:
    1. Cost to buy all desired singles directly
    2. Expected cost to pull them from packs
    3. The arbitrage spread (which is better)
    """
    
    def __init__(self, pack_price: float, pack_config: dict):
        """
        pack_price: Cost per booster pack
        pack_config: {"packs_per_box": 36, "cards_per_pack": 10, ...}
        """
        self.pack_price = pack_price
        self.config = pack_config
        self.packs_per_box = pack_config.get("packs_per_box", 36)
        self.cards_per_pack = pack_config.get("cards_per_pack", 10)
    
    def packs_needed_for_card(self, pull_rate: float, confidence: float = 0.9) -> int:
        """Expected packs to pull a card at given confidence level."""
        return math.ceil(math.log(1 - confidence) / math.log(1 - 1/pull_rate))
    
    def singles_cost(self, desired_cards: list) -> dict:
        """
        Calculate total cost to buy desired singles directly.
        desired_cards: [{"name": "Charizard", "price": 400, "pull_rate": 22}, ...]
        """
        total_cost = sum(c.get("price", 0) for c in desired_cards)
        total_with_shipping = total_cost + (len(desired_cards) * 1.50)  # ~$1.50 shipping per card
        
        return {
            "cards_desired": len(desired_cards),
            "cards_total_value": round(total_cost, 2),
            "estimated_shipping": round(len(desired_cards) * 1.50, 2),
            "total_cost": round(total_with_shipping, 2),
        }
    
    def packs_cost(self, desired_cards: list) -> dict:
        """
        Calculate expected cost to pull desired cards from packs.
        Uses the worst-case (hardest to pull) card to determine packs needed.
        """
        # Find the hardest card to pull
        worst_rate = max(c.get("pull_rate", 100) for c in desired_cards)
        best_card = max(desired_cards, key=lambda c: c.get("pull_rate", 100))
        
        # Packs needed at 90% confidence
        packs_90 = self.packs_needed_for_card(worst_rate, 0.9)
        packs_50 = self.packs_needed_for_card(worst_rate, 0.5)
        
        # Cost
        cost_90 = packs_90 * self.pack_price
        cost_50 = packs_50 * self.pack_price
        
        # Additional cards you'll get (the "bulk" bonus)
        total_cards = packs_90 * self.cards_per_pack
        unique_expected = min(total_cards * 0.7, 200)  # Rough estimate
        
        return {
            "packs_needed_90pct": packs_90,
            "packs_needed_50pct": packs_50,
            "cost_90pct": round(cost_90, 2),
            "cost_50pct": round(cost_50, 2),
            "hardest_card": best_card.get("name", "?"),
            "hardest_pull_rate": worst_rate,
            "total_cards_pulled": total_cards,
            "unique_cards_expected": round(unique_expected),
        }
    
    def arbitrage_analysis(self, desired_cards: list) -> dict:
        """
        Full arbitrage analysis: singles vs packs.
        Returns recommendation with spread calculation.
        """
        singles = self.singles_cost(desired_cards)
        packs = self.packs_cost(desired_cards)
        
        # Spread: how much more/less expensive is one option
        spread = packs["cost_90pct"] - singles["total_cost"]
        spread_pct = (spread / singles["total_cost"] * 100) if singles["total_cost"] > 0 else 0
        
        # Recommendation
        if spread > 0:
            recommendation = "BUY SINGLES"
            reason = f"Packs cost ${spread:,.0f} MORE than buying singles directly"
        else:
            recommendation = "BUY PACKS"
            reason = f"Packs cost ${abs(spread):,.0f} LESS than buying singles"
        
        return {
            "singles": singles,
            "packs": packs,
            "spread": round(spread, 2),
            "spread_pct": round(spread_pct, 1),
            "recommendation": recommendation,
            "reason": reason,
            "pack_price": self.pack_price,
        }
    
    def print_analysis(self, desired_cards: list):
        """Print full analysis."""
        result = self.arbitrage_analysis(desired_cards)
        
        print(f"\n{'='*70}")
        print(f"SINGLES VS PACKS ARBITRAGE ANALYSIS")
        print(f"{'='*70}")
        print(f"Pack price: ${self.pack_price:.2f}")
        print(f"Cards desired: {result['singles']['cards_desired']}")
        
        print(f"\n{'─'*70}")
        print(f"OPTION A: BUY SINGLES")
        print(f"{'─'*70}")
        print(f"  Cards total value:  ${result['singles']['cards_total_value']:>10,.2f}")
        print(f"  Est. shipping:      ${result['singles']['estimated_shipping']:>10,.2f}")
        print(f"  TOTAL COST:         ${result['singles']['total_cost']:>10,.2f}")
        
        print(f"\n{'─'*70}")
        print(f"OPTION B: BUY PACKS")
        print(f"{'─'*70}")
        print(f"  Hardest card:       {result['packs']['hardest_card']}")
        print(f"  Pull rate:          1 in {result['packs']['hardest_pull_rate']}")
        print(f"  Packs needed (90%): {result['packs']['packs_needed_90pct']}")
        print(f"  Packs needed (50%): {result['packs']['packs_needed_50pct']}")
        print(f"  Cost at 90%:        ${result['packs']['cost_90pct']:>10,.2f}")
        print(f"  Cost at 50%:        ${result['packs']['cost_50pct']:>10,.2f}")
        print(f"  Cards pulled:       {result['packs']['total_cards_pulled']}")
        
        print(f"\n{'='*70}")
        print(f"RECOMMENDATION: {result['recommendation']}")
        print(f"  {result['reason']}")
        print(f"  Spread: ${result['spread']:>10,.2f} ({result['spread_pct']:+.1f}%)")
        print(f"{'='*70}")
        
        # Detailed card-by-card comparison
        print(f"\n{'─'*70}")
        print(f"CARD-BY-CARD COMPARISON")
        print(f"{'─'*70}")
        print(f"  {'Card':<25} {'Single $':>10} {'Pack Share':>10} {'Delta':>10}")
        print(f"  {'─'*25} {'─'*10} {'─'*10} {'─'*10}")
        
        for card in desired_cards:
            name = card.get("name", "?")[:24]
            price = card.get("price", 0)
            pull_rate = card.get("pull_rate", 100)
            pack_share = self.pack_price * pull_rate  # Expected pack cost to pull this card
            delta = price - pack_share
            
            print(f"  {name:<25} ${price:>9,.2f} ${pack_share:>9,.2f} ${delta:>+9,.2f}")


# ============================================================
# DEMO: Gem Pack Vol. 2 Eevee
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("SINGLES VS PACKS ARBITRAGE CALCULATOR")
    print("=" * 70)
    
    # Gem Pack Vol. 2 configuration
    calculator = SinglesVsPacks(
        pack_price=5.00,  # Estimated pack price
        pack_config={
            "packs_per_box": 15,
            "cards_per_pack": 4,
        }
    )
    
    # Scenario 1: Want all 9 VMAX cards
    print("\n" + "▓" * 70)
    print("SCENARIO 1: Want all 9 Eeveelution VMAX cards")
    print("▓" * 70)
    
    desired_vmax = [
        {"name": "Eevee VMAX", "price": 3.00, "pull_rate": 12},
        {"name": "Vaporeon VMAX", "price": 2.50, "pull_rate": 12},
        {"name": "Jolteon VMAX", "price": 2.50, "pull_rate": 12},
        {"name": "Flareon VMAX", "price": 2.50, "pull_rate": 12},
        {"name": "Espeon VMAX", "price": 3.50, "pull_rate": 12},
        {"name": "Umbreon VMAX", "price": 5.00, "pull_rate": 12},
        {"name": "Leafeon VMAX", "price": 2.50, "pull_rate": 12},
        {"name": "Glaceon VMAX", "price": 2.50, "pull_rate": 12},
        {"name": "Sylveon VMAX", "price": 4.00, "pull_rate": 12},
    ]
    calculator.print_analysis(desired_vmax)
    
    # Scenario 2: Just want Umbreon VMAX
    print("\n" + "▓" * 70)
    print("SCENARIO 2: Just want Umbreon VMAX")
    print("▓" * 70)
    
    desired_umbreon = [
        {"name": "Umbreon VMAX", "price": 5.00, "pull_rate": 12},
    ]
    calculator.print_analysis(desired_umbreon)
    
    # Scenario 3: Want entire set (140 cards)
    print("\n" + "▓" * 70)
    print("SCENARIO 3: Want complete set (140 cards)")
    print("▓" * 70)
    
    # Estimate: average card value ~$0.30 for commons/uncommons
    desired_set = [{"name": f"Card {i}", "price": 0.30, "pull_rate": 3} for i in range(140)]
    calculator.print_analysis(desired_set)
