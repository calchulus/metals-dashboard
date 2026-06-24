#!/usr/bin/env python3
"""
TCGplayer API Client Library
Documentation: https://docs.tcgplayer.com
Base URL: https://api.tcgplayer.com

Usage:
    client = TCGplayerClient(bearer_token="your_token")
    categories = client.catalog.get_categories()
    prices = client.pricing.get_product_prices(product_ids=[1234])
"""
import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, List, Any


class TCGplayerError(Exception):
    def __init__(self, status_code: int, message: str, errors: list = None):
        self.status_code = status_code
        self.message = message
        self.errors = errors or []
        super().__init__(f"TCGplayer API Error {status_code}: {message}")


class TCGplayerBase:
    """Base class for API communication."""

    BASE_URL = "https://api.tcgplayer.com"

    def __init__(self, bearer_token: str = None, timeout: int = 30):
        self.bearer_token = bearer_token
        self.timeout = timeout
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests

    def _request(self, method: str, path: str, body: dict = None,
                 params: dict = None) -> dict:
        """Make an API request with rate limiting."""
        # Rate limiting
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)

        url = f"{self.BASE_URL}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url += f"?{query}"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                self._last_request_time = time.time()
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            try:
                error_data = json.loads(error_body)
            except json.JSONDecodeError:
                error_data = {"message": error_body}
            raise TCGplayerError(
                e.code,
                error_data.get("message", str(e)),
                error_data.get("errors", [])
            )
        except Exception as e:
            raise TCGplayerError(0, str(e))


# ============================================================
# CATALOG ENDPOINTS
# ============================================================
class CatalogClient(TCGplayerBase):
    """TCGplayer Catalog API endpoints."""

    def get_categories(self) -> dict:
        """GET /catalog/categories - List all categories."""
        return self._request("GET", "/catalog/categories")

    def get_category(self, category_ids: List[int]) -> dict:
        """GET /catalog/categories/{categoryIds} - Get category details."""
        ids = ",".join(str(i) for i in category_ids)
        return self._request("GET", f"/catalog/categories/{ids}")

    def get_category_search_manifest(self, category_id: int) -> dict:
        """GET /catalog/categories/{categoryId}/search/manifest"""
        return self._request("GET", f"/catalog/categories/{category_id}/search/manifest")

    def search_category(self, category_id: int, body: dict) -> dict:
        """POST /catalog/categories/{categoryId}/search"""
        return self._request("POST", f"/catalog/categories/{category_id}/search", body=body)

    def get_category_groups(self, category_id: int, limit: int = 100, offset: int = 0) -> dict:
        """GET /catalog/categories/{categoryId}/groups"""
        return self._request("GET", f"/catalog/categories/{category_id}/groups",
                           params={"limit": limit, "offset": offset})

    def get_category_rarities(self, category_id: int) -> dict:
        """GET /catalog/categories/{categoryId}/rarities"""
        return self._request("GET", f"/catalog/categories/{category_id}/rarities")

    def get_category_printings(self, category_id: int) -> dict:
        """GET /catalog/categories/{categoryId}/printings"""
        return self._request("GET", f"/catalog/categories/{category_id}/printings")

    def get_category_conditions(self, category_id: int) -> dict:
        """GET /catalog/categories/{categoryId}/conditions"""
        return self._request("GET", f"/catalog/categories/{category_id}/conditions")

    def get_category_languages(self, category_id: int) -> dict:
        """GET /catalog/categories/{categoryId}/languages"""
        return self._request("GET", f"/catalog/categories/{category_id}/languages")

    def get_category_media(self, category_id: int) -> dict:
        """GET /catalog/categories/{categoryId}/media"""
        return self._request("GET", f"/catalog/categories/{category_id}/media")

    def get_groups(self, group_ids: List[int] = None, category_id: int = None,
                   limit: int = 100, offset: int = 0) -> dict:
        """GET /catalog/groups"""
        params = {"limit": limit, "offset": offset}
        if group_ids:
            params["groupId"] = ",".join(str(i) for i in group_ids)
        if category_id:
            params["categoryId"] = category_id
        return self._request("GET", "/catalog/groups", params=params)

    def get_group(self, group_ids: List[int]) -> dict:
        """GET /catalog/groups/{groupIds}"""
        ids = ",".join(str(i) for i in group_ids)
        return self._request("GET", f"/catalog/groups/{ids}")

    def get_group_media(self, group_ids: List[int]) -> dict:
        """GET /catalog/groups/{groupId}/media"""
        ids = ",".join(str(i) for i in group_ids)
        return self._request("GET", f"/catalog/groups/{ids}/media")

    def get_products(self, product_ids: List[int] = None, limit: int = 100,
                     offset: int = 0, productListings: bool = False) -> dict:
        """GET /catalog/products"""
        params = {"limit": limit, "offset": offset}
        if product_ids:
            params["productId"] = ",".join(str(i) for i in product_ids)
        if productListings:
            params["productListings"] = "true"
        return self._request("GET", "/catalog/products", params=params)

    def get_product(self, product_ids: List[int]) -> dict:
        """GET /catalog/products/{productIds}"""
        ids = ",".join(str(i) for i in product_ids)
        return self._request("GET", f"/catalog/products/{ids}")

    def get_product_by_gtin(self, gtin: str) -> dict:
        """GET /catalog/products/byGTIN/{gtin}"""
        return self._request("GET", f"/catalog/products/byGTIN/{gtin}")

    def get_product_skus(self, product_id: int) -> dict:
        """GET /catalog/products/{productId}/skus"""
        return self._request("GET", f"/catalog/products/{product_id}/skus")

    def get_product_also_purchased(self, product_id: int) -> dict:
        """GET /catalog/products/{productId}/alsopurchased"""
        return self._request("GET", f"/catalog/products/{product_id}/alsopurchased")

    def get_product_media(self, product_ids: List[int]) -> dict:
        """GET /catalog/products/{productId}/media"""
        ids = ",".join(str(i) for i in product_ids)
        return self._request("GET", f"/catalog/products/{ids}/media")

    def get_skus(self, sku_ids: List[int]) -> dict:
        """GET /catalog/skus/{skuIds}"""
        ids = ",".join(str(i) for i in sku_ids)
        return self._request("GET", f"/catalog/skus/{ids}")

    def get_conditions(self) -> dict:
        """GET /catalog/conditions"""
        return self._request("GET", "/catalog/conditions")

    def search_pokemon_cards(self, name: str = None, group_id: int = None,
                             rarity: str = None, limit: int = 100) -> dict:
        """Search for Pokemon cards (convenience method)."""
        # Pokemon category is typically 1
        body = {"filters": []}
        if name:
            body["filters"].append({"name": "productName", "values": [name]})
        if group_id:
            body["filters"].append({"name": "groupId", "values": [group_id]})
        if rarity:
            body["filters"].append({"name": "rarityName", "values": [rarity]})
        body["limit"] = limit
        return self.search_category(1, body)  # Category 1 = Pokemon


# ============================================================
# PRICING ENDPOINTS
# ============================================================
class PricingClient(TCGplayerBase):
    """TCGplayer Pricing API endpoints."""

    def get_market_price_by_sku(self, sku_id: int) -> dict:
        """GET /pricing/market/{skuId}"""
        return self._request("GET", f"/pricing/market/{sku_id}")

    def get_group_prices(self, group_ids: List[int]) -> dict:
        """GET /pricing/group/{groupIds}"""
        ids = ",".join(str(i) for i in group_ids)
        return self._request("GET", f"/pricing/group/{ids}")

    def get_product_prices(self, product_ids: List[int]) -> dict:
        """GET /pricing/product/{productIds}"""
        ids = ",".join(str(i) for i in product_ids)
        return self._request("GET", f"/pricing/product/{ids}")

    def get_sku_prices(self, sku_ids: List[int]) -> dict:
        """GET /pricing/sku/{skuIds}"""
        ids = ",".join(str(i) for i in sku_ids)
        return self._request("GET", f"/pricing/sku/{ids}")

    def get_product_buylist_prices(self, product_ids: List[int]) -> dict:
        """GET /pricing/buylist/product/{productIds}"""
        ids = ",".join(str(i) for i in product_ids)
        return self._request("GET", f"/pricing/buylist/product/{ids}")

    def get_sku_buylist_prices(self, sku_ids: List[int]) -> dict:
        """GET /pricing/buylist/sku/{skuIds}"""
        ids = ",".join(str(i) for i in sku_ids)
        return self._request("GET", f"/pricing/buylist/sku/{ids}")

    def get_group_buylist_prices(self, group_ids: List[int]) -> dict:
        """GET /pricing/buylist/group/{groupIds}"""
        ids = ",".join(str(i) for i in group_ids)
        return self._request("GET", f"/pricing/buylist/group/{ids}")


# ============================================================
# INVENTORY ENDPOINTS
# ============================================================
class InventoryClient(TCGplayerBase):
    """TCGplayer Inventory API endpoints."""

    def get_product_list_by_id(self, list_id: int) -> dict:
        """GET /inventory/productlist/{listId}"""
        return self._request("GET", f"/inventory/productlist/{list_id}")

    def get_product_list_by_key(self, list_key: str) -> dict:
        """GET /inventory/productlist/key/{listKey}"""
        return self._request("GET", f"/inventory/productlist/key/{list_key}")

    def get_product_lists(self) -> dict:
        """GET /inventory/productlist"""
        return self._request("GET", "/inventory/productlist")

    def create_product_list(self, body: dict) -> dict:
        """POST /inventory/productlist"""
        return self._request("POST", "/inventory/productlist", body=body)


# ============================================================
# STORE ENDPOINTS
# ============================================================
class StoresClient(TCGplayerBase):
    """TCGplayer Stores API endpoints."""

    def get_identity(self) -> dict:
        """GET /store/{storeKey}/identity"""
        return self._request("GET", "/store/identity")

    def get_store_info(self, store_key: str) -> dict:
        """GET /store/{storeKey}/info"""
        return self._request("GET", f"/store/{store_key}/info")

    def search_stores(self, **params) -> dict:
        """GET /store"""
        return self._request("GET", "/store", params=params)

    def get_inventory(self, store_key: str, limit: int = 100, offset: int = 0) -> dict:
        """GET /store/{storeKey}/inventory"""
        return self._request("GET", f"/store/{store_key}/inventory",
                           params={"limit": limit, "offset": offset})

    def get_sku_quantity(self, store_key: str, sku_id: int) -> dict:
        """GET /store/{storeKey}/inventory/sku/{skuId}"""
        return self._request("GET", f"/store/{store_key}/inventory/sku/{sku_id}")

    def update_sku_quantity(self, store_key: str, sku_id: int, quantity: int) -> dict:
        """POST /store/{storeKey}/inventory/sku/{skuId}"""
        return self._request("POST", f"/store/{store_key}/inventory/sku/{sku_id}",
                           body={"quantity": quantity})

    def get_orders(self, store_key: str, **params) -> dict:
        """GET /store/{storeKey}/orders"""
        return self._request("GET", f"/store/{store_key}/orders", params=params)

    def get_order_details(self, store_key: str, order_number: str) -> dict:
        """GET /store/{storeKey}/orders/{orderNumber}"""
        return self._request("GET", f"/store/{store_key}/orders/{order_number}")

    def get_buylist_products(self, store_key: str) -> dict:
        """GET /store/{storeKey}/buylist/products"""
        return self._request("GET", f"/store/{store_key}/buylist/products")


# ============================================================
# MAIN CLIENT
# ============================================================
class TCGplayerClient:
    """
    Main TCGplayer API client.

    Usage:
        client = TCGplayerClient(bearer_token="your_token")

        # Catalog
        categories = client.catalog.get_categories()
        products = client.catalog.get_products(product_ids=[1234])

        # Pricing
        prices = client.pricing.get_product_prices(product_ids=[1234])

        # Inventory
        lists = client.inventory.get_product_lists()

        # Stores
        store = client.stores.get_identity()
    """

    def __init__(self, bearer_token: str = None, timeout: int = 30):
        self.catalog = CatalogClient(bearer_token, timeout)
        self.pricing = PricingClient(bearer_token, timeout)
        self.inventory = InventoryClient(bearer_token, timeout)
        self.stores = StoresClient(bearer_token, timeout)

    def set_token(self, token: str):
        """Update the bearer token for all sub-clients."""
        self.catalog.bearer_token = token
        self.pricing.bearer_token = token
        self.inventory.bearer_token = token
        self.stores.bearer_token = token

    def get_pokemon_category_id(self) -> int:
        """Helper: Get the Pokemon TCG category ID (usually 1)."""
        return 1

    def search_pokemon(self, name: str = None, set_name: str = None,
                       rarity: str = None, limit: int = 100) -> dict:
        """Convenience: Search Pokemon cards."""
        return self.catalog.search_pokemon_cards(name, rarity=rarity, limit=limit)

    def get_product_with_price(self, product_id: int) -> dict:
        """Get product details combined with pricing."""
        product = self.catalog.get_product([product_id])
        prices = self.pricing.get_product_prices([product_id])
        return {"product": product, "prices": prices}

    def get_set_summary(self, group_id: int) -> dict:
        """Get a set's summary with all products and their prices."""
        group = self.catalog.get_group([group_id])
        prices = self.pricing.get_group_prices([group_id])
        return {"group": group, "prices": prices}


# ============================================================
# STANDALONE FUNCTIONALITY (no auth required for some endpoints)
# ============================================================
def get_public_categories():
    """Get all TCGplayer categories (no auth needed)."""
    client = TCGplayerBase()
    return client._request("GET", "/catalog/categories")


def get_public_group_prices(group_ids: List[int]):
    """Get group prices (some endpoints public)."""
    client = TCGplayerBase()
    ids = ",".join(str(i) for i in group_ids)
    return client._request("GET", f"/pricing/group/{ids}")


if __name__ == "__main__":
    print("=" * 60)
    print("TCGplayer API Client Library")
    print("Docs: https://docs.tcgplayer.com")
    print("=" * 60)
    print()
    print("Modules:")
    print("  CatalogClient  - Categories, Groups, Products, SKUs, Search")
    print("  PricingClient  - Market prices, Buylist prices")
    print("  InventoryClient - Product Lists")
    print("  StoresClient   - Store management, Orders, Inventory")
    print()
    print("Usage:")
    print("  from tcgplayer_client import TCGplayerClient")
    print("  client = TCGplayerClient(bearer_token='xxx')")
    print("  products = client.catalog.get_products(product_ids=[1234])")
    print("  prices = client.pricing.get_product_prices(product_ids=[1234])")
    print()
    print("Example (Pokemon category = 1):")
    print("  # Get all Pokemon sets")
    print("  groups = client.catalog.get_category_groups(1)")
    print()
    print("  # Search for Charizard cards")
    print("  results = client.catalog.search_pokemon(name='Charizard')")
    print()
    print("  # Get pricing for a product")
    print("  prices = client.pricing.get_product_prices([12345])")
