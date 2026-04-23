from typing import Any
from typing_extensions import Literal
import os


class BaseEmbeddings:
    def __init__(self, embedding_provider:Literal['cohere','gemini'] = 'gemini', model:str = "gemini-embedding-001", **embedding_params:Any):

        match embedding_provider:
            case "cohere":
                from langchain_cohere import CohereEmbeddings
                _embeddings = CohereEmbeddings(model = model, **embedding_params)
            case "gemini":
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                _embeddings = GoogleGenerativeAIEmbeddings(model = model, **embedding_params)
            case _:
                raise Exception(f"Unknown embedding_provider {embedding_provider}")

        self._embeddings = _embeddings

    def get_embeddings(self):
        return self._embeddings