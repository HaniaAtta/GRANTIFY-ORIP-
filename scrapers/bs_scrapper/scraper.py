# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from app.ai.classifier import classify_grant
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import time


# USER_AGENT = {"User-Agent": "Mozilla/5.0"}

# def fetch_with_requests(url):
#     """Fetch page HTML with requests."""
#     resp = requests.get(url, headers=USER_AGENT, timeout=15)
#     resp.raise_for_status()
#     return resp.text

# def fetch_with_selenium(url):
#     """Fallback fetch with Selenium."""
#     options = Options()
#     options.add_argument("--headless")
#     driver = webdriver.Chrome(options=options)
#     try:
#         driver.get(url)
#         time.sleep(3)
#         return driver.page_source
#     finally:
#         driver.quit()

# def find_landing_page(base_url, html):
#     """Try to identify grant-related landing page link from base URL."""
#     soup = BeautifulSoup(html, "html.parser")
#     candidates = []

#     for a in soup.find_all("a", href=True):
#         text = a.get_text(" ", strip=True).lower()
#         if any(word in text for word in ["grant", "funding", "opportunity", "apply", "call for"]):
#             candidates.append(urljoin(base_url, a["href"]))

#     # Return first candidate, else base URL itself
#     return candidates[0] if candidates else base_url

# def scrape_page(url):
#     """Main scraper: fetch, detect landing page, classify content."""
#     html = None
#     try:
#         html = fetch_with_requests(url)
#     except Exception:
#         try:
#             html = fetch_with_selenium(url)
#         except Exception as e:
#             return {
#                 "url": url,
#                 "status": "error",
#                 "error": str(e),
#                 "categories": [],
#                 "regions": []
#             }

#     landing_url = find_landing_page(url, html)
#     text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

#     # Call AI classifier
#     result = classify_grant(landing_url, text)
#     result["landing_page"] = landing_url
#     result["base_url"] = url
#     return result




# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from app.ai.classifier import classify_grant
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# import time
# import logging

# logger = logging.getLogger(__name__)

# USER_AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# def fetch_with_requests(url):
#     """Fetch page HTML with requests and better error handling."""
#     try:
#         resp = requests.get(url, headers=USER_AGENT, timeout=15)
#         resp.raise_for_status()
#         return resp.text
#     except Exception as e:
#         logger.warning(f"Requests failed for {url}: {str(e)}")
#         raise

# def fetch_with_selenium(url):
#     """Fallback fetch with Selenium and improved options."""
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument(f"user-agent={USER_AGENT['User-Agent']}")
    
#     driver = webdriver.Chrome(options=options)
#     try:
#         driver.get(url)
#         time.sleep(2)  # Reduced from 3 to 2 seconds for faster scraping
        
#         # Try to find and click common cookie consent buttons
#         try:
#             cookie_selectors = [
#                 'button[aria-label*="cookie"]', 
#                 'button[aria-label*="Cookie"]',
#                 'button:contains("Accept")',
#                 'button:contains("accept")',
#                 'button:contains("AGREE")',
#                 '#cookieAccept',
#                 '.cookie-accept'
#             ]
            
#             for selector in cookie_selectors:
#                 try:
#                     button = driver.find_element(By.CSS_SELECTOR, selector)
#                     button.click()
#                     time.sleep(0.5)
#                     break
#                 except:
#                     continue
#         except:
#             pass
        
#         return driver.page_source
#     finally:
#         driver.quit()

# def find_landing_page(base_url, html):
#     """
#     Improved landing page detection with multiple strategies.
#     """
#     soup = BeautifulSoup(html, "html.parser")
    
#     # Strategy 1: Look for grant-specific links in navigation
#     nav_selectors = ["nav", "header", ".navigation", ".menu", "#menu"]
#     grant_keywords = ["grant", "funding", "opportunity", "apply", "proposal", "call"]
    
#     for selector in nav_selectors:
#         nav_elements = soup.select(selector)
#         for nav in nav_elements:
#             for a in nav.find_all("a", href=True):
#                 text = a.get_text(" ", strip=True).lower()
#                 href = a["href"]
                
#                 if any(keyword in text for keyword in grant_keywords):
#                     landing_url = urljoin(base_url, href)
#                     logger.info(f"Found grant page in navigation: {landing_url}")
#                     return landing_url
    
#     # Strategy 2: Look for grant-specific links in main content
#     main_selectors = ["main", "#content", ".content", "article", ".main"]
#     for selector in main_selectors:
#         main_elements = soup.select(selector)
#         for main in main_elements:
#             for a in main.find_all("a", href=True):
#                 text = a.get_text(" ", strip=True).lower()
#                 href = a["href"]
                
#                 if any(keyword in text for keyword in grant_keywords):
#                     landing_url = urljoin(base_url, href)
#                     logger.info(f"Found grant page in content: {landing_url}")
#                     return landing_url
    
#     # Strategy 3: Look for common grant page patterns in URLs
#     for a in soup.find_all("a", href=True):
#         href = a["href"].lower()
#         if any(pattern in href for pattern in ["/grant", "/funding", "/apply", "/opportunity"]):
#             landing_url = urljoin(base_url, a["href"])
#             logger.info(f"Found grant page by URL pattern: {landing_url}")
#             return landing_url
    
#     # Strategy 4: Fallback to base URL
#     logger.info("No specific grant page found, using base URL")
#     return base_url

# def scrape_page(url):
#     """
#     Main scraper with improved error handling and efficiency.
#     """
#     html = None
#     try:
#         html = fetch_with_requests(url)
#     except Exception as e:
#         logger.warning(f"Requests failed, trying selenium: {str(e)}")
#         try:
#             html = fetch_with_selenium(url)
#         except Exception as selenium_error:
#             logger.error(f"Both requests and selenium failed: {str(selenium_error)}")
#             return {
#                 "url": url,
#                 "status": "error",
#                 "error": str(selenium_error),
#                 "categories": [],
#                 "regions": [],
#                 "applicable_to_pakistan": False
#             }

#     try:
#         landing_url = find_landing_page(url, html)
#         soup = BeautifulSoup(html, "html.parser")
        
#         # Remove scripts, styles, and other non-content elements
#         for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
#             element.decompose()
        
#         text = soup.get_text(" ", strip=True)
#         text = " ".join(text.split())  # Normalize whitespace
        
#         # Call AI classifier
#         result = classify_grant(landing_url, text)
#         result["landing_page"] = landing_url
#         result["base_url"] = url
        
#         return result
#     except Exception as e:
#         logger.error(f"Error processing page {url}: {str(e)}")
#         return {
#             "url": url,
#             "status": "error",
#             "error": str(e),
#             "categories": [],
#             "regions": [],
#             "applicable_to_pakistan": False
#         }



# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from app.ai.classifier import classify_grant
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# import time, logging

# logger = logging.getLogger(__name__)

# USER_AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# GRANT_KEYWORDS = ["grant", "funding", "apply", "opportunity", "call", "proposal"]

# def fetch_with_requests(url):
#     try:
#         resp = requests.get(url, headers=USER_AGENT, timeout=15)
#         resp.raise_for_status()
#         return resp.text
#     except Exception as e:
#         logger.warning(f"Requests failed for {url}: {str(e)}")
#         raise

# def fetch_with_selenium(url):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument(f"user-agent={USER_AGENT['User-Agent']}")
#     driver = webdriver.Chrome(options=options)
#     try:
#         driver.get(url)
#         time.sleep(2)
#         # Try to click cookie buttons
#         for selector in [
#             'button[aria-label*="cookie"]', 
#             'button[aria-label*="Cookie"]', 
#             '#cookieAccept', '.cookie-accept'
#         ]:
#             try:
#                 btn = driver.find_element(By.CSS_SELECTOR, selector)
#                 btn.click()
#                 time.sleep(0.5)
#                 break
#             except: continue
#         return driver.page_source
#     finally:
#         driver.quit()

# def get_domain(url):
#     return urlparse(url).netloc.replace("www.", "")

# def find_landing_page(base_url, html):
#     soup = BeautifulSoup(html, "html.parser")
#     nav_selectors = ["nav", "header", ".navigation", ".menu", "#menu"]
#     for selector in nav_selectors:
#         for nav in soup.select(selector):
#             for a in nav.find_all("a", href=True):
#                 href = a["href"]
#                 text = a.get_text(" ", strip=True).lower()
#                 if any(k in text for k in GRANT_KEYWORDS) or any(k in href.lower() for k in GRANT_KEYWORDS):
#                     return urljoin(base_url, href)
#     # Fallback: find first grant-like URL anywhere
#     for a in soup.find_all("a", href=True):
#         href = a["href"].lower()
#         if any(k in href for k in GRANT_KEYWORDS):
#             return urljoin(base_url, a["href"])
#     return base_url

# def collect_relevant_text(base_url, landing_url, html, max_subpages=5):
#     soup = BeautifulSoup(html, "html.parser")
#     text_chunks = []

#     # Remove unwanted elements
#     for el in soup(["script", "style", "header", "footer", "nav", "aside"]):
#         el.decompose()
#     text_chunks.append(" ".join(soup.get_text(" ", strip=True).split()))

#     # Find internal subpages with grant keywords
#     links = set()
#     for a in soup.find_all("a", href=True):
#         href = a["href"]
#         full_url = urljoin(base_url, href)
#         if urlparse(full_url).netloc != urlparse(base_url).netloc:
#             continue  # skip external
#         if any(k in href.lower() for k in GRANT_KEYWORDS) and full_url != landing_url:
#             links.add(full_url)
#     links = list(links)[:max_subpages]  # limit subpages

#     # Fetch subpages
#     for link in links:
#         try:
#             sub_html = fetch_with_requests(link)
#             sub_soup = BeautifulSoup(sub_html, "html.parser")
#             for el in sub_soup(["script", "style", "header", "footer", "nav", "aside"]):
#                 el.decompose()
#             text_chunks.append(" ".join(sub_soup.get_text(" ", strip=True).split()))
#         except Exception as e:
#             logger.warning(f"Failed to fetch subpage {link}: {str(e)}")

#     return " ".join(text_chunks)

# def scrape_page(url):
#     html = None
#     try:
#         html = fetch_with_requests(url)
#     except Exception as e:
#         logger.warning(f"Requests failed, trying Selenium: {str(e)}")
#         try:
#             html = fetch_with_selenium(url)
#         except Exception as e2:
#             logger.error(f"Both requests and selenium failed for {url}: {str(e2)}")
#             return {
#                 "url": url,
#                 "status": "error",
#                 "error": str(e2),
#                 "categories": [],
#                 "regions": [],
#                 "applicable_to_pakistan": False
#             }

#     try:
#         landing_url = find_landing_page(url, html)
#         combined_text = collect_relevant_text(url, landing_url, html)

#         # Call AI classifier
#         result = classify_grant(landing_url, combined_text)
#         result["landing_page"] = landing_url
#         result["base_url"] = url

#         return result
#     except Exception as e:
#         logger.error(f"Error processing {url}: {str(e)}")
#         return {
#             "url": url,
#             "status": "error",
#             "error": str(e),
#             "categories": [],
#             "regions": [],
#             "applicable_to_pakistan": False
#         }






import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.ai.classifier import classify_grant
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)
USER_AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_with_requests(url):
    """Fetch page HTML with requests."""
    try:
        resp = requests.get(url, headers=USER_AGENT, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"Requests failed for {url}: {str(e)}")
        raise

def fetch_with_selenium(url):
    """Fallback fetch using Selenium for dynamic pages."""
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import os
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={USER_AGENT['User-Agent']}")
    
    # Check if Chromium is available (Docker) or use Chrome (local)
    chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/chromium")
    if os.path.exists(chrome_bin):
        options.binary_location = chrome_bin
        logger.info(f"Using Chromium at: {chrome_bin}")
    
    # Use webdriver-manager to automatically handle ChromeDriver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        # Fallback: try without service (if ChromeDriver is in PATH)
        logger.warning(f"ChromeDriverManager failed, trying direct: {e}")
        try:
            driver = webdriver.Chrome(options=options)
        except Exception as e2:
            # Last resort: try with chromium-driver if available
            if os.path.exists("/usr/bin/chromedriver"):
                service = Service("/usr/bin/chromedriver")
                driver = webdriver.Chrome(service=service, options=options)
            else:
                raise e2
    try:
        driver.get(url)
        time.sleep(6)  # wait for page load

        # Accept cookie banners if present
        cookie_selectors = [
            'button[aria-label*="cookie"]', 
            'button[aria-label*="Cookie"]',
            'button:contains("Accept")',
            'button:contains("accept")',
            'button:contains("AGREE")',
            '#cookieAccept',
            '.cookie-accept'
        ]
        for selector in cookie_selectors:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
                btn.click()
                time.sleep(0.5)
                break
            except:
                continue

        return driver.page_source
    finally:
        driver.quit()

# def find_landing_page(base_url, html):
#     """Detect grant landing page using multiple strategies."""
#     soup = BeautifulSoup(html, "html.parser")
#     grant_keywords = ["grant", "funding", "opportunity", "apply", "proposal", "call"]

#     # 1️⃣ Check navigation/header links
#     for selector in ["nav", "header", ".navigation", ".menu", "#menu"]:
#         for nav in soup.select(selector):
#             for a in nav.find_all("a", href=True):
#                 if any(k in a.get_text(" ", strip=True).lower() for k in grant_keywords):
#                     return urljoin(base_url, a["href"])

#     # 2️⃣ Check main content links
#     for selector in ["main", "#content", ".content", "article", ".main"]:
#         for main in soup.select(selector):
#             for a in main.find_all("a", href=True):
#                 if any(k in a.get_text(" ", strip=True).lower() for k in grant_keywords):
#                     return urljoin(base_url, a["href"])

#     # 3️⃣ Check URL patterns
#     for a in soup.find_all("a", href=True):
#         href = a["href"].lower()
#         if any(p in href for p in ["/grant", "/funding", "/apply", "/opportunity"]):
#             return urljoin(base_url, a["href"])

#     # 4️⃣ Fallback to base URL
#     return base_url
def find_landing_page(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    grant_keywords = [
        "grant", "funding", "opportunity", "apply", "proposal", "call",
        "what we fund", "partnership", "projects", "our work", "how to apply"
    ]

    # 1️⃣ Try semantic links
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True).lower()
        if any(k in text for k in grant_keywords):
            href = urljoin(base_url, a["href"])
            if base_url in href and len(href) > len(base_url) + 3:
                return href

    # 2️⃣ If no matches, try sitemap links
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(word in href for word in ["grant", "funding", "apply", "opportunities"]):
            return urljoin(base_url, href)

    # 3️⃣ fallback
    return base_url

def extract_dates_from_text(text):
    """
    Extract open and close dates from text using multiple patterns.
    Returns: (open_date, close_date) as datetime objects or None
    """
    date_patterns = [
        r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',  # DD-MM-YYYY or DD/MM/YYYY
        r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',  # YYYY-MM-DD or YYYY/MM/DD
        r'\b(\d{1,2}\s+\w+\s+\d{4})\b',  # DD Month YYYY
        r'\b(\w+\s+\d{1,2},?\s+\d{4})\b',  # Month DD, YYYY
    ]
    
    date_formats = [
        ["%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"],
        ["%Y-%m-%d", "%Y/%m/%d"],
        ["%d %B %Y", "%d %b %Y"],
        ["%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y"],
    ]
    
    dates_found = []
    for pattern, formats in zip(date_patterns, date_formats):
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            for fmt in formats:
                try:
                    dt = datetime.strptime(match, fmt)
                    dates_found.append(dt)
                    break
                except ValueError:
                    continue
    
    # Look for keywords to identify open/close dates
    text_lower = text.lower()
    open_keywords = ["open", "opening", "start", "begin", "launch"]
    close_keywords = ["close", "closing", "deadline", "end", "due", "submit by"]
    
    open_date = None
    close_date = None
    
    # Try to find dates near keywords
    for i, date in enumerate(dates_found):
        # Check context around date (50 chars before and after)
        start = max(0, text_lower.find(str(date.strftime("%Y-%m-%d"))[:10]) - 50)
        end = min(len(text_lower), start + 100)
        context = text_lower[start:end]
        
        if any(kw in context for kw in open_keywords):
            open_date = date
        elif any(kw in context for kw in close_keywords):
            close_date = date
    
    # If no keyword context, assume first date is open, second is close
    if not open_date and len(dates_found) > 0:
        open_date = dates_found[0]
    if not close_date and len(dates_found) > 1:
        close_date = dates_found[1]
    elif not close_date and len(dates_found) > 0 and open_date != dates_found[0]:
        close_date = dates_found[-1]
    
    return open_date, close_date

def scrape_page(url):
    """Scrape URL + landing page, send text to AI classifier, return full result."""
    # Fix URL if missing scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        logger.info(f"Added https:// scheme to URL: {url}")
    
    html = None
    try:
        html = fetch_with_requests(url)
    except Exception as e:
        logger.warning(f"Requests failed, using Selenium for {url}: {e}")
        try:
            html = fetch_with_selenium(url)
        except Exception as selenium_error:
            logger.error(f"Both requests & Selenium failed for {url}: {selenium_error}")
            return {
                "url": url,
                "status": "error",
                "error": str(selenium_error),
                "categories": [],
                "regions": [],
                "applicable_to_pakistan": False
            }

    try:
        landing_url = find_landing_page(url, html)

        # If landing URL != base URL, fetch landing page
        if landing_url != url:
            try:
                landing_html = fetch_with_requests(landing_url)
            except:
                landing_html = html  # fallback to base HTML
        else:
            landing_html = html

        # Remove non-content elements
        soup = BeautifulSoup(landing_html, "html.parser")
        for el in soup(["script", "style"]):
            el.decompose()
        text = " ".join(soup.get_text(" ", strip=True).split())

        # ✅ Extract dates from HTML before AI classification
        open_date, close_date = extract_dates_from_text(text)
        
        # AI classification
        result = classify_grant(landing_url, text)
        result["landing_page"] = landing_url
        result["base_url"] = url
        
        # ✅ Use extracted dates if AI didn't provide them or if extracted dates are more recent
        if open_date and (not result.get("open_date") or result.get("open_date") == "null"):
            result["open_date"] = open_date.strftime("%Y-%m-%d") if isinstance(open_date, datetime) else open_date
        if close_date and (not result.get("close_date") or result.get("close_date") == "null"):
            result["close_date"] = close_date.strftime("%Y-%m-%d") if isinstance(close_date, datetime) else close_date
        
        # Convert date strings to datetime objects if they're strings
        if isinstance(result.get("open_date"), str) and result["open_date"] not in ["null", ""]:
            try:
                result["open_date"] = datetime.strptime(result["open_date"], "%Y-%m-%d")
            except:
                pass
        if isinstance(result.get("close_date"), str) and result["close_date"] not in ["null", ""]:
            try:
                result["close_date"] = datetime.strptime(result["close_date"], "%Y-%m-%d")
            except:
                pass
        
        return result
    except Exception as e:
        logger.error(f"Error processing page {url}: {str(e)}")
        return {
            "url": url,
            "status": "error",
            "error": str(e),
            "categories": [],
            "regions": [],
            "applicable_to_pakistan": False
        }
