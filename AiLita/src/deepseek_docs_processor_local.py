import os
import sys
from pathlib import Path

sys.path.append(rf"{Path(__file__).parent}")

import streamlit as st

from chromadb import PersistentClient
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import NLTKTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader, TextLoader, UnstructuredWordDocumentLoader
)
from utilities import get_project_root
# from constants import WIN_ENCODING_RU

# ============================================================================================
# ============================================================================================
try:
    user_dir: str = st.secrets.env_vars.USERDIR
except (KeyError, AttributeError) as err:
    user_dir = os.environ["USERDIR"]
try:
    api_key: str = st.secrets.api_credentials.deepseek_api_key
except (KeyError, AttributeError) as err:
    api_key = os.environ["DEEPSEEK_API_KEY"]

# ============================================================================================
knowledge_docs_path: str = rf"{user_dir}\Documents\AiLita_knowledge_docs"
knowledge_db_path: str = f"{get_project_root().parent}/knowledge_db/deepseek"
collection_name: str = "RF_Consumer_Protection_Law"

embedding_func: OllamaEmbeddingFunction = OllamaEmbeddingFunction(
    url="http://localhost:11434",   # Default Ollama server address
    model_name=sys.argv[1],     # DeepSeek model with 32B params - "deepseek-r1:32b"
)
# ============================================================================================

if not os.path.isdir(knowledge_db_path):
    import nltk
    nltk.download('punkt')
    nltk.download('punkt_tab')

    loader = DirectoryLoader(knowledge_docs_path,
        glob="*.docx", loader_cls=UnstructuredWordDocumentLoader,
        loader_kwargs={"autodetect_encoding": True},
        recursive=False, use_multithreading=True, show_progress=True
    )
    text_splitter = NLTKTextSplitter(separator="\n\n", language="russian")
    # chunks format --> Document(metadata={source: '...'}, page_content='...')
    chunks: list[Document] = loader.load_and_split(text_splitter)
    print(f"{'*'*3} Loaded the knowledge documents {'*'*3}")

    seen_docs = set()
    for source in chunks:
        source_meta = source.metadata['source'].split('\\')[-1]
        if source_meta not in seen_docs:
            seen_docs.add(source_meta)
            print(f"\t - {source_meta}")
    print(f"\t{'-'*30} Total documents: {len(seen_docs)}", end='\n')

    client = PersistentClient(path=knowledge_db_path)
    collection = client.create_collection(name=collection_name, embedding_function=embedding_func)

    # Add documents and embeddings to Chroma
    for idx, chunk in enumerate(chunks):
        collection.add(documents=[chunk.page_content],
            metadatas=[{'id': idx}], ids=[str(idx)],  # Ensure IDs are strings
            embeddings=embedding_func([chunk.page_content])
        )
    print(f"{'*' * 3} Created knowledge database (db) {'*'*3}")
# if end

vector_db: Chroma = Chroma(collection_name=collection_name, persist_directory=knowledge_db_path)
print(f"{'*'*3} Retrieved data from the knowledge db {'*'*3}")


def get_vector_db_retriever():
    return vector_db.as_retriever()
