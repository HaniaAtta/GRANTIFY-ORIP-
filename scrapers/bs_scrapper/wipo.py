import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate a user-agent string
def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Check if any keyword suggests an open opportunity
def is_grant_open(text, keywords):
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

# Scraper function for WIPO
def scrape_wipo(url="https://www.wipo.int/en/web/awards/global/how-to-apply"):
    custom_keywords = [
        'call for proposals', 'funding opportunity', 'grant opportunity',
        'apply now', 'accepting applications', 'open for submissions',
        'innovation challenge', 'intellectual property support',
        'now open', 'applications open', 'open call', 'competition open',
        'rfa open', 'funding available', 'grants open'
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

# Local test
# def main():
#     result = scrape_wipo()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
