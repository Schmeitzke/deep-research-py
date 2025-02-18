import asyncio
from pydantic import BaseModel
from .utils.prompt import system_prompt
from .api_client import ApiClient
from .page_scraper import scrape_and_extract

# New model for clarified SERP query
class ClarifyResponse(BaseModel):
    clarified_query: str

class FollowUpResponse(BaseModel):
    questions: list[str]

async def generate_follow_up(query: str) -> list[str]:
    api_client = ApiClient()
    
    # Step 1: Clarify the research topic via LLM with improved prompt
# Optimized prompt to clarify the research topic for SERP query generation
    clarify_prompt = (
        f"Given the research topic: '{query}', generate a single SERP search query that captures the core essence of the topic. "
        "This query should enhance understanding of the topic and serve as a basis for generating precise follow-up questions. "
        "Retain any acronyms and abbreviations exactly as provided—do not expand them into their full forms. "
        "Avoid using overly specific terms; instead, employ a more general context while using the same terminology as the user. "
        "Return your output strictly as a JSON object with a single key 'clarified_query'. "
        "For example, if the input is 'Tell me the latest news about the decision made by DOGE and Elon Musk', then return "
        "<example>{\"clarified_query\": \"latest news DOGE Elon Musk decision\"}</example>."
    )

    clarify_response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=clarify_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ClarifyResponse,
        }
    )
    try:
        clarified = clarify_response.parsed
        clarified_query = clarified.clarified_query
        print(f"Clarified query: {clarified_query}")
    except Exception as e:
        print(f"Error parsing clarified query: {e}")
        clarified_query = query  # fallback to original query

    # Step 2: Retrieve search results using the Brave API with the clarified query
    search_result = await api_client.brave_search(query=clarified_query, offset=0, count=3)
    new_urls = [item.get("url") for item in search_result.get("web", {}).get("results", []) if item.get("url")]

    # Step 3: Scrape pages from the retrieved URLs
    scrape_tasks = [scrape_and_extract(url) for url in new_urls]
    scraped_results = await asyncio.gather(*scrape_tasks)
    scraped_content = "\n".join(result.get("markdown", "") for result in scraped_results if result.get("markdown"))

    # Step 4: Request follow-up questions using the user query and scraped info
    follow_up_prompt = (
        f"Given the research topic: '{query}' and the following information retrieved from a refined SERP query:\n"
        f"{scraped_content}\n\n"
        "Generate 3-5 follow-up questions designed to help the user further refine and clarify their research intent. "
        "The questions should be open-ended and encourage the user to provide additional context, preferences, or specific aspects of the topic they are interested in. "
        "Avoid framing the questions in a way that tests the user or assumes detailed prior knowledge of the subject matter. "
        "Focus solely on clarifying the user's research needs rather than the content of the SERP results. "
        "Return your output strictly as a JSON object with the key 'questions'."
    )
    follow_response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=follow_up_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": FollowUpResponse,
        }
    )
    try:
        result = follow_response.parsed
        return result.questions
    except Exception as e:
        print(f"Error parsing follow-up questions: {e}")
        return []
