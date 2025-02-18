from typing import List, Optional
from dataclasses import dataclass
from config_all.config_project import create_c
from deep_research.utils.prompt import system_prompt
from deep_research.api_client import ApiClient
from pydantic import BaseModel

c = create_c()

@dataclass
class SerpQuery:
    query: str
    research_goal: str

class SerpQueryModel(BaseModel):
    query: str
    research_goal: str

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
