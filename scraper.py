
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
import re
import json
import aiohttp
import asyncio

# Helper function to clean price
def clean_price(price_text):
    price_text = re.sub(r'[^\d.]', '', price_text)  # Remove non-numeric characters
    try:
        return float(price_text)
    except ValueError:
        return None

# Asynchronous fetch with aiohttp
async def fetch_with_aiohttp(url, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()
# Generalized function for scraping, with multiple strategies
def fetch_furniture_data(url):
    """Fetch furniture data from the provided URL with dynamic fallbacks."""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # First, attempt async requests
    print(f"Attempting to fetch data from {url} using aiohttp...")
    try:
        loop = asyncio.get_event_loop()
        html_content = loop.run_until_complete(fetch_with_aiohttp(url, headers))
        soup = BeautifulSoup(html_content, 'html.parser')
        return extract_furniture_data(soup, url)
    except Exception as e:
        print(f"Requests failed with error: {e}")
        print("Trying Playwright...")

    # If requests fail, try Playwright
    try:
        return fetch_furniture_data_with_playwright(url)
    except Exception as e:
        print(f"Playwright failed with error: {e}. Trying Selenium...")

    # If Playwright fails, try Selenium
    try:
        return fetch_furniture_data_with_selenium(url)
    except Exception as e:
        print(f"Selenium failed with error: {e}. Could not fetch data.")
    
    return None, None, None, None, None, None, None  # Return None for all fields if fetching fails

def extract_furniture_data(soup, url):
    """Extract furniture data including price ranges and sale prices."""
    
    name = extract_name(soup)
    sale_price, original_price, min_price, max_price = extract_prices(soup)  # Updated to extract price ranges
    image_url = extract_image_url(soup)
    
    return name, original_price, sale_price, min_price, max_price, image_url, url


# Function for Selenium scraping
def fetch_furniture_data_with_selenium(url):
    """Fetch furniture data using Selenium."""
    options = Options()
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.javascript": 1  # Disable loading images and stylesheets
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return extract_furniture_data(soup, url)
    
    finally:
        driver.quit()

# Function for Playwright scraping
def fetch_furniture_data_with_playwright(url):
    """Fetch furniture data using Playwright for advanced JavaScript-heavy websites."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector('.price', timeout=5000)  # Adjust based on your selector
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        return extract_furniture_data(soup, url)

# Functions for extracting JSON data, name, prices, colors, and image URL
def extract_json_data(soup):
    """Extract JSON-LD data if available in the HTML."""
    try:
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                data = json.loads(script.string)
                if 'name' in data and 'offers' in data:
                    name = data['name']
                    price_info = data['offers']
                    if isinstance(price_info, list):
                        # If it's a list, we can have multiple offers (like for different configurations)
                        min_price = float(price_info[0].get('price', 0))
                        max_price = float(price_info[-1].get('price', 0))  # Assume the last entry is the max price
                    else:
                        min_price = float(price_info.get('price', 0))
                        max_price = min_price  # No range, so min and max are the same
                    
                    # Sale price, if any
                    sale_price = price_info.get('price', None)
                    
                    return name, min_price, max_price, sale_price
            except (ValueError, KeyError):
                continue
        return None, None, None, None
    except Exception as e:
        print(f"Error extracting JSON data: {e}")
        return None, None, None, None


def extract_name(soup):
    """Extract the name of the furniture item."""
    possible_name_classes = ['product-title', 'product-name', 'title', 'product-header', 'name']
    for class_name in possible_name_classes:
        name_tag = soup.find(class_=class_name)
        if name_tag:
            return name_tag.get_text(strip=True)
    for tag in ['h1', 'h2', 'h3']:
        name_tag = soup.find(tag)
        if name_tag:
            return name_tag.get_text(strip=True)
    return None

def extract_prices(soup):
    """Extract the sale price, original price, min price, and max price from the HTML."""
    sale_price = None
    original_price = None
    min_price = None
    max_price = None

    price_classes = ['price', 'sale-price', 'current-price', 'price-sale', 'product-price']

    # Try to extract a range of prices (min/max)
    min_price_tag = soup.find(class_='min-price')  # Update based on website class
    max_price_tag = soup.find(class_='max-price')  # Update based on website class

    if min_price_tag and max_price_tag:
        min_price = clean_price(min_price_tag.get_text(strip=True))
        max_price = clean_price(max_price_tag.get_text(strip=True))

    # If no min/max, extract sale and original price
    for class_name in price_classes:
        price_tag = soup.find(class_=class_name)
        if price_tag:
            sale_price = clean_price(price_tag.get_text(strip=True))
            break

    if not sale_price:
        price_tag = soup.find(string=re.compile(r'\$\d+(?:,\d{3})?(?:\.\d{2})?'))
        if price_tag:
            sale_price = clean_price(price_tag.strip())

    return sale_price, original_price, min_price, max_price


def extract_colors(soup):
    """Extract available colors for the furniture item."""
    colors = []
    
    # Example: Assume color options are stored in elements with the class 'color-option' or 'color-swatch'
    color_tags = soup.find_all(class_='color-option')  # Adjust based on your website's structure
    if not color_tags:
        color_tags = soup.find_all(class_='color-swatch')  # Another possible class name for colors

    for tag in color_tags:
        # Sometimes colors are stored as data attributes or in text
        color = tag.get('data-color') or tag.get_text(strip=True)
        if color:
            colors.append(color)

    # If no colors found, return a default or None
    if not colors:
        print("No colors found")
        return ["default"]

    return colors

def extract_image_url(soup):
    """Extract the furniture image URL from the HTML structure."""
    # Look for the primary product image in the page
    image_tag = soup.find('img', class_='product-image')  # Adjust the class based on actual website structure
    if not image_tag:
        # Try another possible image container (e.g., images in 'img-main' or 'image-gallery')
        image_tag = soup.find('img', class_='img-main') or soup.find('img', class_='image-gallery')

    if image_tag and image_tag.get('src'):
        return image_tag['src']  # Return the source URL of the image
    else:
        print("No image URL found.")
        return None
