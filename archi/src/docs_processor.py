import os
import sys
from pprint import pprint

from archi.src.utilities import get_project_root
from archi.src.constants import WIN_ENCODING_RU
from archi.src.prompts import sys_prompt_ru_1

if "nltk" not in sys.modules:
    import nltk

from langchain_openai import (
    ChatOpenAI, OpenAIEmbeddings
)
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import (
    NLTKTextSplitter #, RecursiveCharacterTextSplitter
)
from langchain_community.document_loaders import (
    TextLoader, DirectoryLoader
)
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# ============================================================================================
# ============================================================================================

PROMPT = PromptTemplate(template=sys_prompt_ru_1, input_variables=["context", "question"])

# -------------------------------------------------------------------------------------------

knowledge_db_dir_path = f"{get_project_root()}/knowledge_db"
knowledge_docs_dir_path = rf"{os.environ["USERDIR"]}\Documents\archi_knowledge_docs"

# ----------------------------------------------------------
openai_api_key = None

# ============================================================================================
# ============================================================================================

try:
    openai_api_key = os.environ["OPENAI_API_KEY"]
except (KeyError, AttributeError) as err:
    print(str(err))

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

if os.path.isdir(knowledge_db_dir_path):
    vector_db = Chroma(persist_directory=knowledge_db_dir_path, embedding_function=embeddings)
else:
    loader = DirectoryLoader(knowledge_docs_dir_path,
        glob="*.txt", loader_cls=TextLoader,
        loader_kwargs={"encoding": WIN_ENCODING_RU},
        recursive=False, use_multithreading=True, show_progress=True
    )

    # TODO
    # add dir check and download package if it is not found
    # nltk_downloader = nltk.downloader.Downloader
    # nltk_downloader.is_installed('punkt')
    nltk.download('punkt')

    text_splitter = NLTKTextSplitter(separator="\n\n", language="russian")
    data = loader.load_and_split(text_splitter)

    print(f"{'*' * 3} Scanned and split the knowledge documents {'*'*3}")
    seen_docs = set()
    for source in data:
        source_meta = source.metadata['source'].split('\\')[-1]
        if source_meta not in seen_docs:
            seen_docs.add(source_meta)
            print(f"\t - {source_meta}")

    # Embed and store the pages data on disk
    vector_db = Chroma.from_documents(
        documents=data,
        embedding=embeddings,
        persist_directory=knowledge_db_dir_path
    )
    print(f"{'*' * 3} Created knowledge database (db) {'*'*3}")
    vector_db.persist()
    print(f"{'*' * 3} Persisted knowledge db to disk {'*'*3}")
# if end
print(f"{'*'*3} Retrieved data from the knowledge db {'*'*3}")

retriever = vector_db.as_retriever()

llm = ChatOpenAI(
    api_key=openai_api_key,
    temperature=0,
    model="gpt-4o-mini-2024-07-18"
    # model="gpt-4-1106-preview"
    # model="gpt-3.5-turbo-16k"
)

# create the chain to answer questions
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)


# ===============================================================
# ===============================================================

# Q1 = "Может ли юридическое лицо быть признано потребителем для целей закона о защите прав потребителей?"
# Q1 = "С какого возраста допускается заключение договора розничной купли-продажи?"
# answer = qa_chain(Q1)
# pprint(answer)
#
# print(type(answer))
# print(f"{answer.get("result")}")


# relevant_docs = retriever.get_relevant_documents(question)
# print(relevant_docs)
# print(len(relevant_docs))
# print(retriever.search_type)

# Q2 = "Как тебя зовут и кто ты?"
# pprint(qa_chain(Q2))


# def process_llm_response(llm_response):
#     print(llm_response['result'])
#     print('\n\nSources:')
#     for source in llm_response["source_documents"]:
#         print(source.metadata['source'])
#
#
# llm_response = qa_chain(question)
# process_llm_response(llm_response)

# def load_docs(dir_path: str):
#     loader = DirectoryLoader(dir_path)
#     documents = loader.load()
#     return documents

# if __name__ == "__main__":
#     pass
