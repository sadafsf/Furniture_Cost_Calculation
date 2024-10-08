import requests
from bs4 import BeautifulSoup
import re
import json

def fetch_furniture_data(url):
    """Fetch the furniture name, sale price, original price, or single price from the URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try extracting structured JSON-LD data
        name, sale_price, original_price = extract_json_data(soup)
        if name and (sale_price or original_price):
            return name, sale_price, original_price, url

        # Fallback to regular HTML parsing if JSON data is not found
        name = extract_name(soup)
        sale_price, original_price = extract_sale_and_original_prices(soup)

        # Handle case where no sale or original price is found and only a single price exists
        if not sale_price and not original_price:
            single_price = extract_single_price(soup)
            sale_price = single_price

        if name and (sale_price or original_price):
            return name, sale_price, original_price, url
        else:
            print("Could not extract price information from the webpage.")
            return None, None, None, None

    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None, None, None, None

def extract_json_data(soup):
    """Extract product information from JSON-LD or embedded JSON."""
    try:
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]  # Sometimes JSON-LD is a list

                if 'name' in data and 'offers' in data:
                    name = data['name']
                    price_info = data['offers']
                    if isinstance(price_info, list):
                        sale_price = float(price_info[0].get('price', 0))
                        original_price = float(price_info[0].get('priceCurrency', sale_price))
                    else:
                        sale_price = float(price_info.get('price', 0))
                        original_price = sale_price

                    return name, sale_price, original_price
            except (ValueError, KeyError):
                continue

        return None, None, None
    except Exception as e:
        print(f"Error extracting JSON data: {e}")
        return None, None, None

def extract_name(soup):
    """Extract the product name from the HTML structure."""
    name_tag = soup.find('h1')  # Common for product names
    if name_tag:
        return name_tag.get_text(strip=True)

    possible_name_classes = ['product-title', 'product-name', 'title', 'product-header', 'name']
    for class_name in possible_name_classes:
        name_tag = soup.find(class_=class_name)
        if name_tag:
            return name_tag.get_text(strip=True)

    # Fallback to extracting the first heading found in case no specific class works
    for tag in ['h1', 'h2', 'h3']:
        name_tag = soup.find(tag)
        if name_tag:
            return name_tag.get_text(strip=True)

    print("Could not find the product name.")
    return None

def extract_sale_and_original_prices(soup):
    """Extract sale and original prices from HTML, if available."""
    sale_price, original_price = None, None

    # Try capturing price ranges (e.g., "$299 - $499")
    price_range_tag = soup.find(string=re.compile(r'\$\d+(?:,\d{3})? - \$\d+(?:,\d{3})?'))
    if price_range_tag:
        price_range = price_range_tag.strip().split('-')
        sale_price = clean_price(price_range[0])
        original_price = clean_price(price_range[1])
        return sale_price, original_price

    # Try extracting sale and original prices from common classes
    sale_price_class = ['price-sale', 'price-discount', 'sale-price', 'current-price', 'price-now']
    original_price_class = ['price-original', 'price-regular', 'original-price', 'was-price']

    for class_name in sale_price_class:
        price_tag = soup.find(class_=class_name)
        if price_tag:
            sale_price_text = price_tag.get_text(strip=True)
            sale_price = clean_price(sale_price_text)
            break

    for class_name in original_price_class:
        price_tag = soup.find(class_=class_name)
        if price_tag:
            original_price_text = price_tag.get_text(strip=True)
            original_price = clean_price(original_price_text)
            break

    # If no sale price is found, fallback to original price as the main price
    if not sale_price and original_price:
        sale_price = original_price
        original_price = None

    return sale_price, original_price

def extract_single_price(soup):
    """Extract a single price when neither sale nor original price is found."""
    price_tag = soup.find(string=re.compile(r'\$\d+(?:,\d{3})?(?:\.\d{2})?'))
    if price_tag:
        price = clean_price(price_tag.strip())
        return price

    print("Could not find any price on the page.")
    return None

def clean_price(price_text):
    """Clean the price text and convert to a float."""
    price_text = re.sub(r'[^\d.]', '', price_text)  # Remove non-numeric characters
    try:
        return float(price_text)
    except ValueError:
        return None
