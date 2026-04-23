import dotenv
import os

dotenv.load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from tool_retriever import get_tools

def llm_node():
    model_params = {
    'model' : 'openai/gpt-4.1',
    "base_url" : "https://lightning.ai/api/v1/",
    "api_key" : os.getenv("LIGHTNING_API_KEY"),
}
    llm = ChatOpenAI(**model_params)
    return llm

def llm_reasoning_node():
    params = {
        'model': 'openai/gpt-oss-120b'
    }
    model = ChatGroq(**params)
    tools = get_tools()
    return model.bind_tools(tools)