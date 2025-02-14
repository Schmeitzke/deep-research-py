from typing import Dict, List
from deep_research.prompt import system_prompt
from deep_research.api_client import ApiClient
from pydantic import BaseModel

# Restored schema as in the original combined file
class SerpResultResponse(BaseModel):
    learnings: list[str]
    followUpQuestions: list[str]

async def process_serp_result(query: str, search_result: dict, num_learnings: int = 3, num_follow_up_questions: int = 3) -> Dict[str, List[str]]:

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
