from typing import List, Dict, TypedDict
import asyncio
from deep_research.serp_generator import generate_serp_queries, SerpQuery
from deep_research.serp_processor import process_serp_result
from deep_research.page_scraper import scrape_and_extract
from pydantic import BaseModel
from deep_research.api_client import ApiClient

class SearchResponse(TypedDict):
    data: List[Dict[str, str]]

class ResearchResult(TypedDict):
    learnings: List[str]
    visited_urls: List[str]

class SerpQueryModel(BaseModel):
    query: str
    research_goal: str

class SerpResultResponse(BaseModel):
    learnings: list[str]
    followUpQuestions: list[str]

class ReportResponse(BaseModel):
    reportMarkdown: str

async def deep_research(query: str, breadth: int, depth: int, concurrency: int, learnings: List[str] = None, visited_urls: List[str] = None) -> Dict[str, List[str]]:
    learnings = learnings or []
    visited_urls = visited_urls or []

    serp_queries = await generate_serp_queries(query=query, num_queries=breadth, learnings=learnings)
    semaphore = asyncio.Semaphore(concurrency)

    async def process_query(serp_query: SerpQuery) -> Dict[str, List[str]]:
        async with semaphore:
            try:
                print(f"Searching for query: {serp_query.query}")
                api_client = ApiClient()
                result = await api_client.brave_search(query=serp_query.query, offset=0)
                # Removed manual sleep call since rate limiting is handled in brave_search

                # Parse the Brave API result; expected structure: { "web": { "results": [ { "url": "..." }, ... ] } }
                new_urls = [item.get("url") for item in result.get("web", {}).get("results", []) if item.get("url")]

                # For each url, scrape the full HTML and extract heading and body via LLM
                scrape_tasks = [scrape_and_extract(url) for url in new_urls]
                scraped_results = await asyncio.gather(*scrape_tasks)
                # Each scraped result is expected as { "markdown": "..." }

                # Build a compatible search_result structure for process_serp_result
                search_result = {"data": scraped_results}
                new_breadth = max(1, breadth // 2)
                new_depth = depth - 1

                # Get learnings using existing serp_processor logic on scraped content
                new_learnings = await process_serp_result(query=serp_query.query, search_result=search_result, num_follow_up_questions=new_breadth)
                print("Learnings:", new_learnings)

                all_learnings = learnings + new_learnings["learnings"]
                all_urls = visited_urls + new_urls

                if new_depth > 0:
                    print(f"Researching deeper, breadth: {new_breadth}, depth: {new_depth}")
                    next_query = f"""
                    Previous research goal: {serp_query.research_goal}
                    Follow-up research directions: {" ".join(new_learnings["followUpQuestions"])}
                    """.strip()
                    return await deep_research(
                        query=next_query,
                        breadth=new_breadth,
                        depth=new_depth,
                        concurrency=concurrency,
                        learnings=all_learnings,
                        visited_urls=all_urls,
                    )
                print("Deep research complete")
                return {"learnings": all_learnings, "visited_urls": all_urls}

            except Exception as e:
                if "Timeout" in str(e):
                    print(f"Timeout error running query: {serp_query.query}: {e}")
                else:
                    print(f"Error running query: {serp_query.query}: {e}")
                return {"learnings": [], "visited_urls": []}

    results = await asyncio.gather(*[process_query(q) for q in serp_queries])
    all_learnings = list(set(learning for result in results for learning in result["learnings"]))
    all_urls = list(set(url for result in results for url in result["visited_urls"]))
    return {"learnings": all_learnings, "visited_urls": all_urls}
