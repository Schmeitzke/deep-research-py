from typing import Dict
from deep_research.config_project import create_c
from deep_research.prompt import system_prompt
from deep_research.api_client import ApiClient

async def process_serp_result(query: str, search_result: dict, num_learnings: int = 3, num_follow_up_questions: int = 3) -> Dict[str, list[str]]:
    contents = []
    for item in search_result["data"]:
        markdown = item.get("markdown", "")
        if markdown:
            contents.append(markdown)

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
            "response_schema": {"type": "json_object"},
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
