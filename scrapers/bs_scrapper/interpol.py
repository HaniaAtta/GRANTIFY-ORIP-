import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session for persistent connections
session = requests.Session()

# Global keywords (overridden per scraper)
open_keywords = []

def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception as e:
        logger.warning(f"⚠️ UserAgent fallback due to error: {e}")
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

def is_grant_open(text):
    text = text.lower()

    has_open_keyword = any(keyword in text for keyword in open_keywords)
    if not has_open_keyword:
        return False

    # Match dates like "20 June 2021"
    date_match = re.search(r'(\d{1,2} \w+ \d{4})', text)
    if date_match:
        try:
            found_date = datetime.strptime(date_match.group(1), "%d %B %Y")
            if found_date < datetime.utcnow():
                return False
        except ValueError:
            pass  # Ignore parsing failures

    return True

def scrape_interpol(url="https://www.interpol.int/Who-we-are/Procurement/Open-calls-for-tender"):
    global open_keywords
    open_keywords = [
        'funding opportunity', 'grant opportunity', 'partnerships open',
        'call for proposals', 'submit application', 'now open',
        'accepting applications', 'open for collaboration',
        'project funding', 'open call', 'security grant',
        'law enforcement funding', 'apply now'
    ]

    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"🔍 Scraping Interpol: {url}")
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
        status = 'open' if is_grant_open(text) else 'closed'

        logger.info(f"✅ [Interpol] Status: {status}")
        return {
            'url': url,
            'status': status
        }
    except Exception as e:
        logger.error(f"❌ [Interpol] Error: {e}")
        return {
            'url': url,
            'status': 'error',
            'error': str(e)
        }

# def main():
#     result = scrape_interpol()
#     print("Scraper Result:")
#     print(result)

# if __name__ == "__main__":
#     main()
