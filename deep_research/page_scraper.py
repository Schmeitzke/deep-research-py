import httpx
from pydantic import BaseModel
from deep_research.api_client import ApiClient

# Import for Selenium fallback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class PageScrapeResponse(BaseModel):
    heading: str
    body: str

async def scrape_and_extract(url: str) -> dict:
    full_html = ""
    # Attempt fetching with httpx
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            full_html = response.text
    except Exception as e:
        print(f"Error fetching URL with httpx for {url}: {e}")
        # Selenium fallback (synchronous, consider running in executor if needed)
        try:
            options = Options()
            # Set headless mode using add_argument
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            full_html = driver.page_source
            driver.quit()
        except Exception as e2:
            print(f"Selenium fallback failed for {url}: {e2}")
            full_html = "<html>Placeholder content: page could not be fetched.</html>"

    prompt_str = (
        f"Below is the complete HTML content of a webpage:\n\n"
        f"<html>\n{full_html}\n</html>\n\n"
        "Extract the main article heading and body. Return a JSON object with the fields 'heading' and 'body' in markdown format. "
        "Make sure to output valid JSON."
    )

    api_client = ApiClient()
    response_llm = await api_client.llm_complete(
        system_instruction="You are a webpage content extractor that reads the full HTML code of a webpage and returns the article heading and body in markdown format.",
        prompt=prompt_str,
        config={
            "response_mime_type": "application/json",
            "response_schema": PageScrapeResponse,
        }
    )
    try:
        parsed = response_llm.parsed
        markdown = f"# {parsed.heading}\n\n{parsed.body}"
        return {"markdown": markdown}
    except Exception as e:
        print(f"Error parsing page scrape response for {url}: {e}")
        return {"markdown": ""}
