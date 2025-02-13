from typing import List, Dict, TypedDict, Optional
from dataclasses import dataclass
import asyncio
from .prompt import system_prompt
from .api_client import ApiClient
from pydantic import BaseModel

class SearchResponse(TypedDict):
    data: List[Dict[str, str]]

class ResearchResult(TypedDict):
    learnings: List[str]
    visited_urls: List[str]

@dataclass
class SerpQuery:
    query: str
    research_goal: str

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

async def generate_serp_queries(query: str, num_queries: int = 3, learnings: Optional[List[str]] = None) -> List[SerpQuery]:
    prompt_str = (f"Given the following prompt: '{query}', generate a list of SERP queries to research the topic. "
                  f"Return a JSON object with a 'queries' array field containing up to {num_queries} unique queries. "
                  "Each query object should have 'query' and 'research_goal' fields.")
    if learnings:
        prompt_str += f" Use these learnings for additional context: {' '.join(learnings)}"
    api_client = ApiClient()
    response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=prompt_str,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[SerpQueryModel],
        }
    )
    try:
        queries_list = response.parsed
        return [SerpQuery(**q.dict()) for q in queries_list][:num_queries]
    except Exception as e:
        print(f"Error parsing JSON response: {e}")
        return []

async def process_serp_result(query: str, search_result: SearchResponse, num_learnings: int = 3, num_follow_up_questions: int = 3) -> Dict[str, List[str]]:

    # Initialize an empty list to store the processed content
    contents = []
    # Iterate through each item in the search results
    for item in search_result["data"]:
        # Get the markdown content if it exists
        markdown = item.get("markdown", "")
        # If markdown exists, trim it and add to contents
        if markdown:
            contents.append(markdown)

    # Create the contents string separately
    contents_str = "".join(f"<content>\n{content}\n</content>" for content in contents)

    prompt_str = (
        f"Given the following contents for the query <query>{query}</query>, generate learnings and follow-up questions. "
        f"Return a JSON object with up to {num_learnings} unique learnings and {num_follow_up_questions} follow-up questions. "
        f"<contents>{contents_str}</contents>"
    )

    api_client = ApiClient()
    response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=prompt_str,
        config={
            "response_mime_type": "application/json",
            "response_schema": SerpResultResponse,
        }
    )
    try:
        result = response.parsed
        return {
            "learnings": result.learnings[:num_learnings],
            "followUpQuestions": result.followUpQuestions[:num_follow_up_questions],
        }
    except Exception as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response}")
        return {"learnings": [], "followUpQuestions": []}

async def write_final_report(prompt: str, learnings: List[str], visited_urls: List[str]) -> str:
    # Build a string of learnings by putting each in XML tags
    learnings_array = []
    for learning in learnings:
        learning_with_tags = "<learning>\n" + learning + "\n</learning>"
        learnings_array.append(learning_with_tags)
    
    # Join all learnings with newlines
    learnings_string = "\n".join(learnings_array)
    
    user_prompt = (
        f"Given the following prompt from the user, write a final report on the topic using "
        f"the learnings from research. Return a JSON object with a 'reportMarkdown' field "
        f"containing a detailed markdown report (aim for 3+ pages). Include ALL the learnings "
        f"from research:\n\n<prompt>{prompt}</prompt>\n\n"
        f"Here are all the learnings from research:\n\n<learnings>\n{learnings_string}\n</learnings>"
    )

    api_client = ApiClient()
    response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=user_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ReportResponse,
        }
    )

    try:
        result = response.parsed
        report = result.reportMarkdown
        urls_section = "\n\n## Sources\n\n" + "\n".join(f"- {url}" for url in visited_urls)
        return report + urls_section
    except Exception as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response}")
        return "Error generating report"


async def deep_research(query: str, breadth: int, depth: int, concurrency: int, learnings: List[str] = None, visited_urls: List[str] = None,) -> ResearchResult:
    learnings = learnings or []
    visited_urls = visited_urls or []

    # Generate search queries
    serp_queries = await generate_serp_queries(query=query, num_queries=breadth, learnings=learnings)

    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(concurrency)

    async def process_query(serp_query: SerpQuery) -> ResearchResult:
        async with semaphore:
            try:
                api_client = ApiClient()
                result = await api_client.firecrawl_search(serp_query.query, timeout=15000, limit=5)
                # Collect new URLs
                new_urls = [item.get("url") for item in result["data"] if item.get("url")]

                # Calculate new breadth and depth for next iteration
                new_breadth = max(1, breadth // 2)
                new_depth = depth - 1

                # Process the search results
                new_learnings = await process_serp_result(query=serp_query.query, search_result=result, num_follow_up_questions=new_breadth)

                all_learnings = learnings + new_learnings["learnings"]
                all_urls = visited_urls + new_urls

                # If we have more depth to go, continue research
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

    # Process all queries concurrently
    results = await asyncio.gather(*[process_query(query) for query in serp_queries])

    # Combine all results
    all_learnings = list(set(learning for result in results for learning in result["learnings"]))

    all_urls = list(set(url for result in results for url in result["visited_urls"]))

    return {"learnings": all_learnings, "visited_urls": all_urls}
