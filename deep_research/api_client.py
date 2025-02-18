import asyncio
from openai import OpenAI
from google import genai
import google.generativeai as genai_old
from google.genai import types
import tiktoken
from config_all.config_project import create_c
import httpx
from .utils.rate_limiter import global_rate_limiter

c = create_c()

class ApiClient:
    def __init__(self, api_provider=c.llm_provider):
        self.api_provider = api_provider
        self.openai_client = None
        self.gemini_client = None
        self.xai_client = None

    async def check_and_trim_prompt(self, system_instruction: str, prompt: str, provider: str) -> str:
        if provider == "openai":
            context_window = 190000
            enc = tiktoken.encoding_for_model("o3-mini")
            sys_tokens = enc.encode(system_instruction)
            prompt_tokens = enc.encode(prompt)
            total = len(sys_tokens) + len(prompt_tokens)
            if total <= context_window:
                return prompt
            allowed_prompt = context_window - len(sys_tokens)
            trimmed_tokens = prompt_tokens[:allowed_prompt]
            return enc.decode(trimmed_tokens)
        elif provider == "gemini":
            dummy_client = genai_old.configure(api_key=c.GEMINI_API_KEY)
            model_info = genai_old.get_model(name=c.gemini_model, client=dummy_client)
            context_window = model_info.input_token_limit
            dummy_model = genai_old.GenerativeModel(c.gemini_model)
            sys_count = int(str(dummy_model.count_tokens(system_instruction)).split(': ')[-1])
            prompt_count = int(str(dummy_model.count_tokens(prompt)).split(': ')[-1])
            total = sys_count + prompt_count
            if total <= context_window:
                return prompt
            allowed_prompt_tokens = context_window - sys_count
            words = prompt.split()
            trimmed = " ".join(words[:allowed_prompt_tokens])
            return trimmed
        elif provider == "xai":
            context_window = 130000
            sys_count = len(system_instruction.split())
            prompt_count = len(prompt.split())
            total = sys_count + prompt_count
            if total <= context_window:
                return prompt
            allowed_prompt_tokens = context_window - sys_count
            trimmed = " ".join(prompt.split()[:allowed_prompt_tokens])
            return trimmed
        else:
            return prompt

    async def llm_complete(self, *, system_instruction: str = "", prompt: str = "", config: dict = None, messages=None, response_format={"type": "json_object"}):
        loop = asyncio.get_event_loop()
        prompt = await self.check_and_trim_prompt(system_instruction, prompt, self.api_provider)
        if messages is None:
            messages = [{"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}]
        if self.api_provider == "openai":
            self.openai_client = OpenAI(api_key=c.OPENAI_API_KEY)
            completion = await loop.run_in_executor(
                None,
                lambda: self.openai_client.beta.chat.completions.parse(
                    model=c.openai_model,
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
                    model=c.gemini_model,
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
                    model=c.xai_model,
                    messages=messages,
                    response_format=config["response_schema"] if config and "response_schema" in config else None,
                )
            )
            return completion.choices[0].message
        else:
            raise ValueError(f"Unknown API provider: {self.api_provider}")

    async def brave_search(self, query: str, offset: int = 0, count: int = 10) -> dict:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": c.BRAVE_API_KEY
        }
        for current_offset in range(offset, 10):
            await global_rate_limiter.wait()
            params = {
                "q": query,
                "safesearch": "off",
                "offset": current_offset,
                "count": count
            }
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    return response.json()  # Expected structure: { "web": { "results": [...] } }
            except Exception as e:
                print(f"Error with offset {current_offset} for query '{query}': {e}")
        raise Exception(f"All offsets failed for query '{query}'")
