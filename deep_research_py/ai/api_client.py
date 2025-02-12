import asyncio
from openai import OpenAI
from google import genai
from firecrawl import FirecrawlApp
from config import create_c
c = create_c()

class ApiClient:
    def __init__(self, api_provider=None):
        self.api_provider = api_provider
        self.openai_client = None
        self.gemini_client = None
        self.xai_client = None
        self.firecrawl_client = None

    async def llm_complete(self, messages, response_format={"type": "json_object"}):
        loop = asyncio.get_event_loop()
        if self.api_provider == "openai":
            self.openai_client = OpenAI(api_key=c.OPENAI_API_KEY)
            completion = await loop.run_in_executor(
                None,
                lambda: self.openai_client.chat.completions.create(
                    model="o3-mini",
                    messages=messages,
                    response_format=response_format,
                )
            )
            return completion.choices[0].message
        elif self.api_provider == "gemini":
            self.gemini_client = genai.Client(c.GEMINI_API_KEY)
            completion = await loop.run_in_executor(
                None,
                lambda: self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash	",
                    messages=messages,
                    response_format=response_format,
                )
            )
            return completion.text
        elif self.api_provider == "xai":
            self.xai_client = OpenAI(api_key=c.OPENAI_API_KEY, base_url="https://api.x.ai/v1")
            completion = await loop.run_in_executor(
                None,
                lambda: self.xai_client.chat.completions.create(
                    model="grok-2-1212",
                    messages=messages,
                    response_format=response_format,
                )
            )
            return completion.choices[0].message
        else:
            raise ValueError(f"Unknown API provider: {self.api_provider}")
        
    async def firecrawl_visit_url(self, messages, response_format={"type": "json_object"}):
        loop = asyncio.get_event_loop()
        self.firecrawl_client = FirecrawlApp(api_key=c.FIRECRAWL_API_KEY)
        return None
    
    async def firecrawl_search(self, query, timeout=None, limit=None):
        loop = asyncio.get_event_loop()
        self.firecrawl_client = FirecrawlApp(api_key=c.FIRECRAWL_API_KEY)
        search_result = await loop.run_in_executor(
            None,
            lambda: self.firecrawl_client.search(
                query=query,
                timeout=timeout,
                limit=limit,
            )
        )
        return search_result
