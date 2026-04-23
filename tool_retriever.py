from typing import Literal, Optional
from langchain_core.tools import BaseTool,tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional,Callable
from retrievers import PubMedSearch
from concurrent.futures import ThreadPoolExecutor, as_completed
from retrievers import TavilyPipeline


class TavilyParameters(BaseModel):
    query: str = Field(description=("Search query to look up"))
    search_depth: Optional[Literal["basic", "advanced", "fast", "ultra-fast"]] = Field(
        default="basic",
        description="""Controls search thoroughness and result comprehensiveness.

        Use "basic" for simple queries requiring quick, straightforward answers.

        Use "advanced" for complex queries, specialized topics,
        rare information, or when in-depth analysis is needed.

        Use "fast" for optimized low latency with high relevance.

        Use "ultra-fast" when latency is prioritized above all else.
        """,  # noqa: E501
    )
    time_range: Optional[Literal["day", "week", "month", "year"]] = Field(
        default=None,
        description="""Limits results to content published within a specific timeframe.

        ONLY set this when the user explicitly mentions a time period
        (e.g., "latest AI news," "articles from last week").

        For less popular or niche topics, use broader time ranges
        ("month" or "year") to ensure sufficient relevant results.

        Options: "day" (24h), "week" (7d), "month" (30d), "year" (365d).

        Default is None.
        """,  # noqa: E501
    )


class PubmedParameters(BaseModel):
    query: List[str] = Field(description=("Search query to look up. should give maximum of three search queries"))
    max_results: int = 5

def get_tools()->List[BaseTool]:

    @tool(args_schema=TavilyParameters)
    def tavilySearch(query:str, search_depth:Optional[str]="basic", time_range:Optional[str]=None):
        """
        description: A search engine optimized for comprehensive, accurate, and trusted results.
        Useful for when you need to answer questions about current events.
        It not only retrieves URLs and snippets, but offers advanced search depths,
        domain management, time range filters, and image search, this tool delivers
        real-time, accurate, and citation-backed results.
        Input should be a search query.
        """
        argument = {
            "query": query,
            "search_depth": search_depth,
        }
        if time_range is not None:
            argument["time_range"] = time_range
        pipeline = TavilyPipeline()
        results = pipeline.run(argument)
        return [results]

    @tool(args_schema=PubmedParameters)
    def PubmedPMC(query:List[str], max_results:Optional[int]=4):
        """
        A specialized biomedical research search tool designed to retrieve high-quality, peer-reviewed scientific articles from PubMed.
        Useful for answering questions related to life sciences, bioenergy .
        It provides access to abstracts, publication metadata, and full-text links from trusted sources, enabling evidence-based insights.
        Supports advanced querying, filtering by publication date, article type, and relevance to ensure precise and reliable results.
        Input should be a well-formed research query.
        """
        query_list = query
        max_results = max_results
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(PubMedSearch, query=query, max_results=max_results)
                for query in query_list
            ]

            for future in as_completed(futures):
                obj = future.result()
                results.append(obj.articles)

        return results

    return [tavilySearch, PubmedPMC]