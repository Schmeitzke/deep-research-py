from deep_research.config_project import create_c
from deep_research.prompt import system_prompt
from deep_research.api_client import ApiClient

async def write_final_report(prompt: str, learnings: list[str], visited_urls: list[str]) -> str:
    # Build a string of learnings by putting each in XML tags
    learnings_array = []
    for learning in learnings:
        learning_with_tags = "<learning>\n" + learning + "\n</learning>"
        learnings_array.append(learning_with_tags)
    
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
            "response_schema": {"type": "json_object"},
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
