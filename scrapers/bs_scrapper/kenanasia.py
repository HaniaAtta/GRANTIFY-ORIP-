import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup session
session = requests.Session()

# Generate random user agent
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Check if content suggests an open grant (no date logic)
def is_grant_open(text, keywords):
    text = text.lower()
    return any(keyword in text for keyword in keywords)

# Scraper function for Kenan Asia
def scrape_kenanasia(url="https://www.kenan-asia.org/2025-yseali-ai/"):
    custom_keywords = [
        "apply now"
    ]

    headers = {'User-Agent': get_user_agent()}
    try:
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ')
        is_open = is_grant_open(text, custom_keywords)
        logger.info(f"[✓] Scraped: {url} | Status: {'open' if is_open else 'closed'}")
        return {'url': url, 'status': 'open' if is_open else 'closed'}
    except Exception as e:
        logger.error(f"[✗] Failed to scrape {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# Main function for test run
# def main():
#     result = scrape_kenanasia()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
