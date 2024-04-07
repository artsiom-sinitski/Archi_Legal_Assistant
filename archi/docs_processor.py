import os
from pprint import pprint

from langchain_openai import (
    ChatOpenAI, OpenAIEmbeddings
)
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, DirectoryLoader
)
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# ============================================================================================
# ============================================================================================

sys_prompt = """
"You are a legal assistant (named Archia) who specializes in the consumer protection laws of the Russian Federation.
Your task is to answer relevant questions or provide comprehensive yet straightforward advice on resolving consumer issues
within the given context. Whenever possible include in your answer the exact laws and their statute numbers as references.
Ensure your explanations can be understood by individuals without the knowledge of the law and legislative terms.
Responses should be delivered in the language of the inquiry.
If the answer is unknown, openly state so, avoiding any guesswork.
Your answers must use these fundamental definitions:
1. Consumer is a citizen (a.k.a. individual, a.k.a. natural person)
2. Consumer is not a legal entity
{context}
Question: {question}
"""

PROMPT = PromptTemplate(template=sys_prompt, input_variables=["context", "question"])

# -------------------------------------------------------------------------------------------

knowledge_db_dir_path = "knowledge_db"
knowledge_docs_dir_path = rf"{os.environ["USERDIR"]}\Documents\archi_knowledge_docs"

# ----------------------------------------------------------
openai_api_key = None
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# ============================================================================================
# ============================================================================================

# print(texts[0])
# print(pages[0])
# print(type(pages))
# print(pages[0].metadata["source"])

try:
    openai_api_key = os.environ["OPENAI_API_KEY"]
except (KeyError, AttributeError) as err:
    print(str(err))


if os.path.isdir(knowledge_db_dir_path):
    vector_db = Chroma(persist_directory=knowledge_db_dir_path, embedding_function=embeddings)
else:
    loader = DirectoryLoader(knowledge_docs_dir_path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "Windows-1251"},
        use_multithreading=True,
        show_progress=True
    )
    # text_splitter = RecursiveCharacterTextSplitter(
    #     separators=[
    #         "\n\n" #, "\n", "\t", " ", ".", ",", "",
    #         # "\u200B",  # Zero-width space
    #         # "\uff0c",  # Full-width comma
    #         # "\u3001",  # Ideographic comma
    #         # "\uff0e",  # Full-width full stop
    #         # "\u3002",  # Ideographic full stop
    #     ],
    #     chunk_size=2000, chunk_overlap=200,
    #     length_function=len, is_separator_regex=False
    # )
    # docs = loader.load()
    # data = text_splitter.split_documents(docs)

    import sys
    if "nltk" not in sys.modules:
        import nltk
        nltk.download('punkt')

    from langchain.text_splitter import NLTKTextSplitter

    text_splitter = NLTKTextSplitter(separator="\n\n", language='russian')
    data = loader.load_and_split(text_splitter)

    print(f"{'*' * 3} Scanned and split the knowledge documents")

    # Embed and store the pages data on disk
    vector_db = Chroma.from_documents(
        documents=data,
        embedding=embeddings,
        persist_directory=knowledge_db_dir_path
    )
    print(f"{'*' * 3} Created knowledge database (db)")
    vector_db.persist()
    print(f"{'*' * 3} Persisted knowledge db to disk")
# if end
print(f"{'*'*3} Retrieved data from the knowledge db")

retriever = vector_db.as_retriever()

llm = ChatOpenAI(
    api_key=openai_api_key,
    temperature=0,
    # model="gpt-4-1106-preview"
    model="gpt-3.5-turbo-16k"
)

# create the chain to answer questions
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)

Q1 = "Может ли юридическое лицо быть признано потребителем для целей закона о защите прав потребителей?"
pprint(qa_chain(Q1))
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

print("\nFinished task!")

# def load_docs(dir_path: str):
#     loader = DirectoryLoader(dir_path)
#     documents = loader.load()
#     return documents

if __name__ == "__main__":
    pass
