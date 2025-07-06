import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate random user-agent safely
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Keyword matching function
def is_grant_open(text, keywords):
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

# Scraper for UPU procurement page
def scrape_upu(url="https://www.upu.int/en/universal-postal-union/procurement"):
    custom_keywords = [
        "submission of tenders",
        "current calls for tenders"
    ]

    headers = {'User-Agent': get_user_agent()}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ')
        is_open = is_grant_open(text, custom_keywords)
        logger.info(f"[✓] Scraped: {url} | Status: {'open' if is_open else 'closed'}")
        return {'url': url, 'status': 'open' if is_open else 'closed'}
    except Exception as e:
        logger.error(f"[✗] Failed to scrape {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# For direct testing
# if __name__ == "__main__":
#     result = scrape_upu()
#     print("Result:", result)
