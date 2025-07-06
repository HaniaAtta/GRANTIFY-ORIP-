import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import datetime
import re

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

# Determine if page content contains open grant keywords (and optional date)
def is_grant_open(text, keywords):
    text = text.lower()
    has_open_keyword = any(keyword in text for keyword in keywords)
    if not has_open_keyword:
        return False

    # Optional: reject if only expired date is found
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                return False
        except ValueError:
            pass

    return True

# Main Acumen scraper
def scrape_acumen(url="https://acumen.org"):
    custom_keywords = [
        'apply now', 'fellowship open', 'accepting applications',
        'open call', 'accelerator open', 'now open', 'currently accepting',
        'program open', 'funding opportunity', 'submissions open',
        'grant opportunity', 'inviting applications', 'applications open'
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

# For direct script execution
# def main():
#     result = scrape_acumen()
#     print("Result:", result)

# if __name__ == "__main__":
#     main()
