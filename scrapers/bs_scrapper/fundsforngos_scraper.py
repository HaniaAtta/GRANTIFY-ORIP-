# import requests
# from bs4 import BeautifulSoup
# from scrapers.utils import get_user_agent, is_grant_open 

# def scrape_fundsforngos(url="https://www.fundsforngos.org/"):
#     headers = {'User-Agent': get_user_agent()}
#     try:
#         res = requests.get(url, headers=headers, timeout=10)
#         res.raise_for_status()
#         text = BeautifulSoup(res.text, 'html.parser').get_text()
#         return {'url': url, 'status': 'open' if is_grant_open(text) else 'closed'}
#     except Exception as e:
#         return {'url': url, 'status': 'error', 'error': str(e)}

# import requests
# from bs4 import BeautifulSoup
# import random

# # Example User-Agent list for get_user_agent
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
#     " Chrome/58.0.3029.110 Safari/537.3",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
#     " Version/14.0 Safari/605.1.15",
#     # Add more user agents as needed
# ]

# def get_user_agent():
#     """Return a random user-agent string."""
#     return random.choice(USER_AGENTS)

# def is_grant_open(text):
#     """
#     Dummy implementation:
#     Check if grant is open by searching keywords in page text.
#     Replace with your actual logic.
#     """
#     keywords_open = ["apply now", "open for applications", "deadline", "submit a grant"]
#     text_lower = text.lower()
#     return any(keyword in text_lower for keyword in keywords_open)

# def scrape_fundsforngos():
#     url = "https://www.fundsforngos.org/"
#     headers = {'User-Agent': get_user_agent()}
#     try:
#         res = requests.get(url, headers=headers, timeout=10)
#         res.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
#         text = BeautifulSoup(res.text, 'html.parser').get_text(separator=' ')
#         status = 'open' if is_grant_open(text) else 'closed'
#         return {'url': url, 'status': status}
#     except Exception as e:
#         return {'url': url, 'status': 'error', 'error': str(e)}

# if __name__ == "__main__":
#     result = scrape_fundsforngos()
#     print(result)




# import requests
# import time
# import random
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from app.ai.classifier import classify_grant

# # ✅ User agents for requests
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
# ]

# KEYWORDS_LINKS = ["apply", "submit", "opportunity"]

# def get_headers(base_url):
#     return {
#         "User-Agent": random.choice(USER_AGENTS),
#         "Accept-Language": "en-US,en;q=0.9",
#         "Referer": base_url,
#         "Cache-Control": "no-cache",
#         "Pragma": "no-cache",
#     }

# def fetch_page(url, base_url, retries=3):
#     """Fetch a page with retries + backoff"""
#     for i in range(retries):
#         try:
#             headers = get_headers(base_url)
#             res = requests.get(url, headers=headers, timeout=20)
#             res.raise_for_status()
#             return res.text
#         except requests.exceptions.RequestException as e:
#             wait = 2 ** i + random.random()  # exponential backoff
#             time.sleep(wait)
#             if i == retries - 1:
#                 raise e

# def scrape_fundsforngos(base_url="https://www.fundsforngos.org/"):
#     results = []
#     visited = set()
#     to_visit = [base_url]
#     domain = urlparse(base_url).netloc
#     candidate_pages = []

#     try:
#         # Step 1: Crawl & collect candidate links
#         while to_visit:
#             current_url = to_visit.pop(0)
#             if current_url in visited:
#                 continue
#             visited.add(current_url)

#             html = fetch_page(current_url, base_url)
#             soup = BeautifulSoup(html, "html.parser")
#             text = soup.get_text(" ", strip=True)

#             for link in soup.find_all("a", href=True):
#                 href = urljoin(current_url, link["href"])
#                 link_text = link.get_text(" ", strip=True).lower()
#                 if any(keyword in href.lower() or keyword in link_text for keyword in KEYWORDS_LINKS):
#                     if urlparse(href).netloc == domain and href not in visited:
#                         candidate_pages.append(href)
#                         to_visit.append(href)

#             # ⏳ Random sleep to avoid rate limit
#             time.sleep(random.uniform(2, 5))

#         # Step 2: Try AI classification on candidate pages
#         for landing_page in candidate_pages:
#             html = fetch_page(landing_page, base_url)
#             page_text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

#             ai_result = classify_grant(landing_page, page_text)
#             if ai_result.get("status") in ["open", "closed"]:
#                 results.append({
#                     "url": landing_page,
#                     "status": ai_result["status"],
#                     "landing_page": landing_page,
#                     "categories": ai_result.get("categories", ["Other"]),
#                     "source": "AI-candidate"
#                 })
#                 return results  # stop at first valid match

#         # Step 3: Fallback to base page
#         ai_result = classify_grant(base_url, text)
#         results.append({
#             "url": base_url,
#             "status": ai_result.get("status", "unknown"),
#             "landing_page": base_url,
#             "categories": ai_result.get("categories", ["Other"]),
#             "source": "AI-base-fallback"
#         })

#     except Exception as e:
#         # Final fallback → try Selenium if request scraping fails completely
#         try:
#             from selenium import webdriver
#             from selenium.webdriver.chrome.service import Service
#             from selenium.webdriver.chrome.options import Options
#             from selenium.webdriver.common.by import By
#             from selenium.webdriver.support.ui import WebDriverWait
#             from selenium.webdriver.support import expected_conditions as EC

#             chrome_options = Options()
#             chrome_options.add_argument("--headless=new")
#             chrome_options.add_argument("--disable-gpu")
#             chrome_options.add_argument("--no-sandbox")
#             chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

#             driver = webdriver.Chrome(service=Service(), options=chrome_options)
#             driver.get(base_url)
#             WebDriverWait(driver, 15).until(
#                 lambda d: d.execute_script('return document.readyState') == 'complete'
#             )
#             page_text = driver.find_element(By.TAG_NAME, "body").text
#             ai_result = classify_grant(base_url, page_text)
#             results.append({
#                 "url": base_url,
#                 "status": ai_result.get("status", "unknown"),
#                 "landing_page": base_url,
#                 "categories": ai_result.get("categories", ["Other"]),
#                 "source": "AI-selenium-fallback"
#             })
#             driver.quit()
#         except Exception as se:
#             results.append({
#                 "url": base_url,
#                 "status": "error",
#                 "error": f"{e} | Selenium also failed: {se}",
#                 "landing_page": base_url,
#                 "categories": ["Other"],
#                 "source": "error"
#             })

#     return results











from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import urljoin, urlparse
from app.ai.classifier import classify_grant
import random
import time
# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

LINK_KEYWORDS = ["apply", "application", "submit", "opportunity"]

def scrape_fundsforngos(base_url="https://www.fundsforngos.org/"):
    results = []
    visited = set()
    to_visit = [base_url]
    domain = urlparse(base_url).netloc

    # Selenium setup
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")

    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        while to_visit:
            url = to_visit.pop(0)
            if url in visited:
                continue
            visited.add(url)

            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(1)  # Give some extra time for JS
                text = driver.find_element(By.TAG_NAME, "body").text

                # Look for landing links
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    link_text = link.text.lower()
                    if href and any(k in href.lower() or k in link_text for k in LINK_KEYWORDS):
                        landing_page = urljoin(url, href)
                        try:
                            driver.get(landing_page)
                            WebDriverWait(driver, 10).until(
                                lambda d: d.execute_script('return document.readyState') == 'complete'
                            )
                            landing_text = driver.find_element(By.TAG_NAME, "body").text
                            ai_result = classify_grant(landing_page, landing_text)
                            results.append({
                                "url": landing_page,
                                "status": ai_result.get("status", "unknown"),
                                "landing_page": landing_page,
                                "categories": ai_result.get("categories", ["Other"]),
                                "regions": ai_result.get("regions", []),
                                "source": "AI-link"
                            })
                            return results
                        except TimeoutException:
                            ai_result = classify_grant(url, text)
                            results.append({
                                "url": landing_page,
                                "status": ai_result.get("status", "unknown"),
                                "landing_page": landing_page,
                                "categories": ai_result.get("categories", ["Other"]),
                                "regions": ai_result.get("regions", []),
                                "source": f"AI-base-fallback due to timeout"
                            })
                            return results

                # AI classification on current page if no landing link found
                ai_result = classify_grant(url, text)
                results.append({
                    "url": url,
                    "status": ai_result.get("status", "unknown"),
                    "landing_page": url,
                    "categories": ai_result.get("categories", ["Other"]),
                    "regions": ai_result.get("regions", []),
                    "source": "AI-base"
                })
                return results

            except Exception as e:
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e),
                    "landing_page": url,
                    "categories": ["Other"],
                    "regions": [],
                    "source": "error"
                })

    finally:
        driver.quit()

    return results