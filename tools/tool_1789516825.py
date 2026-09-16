import random
import textwrap

# Mock data for product categories and adjectives
CATEGORIES = [
    "electronics", "home & kitchen", "beauty", "sports", "toys", "fashion",
    "books", "pet supplies", "gaming", "outdoor"
]

ADJECTIVES = [
    "amazing", "revolutionary", "must-have", "incredible", "top-rated",
    "best-selling", "awesome", "trendy", "cutting‑edge", "high‑performance"
]

PRODUCT_NOUNS = [
    "headphones", "blender", "skin serum", "yoga mat", "drone", "smartwatch",
    "gaming chair", "backpack", "LED lamp", "electric kettle", "vacuum",
    "coffee maker", "sneakers", "wireless charger", "action camera"
]

FEATURES = [
    "long battery life", "crystal‑clear sound", "water‑resistant", "compact design",
    "easy to use", "affordable price", "premium quality", "eco‑friendly materials",
    "fast charging", "adjustable settings"
]

CALL_TO_ACTIONS = [
    "Swipe up to grab yours!", "Check the link in bio!", "Don’t miss out!",
    "Grab yours before it’s gone!", "Tap to shop now!", "Get it while it lasts!"
]

def mock_trending_products(n=5):
    """Generate a list of mock trending product dictionaries."""
    products = []
    for _ in range(n):
        product = {
            "name": f"{random.choice(ADJECTIVES).title()} {random.choice(PRODUCT_NOUNS)}",
            "category": random.choice(CATEGORIES),
            "price": round(random.uniform(10, 250), 2),
            "feature": random.choice(FEATURES),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews": random.randint(50, 5000)
        }
        products.append(product)
    return products

def generate_tiktok_script(product):
    """Create a ~30‑second TikTok script for a given product."""
    lines = [
        f"🔥 Hey TikTok! Check out this {product['name']} – the {product['feature']} you’ve been waiting for!",
        f"💰 Only ${product['price']} and it’s got a {product['rating']}⭐ rating from {product['reviews']} happy customers.",
        f"🛍️ Perfect for anyone into {product['category']}. Trust me, you’ll love how it {product['feature']}.",
        random.choice(CALL_TO_ACTIONS)
    ]
    script = " ".join(lines)
    # Ensure script length roughly fits 30 seconds (≈70‑80 words)
    if len(script.split()) > 80:
        script = " ".join(script.split()[:80])
    return textwrap.fill(script, width=70)

def main():
    trending = mock_trending_products()
    for idx, product in enumerate(trending, 1):
        print(f"--- Trending Product #{idx} ---")
        print(f"Name: {product['name']}")
        print(f"Category: {product['category']}")
        print(f"Price: ${product['price']}")
        print(f"Feature: {product['feature']}")
        print(f"Rating: {product['rating']} ⭐ ({product['reviews']} reviews)")
        print("\nTikTok Script:")
        print(generate_tiktok_script(product))
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()