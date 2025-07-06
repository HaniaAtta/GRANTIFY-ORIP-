import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from datetime import datetime
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate random user-agent
def get_user_agent():
    try:
        from fake_useragent import UserAgent
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Determine if text suggests an open grant/tender
def is_grant_open(text, keywords):
    text = text.lower()

    has_open_keyword = any(keyword.lower() in text for keyword in keywords)
    if not has_open_keyword:
        return False

    # Optional: check for a future-looking date
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                return False
        except ValueError:
            pass

    return True

# Scraper using Selenium
def scrape_trademarkafrica(url="https://www.trademarkafrica.com/procurement/"):
    custom_keywords = [
        "download tender", "deadline"
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
        html = driver.page_source
        text = BeautifulSoup(html, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text, custom_keywords) else 'closed'
        logger.info(f"[✓] Scraped: {url} | Status: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"[✗] Error scraping {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}
    finally:
        if driver:
            driver.quit()

# Entry point for direct run
# def main():
#     result = scrape_trademarkafrica()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
