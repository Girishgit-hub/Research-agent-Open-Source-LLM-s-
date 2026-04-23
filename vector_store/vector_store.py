"wrapper for langchain_vectorstore"

from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Vectorstorewrapper:
    def __init__(self, vector_store: VectorStore) :
        self.vector_store = vector_store

    def load(self, documents):
        langchain_documents = self._create_langchain_documents(documents)
        splitted_documents = self._split_documents(langchain_documents)
        self.vector_store.add_documents(splitted_documents)


    def _create_langchain_documents(self, docs: List[Dict[str, str]]) -> List[Document]:
        document = [Document(page_content = item.get('raw_content',''), metadata = {'source': item.get('url','') , 'title': item.get('title','')}) for item in docs]
        return document

    def _split_documents(self, docs: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:

        text_splitter  =  RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap
        )
        return text_splitter.split_documents(docs)

    def _similarity_search(self, query:str, k:int, filter):
        results = self.vector_store.asimilarity_search(query, k=k, filter=filter)
        return results






