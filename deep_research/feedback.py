from pydantic import BaseModel
from .prompt import system_prompt
from .api_client import ApiClient

class FollowUpResponse(BaseModel):
    questions: list[str]

async def generate_feedback(query: str) -> list[str]:
    api_client = ApiClient()
    instruction = system_prompt()
    prompt_str = (f"Given this research topic: {query}, generate 3-5 follow-up questions to better understand the user's research needs.")
    config = {
        "response_mime_type": "application/json",
        "response_schema": FollowUpResponse,
    }
    response = await api_client.llm_complete(system_instruction=instruction, prompt=prompt_str, config=config)
    try:
        result = response.parsed
        return result.questions
    except Exception as e:
        print(f"Error parsing response: {e}")
        return []
