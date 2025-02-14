# api_server.py
# uvicorn deep_research.api_server:app --reload --port 8000


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_research.deep_research import deep_research, write_final_report
from deep_research.feedback import generate_feedback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# /api/feedback endpoint
# ---------------------------
class FeedbackRequest(BaseModel):
    query: str

class FeedbackResponse(BaseModel):
    questions: list[str]

@app.post("/api/feedback", response_model=FeedbackResponse)
async def feedback_endpoint(req: FeedbackRequest):
    """
    Calls the LLM to get follow-up questions about the user query.
    """
    try:
        questions = await generate_feedback(req.query)
        return FeedbackResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))
