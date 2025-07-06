import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global open keywords
open_keywords = [
    "call for proposals",
    "applications are open",
    "apply now",
    "deadline to submit",
    "now open"
]

# Get a random user-agent string
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Check if the grant page contains open indicators
def is_grant_open(text):
    text = text.lower()

    # Check for open keywords
    if not any(keyword in text for keyword in open_keywords):
        return False

    # Optional: Check for future dates
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                return False
        except ValueError:
            pass

    return True

# Updated Selenium-based scraper
def scrape_partners(url="https://members.partners.net/page/foundation-grants"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f'user-agent={get_user_agent()}')

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text = soup.get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"[✓] Scraped: {url} | Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"[✗] Failed to scrape {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}
    finally:
        if driver:
            driver.quit()

# Main test function
# def main():
#     result = scrape_partners()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
