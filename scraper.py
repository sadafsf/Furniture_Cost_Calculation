# import requests
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from playwright.sync_api import sync_playwright
# import re
# import json

# # Helper function to clean price
# def clean_price(price_text):
#     price_text = re.sub(r'[^\d.]', '', price_text)  # Remove non-numeric characters
#     try:
#         return float(price_text)
#     except ValueError:
#         return None

# # Generalized function for scraping, with multiple strategies
# def fetch_furniture_data(url):
#     """Fetch furniture data from the provided URL with dynamic fallbacks."""
    
#     # Try with Requests (for static websites)
#     print(f"Attempting to fetch data from {url} using requests...")
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
    
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Try extracting data (works if site is static)
#         print("Trying to extract data using requests...")
#         return extract_furniture_data(soup, url)

#     except requests.exceptions.HTTPError as e:
#         print(f"Requests failed with error: {e}")
#         if e.response.status_code == 403:
#             print("Received 403 Forbidden. Trying Selenium...")

#     # If static scraping failed or 403 was returned, try Selenium
#     print(f"Attempting to fetch data from {url} using Selenium...")
#     try:
#         return fetch_furniture_data_with_selenium(url)
#     except Exception as e:
#         print(f"Selenium failed with error: {e}. Trying Playwright...")

#     # If Selenium fails, try Playwright
#     print(f"Attempting to fetch data from {url} using Playwright...")
#     try:
#         return fetch_furniture_data_with_playwright(url)
#     except Exception as e:
#         print(f"Playwright failed with error: {e}. Could not fetch data.")
    
#     return None, None, None, None


# # Function to extract data with BeautifulSoup (for requests and Selenium)
# def extract_furniture_data(soup, url):
#     """Extract furniture name and prices from the parsed HTML."""
#     # 1. Try extracting JSON-LD or structured data
#     print("Trying to extract JSON-LD data...")
#     name, sale_price, original_price = extract_json_data(soup)
#     if name and (sale_price or original_price):
#         print(f"Extracted JSON-LD Data: Name={name}, Sale Price={sale_price}, Original Price={original_price}")
#         return name, sale_price, original_price, url

#     # 2. Fallback to common HTML structure parsing
#     print("Fallback to extracting data from HTML structure...")
#     name = extract_name(soup)
#     sale_price, original_price = extract_prices(soup)

#     if name and (sale_price or original_price):
#         print(f"Extracted HTML Data: Name={name}, Sale Price={sale_price}, Original Price={original_price}")
#         return name, sale_price, original_price, url
    
#     print("Could not extract price information from the webpage.")
#     return None, None, None, None

# # Function for Selenium scraping
# def fetch_furniture_data_with_selenium(url):
#     """Fetch furniture data using Selenium."""
#     options = Options()
#     options.add_argument('--headless')  # Run in headless mode
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument("user-agent=Mozilla/5.0")

#     driver = webdriver.Chrome(options=options)
    
#     try:
#         driver.get(url)
#         page_source = driver.page_source
#         soup = BeautifulSoup(page_source, 'html.parser')
#         return extract_furniture_data(soup, url)
    
#     finally:
#         driver.quit()

# # Function for Playwright scraping
# def fetch_furniture_data_with_playwright(url):
#     """Fetch furniture data using Playwright for advanced JavaScript-heavy websites."""
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(url)
#         page.wait_for_selector('body')
#         html = page.content()
#         soup = BeautifulSoup(html, 'html.parser')
#         return extract_furniture_data(soup, url)

# # Functions for extracting JSON data, name, and prices
# def extract_json_data(soup):
#     try:
#         script_tags = soup.find_all('script', type='application/ld+json')
#         for script in script_tags:
#             try:
#                 data = json.loads(script.string)
#                 if 'name' in data and 'offers' in data:
#                     name = data['name']
#                     price_info = data['offers']
#                     if isinstance(price_info, list):
#                         sale_price = float(price_info[0].get('price', 0))
#                         original_price = float(price_info[0].get('priceCurrency', sale_price))
#                     else:
#                         sale_price = float(price_info.get('price', 0))
#                         original_price = sale_price
#                     return name, sale_price, original_price
#             except (ValueError, KeyError):
#                 continue
#         return None, None, None
#     except Exception as e:
#         print(f"Error extracting JSON data: {e}")
#         return None, None, None

# def extract_name(soup):
#     possible_name_classes = ['product-title', 'product-name', 'title', 'product-header', 'name']
#     for class_name in possible_name_classes:
#         name_tag = soup.find(class_=class_name)
#         if name_tag:
#             return name_tag.get_text(strip=True)
#     for tag in ['h1', 'h2', 'h3']:
#         name_tag = soup.find(tag)
#         if name_tag:
#             return name_tag.get_text(strip=True)
#     return None

# def extract_prices(soup):
#     price_classes = ['price', 'sale-price', 'current-price', 'price-sale', 'product-price']
#     sale_price, original_price = None, None

#     for class_name in price_classes:
#         price_tag = soup.find(class_=class_name)
#         if price_tag:
#             sale_price = clean_price(price_tag.get_text(strip=True))
#             break

#     if not sale_price:
#         price_tag = soup.find(string=re.compile(r'\$\d+(?:,\d{3})?(?:\.\d{2})?'))
#         if price_tag:
#             sale_price = clean_price(price_tag.strip())

#     return sale_price, original_price

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
    
    return None, None, None, None

# Function to extract data with BeautifulSoup (for aiohttp and Selenium)
def extract_furniture_data(soup, url):
    """Extract furniture name and prices from the parsed HTML."""
    # 1. Try extracting JSON-LD or structured data
    print("Trying to extract JSON-LD data...")
    name, sale_price, original_price = extract_json_data(soup)
    if name and (sale_price or original_price):
        print(f"Extracted JSON-LD Data: Name={name}, Sale Price={sale_price}, Original Price={original_price}")
        return name, sale_price, original_price, url

    # 2. Fallback to common HTML structure parsing
    print("Fallback to extracting data from HTML structure...")
    name = extract_name(soup)
    sale_price, original_price = extract_prices(soup)

    if name and (sale_price or original_price):
        print(f"Extracted HTML Data: Name={name}, Sale Price={sale_price}, Original Price={original_price}")
        return name, sale_price, original_price, url
    
    print("Could not extract price information from the webpage.")
    return None, None, None, None

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

# Functions for extracting JSON data, name, and prices
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
    """Extract the sale price and original price from the HTML."""
    price_classes = ['price', 'sale-price', 'current-price', 'price-sale', 'product-price']
    sale_price, original_price = None, None

    for class_name in price_classes:
        price_tag = soup.find(class_=class_name)
        if price_tag:
            sale_price = clean_price(price_tag.get_text(strip=True))
            break

    if not sale_price:
        price_tag = soup.find(string=re.compile(r'\$\d+(?:,\d{3})?(?:\.\d{2})?'))
        if price_tag:
            sale_price = clean_price(price_tag.strip())

    return sale_price, original_price
