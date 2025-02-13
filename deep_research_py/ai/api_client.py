import asyncio
from openai import OpenAI
from google import genai
from google.genai import types
from firecrawl import FirecrawlApp
from config import create_c
c = create_c()

class ApiClient:
    def __init__(self, api_provider=c.llm_provider):
        self.api_provider = api_provider
        self.openai_client = None
        self.gemini_client = None
        self.xai_client = None
        self.firecrawl_client = None

    async def llm_complete(self, *, system_instruction: str = "", prompt: str = "", config: dict = None, messages=None, response_format={"type": "json_object"}):
        loop = asyncio.get_event_loop()
        if messages is None:
            messages = [{"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}]
        if self.api_provider == "openai":
            self.openai_client = OpenAI(api_key=c.OPENAI_API_KEY)
            completion = await loop.run_in_executor(
                None,
                lambda: self.openai_client.beta.chat.completions.parse(
                    model="gpt-4o",
                    messages=messages,
                    response_format=config["response_schema"] if config and "response_schema" in config else None,
                )
            )
            return completion.choices[0].message
        elif self.api_provider == "gemini":
            self.gemini_client = genai.Client(api_key=c.GEMINI_API_KEY)
            extra_config = config if config else {}
            response = await loop.run_in_executor(
                None,
                lambda: self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    config=types.GenerateContentConfig(system_instruction=system_instruction, **extra_config),
                    contents=[prompt]
                )
            )
            return response
        elif self.api_provider == "xai":
            self.xai_client = OpenAI(api_key=c.OPENAI_API_KEY, base_url="https://api.x.ai/v1")
            completion = await loop.run_in_executor(
                None,
                lambda: self.xai_client.beta.chat.completions.parse(
                    model="grok-2-latest",
                    messages=messages,
                    response_format=config["response_schema"] if config and "response_schema" in config else None,
                )
            )
            return completion.choices[0].message
        else:
            raise ValueError(f"Unknown API provider: {self.api_provider}")
 
    async def firecrawl_search(self, query, timeout=None, limit=None):
        loop = asyncio.get_event_loop()
        self.firecrawl_client = FirecrawlApp(api_key=c.FIRECRAWL_API_KEY)
        params = {
            "timeout": timeout, 
            "limit": limit,
            "scrapeOptions": {
            "formats": ["markdown"]
            }
        }
        search_result = await loop.run_in_executor(
            None,
            lambda: self.firecrawl_client.search(query=query, params=params)
        )
        return search_result
