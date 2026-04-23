import requests
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Literal
import logging
from langchain_core.documents import Document
logging.basicConfig(level=logging.INFO)

load_dotenv()


class PubMedCentralSearch:

    def __init__(self, query: str, query_domains = None, max_results:int = 5):
        self.base_search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi" 
        self.base_fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.query = query # important.....
        self.max_results = max_results
        self.api_key = os.getenv("NCBI_API_KEY")
        self.db_type = os.getenv("PUBMED_DB",'pmc')
        self.params = self._populate_params()

    def _populate_params(self):

        params = {}
        params.setdefault("retmode", 'json')
        params.setdefault("sort",'relevance')
        return params

    def search_articles(self):

        if self.db_type == 'pubmed':
            search_term = f"{self.query} AND (ffrft[filter] OR pmc[filter])"
        else:
            search_term = f"{self.query}"

        param = {
            'db' : self.db_type,
            'term' : search_term,
            'api_key' : self.api_key,
            'retmax' : self.max_results,
            **self.params
        }

        try:
            response = requests.get(self.base_search_url, params = param)
            status = response.raise_for_status()
            data = response.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            print(f"found {len(id_list)} articles successfully")
            return id_list

        except requests.RequestException as e:
            print("Failed to search articles")
            return None

    def abstract(self, article_id: str):

        params = {
            'db' : 'pmc' if self.db_type == 'pubmed' else 'pubmed',
            'id' : article_id,
            'api_key' : self.api_key,
            'rettype' : 'abstract',
            'retmode' : 'xml',
        }

        try:
            response = requests.get(self.base_fetch_url, params = params)
            response.raise_for_status()

            try:
                tree = ET.fromstring(response.text)

                title = tree.find(".//article-title")
                title_text = "".join(title.itertext()) if title is not None else ""

                abstract = tree.find(".//abstract")
                abstract_text = " ".join(abstract.itertext()) if abstract is not None else ""

                full_content = f"Title: {title_text}\n\nAbstract: {abstract_text}"

                if self.db_type == 'pmc' or article_id.startswith("PMC"):
                    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/"
                else:
                    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{article_id}/"

                return {
                    'url' : url,
                    'raw_content' : full_content,
                    'title' : title,
                }
            except ET.ParseError as e:
                logging.log(logging.ERROR, e)
                return None
        except requests.RequestException as e:
            return None

    def get_full_text(self, article_id:str):

        params = {
            'db' : 'pmc' if self.db_type == 'pmc' else 'pmc',
            'term' : article_id,
            'api_key' : self.api_key,
            'rettype' : 'full',
            'retmode' : 'xml',
        }

        try:
            response = requests.get(self.base_fetch_url, params = params)
            response.raise_for_status()

            try:
                tree = ET.fromstring(response.text)

                title = tree.find(".//title-text")
                title_text =  " ".join(title.itertext())  if title is not None else ""

                abstract = tree.find(".//abstract")
                abstract_text = " ".join(abstract.itertext()) if abstract is not None else ""

                body = tree.find(".//body")
                body_text = " ".join(body.iteritext()) if body is not None else ""

                full_content = f"Title: {title_text}\n\nAbstract: {abstract_text}\n\nBody: {body_text}"

                if self.db_type == 'pmc' or article_id.startswith("PMC"):
                    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id}/"
                else:
                    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{article_id}/"

                return {
                    'url' : url,
                    'raw_content' : full_content,
                    'title' : title_text,
                }
            except ET.ParseError as e:
                return None
        except requests.RequestException as e:
            return None

    def search_and_retrieve(self, search_type:Literal['abstract','full_text'] = 'abstract'):
        params = {
            'abstract' : self.abstract,
            'full_text' : self.get_full_text
        }
        article_ids = self.search_articles()
        if not article_ids:
            return None
        results = []
        for article_id in article_ids:
            article_content = params.get(search_type)(article_id)
            if article_content:
                results.append(article_content)
            documents = [Document(page_content=item['raw_content'], metadata={"source": item['url'], "title": item['title']}) for
                 item in results]
        return self.query, documents


