# Furniture Tracker Web Application

## Project Overview
The Furniture Tracker is a web application designed to help users manage their furniture items, organize them by room, and calculate the total price for each room and overall. Users can add items by manually entering details or by fetching product information from URLs (from furniture stores). The app also allows for updating and removing furniture items.

## Features
- **Add Furniture**: Users can add new furniture items manually or fetch product details by providing a URL from supported furniture stores.
- **View Furniture by Room**: View a categorized list of all furniture items, sorted by room, with prices displayed.
- **Price Calculations**: Automatically calculates total prices for each room and the overall total for all items.
- **Update Furniture**: Modify furniture details like price, room, or URL.
- **Remove Furniture**: Delete unwanted furniture items from the tracker.
- **Responsive Design**: The application is styled to be mobile-friendly and responsive across devices.

## Tech Stack
- **Frontend**:
  - HTML
  - CSS (with optional Bootstrap)
  - JavaScript

- **Backend**:
  - **Python** (with Flask): Handles the server-side logic, routes, and data storage.
  - **Selenium & BeautifulSoup**: Used for scraping data from websites to fetch furniture details.
  - **JSON**: Used for storing and managing the furniture data locally.

## Installation Instructions

### Prerequisites
Make sure the following software is installed on your machine:
- **Python 3.x**
- **Flask**: Install Flask using pip:
  ```bash
  pip install flask
  pip install selenium beautifulsoup4
