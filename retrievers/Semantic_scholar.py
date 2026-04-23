import requests
import logging
from typing import List, Dict
import time

class SemanticScholarSearch:
    """
    Semantic Scholar API Retriever
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    VALID_SORT_CRITERIA = ["relevance", "citationCount", "publicationDate"]

    def __init__(self, query: str, sort: str = "relevance", query_domains=None):
        """
        Initialize the SemanticScholarSearch class with a query and sort criterion.

        :param query: Search query string
        :param sort: Sort criterion ('relevance', 'citationCount', 'publicationDate')
        """
        self.query = query
        assert sort in self.VALID_SORT_CRITERIA, "Invalid sort criterion"
        self.sort = sort.lower()

    def search(self, max_results: int = 20) -> List[Dict[str, str]]:
        """
        Perform the search on Semantic Scholar and return results.

        :param max_results: Maximum number of results to retrieve
        :return: List of dictionaries containing title, href, and body of each paper
        """
        params = {
            "query": self.query,
            "limit": max_results,
            "fields": "title,abstract,url,venue,year,authors,isOpenAccess,openAccessPdf",
            "sort": self.sort,
        }
        while True:
            response = requests.get(self.BASE_URL, params=params)
            if response.status_code == 429:
                logging.log(logging.ERROR, f"Rate limit reached. Retrying...")
                time.sleep(5)
                continue
            break

        results = response.json().get("data", [])
        search_result = []

        for result in results:
            if result.get("isOpenAccess") and result.get("openAccessPdf"):
                search_result.append(
                    {
                        "title": result.get("title", "No Title"),
                        "href": result["openAccessPdf"].get("url", "No URL"),
                        "body": result.get("abstract", "Abstract not available"),
                    }
                )
        logging.log(logging.INFO, f"Found {len(search_result)} papers")
        return search_result