# Deep Research Python Project

This codebase is an asynchronous research engine that guides users through in-depth research cycles and generates a final report. It uses several key components and external APIs to collect information, generate follow-up questions, search online, and compile research learnings.

## Overview

- **run.py:**  
  Contains the CLI entry point built with Typer and asyncio. It gathers user inputs for the research topic, breadth, and depth, and orchestrates the research cycle by calling the relevant functions.

- **prompt.py:**  
  Generates a system prompt including the current timestamp. This prompt is used as a context for LLM completions throughout the project.

- **follow_up.py:**  
  Utilizes the system prompt from `prompt.py` and the API client to generate follow-up questions for the research topic. These questions help clarify what further information is needed.

- **deep_research.py:**  
  Serves as the core engine for the research process:
  - **SERP Query Generation:** Uses LLM to produce search queries (`generate_serp_queries`).
  - **Processing Search Results:** Through `process_serp_result`, it extracts learnings and follow-up questions from search results.
  - **Recursive Research:** The `deep_research` function recursively calls itself to go deeper into the subject by reducing the depth and gradually refining the research.
  - **Final Report Compilation:** The `write_final_report` function gathers all learnings and visited URLs to create a comprehensive markdown report.

- **config.py:**  
  Manages API keys and configurations by reading environment variables and setting up the client configuration.

- **ai/text_splitter.py & ai/providers.py:**  
  Implement strategies to handle large texts:
  - **Text Splitting:** The `RecursiveCharacterTextSplitter` class recursively splits texts to ensure prompts do not exceed the maximum context size.
  - **Trimming Prompts:** `trim_prompt` in `providers.py` ensures that query prompts are within context limits by leveraging the text splitter.

## Research Process Flow

1. **User Input & Initialization (run.py):**
   - The tool starts by prompting the user for a research query, research breadth, and depth.
   - It then generates follow-up questions to refine the research plan.

2. **Generating Research Queries (deep_research.py):**
   - Using the refined research topic and initial learnings, the code calls `generate_serp_queries` to create a list of queries based on user follow_up and context.
   - Each query is processed asynchronously to adhere to API concurrency limits.

3. **Processing Search Results:**
   - For each generated query, search results are obtained using Firecrawl.
   - The `process_serp_result` function extracts relevant learnings and additional follow-up questions from the results.

4. **Recursive Deep Dive:**
   - If the specified research depth allows, the function recursively explores deeper queries. Each subsequent level reduces breadth and depth to refine the research and expand the list of learnings.

5. **Report Generation:**
   - Once the research cycles finish, `write_final_report` collates all learnings and visited URLs to provide a comprehensive report in markdown format.
   - The report includes detailed research learnings and sources.

6. **Text Management:**
   - Throughout the process, large texts are managed by splitting them into smaller chunks using the `RecursiveCharacterTextSplitter` and trimmed with `trim_prompt` to fit within API constraints.

## Relationships Between Components

- **LLM and API Client:**  
  Most modules (follow_up, deep_research, text splitting) interact with the LLM via a central API client, ensuring consistent behavior and error handling.

- **Reused Prompts:**  
  The `system_prompt` from `prompt.py` is a key component that is injected into several API calls, ensuring that the context remains consistent.

- **Asynchronous Operations:**  
  The project is built on `asyncio` to handle multiple API requests concurrently, controlled by semaphores to respect rate limits.

- **Recursion:**  
  The main driver of research is the recursive call within `deep_research` which adjusts its strategy based on previous findings, thereby refining the output progressively.

This overview should provide a clear understanding of the codebase structure, the research flow, and how modules interact to create a robust research tool.
