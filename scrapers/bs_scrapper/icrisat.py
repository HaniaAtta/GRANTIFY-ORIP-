import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate a safe user-agent string
def get_user_agent():
    try:
        return UserAgent().random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# Check for open grant keywords
def is_grant_open(text, keywords):
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

# ICRISAT scraper function
def scrape_icrisat(url="https://www.icrisat.org/services/business-incubation"):
    custom_keywords = [
        "business incubation portal","portal"
    ]

    headers = {'User-Agent': get_user_agent()}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        is_open = is_grant_open(text, custom_keywords)
        logger.info(f"[✓] Scraped: {url} | Status: {'open' if is_open else 'closed'}")
        return {'url': url, 'status': 'open' if is_open else 'closed'}
    except Exception as e:
        logger.error(f"[✗] Failed to scrape {url}: {e}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# Main function for manual testing
# if __name__ == "__main__":
#     result = scrape_icrisat()
#     print("Result:", result)
