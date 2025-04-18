import os
import sys
from pathlib import Path

sys.path.append(rf"{Path(__file__).parent}")

import streamlit as st

from chromadb import PersistentClient
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain.text_splitter import (
    NLTKTextSplitter #, RecursiveCharacterTextSplitter
)
from langchain_community.document_loaders import (
    TextLoader, DirectoryLoader, UnstructuredWordDocumentLoader
)
from utilities import get_project_root
from constants import WIN_ENCODING_RU

# ============================================================================================

def load_and_split_docx_files(dir_path: str, splitter) -> list[Document]:
    from langchain_community.document_loaders import Docx2txtLoader

    chunks: list[Document] = []
    docx_files: list[str] = [file for file in os.listdir(dir_path) if file.endswith(".docx")]
    print(docx_files)

    for file in docx_files:
        loader = Docx2txtLoader(rf"{dir_path}\{file}")
        chunk = loader.load_and_split(splitter)
        print(chunk)
        chunks += chunk if chunks else chunk
    return chunks

# ============================================================================================
try:
    user_dir: str = st.secrets.env_vars.USERDIR
except (KeyError, AttributeError) as err:
    user_dir = os.environ["USERDIR"]
# ---------------------------------------------------------------------------
knowledge_docs_path: str = rf"{user_dir}\Documents\AiLita_knowledge_docs"
knowledge_db_path: str = f"{get_project_root().parent}/knowledge_db/deepseek"
# ---------------------------------------------------------------------------
try:
    api_key: str = st.secrets.api_credentials.deepseek_api_key
except (KeyError, AttributeError) as err:
    api_key = os.environ["DEEPSEEK_API_KEY"]

# ============================================================================================
collection_name: str = "RF_Consumer_Protection_Law"

embedding_func: OllamaEmbeddingFunction = OllamaEmbeddingFunction(
    url="http://localhost:11434",   # Default Ollama server address
    model_name="deepseek-r1:8b",    # DeepSeek model with 8B params in Ollama
)
# ============================================================================================

if not os.path.isdir(knowledge_db_path):
    import nltk
    # TODO: add dir check and download package if it is not found
    # nltk_downloader = nltk.downloader.Downloader
    # nltk_downloader.is_installed('punkt')
    nltk.download('punkt')
    nltk.download('punkt_tab')

    # loader = DirectoryLoader(knowledge_docs_path,
    #     glob="*.txt", loader_cls=TextLoader,
    #     loader_kwargs={"encoding": WIN_ENCODING_RU}, #{"autodetect_encoding": True}
    #     recursive=False, use_multithreading=True, show_progress=True
    # )
    # try:
    #     import exceptions
    # except ImportError:
    # import builtins as exceptions
    # import docx
    # loader = DirectoryLoader(knowledge_docs_path,
    #     glob="*.docx", loader_cls=UnstructuredWordDocumentLoader,
    #     loader_kwargs={"autodetect_encoding": True},
    #     recursive=False, use_multithreading=True, show_progress=True
    # )
    text_splitter = NLTKTextSplitter(separator="\n\n", language="russian")
    # chunks format --> Document(metadata={source: '...'}, page_content='...')
    # chunks: list[Document] = loader.load_and_split(text_splitter)
    chunks: list[Document] = load_and_split_docx_files(knowledge_docs_path, text_splitter)

    print(f"{'*'*3} Scanned and split the knowledge documents {'*'*3}")
    seen_docs = set()
    for source in chunks:
        source_meta = source.metadata['source'].split('\\')[-1]
        if source_meta not in seen_docs:
            seen_docs.add(source_meta)
            print(f"\t - {source_meta}")
    print(f"{'-'*25} Total documents: {len(seen_docs)}", end='\n')

    client = PersistentClient(path=knowledge_db_path)
    collection = client.create_collection(name=collection_name, embedding_function=embedding_func)

    # Add documents and embeddings to Chroma
    for idx, chunk in enumerate(chunks):
        collection.add(documents=[chunk.page_content],
            metadatas=[{'id': idx}], ids=[str(idx)],  # Ensure IDs are strings
            # embeddings=[embedding_func.embed_query(chunk.page_content)[idx]]
            embeddings=embedding_func([chunk.page_content])
        )
    print(f"{'*' * 3} Created knowledge database (db) {'*'*3}")
# if end

vector_db: Chroma = Chroma(
    collection_name=collection_name, #client=client,
    persist_directory=knowledge_db_path #, embedding_function=embedding_func
)
print(f"{'*'*3} Retrieved data from the knowledge db {'*'*3}")


def get_vector_db_retriever():
    return vector_db.as_retriever()


exit(0)