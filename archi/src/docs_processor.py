import os
import sys
from pathlib import Path
sys.path.append(rf"{Path(__file__).parent}")

__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# from pprint import pprint
import streamlit as st

# from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

# from langchain_community.vectorstores import Chroma

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
user_dir: str = ''
openai_api_key: str = ''
knowledge_db_path: str = f"{get_project_root().parent}/knowledge_db"

try:
    user_dir = st.secrets.env_vars.USERDIR
except (KeyError, AttributeError) as err:
    # print(f"{'*' * 5} {str(err)}")
    user_dir = os.environ["USERDIR"]

knowledge_docs_path: str = rf"{user_dir}\Documents\archi_knowledge_docs"
# ----------------------------------------------------------

# ============================================================================================
# ============================================================================================
try:
    openai_api_key = st.secrets.api_credentials.api_key
except (KeyError, AttributeError) as err:
    # print(f"{'*'*5} {str(err)}")
    openai_api_key = os.environ["OPENAI_API_KEY"]

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

if os.path.isdir(knowledge_db_path):
    vector_db = Chroma(persist_directory=knowledge_db_path, embedding_function=embeddings)
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
    data = loader.load_and_split(text_splitter)

    print(f"{'*'*3} Scanned and split the knowledge documents {'*'*3}")
    seen_docs = set()
    for source in data:
        source_meta = source.metadata['source'].split('\\')[-1]
        if source_meta not in seen_docs:
            seen_docs.add(source_meta)
            print(f"\t - {source_meta}")
    print(f"{'-'*25} Total documents: {len(seen_docs)}", end='\n')

    # Embed and store the pages data on disk
    vector_db = Chroma.from_documents(
        documents=data,
        embedding=embeddings,
        persist_directory=knowledge_db_path
    )
    print(f"{'*' * 3} Created knowledge database (db) {'*'*3}")
# if end
print(f"{'*'*3} Retrieved data from the knowledge db {'*'*3}")


def get_vector_db_retriever():
    return vector_db.as_retriever()
