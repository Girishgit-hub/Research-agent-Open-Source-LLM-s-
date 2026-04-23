from typing import List, Dict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embeddings_pack.embeddings import BaseEmbeddings
from langchain_community.vectorstores import FAISS
import dotenv
import time
import hashlib
dotenv.load_dotenv()
import os


class RAGPipeline:

    @staticmethod
    def _get_hash(text):
        return hashlib.md5(text.strip().encode()).hexdigest()

    @classmethod
    def store(cls, documents: List[Document]):

        # Step 1: Split
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(documents)

        # Step 2: Embedding object (FIXED)
        _BaseEmbeddings = BaseEmbeddings(embedding_provider="cohere", model = "embed-v4.0")
        embeddings = _BaseEmbeddings.get_embeddings()

        # Step 3: Load existing DB
        if os.path.exists('faiss_index'):
            db = FAISS.load_local(
                "faiss_index",
                embeddings,
                allow_dangerous_deserialization=True
            )
            print("Loaded existing FAISS index")

            existing_hashes = {
                d.metadata.get("hash")
                for d in db.docstore._dict.values()
                if "hash" in d.metadata
            }

        else:
            db = None
            existing_hashes = set()
            print("Creating new FAISS index")

        # Step 4: Deduplicate
        filtered_chunks = []
        for doc in chunks:
            h = cls._get_hash(doc.page_content)
            if h not in existing_hashes:
                doc.metadata["hash"] = h
                filtered_chunks.append(doc)

        if not filtered_chunks:
            print("No new unique documents to add.")
            return db

        # Step 5: Batch insert
        BATCH_SIZE = 50
        DELAY = 9

        for i in range(0, len(filtered_chunks), BATCH_SIZE):
            batch = filtered_chunks[i:i + BATCH_SIZE]

            print(f"Processing batch {i // BATCH_SIZE + 1}")

            if db is None:
                db = FAISS.from_documents(batch, embeddings)
            else:
                db.add_documents(batch)

            time.sleep(DELAY)

        # Step 6: Save DB (CRITICAL)
        if db is not None:
            db.save_local("faiss_index")

        return db