import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# === Logging setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Keyword Lists ===
open_keywords = [
    'request for application', '2025/2026 request for applications',
    'submit your application', 'applications open', 'deadline',
    'closing date', 'funding available', 'research funding'
]

closed_keywords = [
    'now closed', 'closed', 'deadline passed', 
    'no longer accepting', 'submission closed'
]

# === User-Agent ===
def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# === Status Checker ===
def is_grant_open(text):
    text = text.lower()
    if any(kw in text for kw in closed_keywords):
        return False
    if any(kw in text for kw in open_keywords):
        return True

    # Optional: fallback check for any future-looking date
    date_matches = re.findall(r'(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4})', text)
    for date_str in date_matches:
        for fmt in ['%d %B %Y', '%B %d, %Y']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt).date()
                if dt >= datetime.utcnow().date():
                    return True
            except:
                continue

    return False

# === Main Scraper ===
def scrape_knh(url="https://knh.or.ke/index.php/funding-rfa/"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping KNH: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        status = "open" if is_grant_open(text) else "closed"
        logger.info(f"KNH status detected as: {status}")
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Optional Test Run
# if __name__ == "__main__":
#     print(scrape_knh())
