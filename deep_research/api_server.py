from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_research.deep_research import deep_research
from deep_research.report_writer import write_final_report
from deep_research.follow_up import generate_follow_up
import logging
import traceback
import asyncio
import json
from fastapi.responses import StreamingResponse

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


# ---------------------------
# Streaming endpoints for progress updates
# ---------------------------
@app.post("/api/research_stream")
async def perform_research_stream(req: ResearchRequest):
    async def event_generator():
        progress_queue = asyncio.Queue()

        def progress_callback(update: dict):
            progress_queue.put_nowait(update)

        research_task = asyncio.create_task(deep_research(
            query=req.query,
            breadth=req.breadth,
            depth=req.depth,
            concurrency=req.concurrency,
            progress_callback=progress_callback
        ))
        while not research_task.done():
            try:
                update = await asyncio.wait_for(progress_queue.get(), timeout=1)
                yield f"data: {json.dumps({'type': 'progress', 'data': update})}\n\n"
            except asyncio.TimeoutError:
                continue
        try:
            research_results = await research_task
            final_report = await write_final_report(
                prompt=req.query,
                learnings=research_results.get("learnings", []),
                visited_urls=research_results.get("visited_urls", []),
            )
            final_response = {
                "learnings": research_results.get("learnings", []),
                "visited_urls": research_results.get("visited_urls", []),
                "final_report": final_report
            }
            yield f"data: {json.dumps({'type': 'final', 'data': final_response})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/follow_up_stream")
async def follow_up_stream(req: follow_upRequest):
    async def event_generator():
        # Simulate progress stages for follow-up generation.
        progress_updates = [
            {"stage": "clarify", "message": "Generating clarified query..."},
            {"stage": "search", "message": "Fetching search results..."},
            {"stage": "scrape", "message": "Scraping pages..."},
            {"stage": "questions", "message": "Generating follow-up questions..."}
        ]
        for update in progress_updates:
            yield f"data: {json.dumps({'type': 'progress', 'data': update})}\n\n"
            await asyncio.sleep(1)
        try:
            questions = await generate_follow_up(req.query)
            yield f"data: {json.dumps({'type': 'final', 'data': {'questions': questions}})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
