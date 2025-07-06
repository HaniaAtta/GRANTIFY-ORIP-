import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate a random User-Agent
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Check if grant-related keywords exist in text
def is_grant_open(text, keywords):
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

# Selenium-based scraper function
def scrape_makingcents(url="https://makingcents.com"):
    custom_keywords = [
        'apply now', 'accepting applications', 'request for proposals',
        'open rfp', 'funding opportunity', 'training opportunity',
        'consulting opportunity', 'now accepting', 'call for proposals',
        'submissions open', 'opportunity open', 'project funding'
    ]

    options = Options()
    options.add_argument("--headless")  # run without GUI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={get_user_agent()}")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

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

# Manual test run
# def main():
#     result = scrape_makingcents()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
