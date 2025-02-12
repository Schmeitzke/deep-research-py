import asyncio
import typer
from functools import wraps
from prompt_toolkit import PromptSession

from deep_research_py.deep_research import deep_research, write_final_report
from deep_research_py.feedback import generate_feedback

app = typer.Typer()
session = PromptSession()


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


async def async_prompt(message: str, default: str = "") -> str:
    """Async wrapper for prompt_toolkit."""
    return await session.prompt_async(message)


@app.command()
@coro
async def main(
    concurrency: int = typer.Option(
        default=2, help="Number of concurrent tasks, depending on your API rate limits."
    ),
):
    # Get initial inputs with clear formatting
    query = await async_prompt("\nWhat would you like to research? ")
    print()

    breadth_prompt = "Research breadth (recommended 2-10) [4]: "
    breadth = int((await async_prompt(breadth_prompt)) or "4")
    print()

    depth_prompt = "Research depth (recommended 1-5) [2]: "
    depth = int((await async_prompt(depth_prompt)) or "2")
    print()

    # First show progress for research plan
    print("\nCreating research plan...")
    follow_up_questions = await generate_feedback(query)

    # Then collect answers separately from progress display
    print("\nFollow-up Questions:")
    answers = []
    for i, question in enumerate(follow_up_questions, 1):
        print(f"\nQ{i}: {question}")
        answer = await async_prompt("➤ Your answer: ")
        answers.append(answer)
        print()

    # Combine information
    combined_query = f"""
    Initial Query: {query}
    Follow-up Questions and Answers:
    {chr(10).join(f"Q: {q} A: {a}" for q, a in zip(follow_up_questions, answers))}
    """

    # Now use Progress for the research phase
    print("\nResearching your topic...")
    research_results = await deep_research(
        query=combined_query,
        breadth=breadth,
        depth=depth,
        concurrency=concurrency,
    )

    # Show learnings
    print("\nLearnings:")
    for learning in research_results["learnings"]:
        print(f"- {learning}")

    # Generate report
    print("\nWriting final report...")
    report = await write_final_report(
        prompt=combined_query,
        learnings=research_results["learnings"],
        visited_urls=research_results["visited_urls"],
    )

    # Show results
    print("\nResearch Complete!")
    print("\nFinal Report:")
    print(report)

    # Show sources
    print("\nSources:")
    for url in research_results["visited_urls"]:
        print(f"- {url}")

    # Save report
    with open("output.md", "w") as f:
        f.write(report)
    print("\nReport has been saved to output.md")


def run():
    """Synchronous entry point for the CLI tool."""
    asyncio.run(app())


if __name__ == "__main__":
    asyncio.run(app())
