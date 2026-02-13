# import logging
# import requests
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
# import re
# from datetime import datetime

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# session = requests.Session()

# open_keywords = [
#    'submit a grant', 'accepting proposals', 'open', 'now open', 'currently open',
#    'applications open', 'accepting applications', 'application window open',
#    'available', 'apply now', 'submissions open', 'call for proposals',
#    'funding available', 'enrollment open', 'opportunity open',
#    'accepting submissions', 'now accepting applications', 'call open',
#    'rfa open', 'cfp open', 'solicitation open', 'registration open',
#    'live', 'active', 'ongoing', 'deadline', 'closing date',
#    'open for submission', 'now accepting applications', 'open call',
   
# ]

# def get_user_agent():
#     try:
#         ua = UserAgent()
#         return ua.random
#     except:
#         return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

# def is_grant_open(text):
#     text = text.lower()

#     # Keyword check
#     has_open_keyword = any(keyword in text for keyword in open_keywords)
#     if not has_open_keyword:
#         return False

#     # Common date formats to try
#     date_formats = [
#         "%d %B %Y",        # 20 June 2021
#         "%B %d, %Y",       # February 23, 2025
#         "%d %b %Y",        # 20 Jun 2021
#         "%b %d, %Y",       # Jun 20, 2021
#         "%Y-%m-%d",        # 2021-06-20
#         "%d/%m/%Y",        # 20/06/2021
#         "%m/%d/%Y",        # 06/20/2021
#         "%B %Y",           # June 2021 (treated as first of the month)
#         "%b %Y"            # Jun 2021
#     ]

#     # Extract date-like patterns from text
#     possible_dates = re.findall(
#         r'(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{4})',
#         text
#     )

#     for date_str in possible_dates:
#         for fmt in date_formats:
#             try:
#                 parsed_date = datetime.strptime(date_str, fmt)

#                 # If no day is in the string (e.g. "June 2024"), default to 1st
#                 if "%d" not in fmt:
#                     parsed_date = parsed_date.replace(day=1)

#                 if parsed_date >= datetime.utcnow():
#                     return True
#                 else:
#                     logger.info(f"🕒 Found expired date: {parsed_date.strftime('%Y-%m-%d')}")
#                     return False
#             except ValueError:
#                 continue

#     return True  # If keyword present and no stale date invalidates it

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random

KEYWORDS = ["grant", "funding", "opportunit", "apply", "call", "research"]

def find_grant_page(base_url: str) -> str:
    """Find the most likely grant-related page starting from homepage."""
    res = requests.get(base_url, headers={"User-Agent": get_user_agent()}, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    links = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)]
    grant_links = [link for link in links if any(k in link.lower() for k in KEYWORDS)]

    # return first matching link (or homepage fallback)
    return grant_links[0] if grant_links else base_url


def scrape_page(url: str) -> str:
    """Scrape raw text content from a webpage."""
    res = requests.get(url, headers={"User-Agent": get_user_agent()}, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text(separator=" ")


def is_grant_open(text: str) -> bool:
    """
    Quick heuristic to check if a grant is open.
    Searches for common keywords in the text.
    """
    text = text.lower()
    open_keywords = ["apply now", "open for applications", "deadline", "submission"]
    closed_keywords = ["closed", "expired", "ended"]

    if any(word in text for word in closed_keywords):
        return False
    if any(word in text for word in open_keywords):
        return True
    return False  # default unknown


def get_user_agent() -> str:
    """Return a random User-Agent string for requests."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    ]
    return random.choice(user_agents)
