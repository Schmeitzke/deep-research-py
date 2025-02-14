from typing import List, Dict, TypedDict, Optional
from dataclasses import dataclass
import asyncio
from .prompt import system_prompt
from deep_research.serp_generator import generate_serp_queries, SerpQuery
from deep_research.serp_processor import process_serp_result
from deep_research.report_writer import write_final_report
from deep_research.api_client import ApiClient
from pydantic import BaseModel

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

class Firecrawl:
    def __init__(self):
        self.api_client = ApiClient()

    async def search(self, query: str) -> SearchResponse:
        """Search using Firecrawl SDK in a thread pool to keep it async."""
        try:
            response = await self.api_client.firecrawl_search(query=query, timeout=15000, limit=5)

            # Handle the response format from the SDK
            if isinstance(response, dict) and "data" in response:
                # Response is already in the right format
                return response
            elif isinstance(response, dict) and "success" in response:
                # Response is in the documented format
                return {"data": response.get("data", [])}
            elif isinstance(response, list):
                # Response is a list of results
                formatted_data = []
                for item in response:
                    if isinstance(item, dict):
                        formatted_data.append(item)
                    else:
                        # Handle non-dict items (like objects)
                        formatted_data.append(
                            {
                                "url": getattr(item, "url", ""),
                                "markdown": getattr(item, "markdown", "")
                                or getattr(item, "content", ""),
                                "title": getattr(item, "title", "")
                                or getattr(item, "metadata", {}).get("title", ""),
                            }
                        )
                return {"data": formatted_data}
            else:
                print(f"Unexpected response format from Firecrawl: {type(response)}")
                return {"data": []}

        except Exception as e:
            print(f"Error searching with Firecrawl: {e}")
            print(f"Response type: {type(response) if 'response' in locals() else 'N/A'}")
            return {"data": []}

async def deep_research(query: str, breadth: int, depth: int, concurrency: int, learnings: List[str] = None, visited_urls: List[str] = None) -> Dict[str, List[str]]:
    learnings = learnings or []
    visited_urls = visited_urls or []

    serp_queries = await generate_serp_queries(query=query, num_queries=breadth, learnings=learnings)

    semaphore = asyncio.Semaphore(concurrency)

    async def process_query(serp_query: SerpQuery) -> Dict[str, List[str]]:
        async with semaphore:
            try:
                api_client = ApiClient()
                result = await api_client.firecrawl_search(serp_query.query, timeout=15000, limit=5)
                new_urls = [item.get("url") for item in result["data"] if item.get("url")]

                new_breadth = max(1, breadth // 2)
                new_depth = depth - 1

                new_learnings = await process_serp_result(query=serp_query.query, search_result=result, num_follow_up_questions=new_breadth)

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
