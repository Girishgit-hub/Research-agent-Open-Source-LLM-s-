from Bio import Entrez
import pandas as pd

# Define your email to use with NCBI Entrez
Entrez.email = "place your mail id here"


def search_pubmed(keyword):
    # Adjust the search term to focus on abstracts
    search_term = f"{keyword}[Abstract]"
    handle = Entrez.esearch(db="pubmed", term=search_term, retmax=10)
    record = Entrez.read(handle)
    handle.close()
    # Get the list of Ids returned by the search
    id_list = record["IdList"]
    return id_list


def fetch_details(id_list):
    ids = ','.join(id_list)
    handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
    records = Entrez.read(handle)
    handle.close()

    # Create a list to hold our article details
    articles = []

    for pubmed_article in records['PubmedArticle']:
        article = {}
        article_data = pubmed_article['MedlineCitation']['Article']
        article['Title'] = article_data.get('ArticleTitle')

        # Directly output the abstract
        abstract_text = article_data.get('Abstract', {}).get('AbstractText', [])
        if isinstance(abstract_text, list):
            abstract_text = ' '.join(abstract_text)
        article['Abstract'] = abstract_text

        article['Journal'] = article_data.get('Journal', {}).get('Title')

        articles.append(article)

    return articles


def perform_search_and_fetch(keyword):
    id_list = search_pubmed(keyword)
    return fetch_details(id_list)


# Example usage: Performing two searches
keyword = """ bioenrgy biofuels tredns 2025 sustanblity reseach"""


