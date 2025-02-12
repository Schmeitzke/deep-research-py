from typing import List
import json
from .prompt import system_prompt
from .ai.api_client import ApiClient

async def generate_feedback(query: str) -> List[str]:
    """Generates follow-up questions to clarify research direction."""
    api_client = ApiClient()
    messages = [
        {"role": "system", "content": system_prompt()},
        {
            "role": "user",
            "content": f"Given this research topic: {query}, generate 3-5 follow-up questions to better understand the user's research needs. Return the response as a JSON object with a 'questions' array field.",
        },
    ]
    
    response = await api_client.llm_complete(  # changed code
        messages=messages,
        model="o3-mini",
        response_format={"type": "json_object"}
    )

    # Parse the JSON response
    try:
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response.choices[0].message.content}")
        return []

