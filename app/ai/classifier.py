# import os, json
# from urllib.parse import urlparse
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# # Load categories config
# with open("app/config/categories.json", "r") as f:
#     CATEGORY_CONFIG = json.load(f)

# def get_domain(url):
#     """Extract domain from URL (example: https://example.org/path → example.org)."""
#     return urlparse(url).netloc.replace("www.", "")

# def classify_grant(url, text):
#     """
#     Classify grant as open/closed and assign categories from categories.json.
#     """
#     domain = get_domain(url)
#     categories = CATEGORY_CONFIG.get(domain, ["Other"])  # fallback list

#     prompt = f"""
#     You are an assistant that classifies grant opportunities.

#     From the following website text, determine:
#     1. Whether the grant is currently "open" or "closed".
#     2. Which categories from this list apply: {categories}.

#     Return only JSON in this format:
#     {{
#         "status": "open" | "closed",
#         "categories": ["..."]
#     }}

#     Text to analyze:
#     {text[:3500]}  # trimming for safety
#     """

#     try:
#         response = client.responses.create(
#             model="gpt-4o-mini",
#             input=prompt,
#             max_output_tokens=400
#         )

#         answer = response.output[0].content[0].text.strip()

#         # Parse JSON safely
#         result = json.loads(answer)

#         # Ensure valid fallback values
#         if "status" not in result or result["status"] not in ["open", "closed"]:
#             raise ValueError("Invalid status in response")

#         if not isinstance(result.get("categories"), list):
#             result["categories"] = categories

#     except Exception as e:
#         # fallback keyword check
#         lowered = text.lower()
#         status = "closed" if "closed" in lowered else "open" if "open" in lowered else "unknown"
#         result = {
#             "status": status,
#             "categories": categories
#         }

#     return result




# import os, json, time, random
# from urllib.parse import urlparse
# from openai import OpenAI

# # ⚡ Hardcoded OpenAI key

# # Load categories config
# with open("app/config/categories.json", "r") as f:
#     CATEGORY_CONFIG = json.load(f)

# # Keywords for region classification
# ELIGIBILITY_KEYWORDS = [
#     "pakistan",
#     "south asia",
#     "asia-pacific",
#     "developing countries",
#     "underdeveloped",
#     "low income countries",
#     "global south",
#     "emerging economies"
# ]

# def get_domain(url):
#     """Extract domain from URL."""
#     return urlparse(url).netloc.replace("www.", "")

# def classify_grant(url, text, max_retries=5):
#     """
#     Classify grant as open/closed, assign categories, and detect regions.
#     Returns: { "status": "open"|"closed"|"unknown", "categories": [...], "regions": [...] }
#     """
#     domain = get_domain(url)
#     categories = CATEGORY_CONFIG.get(domain, ["Other"])  # fallback

#     # Prepare region info hint for AI
#     region_hint = f"Check for the following eligible regions or countries: {', '.join(ELIGIBILITY_KEYWORDS)}."

#     prompt = f"""
#     You are an assistant that classifies grant opportunities.

#     From the following website text, determine:
#     1. Whether the grant is currently "open" or "closed".
#     2. Which categories from this list apply: {categories}.
#     3. Which regions or countries from this list are mentioned or eligible: {', '.join(ELIGIBILITY_KEYWORDS)}.

#     Return ONLY valid JSON. No explanations, no extra text. 
#     Format:
#     {{
#         "status": "open" | "closed",
#         "categories": ["..."],
#         "regions": ["..."]
#     }}

#     {region_hint}

#     Text to analyze:
#     {text[:3000]}
#     """

#     models_to_try = ["gpt-4o-mini", "gpt-3.5-turbo"]

#     for model in models_to_try:
#         for attempt in range(max_retries):
#             try:
#                 response = client.responses.create(
#                     model=model,
#                     input=prompt,
#                     max_output_tokens=500
#                 )

#                 answer = response.output[0].content[0].text.strip()

#                 # --- JSON Handling ---
#                 try:
#                     result = json.loads(answer)
#                 except json.JSONDecodeError:
#                     import re
#                     match = re.search(r"\{.*\}", answer, re.DOTALL)
#                     if match:
#                         try:
#                             result = json.loads(match.group())
#                         except:
#                             print("⚠️ Model returned invalid JSON:", answer)
#                             return {"status": "unknown", "categories": categories, "regions": []}
#                     else:
#                         print("⚠️ Model returned non-JSON:", answer)
#                         return {"status": "unknown", "categories": categories, "regions": []}

#                 # Validate fields
#                 if result.get("status") not in ["open", "closed"]:
#                     result["status"] = "unknown"
#                 if not isinstance(result.get("categories"), list):
#                     result["categories"] = categories
#                 if not isinstance(result.get("regions"), list):
#                     result["regions"] = []

#                 return result

#             except Exception as e:
#                 wait = (2 ** attempt) + random.random()
#                 print(f"⚠️ {model} retry {attempt+1}/{max_retries} after {wait:.1f}s due to: {e}")
#                 if "insufficient_quota" in str(e):
#                     print(f"💡 Switching from {model} to next model due to quota")
#                     break
#                 time.sleep(wait)

#     # Fallback: keyword-based region detection
#     lowered = text.lower()
#     regions_found = [r for r in ELIGIBILITY_KEYWORDS if r in lowered]
#     status = "closed" if "closed" in lowered else "open" if "open" in lowered else "unknown"

#     return {
#         "status": status,
#         "categories": categories,
#         "regions": regions_found
#     }
















# import os, json, time, random, re
# from urllib.parse import urlparse
# from openai import OpenAI

# # ⚡ Hardcoded OpenAI key (can later switch to env var for safety)

# # Load categories config
# with open("app/config/categories.json", "r") as f:
#     CATEGORY_CONFIG = json.load(f)

# # Keywords for region classification
# ELIGIBILITY_KEYWORDS = [
#     "pakistan",
#     "south asia",
#     "asia-pacific",
#     "developing countries",
#     "underdeveloped",
#     "low income countries",
#     "global south",
#     "emerging economies"
# ]

# def get_domain(url):
#     """Extract domain from URL."""
#     return urlparse(url).netloc.replace("www.", "")


# def classify_grant(url, text, max_retries=5):
#     """
#     Classify grant using AI and fallback rules.
#     """
#     domain = get_domain(url)

#     # --- Extract categories from categories.json ---
#     categories = ["Other"]
#     for funder in CATEGORY_CONFIG:
#         if domain in funder["url"]:
#             categories = funder.get("categories", ["Other"])
#             break

#     region_hint = f"Check for the following eligible regions or countries: {', '.join(ELIGIBILITY_KEYWORDS)}."

#     prompt = f"""
#     You are an assistant that classifies grant opportunities.

#     From the following text, extract structured info:
#     1. Grant status: "open" | "closed" | "unknown"
#     2. Open date (YYYY-MM-DD or null)
#     3. Close date (YYYY-MM-DD or null)
#     4. Eligibility (countries, regions, institution types)
#     5. Thematic areas (list of categories like health, education, AI, etc.)
#     6. Regions or countries from this list: {', '.join(ELIGIBILITY_KEYWORDS)}

#     Use these predefined categories if relevant: {categories}.

#     Return ONLY valid JSON in this format:
#     {{
#         "status": "open" | "closed" | "unknown",
#         "categories": ["..."],
#         "regions": ["..."],
#         "open_date": "YYYY-MM-DD" | null,
#         "close_date": "YYYY-MM-DD" | null,
#         "eligibility": "...",
#         "thematic_areas": ["..."]
#     }}

#     {region_hint}

#     Text to analyze:
#     {text[:3000]}
#     """

#     models_to_try = ["gpt-4o-mini", "gpt-3.5-turbo"]

#     for model in models_to_try:
#         for attempt in range(max_retries):
#             try:
#                 response = client.responses.create(
#                     model=model,
#                     input=prompt,
#                     max_output_tokens=600,
#                     temperature=0
#                 )

#                 answer = response.output[0].content[0].text.strip()

#                 # --- JSON Handling ---
#                 try:
#                     result = json.loads(answer)
#                 except json.JSONDecodeError:
#                     match = re.search(r"\{.*\}", answer, re.DOTALL)
#                     if match:
#                         try:
#                             result = json.loads(match.group())
#                         except:
#                             print("⚠️ Model returned invalid JSON:", answer)
#                             return default_fallback(text, categories)
#                     else:
#                         print("⚠️ Model returned non-JSON:", answer)
#                         return default_fallback(text, categories)

#                 # Validate + defaults
#                 if result.get("status") not in ["open", "closed", "unknown"]:
#                     result["status"] = "unknown"
#                 if not isinstance(result.get("categories"), list):
#                     result["categories"] = categories
#                 if not isinstance(result.get("regions"), list):
#                     result["regions"] = []
#                 if not result.get("open_date"):
#                     result["open_date"] = None
#                 if not result.get("close_date"):
#                     result["close_date"] = None
#                 if not result.get("eligibility"):
#                     result["eligibility"] = ""
#                 if not isinstance(result.get("thematic_areas"), list):
#                     result["thematic_areas"] = []

#                 return result

#             except Exception as e:
#                 wait = (2 ** attempt) + random.random()
#                 print(f"⚠️ {model} retry {attempt+1}/{max_retries} after {wait:.1f}s due to: {e}")
#                 if "insufficient_quota" in str(e).lower():
#                     print(f"💡 Switching from {model} to next model due to quota")
#                     break
#                 time.sleep(wait)

#     # --- Fallback if all models fail ---
#     return default_fallback(text, categories)



# def default_fallback(text, categories):
#     """Fallback classification without AI (keyword-based)."""
#     lowered = text.lower()
#     regions_found = [r for r in ELIGIBILITY_KEYWORDS if r in lowered]
#     status = "closed" if "closed" in lowered else "open" if "open" in lowered else "unknown"

#     return {
#         "status": status,
#         "categories": categories,
#         "regions": regions_found,
#         "open_date": None,
#         "close_date": None,
#         "eligibility": "",
#         "thematic_areas": []
#     }



# import os, json, time, random, re 
# from urllib.parse import urlparse
# from openai import OpenAI
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Get API key from environment variable (SECURE)
# api_key = os.getenv("OPENAI_API_KEY", "your-fallback-key-here")
# client = OpenAI(api_key=api_key)

# # Load categories config
# try:
#     with open("app/config/categories.json", "r") as f:
#         CATEGORY_CONFIG = json.load(f)
# except FileNotFoundError:
#     logger.error("Categories config file not found")
#     CATEGORY_CONFIG = []

# # Keywords for region classification
# ELIGIBILITY_KEYWORDS = [
#     "pakistan", "south asia", "asia-pacific", "developing countries", 
#     "underdeveloped", "low income countries", "global south", "emerging economies",
#     "pakistani", "south asian"
# ]

# def get_domain(url):
#     """Extract domain from URL."""
#     return urlparse(url).netloc.replace("www.", "")

# def classify_grant(url, text, max_retries=3):
#     """
#     Classify grant using AI and fallback rules with improved efficiency.
#     """
#     domain = get_domain(url)
    
#     # Find matching categories
#     categories = ["Other"]
#     for funder in CATEGORY_CONFIG:
#         if domain in funder["url"]:
#             categories = funder.get("categories", ["Other"])
#             break
    
#     # Check if text is too short for meaningful analysis
#     if len(text.strip()) < 100:
#         return default_fallback(text, categories)
    
#     # Prepare prompt with more specific instructions
#     region_hint = f"Specifically check if this grant is applicable to Pakistan or South Asian countries: {', '.join(ELIGIBILITY_KEYWORDS)}."
    
#     prompt = f"""
#     Analyze this grant webpage content and extract the following information:
    
#     1. Status: "open", "closed", or "unknown"
#     2. Opening date (YYYY-MM-DD format or null if not found)
#     3. Closing date (YYYY-MM-DD format or null if not found)
#     4. Eligibility criteria (especially for Pakistan/South Asia)
#     5. Thematic areas/categories
#     6. Whether this grant is specifically applicable to Pakistan
    
#     {region_hint}
    
#     Use these predefined categories if relevant: {categories}.
    
#     Return ONLY valid JSON in this exact format:
#     {{
#         "status": "open|closed|unknown",
#         "open_date": "YYYY-MM-DD|null",
#         "close_date": "YYYY-MM-DD|null",
#         "eligibility": "text description",
#         "thematic_areas": ["category1", "category2"],
#         "applicable_to_pakistan": true|false,
#         "regions": ["region1", "region2"]
#     }}
    
#     Webpage content to analyze:
#     {text[:4000]}  # Increased from 3000 to 4000 for better context
#     """
    
#     models_to_try = ["gpt-4o-mini", "gpt-3.5-turbo"]
    
#     for model in models_to_try:
#         for attempt in range(max_retries):
#             try:
#                 response = client.chat.completions.create(
#                     model=model,
#                     messages=[{"role": "user", "content": prompt}],
#                     max_tokens=800,
#                     temperature=0.1  # Lower temperature for more consistent results
#                 )
                
#                 answer = response.choices[0].message.content.strip()
                
#                 # Improved JSON extraction with better error handling
#                 try:
#                     # Try to find JSON in the response
#                     json_match = re.search(r'\{[\s\S]*\}', answer)
#                     if json_match:
#                         result = json.loads(json_match.group())
#                     else:
#                         # If no JSON found, try to parse the whole response
#                         result = json.loads(answer)
#                 except json.JSONDecodeError:
#                     logger.warning(f"JSON parse failed, using fallback for: {url}")
#                     return default_fallback(text, categories)
                
#                 # Validate and set defaults
#                 result.setdefault("status", "unknown")
#                 result.setdefault("categories", categories)
#                 result.setdefault("regions", [])
#                 result.setdefault("open_date", None)
#                 result.setdefault("close_date", None)
#                 result.setdefault("eligibility", "")
#                 result.setdefault("thematic_areas", [])
#                 result.setdefault("applicable_to_pakistan", False)
                
#                 # Check for Pakistan eligibility
#                 text_lower = text.lower()
#                 if any(keyword in text_lower for keyword in ELIGIBILITY_KEYWORDS):
#                     result["applicable_to_pakistan"] = True
#                     if "pakistan" not in result["regions"]:
#                         result["regions"].append("pakistan")
                
#                 return result
                
#             except Exception as e:
#                 wait_time = (2 ** attempt) + random.random()
#                 logger.warning(f"Retry {attempt+1}/{max_retries} after {wait_time:.1f}s due to: {str(e)}")
                
#                 if "rate limit" in str(e).lower() or "quota" in str(e).lower():
#                     logger.info(f"Switching from {model} due to quota/rate limit")
#                     break
                    
#                 time.sleep(wait_time)
    
#     # Final fallback if all retries fail
#     return default_fallback(text, categories)

# def default_fallback(text, categories):
#     """Improved fallback classification with better keyword detection."""
#     lowered = text.lower()
    
#     # Check status
#     if "closed" in lowered or "ended" in lowered or "finished" in lowered:
#         status = "closed"
#     elif "open" in lowered or "accepting" in lowered or "apply" in lowered:
#         status = "open"
#     else:
#         status = "unknown"
    
#     # Check regions
#     regions_found = [r for r in ELIGIBILITY_KEYWORDS if r in lowered]
    
#     # Check Pakistan specifically
#     applicable_to_pakistan = any(keyword in lowered for keyword in ["pakistan", "south asia"])
    
#     # Try to find dates with regex
#     date_pattern = r'\b(20\d{2}[-/][01]\d[-/][0-3]\d)\b'
#     dates = re.findall(date_pattern, text)
#     open_date = dates[0] if len(dates) > 0 else None
#     close_date = dates[1] if len(dates) > 1 else None
    
#     return {
#         "status": status,
#         "categories": categories,
#         "regions": regions_found,
#         "open_date": open_date,
#         "close_date": close_date,
#         "eligibility": "",
#         "thematic_areas": [],
#         "applicable_to_pakistan": applicable_to_pakistan
#     }



import os
import re
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- FIX 1: Load API key safely ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Missing OPENAI_API_KEY. Please set it in your .env file.")
client = OpenAI(api_key=api_key)


# --- FIX 2: Improved fallback classification ---
def default_fallback(text, categories):
    """Fallback classifier with keyword-based heuristics."""
    lowered = text.lower()

    # Determine status
    if "closed" in lowered:
        status = "closed"
    elif any(k in lowered for k in ["apply", "open for", "submit your application"]):
        status = "open"
    else:
        status = "unknown"

    # Detect regions
    regions_found = []
    if "pakistan" in lowered:
        regions_found.append("pakistan")
    if "south asia" in lowered:
        regions_found.append("south asia")

    applicable_to_pakistan = "pakistan" in lowered or "south asia" in lowered

    # Extract possible dates
    date_pattern = r"\b(\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*20\d{2}|\b20\d{2}[-/\.]\d{1,2}[-/\.]\d{1,2})\b"
    dates = re.findall(date_pattern, text)
    open_date = dates[0] if len(dates) > 0 else None
    close_date = dates[1] if len(dates) > 1 else None

    # Trim eligibility
    eligibility = text[:400] + "..." if len(text) > 400 else text

    thematic_areas = categories if categories != ["Other"] else []

    return {
        "status": status,
        "categories": categories,
        "regions": regions_found,
        "open_date": open_date,
        "close_date": close_date,
        "eligibility": eligibility,
        "thematic_areas": thematic_areas,
        "applicable_to_pakistan": applicable_to_pakistan,
    }


# --- FIX 3: Improved AI-based classification with better accuracy ---
def classify_grant(url, text):
    """
    Classify a grant opportunity text using OpenAI model with improved accuracy.
    Returns a structured dictionary with grant details.
    """
    prompt = f"""
You are an expert grant analyst. Analyze the following grant webpage content and extract accurate information.

CRITICAL INSTRUCTIONS TO AVOID FALSE POSITIVES/NEGATIVES:
1. STATUS: Only mark as "open" if there is CLEAR evidence the grant is currently accepting applications. 
   - Look for: "apply now", "applications open", "accepting proposals", "deadline", "submit by"
   - Mark "closed" only if explicitly stated: "closed", "ended", "no longer accepting", "deadline passed"
   - Mark "unknown" if status is unclear - DO NOT guess
   
2. DATES: Extract dates ONLY if they are clearly mentioned. Use null if uncertain.
   - Look for: "opening date", "application opens", "deadline", "closing date", "submit by"
   - Format: YYYY-MM-DD or null
   
3. PAKISTAN ELIGIBILITY: Only mark true if Pakistan is EXPLICITLY mentioned as eligible.
   - Look for: "Pakistan", "South Asia", "developing countries" (if Pakistan is included)
   - DO NOT mark true just because it's a global grant - be specific
   
4. REGIONS: Only include regions/countries that are EXPLICITLY mentioned as eligible.
   - Be precise - don't infer regions from general terms
   
5. CATEGORIES: Assign relevant categories based on grant focus (Health, Education, Technology, etc.)

Return ONLY valid JSON in this exact format (no markdown, no explanations):
{{
    "status": "open" | "closed" | "unknown",
    "open_date": "YYYY-MM-DD" | null,
    "close_date": "YYYY-MM-DD" | null,
    "eligibility": "brief one-line description",
    "thematic_areas": ["area1", "area2"],
    "applicable_to_pakistan": true | false,
    "regions": ["region1", "region2"],
    "categories": ["category1", "category2"]
}}

Grant webpage content:
{text[:15000]}
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert grant analyst. Be precise and avoid false positives. Only mark information as true if explicitly stated in the text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more consistent, accurate results
            max_tokens=1000,  # Ensure enough tokens for complete response
        )

        answer = completion.choices[0].message.content.strip()

        # --- FIX 4: Improved parsing logic ---
        try:
            json_match = re.search(r"\{[\s\S]*\}", answer)
            result = json.loads(json_match.group() if json_match else answer)
        except Exception as e:
            logger.error(f"⚠️ Invalid AI JSON for {url}: {answer[:400]}...")
            return default_fallback(text, ["Other"])

        # Sanity-check minimal fields
        if not isinstance(result, dict) or "status" not in result:
            logger.warning(f"⚠️ AI result incomplete for {url}. Falling back.")
            return default_fallback(text, ["Other"])

        logger.info(f"✅ AI classification successful for {url}")
        return result

    except Exception as e:
        error_str = str(e)
        # Check for quota/billing errors
        if "quota" in error_str.lower() or "insufficient_quota" in error_str.lower() or "429" in error_str:
            logger.warning(f"⚠️ OpenAI API quota exceeded for {url}. Using fallback classification.")
            logger.warning(f"💡 Please update OPENAI_API_KEY in .env file with a valid key that has quota.")
        else:
            logger.error(f"❌ AI classification failed for {url}: {e}")
        return default_fallback(text, ["Other"])

