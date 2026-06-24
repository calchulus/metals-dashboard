#!/usr/bin/env python3
"""
PSA Population Data Fetcher - Complete framework
API: api.psacard.com/publicapi
Quota: 100 calls/day (resets at midnight UTC)
"""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")
RESULTS_DIR = OUTPUT_DIR / "psa_results"
RESULTS_DIR.mkdir(exist_ok=True)

API_KEY = "E4AbYUoh7R3FQRCqZlnjFplmvM38B1fo8digTjcqzMNRhJHiw23-E11OzEdX66BH0hrp61qijuj3YT1oLV6b4-15qsRVLuFv9g6_t5rnLOLiLZ1JCxLf9zZV2d-ckZv0PpgB-ljcYQ6ZUR_ZtbFVCNsLWL5qEfp16ifqW_QqlEsQ_mGcqoQaLYuIb9vuVqQ749qL5EyTofcGSh7ulJ_X0M6aufNgoOqyGWxilz1ejPsgG9ltlayvrt81z9dsD2daRgt_i5cEiVCP2YQCYJI0nDUke-DHl_Ebam8pN1AU_2NUSKnY"

BASE = "https://api.psacard.com/publicapi"
QUOTA_FILE = RESULTS_DIR / "quota_tracker.json"


def load_quota():
    if QUOTA_FILE.exists():
        with open(QUOTA_FILE) as f:
            data = json.load(f)
        today = datetime.now().strftime("%Y-%m-%d")
        if data.get("date") != today:
            return {"date": today, "calls": 0}
        return data
    return {"date": datetime.now().strftime("%Y-%m-%d"), "calls": 0}


def save_quota(quota):
    with open(QUOTA_FILE, "w") as f:
        json.dump(quota, f)


def api_get(path):
    """Make API call with quota tracking."""
    quota = load_quota()
    if quota["calls"] >= 100:
        print(f"  QUOTA EXCEEDED ({quota['calls']}/100 calls today)")
        return None

    url = f"{BASE}{path}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
        "User-Agent": "PokemonTCGScraper/1.0"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        ctx = __import__('ssl').create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = __import__('ssl').CERT_NONE
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            quota["calls"] += 1
            save_quota(quota)
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"  RATE LIMITED (quota: {quota['calls']}/100)")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def get_cert(cert_number):
    """Get card details from PSA cert number."""
    return api_get(f"/cert/GetByCertNumber/{cert_number}")


def get_population(spec_id):
    """Get population data for a spec ID."""
    return api_get(f"/pop/GetPSASpecPopulation/{spec_id}")


# Known Base Set spec IDs (from research)
BASE_SET_SPECS = {
    "base_set_charizard": {"spec_id": 100, "name": "Charizard", "number": "4/102"},
    "base_set_pikachu": {"spec_id": 101, "name": "Pikachu", "number": "58/102"},
    "base_set_blastoise": {"spec_id": 102, "name": "Blastoise", "number": "2/102"},
    "base_set_venusaur": {"spec_id": 103, "name": "Venusaur", "number": "15/102"},
    "base_set_mewtwo": {"spec_id": 104, "name": "Mewtwo", "number": "10/102"},
    "base_set_alakazam": {"spec_id": 105, "name": "Alakazam", "number": "1/102"},
}


def fetch_all_populations():
    """Fetch population data for all tracked cards."""
    print("=" * 60)
    print("PSA Population Data Fetcher")
    print("=" * 60)

    quota = load_quota()
    print(f"API calls used today: {quota['calls']}/100")
    print(f"Remaining: {100 - quota['calls']}")
    print()

    results = {}
    for key, info in BASE_SET_SPECS.items():
        print(f"Fetching {info['name']} (SpecID: {info['spec_id']})...")
        data = get_population(info["spec_id"])
        if data:
            results[key] = {
                "spec_id": info["spec_id"],
                "name": info["name"],
                "number": info["number"],
                "data": data,
            }
            print(f"  ✓ Got population data")
        else:
            print(f"  ✗ Failed")
        time.sleep(2)  # Be nice to API

    # Save results
    output_file = RESULTS_DIR / "psa_populations.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} cards to {output_file}")

    return results


if __name__ == "__main__":
    fetch_all_populations()
