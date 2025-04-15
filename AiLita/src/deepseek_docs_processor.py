import os
import sys
from pathlib import Path

from langchain_core.documents import Document

sys.path.append(rf"{Path(__file__).parent}")

# from pprint import pprint
import streamlit as st

import ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

from langchain_chroma import Chroma
from langchain.text_splitter import (
    NLTKTextSplitter #, RecursiveCharacterTextSplitter
)
from langchain_community.document_loaders import (
    TextLoader, DirectoryLoader
)
from utilities import get_project_root
from constants import WIN_ENCODING_RU

# ============================================================================================
# ============================================================================================
try:
    user_dir: str = st.secrets.env_vars.USERDIR
except (KeyError, AttributeError) as err:
    # print(f"{'*' * 5} {str(err)}")
    user_dir = os.environ["USERDIR"]
# ---------------------------------------------------------------------------
knowledge_docs_path: str = rf"{user_dir}\Documents\AiLita_knowledge_docs"
knowledge_db_path: str = f"{get_project_root().parent}/knowledge_db/deepseek"
# ---------------------------------------------------------------------------
try:
    api_key: str = st.secrets.api_credentials.deepseek_api_key
except (KeyError, AttributeError) as err:
    api_key = os.environ["DEEPSEEK_API_KEY"]

# embeddings = OllamaEmbeddings(model="deepseek-r1", base_url="https://api.deepseek.com")
# embedding_func = OllamaEmbeddings(model="deepseek-r1", api_key=api_key)
embedding_func = OpenAIEmbeddings(api_key=api_key, model="deepseek-r1", base_url="https://api.deepseek.com")
# ============================================================================================
# ============================================================================================
collection_name: str = "RF_consumer_protection_law"

if os.path.isdir(knowledge_db_path):
    vector_db = Chroma(collection_name=collection_name,
        persist_directory=knowledge_db_path, embedding_function=embedding_func
    )
else:
    import nltk  # if "nltk" not in sys.modules:

    loader = DirectoryLoader(knowledge_docs_path,
        glob="*.txt", loader_cls=TextLoader,
        loader_kwargs={"encoding": WIN_ENCODING_RU},
        recursive=False, use_multithreading=True, show_progress=True
    )

    # TODO
    # add dir check and download package if it is not found
    # nltk_downloader = nltk.downloader.Downloader
    # nltk_downloader.is_installed('punkt')
    nltk.download('punkt')
    nltk.download('punkt_tab')

    text_splitter = NLTKTextSplitter(separator="\n\n", language="russian")
    chunks: list[Document] = loader.load_and_split(text_splitter)

    print(f"{'*'*3} Scanned and split the knowledge documents {'*'*3}")
    seen_docs = set()
    for source in chunks:
        source_meta = source.metadata['source'].split('\\')[-1]
        if source_meta not in seen_docs:
            seen_docs.add(source_meta)
            print(f"\t - {source_meta}")
    print(f"{'-'*25} Total documents: {len(seen_docs)}", end='\n')

    from concurrent.futures import ThreadPoolExecutor
    from chromadb.config import Settings
    from chromadb import Client

    # Parallelize embedding generation
    def generate_embedding(chunk):
        return embedding_func.embed_query(chunk.page_content)

    # with ThreadPoolExecutor() as executor:
    #     embeddings = list(executor.map(generate_embedding, chunks))

    client = Client(Settings())
    # client.delete_collection(name=collection_name)  # Delete existing collection (if any)
    collection = client.create_collection(name=collection_name)
    # Add documents and embeddings to Chroma
    for idx, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk.page_content],
            metadatas=[{'id': idx}],
            embeddings=[embedding_func.embed_query(chunk.page_content)[idx]],
            ids=[str(idx)]  # Ensure IDs are strings
        )
    # for end
    vector_db = Chroma(collection_name=collection_name, client=client,
        persist_directory=knowledge_db_path, embedding_function=embedding_func
    )
    print(f"{'*' * 3} Created knowledge database (db) {'*'*3}")
# if end
print(f"{'*'*3} Retrieved data from the knowledge db {'*'*3}")


def get_vector_db_retriever():
    return vector_db.as_retriever()
