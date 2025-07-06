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
    'apply now', 'applications open', 'apply by', 'submit application',
    'scholarship', 'deadline', 'closing date', 'call for proposals',
    'request for application', 'now accepting'
]

closed_keywords = [
    'applications closed', 'now closed', 'deadline passed',
    'submission closed', 'no longer accepting'
]

# === User-Agent ===
def get_user_agent():
    try:
        return UserAgent().random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# === FNF-Specific Month Check ===
def is_fnf_open_by_month():
    return datetime.utcnow().month in [4, 10]  # April or October

# === Status Checker ===
def is_grant_open_fnf(text):
    text = text.lower()
    if not is_fnf_open_by_month():
        return False
    if any(kw in text for kw in closed_keywords):
        return False
    if any(kw in text for kw in open_keywords):
        return True

    # Optional: fallback check for valid upcoming date
    date_matches = re.findall(r'(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4})', text)
    for date_str in date_matches:
        for fmt in ['%d %B %Y', '%B %d, %Y']:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt).date()
                if parsed >= datetime.utcnow().date():
                    return True
            except:
                continue
    return False

# === Main Scraper ===
def scrape_fnf(url="https://www.freiheit.org/scholarships-friedrich-naumann-foundation-freedom"):
    headers = {'User-Agent': get_user_agent()}
    try:
        logger.info(f"Scraping FNF: {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        status = "open" if is_grant_open_fnf(text) else "closed"
        return {'url': url, 'status': status}
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Optional Test Run
# if __name__ == "__main__":
#     print(scrape_fnf())
