#!/usr/bin/env python3
"""
PSA Optimized Fetcher - Maximize data per API call
Strategy: 1 cert → spec_id → full population (20+ data points per 2 calls)
Plus local caching to never waste repeat calls
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
CACHE_DIR = RESULTS_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)
QUOTA_FILE = RESULTS_DIR / "quota.json"


def load_quota():
    today = datetime.now().strftime("%Y-%m-%d")
    if QUOTA_FILE.exists():
        with open(QUOTA_FILE) as f:
            data = json.load(f)
        if data.get("date") == today:
            return data
    return {"date": today, "calls": 0, "log": []}


def save_quota(quota):
    with open(QUOTA_FILE, "w") as f:
        json.dump(quota, f, indent=2)


def api_get(path, label=""):
    """Cached API call with quota tracking."""
    quota = load_quota()
    if quota["calls"] >= 100:
        print(f"  [QUOTA] {quota['calls']}/100 used today")
        return None

    # Check cache first
    cache_key = path.replace("/", "_").replace("?", "_")
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            print(f"  [CACHE HIT] {label}")
            return json.load(f)

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
            data = json.loads(resp.read().decode("utf-8"))
            quota["calls"] += 1
            quota["log"].append({"path": path, "time": datetime.now().isoformat()})
            save_quota(quota)

            # Cache the result
            with open(cache_file, "w") as f:
                json.dump(data, f)

            return data
    except urllib.error.HTTPError as e:
        print(f"  [HTTP {e.code}] {label}")
        return None
    except Exception as e:
        print(f"  [ERROR] {label}: {e}")
        return None


# ============================================================
# High-value cert numbers (known Pokemon cards from testing)
# ============================================================
KNOWN_CERTS = {
    "base_set_charizard": {"cert": "4", "name": "Base Set Charizard"},
    "base_set_pikachu": {"cert": "10", "name": "Base Set Pikachu"},
    "base_set_blastoise": {"cert": "100", "name": "Base Set Blastoise"},
    "hidden_fates_sv49": {"cert": "1000000", "name": "Hidden Fates SV49"},
}


def get_cert_and_pop(cert_number, label=""):
    """Get cert info AND population in 2 calls."""
    print(f"  [{label}] Fetching cert {cert_number}...")
    cert_data = api_get(f"/cert/GetByCertNumber/{cert_number}", label)
    if not cert_data or not cert_data.get("PSACert"):
        return None

    cert = cert_data["PSACert"]
    spec_id = cert.get("SpecID")

    print(f"  [{label}] Got cert → SpecID {spec_id}, fetching population...")
    pop_data = api_get(f"/pop/GetPSASpecPopulation/{spec_id}", label)

    return {
        "cert_number": cert.get("CertNumber"),
        "spec_id": spec_id,
        "brand": cert.get("Brand"),
        "card_number": cert.get("CardNumber"),
        "subject": cert.get("Subject"),
        "grade": cert.get("CardGrade"),
        "year": cert.get("Year"),
        "population": pop_data,
    }


def fetch_known_cards():
    """Fetch data for all known high-value cards."""
    print("=" * 60)
    print("PSA Optimized Fetcher")
    print("Strategy: cert → spec_id → full population (2 calls/card)")
    print("=" * 60)

    quota = load_quota()
    print(f"\nQuota: {quota['calls']}/100 calls used today")
    print(f"Available: {100 - quota['calls']} calls")
    print(f"Cards to fetch: {len(KNOWN_CERTS)} (need ~{len(KNOWN_CERTS)*2} calls)")
    print()

    if 100 - quota["calls"] < len(KNOWN_CERTS) * 2:
        print("WARNING: Not enough quota for all cards!")
        print("Fetching what we can...\n")

    results = {}
    for key, info in KNOWN_CERTS.items():
        if quota["calls"] >= 98:  # Leave 2 calls buffer
            print("Quota nearly exhausted, stopping.")
            break

        data = get_cert_and_pop(info["cert"], info["name"])
        if data:
            results[key] = data
            print(f"  ✓ {info['name']}: SpecID={data['spec_id']}, Grade={data['grade']}")
        else:
            print(f"  ✗ {info['name']}: Failed")

        quota = load_quota()
        time.sleep(1)

    # Save
    output = RESULTS_DIR / "psa_optimized_results.json"
    with open(output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Cards fetched: {len(results)}/{len(KNOWN_CERTS)}")
    print(f"API calls used: {quota['calls']}/100")
    print(f"Data points: ~{len(results) * 20} (grades 1-10 + qualifiers)")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    fetch_known_cards()
