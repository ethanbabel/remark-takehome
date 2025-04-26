import requests

class ShopifyClient:
    def __init__(self, store_url):
        self.store_url = store_url
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def fetch_products(self, limit=50, page=1):
        url = f"https://{self.store_url}/products.json?limit={limit}&page={page}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        products = response.json().get('products', [])
        return products
    
    def fetch_all_products(self, per_page=250):
        """Fetch all raw products from the store across all pages."""
        all_products = []
        page = 1
        while True:
            batch = self.fetch_products(limit=per_page, page=page)
            if not batch:
                break
            all_products.extend(batch)
            page += 1
        return all_products