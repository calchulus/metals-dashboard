#!/usr/bin/env python3
"""
SEALED PRODUCT VALUATION MODEL
Values: Case → Box → Pack → Individual Cards
Considers: Sealed premium, optionality, condition, grading potential
"""
import math
import json


class SealedProductValuation:
    """
    Values Pokemon TCG sealed products at every tier:
    - Case (sealed, 20 boxes)
    - Box (sealed, 15 packs)
    - Pack (sealed, 4 cards)
    - Individual cards (ungraded vs graded)
    
    Key concept: OPTIONALITY PREMIUM
    Keeping a product sealed = holding an option on:
    1. Future price appreciation
    2. The right to open it later (or not)
    3. Grading potential of contents
    """
    
    def __init__(self, product_name: str, config: dict):
        self.name = product_name
        self.boxes_per_case = config.get("boxes_per_case", 20)
        self.packs_per_box = config.get("packs_per_box", 15)
        self.cards_per_pack = config.get("cards_per_pack", 4)
        self.set_size = config.get("set_size", 140)
        
        # Pricing
        self.sealed_case_price = config.get("sealed_case_price", 0)
        self.sealed_box_price = config.get("sealed_box_price", 0)
        self.sealed_pack_price = config.get("sealed_pack_price", 0)
        
        # Rarity distribution
        self.rarity_dist = config.get("rarity_dist", {})
        self.rarity_values = config.get("rarity_values", {})
        
        # Market context
        self.release_date = config.get("release_date", "")
        self.language = config.get("language", "Chinese")
        self.region = config.get("region", "China")
    
    def calculate_pack_ev(self) -> float:
        """Calculate expected value of opening one pack."""
        cards_per_pack = self.cards_per_pack
        ev = 0
        
        # Assuming 1 Common + 1 Uncommon + 1 Rare + 1 Hit per pack
        for rarity, info in self.rarity_dist.items():
            p = info["packs_per"] / cards_per_pack
            val = self.rarity_values.get(rarity, 0.10)
            ev += p * val
        
        return ev
    
    def calculate_box_ev(self) -> dict:
        """Calculate expected value of opening one box."""
        pack_ev = self.calculate_pack_ev()
        box_ev = pack_ev * self.packs_per_box
        
        # Card distribution in 60 cards
        distribution = {}
        for rarity, info in self.rarity_dist.items():
            expected = info["packs_per"] * self.packs_per_box / self.cards_per_pack
            distribution[rarity] = round(expected, 2)
        
        return {
            "pack_ev": round(pack_ev, 2),
            "box_ev": round(box_ev, 2),
            "cards_per_box": self.packs_per_box * self.cards_per_pack,
            "distribution": distribution,
        }
    
    def calculate_case_ev(self) -> dict:
        """Calculate expected value of opening one case."""
        box = self.calculate_box_ev()
        case_ev = box["box_ev"] * self.boxes_per_case
        
        return {
            "box_ev": box["box_ev"],
            "case_ev": round(case_ev, 2),
            "total_cards": self.packs_per_box * self.cards_per_pack * self.boxes_per_case,
            "boxes": self.boxes_per_case,
        }
    
    def sealed_premium(self, sealed_price: float, opened_ev: float) -> dict:
        """Calculate sealed premium over opened EV."""
        premium = sealed_price - opened_ev
        premium_pct = (premium / opened_ev * 100) if opened_ev > 0 else 0
        
        return {
            "sealed_price": sealed_price,
            "opened_ev": round(opened_ev, 2),
            "premium": round(premium, 2),
            "premium_pct": round(premium_pct, 1),
            "verdict": "OVERPRICED" if premium > 0 else "UNDERPRICED",
        }
    
    def optionality_value(self, years_held: int = 1, annual_appreciation: float = 0.15) -> dict:
        """
        Calculate optionality value of keeping sealed.
        
        Optionality = the right (but not obligation) to:
        1. Open the product later
        2. Sell it sealed (appreciation)
        3. Grade the contents (if opened)
        
        This is like a financial call option on the underlying card values.
        """
        current_ev = self.calculate_box_ev()["box_ev"]
        
        # Future value with appreciation
        future_value = current_ev * ((1 + annual_appreciation) ** years_held)
        
        # Option value = max(0, future_value - current_cost)
        # But we also need to account for the "time value" of holding sealed
        option_value = future_value - current_ev
        
        # Risk-adjusted: probability of price decline
        prob_decline = 0.20  # 20% chance of price drop
        expected_value = (1 - prob_decline) * future_value + prob_decline * (current_ev * 0.7)
        
        return {
            "current_ev": round(current_ev, 2),
            "future_value_1yr": round(future_value, 2),
            "option_value_1yr": round(option_value, 2),
            "expected_value_risk_adj": round(expected_value, 2),
            "annual_appreciation": f"{annual_appreciation:.0%}",
            "years_held": years_held,
        }
    
    def grading_potential(self, cards_per_box: int = 60) -> dict:
        """
        Estimate value if you grade the best cards from a box.
        
        Assumptions:
        - You grade the top 10 cards from each box
        - Average PSA 9 grade (most common)
        - PSA 9 multiplier: 2-3x raw value
        """
        box_ev = self.calculate_box_ev()
        
        # Estimate: top 10 cards represent ~80% of box value
        top_10_value = box_ev["box_ev"] * 0.80
        
        # PSA 9 multiplier (conservative)
        psa9_mult = 2.5
        graded_value = top_10_value * psa9_mult
        
        # Grading cost
        grading_cost_per_card = 50  # $50 per card (PSA economy)
        total_grading_cost = 10 * grading_cost_per_card
        
        # Net value
        net_value = graded_value - total_grading_cost
        roi = ((net_value / total_grading_cost) * 100) if total_grading_cost > 0 else 0
        
        return {
            "top_10_raw_value": round(top_10_value, 2),
            "psa9_multiplier": psa9_mult,
            "graded_value": round(graded_value, 2),
            "grading_cost": total_grading_cost,
            "net_value": round(net_value, 2),
            "roi_pct": round(roi, 1),
            "cards_graded": 10,
        }
    
    def full_valuation(self) -> dict:
        """Complete valuation across all tiers."""
        box = self.calculate_box_ev()
        case = self.calculate_case_ev()
        
        return {
            "product": self.name,
            "language": self.language,
            "region": self.region,
            "pack": {
                "cards": self.cards_per_pack,
                "ev": box["pack_ev"],
                "sealed_price": self.sealed_pack_price,
                "premium": round(self.sealed_pack_price - box["pack_ev"], 2) if self.sealed_pack_price > 0 else 0,
            },
            "box": {
                "packs": self.packs_per_box,
                "cards": box["cards_per_box"],
                "ev": box["box_ev"],
                "sealed_price": self.sealed_box_price,
                "premium": round(self.sealed_box_price - box["box_ev"], 2) if self.sealed_box_price > 0 else 0,
            },
            "case": {
                "boxes": self.boxes_per_case,
                "cards": case["total_cards"],
                "ev": case["case_ev"],
                "sealed_price": self.sealed_case_price,
                "premium": round(self.sealed_case_price - case["case_ev"], 2) if self.sealed_case_price > 0 else 0,
            },
            "grading": self.grading_potential(),
            "optionality": self.optionality_value(),
        }
    
    def print_valuation(self):
        """Print comprehensive valuation report."""
        val = self.full_valuation()
        
        print("=" * 70)
        print(f"SEALED PRODUCT VALUATION: {self.name}")
        print(f"Language: {self.language} | Region: {self.region}")
        print("=" * 70)
        
        # Pack tier
        print(f"\n{'─'*70}")
        print(f"TIER 1: PACK ({self.cards_per_pack} cards)")
        print(f"{'─'*70}")
        print(f"  Sealed price:  ${val['pack']['sealed_price']:>10.2f}")
        print(f"  Opened EV:     ${val['pack']['ev']:>10.2f}")
        print(f"  Premium:       ${val['pack']['premium']:>10.2f} ({val['pack']['premium']/val['pack']['ev']*100 if val['pack']['ev']>0 else 0:.1f}%)")
        
        # Box tier
        print(f"\n{'─'*70}")
        print(f"TIER 2: BOX ({self.packs_per_box} packs, {val['box']['cards']} cards)")
        print(f"{'─'*70}")
        print(f"  Sealed price:  ${val['box']['sealed_price']:>10.2f}")
        print(f"  Opened EV:     ${val['box']['ev']:>10.2f}")
        print(f"  Premium:       ${val['box']['premium']:>10.2f} ({val['box']['premium']/val['box']['ev']*100 if val['box']['ev']>0 else 0:.1f}%)")
        
        # Case tier
        print(f"\n{'─'*70}")
        print(f"TIER 3: CASE ({self.boxes_per_case} boxes, {val['case']['cards']} cards)")
        print(f"{'─'*70}")
        print(f"  Sealed price:  ${val['case']['sealed_price']:>10.2f}")
        print(f"  Opened EV:     ${val['case']['ev']:>10.2f}")
        print(f"  Premium:       ${val['case']['premium']:>10.2f} ({val['case']['premium']/val['case']['ev']*100 if val['case']['ev']>0 else 0:.1f}%)")
        
        # Grading potential
        print(f"\n{'─'*70}")
        print(f"GRADING POTENTIAL (top 10 cards from 1 box)")
        print(f"{'─'*70}")
        g = val['grading']
        print(f"  Raw value (top 10):  ${g['top_10_raw_value']:>10.2f}")
        print(f"  PSA 9 value:         ${g['graded_value']:>10.2f} ({g['psa9_multiplier']}x)")
        print(f"  Grading cost:        ${g['grading_cost']:>10.2f}")
        print(f"  Net value:           ${g['net_value']:>10.2f}")
        print(f"  ROI:                 {g['roi_pct']:>9.1f}%")
        
        # Optionality
        print(f"\n{'─'*70}")
        print(f"OPTIONALITY VALUE (keeping sealed)")
        print(f"{'─'*70}")
        o = val['optionality']
        print(f"  Current EV:          ${o['current_ev']:>10.2f}")
        print(f"  Future value (1yr):  ${o['future_value_1yr']:>10.2f} ({o['annual_appreciation']})")
        print(f"  Option value:        ${o['option_value_1yr']:>10.2f}")
        print(f"  Risk-adjusted EV:    ${o['expected_value_risk_adj']:>10.2f}")
        
        # Recommendation
        print(f"\n{'='*70}")
        print(f"RECOMMENDATION")
        print(f"{'='*70}")
        
        if val['case']['sealed_price'] > 0 and val['case']['ev'] > 0:
            case_premium = val['case']['premium']
            if case_premium > 0:
                print(f"  Case is SEALED at ${val['case']['sealed_price']:,.2f}")
                print(f"  Opened EV is ${val['case']['ev']:,.2f}")
                print(f"  Sealed premium: ${case_premium:,.2f} ({case_premium/val['case']['ev']*100:.1f}%)")
                print(f"\n  → Keep sealed if you believe in appreciation")
                print(f"  → Open if you want the cards NOW")
                print(f"  → Grade top 10 cards for maximum value")
            else:
                print(f"  Case is UNDERPRICED vs opened EV!")
                print(f"  Open immediately for instant profit")
        
        print(f"{'='*70}")


# ============================================================
# DEMO: Chinese Gem Pack Vol. 2 Eevee Case
# ============================================================
if __name__ == "__main__":
    product = SealedProductValuation(
        product_name="Pokemon Chinese Gem Pack Vol. 2 Eevee (CBB2C)",
        config={
            "boxes_per_case": 20,
            "packs_per_box": 15,
            "cards_per_pack": 4,
            "set_size": 140,
            "language": "Chinese (Simplified)",
            "region": "China",
            "release_date": "2025-05-16",
            # Pricing (estimated)
            "sealed_case_price": 600,  # Estimated case price
            "sealed_box_price": 35,    # Estimated box price
            "sealed_pack_price": 3.50, # Estimated pack price
            # Rarity distribution (from TCGCollector data)
            "rarity_dist": {
                "Common": {"packs_per": 3.0},
                "Uncommon": {"packs_per": 3.0},
                "Rare": {"packs_per": 4.5},
                "Double Rare": {"packs_per": 7.0},
                "Triple Rare": {"packs_per": 12.0},
            },
            # Estimated values (conservative Chinese market)
            "rarity_values": {
                "Common": 0.05,
                "Uncommon": 0.10,
                "Rare": 0.20,
                "Double Rare": 0.50,
                "Triple Rare": 1.50,
            },
        }
    )
    
    product.print_valuation()
