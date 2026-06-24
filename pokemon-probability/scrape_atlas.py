#!/usr/bin/env python3
"""
Pokemon TCG Scraper - Atlas-based approach
Uses Firecrawl API pattern from atlas-scraper for:
  - Batch scraping with retry
  - Rate limiting with exponential backoff
  - Progress tracking and resume
  - Clean markdown output for LLM consumption
"""
import json
import os
import sys
import time
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("/Users/calvinchu/Desktop/mimo/pokemon-probability")
RESULTS_DIR = OUTPUT_DIR / "scrape_results"
RESULTS_DIR.mkdir(exist_ok=True)

# Firecrawl API config (from atlas-scraper pattern)
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1"
BATCH_SIZE = 10  # URLs per batch (conservative for Pokemon TCG)

# Rate limiting config
BASE_DELAY = 2.0  # seconds between requests
MAX_RETRIES = 5
BACKOFF_FACTOR = 2.0


class RateLimitedScraper:
    """Scraper with rate limiting, retries, and progress tracking."""

    def __init__(self, name="default"):
        self.name = name
        self.progress_file = RESULTS_DIR / f"{name}_progress.json"
        self.results_file = RESULTS_DIR / f"{name}_results.json"
        self.completed = set()
        self.results = []
        self._load_progress()

    def _load_progress(self):
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                data = json.load(f)
                self.completed = set(data.get("completed", []))
                print(f"Resumed: {len(self.completed)} URLs already scraped")

    def _save_progress(self):
        with open(self.progress_file, "w") as f:
            json.dump({
                "completed": list(self.completed),
                "total_scraped": len(self.results),
                "timestamp": datetime.now().isoformat()
            }, f)

    def _save_results(self):
        with open(self.results_file, "w") as f:
            json.dump(self.results, f, indent=2)

    def _url_hash(self, url):
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def fetch_url(self, url, retries=MAX_RETRIES):
        """Fetch URL with exponential backoff retry."""
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/json",
                    "Accept-Language": "en-US,en;q=0.9",
                })
                ctx = __import__('ssl').create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = __import__('ssl').CERT_NONE
                with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                    return resp.read().decode("utf-8", errors="replace")
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    delay = BASE_DELAY * (BACKOFF_FACTOR ** attempt)
                    print(f"    429 rate limited, waiting {delay:.0f}s...")
                    time.sleep(delay)
                elif e.code == 403:
                    delay = BASE_DELAY * (BACKOFF_FACTOR ** attempt) * 2
                    print(f"    403 forbidden, waiting {delay:.0f}s...")
                    time.sleep(delay)
                elif e.code == 404:
                    return None
                else:
                    time.sleep(BASE_DELAY)
            except Exception as e:
                time.sleep(BASE_DELAY * (attempt + 1))
        return None

    def scrape_urls(self, urls, delay=BASE_DELAY):
        """Scrape a list of URLs with rate limiting and progress tracking."""
        new_urls = [u for u in urls if self._url_hash(u) not in self.completed]
        print(f"Scraping {len(new_urls)} new URLs ({len(self.completed)} already done)...")

        for i, url in enumerate(new_urls):
            url_id = self._url_hash(url)
            print(f"  [{i+1}/{len(new_urls)}] {url[:60]}...", end=" ", flush=True)

            html = self.fetch_url(url)
            if html:
                self.results.append({
                    "url": url,
                    "hash": url_id,
                    "content": html,
                    "length": len(html),
                    "timestamp": datetime.now().isoformat()
                })
                self.completed.add(url_id)
                print(f"OK ({len(html):,} bytes)")
            else:
                print("FAILED")

            # Save progress every 5 URLs
            if (i + 1) % 5 == 0:
                self._save_progress()
                self._save_results()

            time.sleep(delay)

        self._save_progress()
        self._save_results()
        print(f"\nDone: {len(self.results)} results saved")


class FirecrawlBatchScraper:
    """Uses Firecrawl API for batch scraping (from atlas-scraper pattern)."""

    def __init__(self, api_key=None):
        self.api_key = api_key or FIRECRAWL_API_KEY
        self.api_url = FIRECRAWL_API_URL

    def scrape_batch(self, urls):
        """Submit batch scrape to Firecrawl API."""
        if not self.api_key:
            print("No Firecrawl API key - falling back to single URL mode")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "urls": urls,
            "formats": ["markdown"],
            "onlyMainContent": True
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.api_url}/batch/scrape",
            data=data,
            headers=headers,
            method="POST"
        )

        try:
            ctx = __import__('ssl').create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = __import__('ssl').CERT_NONE
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"Firecrawl error: {e}")
            return None


# ============================================================
# Pokemon TCG Specific Scraping
# ============================================================

def build_tcgdex_urls():
    """Build TCGdex API URLs for all sets."""
    base = "https://api.tcgdex.net/v2/en"
    # Core Pokemon TCG sets (English)
    set_ids = [
        "base1", "base2", "base3", "base4", "base5",
        "gym1", "gym2", "neo1", "neo2", "neo3", "neo4",
        "ecard1", "ecard2", "ecard3",
        "ex1", "ex2", "ex3", "ex4", "ex5", "ex6", "ex7", "ex8", "ex9",
        "ex10", "ex11", "ex12", "ex13", "ex14", "ex15", "ex16",
        "dp1", "dp2", "dp3", "dp4", "dp5", "dp6", "dp7",
        "pl1", "pl2", "pl3", "pl4",
        "hgss1", "hgss2", "hgss3", "hgss4", "col1",
        "bw1", "bw2", "bw3", "bw4", "bw5", "bw6", "bw7", "bw8", "bw9", "bw10", "bw11",
        "xy1", "xy2", "xy3", "xy4", "xy5", "xy6", "xy7", "xy8", "xy9", "xy10", "xy11", "xy12",
        "sm1", "sm2", "sm3", "sm4", "sm5", "sm6", "sm7", "sm8", "sm9", "sm10", "sm11", "sm12",
        "swsh1", "swsh2", "swsh3", "swsh4", "swsh5", "swsh6", "swsh7", "swsh8", "swsh9", "swsh10", "swsh11", "swsh12", "swsh12.5",
        "sv01", "sv02", "sv03", "sv03.5", "sv04", "sv04.5", "sv05", "sv06", "sv06.5", "sv07", "sv08", "sv08.5", "sv09", "sv10",
        "me01", "me02", "me02.5", "me03", "me04",
    ]
    return [f"{base}/sets/{sid}" for sid in set_ids]


def build_limitless_urls():
    """Build Limitless TCG URLs for all sets."""
    set_codes = [
        "CRI", "POR", "ASC", "PFL", "MEG", "MEP",
        "BLK", "WHT", "DRI", "JTG", "PRE", "SSP", "SCR", "SFA", "TWM",
        "TEF", "PAF", "PAR", "MEW", "OBF", "PAL", "SVI", "SVE", "SVP",
        "CRZ", "SIT", "LOR", "PGO", "ASR", "BRS", "FST", "CEL", "EVS",
        "CRE", "BST", "SHF", "VIV", "CPA", "DAA", "RCL", "SSH", "SP",
        "CEC", "HIF", "UNM", "UNB", "DET", "TEU", "LOT", "DRM", "CES",
        "FLI", "UPR", "CIN", "SLG", "BUS", "GRI", "SUM", "SMP",
        "EVO", "STS", "FCO", "GEN", "BKP", "BKT", "AOR", "ROS", "DCR",
        "PRC", "PHF", "FFI", "FLF", "XY", "KSS", "XYP",
        "LTR", "PLB", "PLF", "PLS", "BCR", "DRV", "DRX", "DEX", "NXD",
        "NVI", "EPO", "BLW", "BWP",
        "CL", "TM", "UD", "UL", "HS", "HSP",
        "RM", "AR", "SV", "RR", "P9", "PL", "SF", "P8", "LA", "MD",
        "P7", "GE", "SW", "P6", "MT", "DP", "DPP",
        "P5", "PK", "DF", "CG", "P4", "HP", "P3", "LM", "DS", "UF",
        "P2", "EM", "UG", "TRR", "FRLG", "DK", "SS", "RS", "TL",
        "HL", "EX", "GR", "FL", "DX",
        "N4", "N3", "N2", "N1", "SI",
        "BS", "JU", "FO", "TR", "G1", "G2", "EC1", "EC2", "EC3", "LC",
    ]
    return [f"https://limitlesstcg.com/cards/{code}" for code in set_codes]


def run_tcgdex_scraper():
    """Run TCGdex API scraper using atlas pattern."""
    print("=" * 60)
    print("TCGdex Scraper (Atlas Pattern)")
    print("=" * 60)

    scraper = RateLimitedScraper("tcgdex")
    urls = build_tcgdex_urls()
    print(f"Total URLs: {len(urls)}")
    scraper.scrape_urls(urls, delay=0.5)  # TCGdex allows faster requests

    # Parse and save structured data
    all_data = []
    for result in scraper.results:
        try:
            data = json.loads(result["content"])
            if "cards" in data:
                for card in data["cards"]:
                    card["set_id"] = data.get("id", "")
                    card["set_name"] = data.get("name", "")
                all_data.extend(data["cards"])
        except json.JSONDecodeError:
            pass

    # Save as CSV
    import csv
    csv_path = OUTPUT_DIR / "tcgdex_full_cards.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["set_id", "set_name", "card_id", "local_id", "name", "image"])
        writer.writeheader()
        writer.writerows(all_data)

    print(f"\nSaved {len(all_data)} cards to tcgdex_full_cards.csv")
    return all_data


def run_limitless_scraper():
    """Run Limitless TCG scraper using atlas pattern."""
    print("\n" + "=" * 60)
    print("Limitless TCG Scraper (Atlas Pattern)")
    print("=" * 60)

    scraper = RateLimitedScraper("limitless")
    urls = build_limitless_urls()
    print(f"Total URLs: {len(urls)}")
    scraper.scrape_urls(urls, delay=3.0)  # Limitless needs more time

    print(f"\nSaved {len(scraper.results)} page results")


if __name__ == "__main__":
    print("Pokemon TCG Scraper - Atlas-based Approach")
    print("Pattern from: atlas-scraper (ImpossibleFinance)")
    print()

    # Run TCGdex scraper (API, fast)
    run_tcgdex_scraper()

    # Run Limitless scraper (HTML, slower)
    # run_limitless_scraper()  # Uncomment for full scrape

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Results saved to: {RESULTS_DIR}")
