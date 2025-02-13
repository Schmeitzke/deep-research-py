import os

class Stub:
    pass

def api_keys(c):
    c.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    c.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY_CONSULTANT")
    c.XAI_API_KEY = os.environ.get("XAI_API_KEY")
    c.FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_CONSULTANT")
    return c

def llm(c):
    c.llm_provider = "gemini"
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
