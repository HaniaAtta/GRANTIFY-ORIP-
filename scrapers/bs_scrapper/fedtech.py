import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# === Configure logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === FedTech-specific open keywords ===
open_keywords = [
    "explore solutions"
]

# === Keyword + Date Logic ===
def is_grant_open(text):
    text = text.lower()

    has_open_keyword = any(keyword in text for keyword in open_keywords)
    if not has_open_keyword:
        return False

    # Look for date formats like "20 June 2024" or "June 20, 2024"
    date_patterns = [
        r'(\d{1,2} \w+ \d{4})',
        r'(\w+ \d{1,2}, \d{4})'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            for fmt in ("%d %B %Y", "%B %d, %Y"):
                try:
                    found_date = datetime.strptime(date_str, fmt)
                    if found_date < datetime.utcnow():
                        logger.info(f"🕒 Found past date: {found_date}")
                        return False
                except ValueError:
                    continue

    return True

# === FedTech Scraper using Selenium ===
def scrape_fedtech(url="https://www.fedtech.io/corporates"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36")

    driver = None
    try:
        logger.info(f"🌐 Visiting FedTech: {url}")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        html = driver.page_source
        text = BeautifulSoup(html, 'html.parser').get_text(separator=' ')

        status = 'open' if is_grant_open(text) else 'closed'
        logger.info(f"✅ FedTech Grant Status: {status}")

        return {'url': url, 'status': status}

    except Exception as e:
        logger.error(f"❌ Error scraping FedTech: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

    finally:
        if driver:
            driver.quit()

# === Optional CLI Entry ===
# if __name__ == "__main__":
#     result = scrape_fedtech()
#     print("=== FedTech Scraper Result ===")
#     print(result)
