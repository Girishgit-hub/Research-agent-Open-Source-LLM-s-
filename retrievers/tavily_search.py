from langchain_tavily import TavilySearch, TavilyExtract
from langchain_core.documents import Document
import dotenv

dotenv.load_dotenv()
from typing import Any, Dict, List, Literal, Optional, Type, Union


class TavilyPipeline:
    def __init__(self):
        self.search_tool = TavilySearch()
        self.extract_tool = TavilyExtract()

    def search(self, input:Dict[str, Any] ) -> Dict[str, Any]:
        response = self.search_tool.invoke(input)
        query = response.get('query', None)
        results = response.get('results', None)
        documents = [Document(page_content=item['content'], metadata={"source": item['url'], "title": item['title']})
                     for item in results]
        return {'query': query, 'documents': documents}

    def extract(self, query:str, docs:List[Document]) -> Dict[str, Any]:
        urls = [item.metadata['source'] for item in docs]
        tavily_extract_tool = TavilyExtract()
        results = tavily_extract_tool.invoke(input={'urls': urls})
        documents = [
            Document(page_content=item['raw_content'], metadata={"source": item['url'], "title": item['title']}) for
            item in results['results']]
        return {'query': query, 'documents': documents}

    def run(self, input:Dict[str,Any] )-> Dict[str, Any]:
        search_output = self.search(input)
        return self.extract(
            query=search_output["query"],
            docs=search_output["documents"]
        )
