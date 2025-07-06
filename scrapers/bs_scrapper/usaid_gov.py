import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

# === Helper Functions ===

def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

open_keywords = [
    "apply now", "funding opportunity", "call for proposals",
    "request for applications", "grants", "currently open",
    "accepting applications", "active opportunities", "submit proposal",
    "funding available", "rfa", "solicitation", "deadline",
    "open grant", "open call", "grant cycle", "program open"
]

def is_grant_open(text):
    text = text.lower()
    
    has_keyword = any(keyword in text for keyword in open_keywords)
    if not has_keyword:
        return False

    # Date logic (check for future dates)
    possible_dates = re.findall(
        r'(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{4})',
        text
    )

    date_formats = [
        "%d %B %Y", "%B %d, %Y", "%d %b %Y", "%b %d, %Y",
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %Y", "%b %Y"
    ]

    for date_str in possible_dates:
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if "%d" not in fmt:
                    dt = dt.replace(day=1)
                if dt >= datetime.utcnow():
                    return True
            except:
                continue

    return True  # fallback if keywords are present and no past-dated deadline found

# === Scraper ===

def scrape_usaid(url="https://www.usaid.gov/"):
    headers = {'User-Agent': get_user_agent()}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        status = 'open' if is_grant_open(text) else 'closed'
        return {'url': url, 'status': status}
    except Exception as e:
        return {'url': url, 'status': 'error', 'error': str(e)}

# === Testable Entry Point ===

# if __name__ == "__main__":
#     result = scrape_usaid()
#     print(result)
