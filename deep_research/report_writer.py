from deep_research.utils.prompt import system_prompt
from deep_research.api_client import ApiClient
from pydantic import BaseModel
from typing import List

# Define Pydantic models for structured outputs at each stage.
class ReportStage1Response(BaseModel):
    introduction: str
    problem_statement: str

class ReportStage2Response(BaseModel):
    in_depth_answer: str

class ReportStage3Response(BaseModel):
    conclusion: str
    references: str

async def write_final_report(prompt: str, learnings: List[str], visited_urls: List[str]) -> str:
    print("!!!!!!!!!!!!!!!!!!!", learnings)
    # Format the research learnings by wrapping each in XML-like tags.
    learnings_array = [f"<learning>\n{learning}\n</learning>" for learning in learnings]
    learnings_string = "\n".join(learnings_array)
    
    # You may also include visited URLs as part of the research context if desired.
    urls_string = "\n".join(f"- {url}" for url in visited_urls) if visited_urls else ""
    retrieved_urls = f"Retrieved URLs:\n{urls_string}" if urls_string else ""
    
    api_client = ApiClient()
    
    # ------------------
    # Stage 1: Introduction and Problem Statement
    # ------------------
    stage1_prompt = (
        f"Given the following user prompt:\n<prompt>{prompt}</prompt>\n\n"
        f"And these research learnings:\n<learnings>\n{learnings_string}\n</learnings>\n\n"
        f"{retrieved_urls}\n\n"
        "Please write the report's Introduction and Problem Statement in markdown format. "
        "Aim for approximately half a page for each section. "
        "Do not include a headers for these sections. "
        "Do not write about the process of research. Write as if you are writing the final report basing it on the research findings. "
        "Return a JSON object with the fields 'introduction' and 'problem_statement'."
    )
    stage1_response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=stage1_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ReportStage1Response,
        }
    )
    try:
        stage1_result: ReportStage1Response = stage1_response.parsed
    except Exception as e:
        print(f"Error parsing Stage 1 response: {e}")
        return "Error generating report at stage 1"

    # ------------------
    # Stage 2: In-Depth Answer
    # ------------------
    # Include stage 1 output along with the full learnings so that the model bases its output on all available info.
    stage2_prompt = (
        f"The report so far includes the following sections:\n"
        f"## Introduction\n{stage1_result.introduction}\n\n"
        f"## Problem Statement\n{stage1_result.problem_statement}\n\n"
        f"Additionally, here are the research learnings:\n<learnings>\n{learnings_string}\n</learnings>\n\n"
        f"{retrieved_urls}\n\n"
        "Based on all of the above, please provide an In-Depth Answer that comprehensively addresses the research question. "
        "In other words, write the body of the report that answers the question in detail and based on the facts retrieved. "
        "Do not write about the process of research. Write as if you are writing the final report basing it on the research findings. "
        "Make as little as possible use of bullet points or lists, only if necessary. "
        "Do not include a conclusion or references at this stage, just the main content. "
        "Do not include a header for this section. "
        "Aim for at least two pages of content in markdown format. "
        "Return a JSON object with the field 'in_depth_answer'."
    )
    stage2_response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=stage2_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ReportStage2Response,
        }
    )
    try:
        stage2_result: ReportStage2Response = stage2_response.parsed
    except Exception as e:
        print(f"Error parsing Stage 2 response: {e}")
        return "Error generating report at stage 2"

    # ------------------
    # Stage 3: Conclusion and References
    # ------------------
    # Provide all previously generated content along with the learnings as context.
    stage3_prompt = (
        f"The report so far includes the following sections:\n"
        f"## Introduction\n{stage1_result.introduction}\n\n"
        f"## Problem Statement\n{stage1_result.problem_statement}\n\n"
        f"## In-Depth Answer\n{stage2_result.in_depth_answer}\n\n"
        f"Also included are the complete set of research learnings:\n<learnings>\n{learnings_string}\n</learnings>\n\n"
        f"{retrieved_urls}\n\n"
        "Now, please write a Conclusion that summarizes the findings and provide a References section based on the research. "
        "Do not write about the process of research. Write as if you are writing the final report basing it on the research findings. "
        "Aim for approximately half a page for the Conclusion and include a list of references which follow the APA7 guidelines, both in markdown format. "
        "Return a JSON object with the fields 'conclusion' and 'references'."
    )
    stage3_response = await api_client.llm_complete(
        system_instruction=system_prompt(),
        prompt=stage3_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ReportStage3Response,
        }
    )
    try:
        stage3_result: ReportStage3Response = stage3_response.parsed
    except Exception as e:
        print(f"Error parsing Stage 3 response: {e}")
        return "Error generating report at stage 3"

    # ------------------
    # Combine all sections into one markdown-formatted report.
    # ------------------
    markdown_report = (
        f"## Introduction\n{stage1_result.introduction}\n\n"
        f"## Problem Statement\n{stage1_result.problem_statement}\n\n"
        f"## In-Depth Answer\n{stage2_result.in_depth_answer}\n\n"
        f"## Conclusion\n{stage3_result.conclusion}\n\n"
        f"## References\n{stage3_result.references}\n\n"
    )

    # Optionally, append the visited URLs as a sources section if not already included.
    if urls_string:
        markdown_report += "\n## Sources\n" + urls_string

    return markdown_report
