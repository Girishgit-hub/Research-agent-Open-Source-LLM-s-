from Bio import Entrez
import pandas as pd

# Define your email to use with NCBI Entrez
Entrez.email = "gk3719695@gmai.com"


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
keyword1 = """ bioenrgy biofuels tredns 2025 sustanblity reseach"""

# Fetch articles for both keywords
articles1 = perform_search_and_fetch(keyword1)

print(articles1)
# Convert both lists of articles to DataFrames
#df1 = pd.DataFrame(articles1)


# Add a column to differentiate the search terms in the final DataFrame
#df1['SearchTerm'] = keyword1


# Concatenate the DataFrames

# Save the combined DataFrame to an Excel file
#excel_filename = keyword1 + "_pubmed_search_results.xlsx"
#df1.to_excel(excel_filename, index=False)

#print(f"Saved combined search results to {excel_filename}")
