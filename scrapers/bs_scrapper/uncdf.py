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

# Generate a random user-agent
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Determine if the page content suggests an open grant
def is_grant_open(text, keywords):
    text = text.lower()
    has_open_keyword = any(keyword in text for keyword in keywords)
    if not has_open_keyword:
        return False

    # Optional: check for future-valid date
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                return False
        except ValueError:
            pass

    return True

# Selenium-based scraper for UNCDF Calls for Tenders
def scrape_uncdf(url="https://www.uncdf.org"):
    custom_keywords = [
        "calls for tenders",
        "active calls",
        "submit proposal",
        "currently open",
        "open call",
        "call for proposals"
    ]

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={get_user_agent()}")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        # Optional: wait if JavaScript content is slow-loading (WebDriverWait can be added later)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text = soup.get_text(separator=' ')

        is_open = is_grant_open(text, custom_keywords)
        logger.info(f"[✓] Scraped: {url} | Status: {'open' if is_open else 'closed'}")
        return {'url': url, 'status': 'open' if is_open else 'closed'}

    except Exception as e:
        logger.error(f"[✗] Failed to scrape {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

    finally:
        if driver:
            driver.quit()

# For manual testing
# def main():
#     result = scrape_uncdf()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
