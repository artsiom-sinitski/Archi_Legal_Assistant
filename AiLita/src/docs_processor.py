import os
import sys
from pathlib import Path

from google.auth.exceptions import InvalidValue

sys.path.append(rf"{Path(__file__).parent}")

# from pprint import pprint
import streamlit as st

# from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

# Workaround for DeepSeek embeddings
import ollama
from langchain_community.embeddings import OllamaEmbeddings

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

try:
    user_dir: str = st.secrets.env_vars.USERDIR
except (KeyError, AttributeError) as err:
    # print(f"{'*' * 5} {str(err)}")
    user_dir = os.environ["USERDIR"]

knowledge_docs_path: str = rf"{user_dir}\Documents\AiLita_knowledge_docs"
knowledge_db_path: str = f"{get_project_root().parent}/knowledge_db"
# -----------------------------------------------------------------------

def setup_knowledge_db(provider: str="openai",
                       db_path: str=knowledge_db_path) -> (str, any, str):
    api_key: str = str()
    embeddings = None
    match provider.lower():
        case "deepseek-reasoner":
            try:
                api_key = st.secrets.api_credentials.deepseek_api_key
            except (KeyError, AttributeError) as err:
                api_key = os.environ["DEEPSEEK_API_KEY"]
            embeddings = OllamaEmbeddings(model="deepseek-r1")
            db_path = f"{db_path}/deepseek"
        case "openai" | "o1" | "o3-mini'":
            try:
                api_key = st.secrets.api_credentials.openai_api_key
            except (KeyError, AttributeError) as err:
                api_key = os.environ["OPENAI_API_KEY"]
            embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            db_path = f"{db_path}/openai"
        case _:
            raise InvalidValue("Unknown LLM provider!")

    return api_key, embeddings, db_path

# ============================================================================================
# ============================================================================================
# try:
#     openai_api_key = st.secrets.api_credentials.api_key
# except (KeyError, AttributeError) as err:
#     # print(f"{'*'*5} {str(err)}")
#     openai_api_key = os.environ["OPENAI_API_KEY"]


provider: str = sys.argv[1]

print(f"docs_processor :: {provider = }")
print({f"docs_processor :: {db_path = }"})

api_key, embeddings, knowledge_db_path = setup_knowledge_db(provider, knowledge_db_path)

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
