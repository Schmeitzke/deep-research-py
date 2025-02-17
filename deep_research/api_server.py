from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_research.deep_research import deep_research
from deep_research.report_writer import write_final_report
from deep_research.follow_up import generate_follow_up
import logging
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# /api/research
# ---------------------------
class ResearchRequest(BaseModel):
    query: str
    breadth: int = 2
    depth: int = 1
    concurrency: int = 2

class ResearchResponse(BaseModel):
    learnings: list[str]
    visited_urls: list[str]
    final_report: str

@app.post("/api/research", response_model=ResearchResponse)
async def perform_research(req: ResearchRequest):
    try:
        research_results = await deep_research(
            query=req.query,
            breadth=req.breadth,
            depth=req.depth,
            concurrency=req.concurrency,
        )
        final_report = await write_final_report(
            prompt=req.query,
            learnings=research_results.get("learnings", []),
            visited_urls=research_results.get("visited_urls", []),
        )
        return ResearchResponse(
            learnings=research_results.get("learnings", []),
            visited_urls=research_results.get("visited_urls", []),
            final_report=final_report,
        )
    except Exception as e:
        logging.error("Error in /api/research endpoint: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# /api/follow_up endpoint
# ---------------------------
class follow_upRequest(BaseModel):
    query: str

class follow_upResponse(BaseModel):
    questions: list[str]

@app.post("/api/follow_up", response_model=follow_upResponse)
async def follow_up_endpoint(req: follow_upRequest):
    """
    Calls the LLM to get follow-up questions about the user query.
    """
    try:
        questions = await generate_follow_up(req.query)
        return follow_upResponse(questions=questions)
    except Exception as e:
        logging.error("Error in /api/follow_up endpoint: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))