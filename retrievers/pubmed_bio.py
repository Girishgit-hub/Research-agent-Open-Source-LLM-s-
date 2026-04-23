import os
import dotenv
import requests
dotenv.load_dotenv()
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Literal
from langchain_core.documents import Document
import logging
logging.basicConfig(level=logging.INFO)


class PubMedSearch:

    def __init__(self, query: str, query_domains = None,max_results:int = 5):
        self.base_search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.base_fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.query = query # important.....
        self.max_results = max_results
        self.api_key = os.getenv("NCBI_API_KEY")
        self.params = self._populate_params()
        self.articles = self.search_and_retrieve()


    def _populate_params(self):

        params = {}
        params.setdefault("retmode", 'json')
        params.setdefault("sort",'relevance')
        return params

    def search_articles(self):

        search_term = f"{self.query}"

        param = {
            'db' : 'pmc',
            'term' : search_term,
            'api_key' : self.api_key,
            'retmax' : self.max_results,
            **self.params
        }

        try:
            response = requests.get(self.base_search_url, params = param)
            data = response.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            print(f"found {len(id_list)} articles successfully")
            return id_list

        except requests.RequestException as e:
            print("Failed to search articles")
            return None

    def get_full_text(self, article_id:str):

        params = {
            'db' : 'pmc',
            'id' : article_id,
            'api_key' : self.api_key,
            'rettype' : 'full',
            'retmode' : 'xml',
        }

        try:
            response = requests.get(self.base_fetch_url, params = params)

            try:
                tree = ET.fromstring(response.text)

                title = tree.find(".//article-title")
                title_text =  " ".join(title.itertext())  if title is not None else ""

                abstract = tree.find(".//abstract")
                abstract_text = " ".join(abstract.itertext()) if abstract is not None else ""

                body = tree.find(".//body")
                body_text = " ".join(body.itertext()) if body is not None else ""

                full_content = f"Title: {title_text}\n\nAbstract: {abstract_text}\n\nBody: {body_text}"


                url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/"

                return {'url': url, 'raw_content': full_content, 'title': title_text}
            except ET.ParseError as e:
                logging.error(e)
                return None
        except requests.RequestException as e:
            logging.error(e)
            return None

    def search_and_retrieve(self):
        article_ids = self.search_articles()
        if not article_ids:
            return None
        results = []
        for article_id in article_ids:
            article_content = self.get_full_text(article_id)
            if article_content:
                results.append(article_content)
        documents = [Document(page_content=item['raw_content'], metadata={"source": item['url'], "title": item['title']}) for
            item in results]
        return {'query':self.query, 'documents':documents}


