import os

class Stub:
    pass

def api_keys(c):
    c.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    c.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY_CONSULTANT")
    c.XAI_API_KEY = os.environ.get("XAI_API_KEY")
    c.FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_CONSULTANT")
    c.BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY")
    return c

def llm(c):
    # Set the API provider
    c.llm_provider = "gemini"

    # Set the API models
    c.gemini_model = "models/gemini-2.0-flash"
    c.openai_model = "o3-mini"
    c.xai_model = "grok-2-1212"
    return c

def make_c():
    c = Stub()
    functions = [
        api_keys,
        llm,
    ]
    for f in functions:
        c = f(c)
    return c

def create_c():
    return make_c()
