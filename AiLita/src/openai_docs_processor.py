import os
import sys
from pathlib import Path

sys.path.append(rf"{Path(__file__).parent}")

# from pprint import pprint
import streamlit as st

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import NLTKTextSplitter
from langchain_core.documents import Document
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
    user_dir = os.environ["USERDIR"]
try:
    api_key = st.secrets.api_credentials.openai_api_key
except (KeyError, AttributeError) as err:
    api_key = os.environ["OPENAI_API_KEY"]
# -------------------------------------------------------------------------
knowledge_docs_path: str = rf"{user_dir}\Documents\AiLita_knowledge_docs"
knowledge_db_path: str = f"{get_project_root().parent}/knowledge_db/openai"

embedding_func = OpenAIEmbeddings(api_key=api_key)
# ============================================================================================
# ============================================================================================

if os.path.isdir(knowledge_db_path):
    vector_db = Chroma(persist_directory=knowledge_db_path, embedding_function=embedding_func)
else:
    import nltk
    nltk.download('punkt')
    nltk.download('punkt_tab')

    loader = DirectoryLoader(knowledge_docs_path,
        glob="*.txt", loader_cls=TextLoader,
        loader_kwargs={"encoding": WIN_ENCODING_RU},
        recursive=False, use_multithreading=True, show_progress=True
    )
    text_splitter = NLTKTextSplitter(separator="\n\n", language="russian")
    chunks: list[Document] = loader.load_and_split(text_splitter)

    print(f"{'*'*3} Loaded knowledge documents {'*'*3}")
    seen_docs = set()
    for source in chunks:
        source_meta = source.metadata['source'].split('\\')[-1]
        if source_meta not in seen_docs:
            seen_docs.add(source_meta)
            print(f"\t - {source_meta}")
    print(f"\t{'-'*30} Total documents: {len(seen_docs)}", end='\n')

    # Embed and store the pages data on disk
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_func,
        persist_directory=knowledge_db_path
    )
    print(f"{'*' * 3} Created knowledge database (db) {'*'*3}")
# if end
print(f"{'*'*3} Retrieved data from the knowledge db {'*'*3}")


def get_vector_db_retriever():
    return vector_db.as_retriever()
