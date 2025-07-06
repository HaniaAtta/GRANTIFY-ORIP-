import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session = requests.Session()

open_keywords = [
   'submit a grant', 'accepting proposals', 'open', 'now open', 'currently open',
   'applications open', 'accepting applications', 'application window open',
   'available', 'apply now', 'submissions open', 'call for proposals',
   'funding available', 'enrollment open', 'opportunity open',
   'accepting submissions', 'now accepting applications', 'call open',
   'rfa open', 'cfp open', 'solicitation open', 'registration open',
   'live', 'active', 'ongoing', 'deadline', 'closing date',
   'open for submission', 'now accepting applications', 'open call',
   
]

def get_user_agent():
    try:
        ua = UserAgent()
        return ua.random
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

def is_grant_open(text):
    text = text.lower()

    # Keyword check
    has_open_keyword = any(keyword in text for keyword in open_keywords)
    if not has_open_keyword:
        return False

    # Common date formats to try
    date_formats = [
        "%d %B %Y",        # 20 June 2021
        "%B %d, %Y",       # February 23, 2025
        "%d %b %Y",        # 20 Jun 2021
        "%b %d, %Y",       # Jun 20, 2021
        "%Y-%m-%d",        # 2021-06-20
        "%d/%m/%Y",        # 20/06/2021
        "%m/%d/%Y",        # 06/20/2021
        "%B %Y",           # June 2021 (treated as first of the month)
        "%b %Y"            # Jun 2021
    ]

    # Extract date-like patterns from text
    possible_dates = re.findall(
        r'(\d{1,2} \w+ \d{4}|\w+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d{4})',
        text
    )

    for date_str in possible_dates:
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)

                # If no day is in the string (e.g. "June 2024"), default to 1st
                if "%d" not in fmt:
                    parsed_date = parsed_date.replace(day=1)

                if parsed_date >= datetime.utcnow():
                    return True
                else:
                    logger.info(f"🕒 Found expired date: {parsed_date.strftime('%Y-%m-%d')}")
                    return False
            except ValueError:
                continue

    return True  # If keyword present and no stale date invalidates it
