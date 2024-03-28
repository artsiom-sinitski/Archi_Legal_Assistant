# import openai
from langchain_community.vectorstores import Chroma

# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import (
    OpenAI, OpenAIEmbeddings
)

# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, DirectoryLoader
)
import streamlit as st
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA


openai_api_key = st.secrets.api_credentials.api_key

dir_path = 'content/docs'
file_name = "RussianConsumerLaws.pdf"

# print(f"{dir_path}/{file_name}")

# load and process pdf files
# loader = PyPDFLoader(f"{dir_path}/{file_name}")
loader = DirectoryLoader('./content/docs', glob="./*.pdf", loader_cls=PyPDFLoader)
pages = loader.load_and_split()
print(f"{'*'*3} Loaded and split the documents")

# split the text into chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# texts = text_splitter.split_documents(pages)

# print(texts[0])
# print(pages[0])
# print(type(pages))
# print(pages[0].metadata["source"])

# Embed and store the pages
# Supplying a persist_directory will store the embeddings on disk
persist_directory = 'db'

# here we are using OpenAI embeddings but in future we will swap out to local embeddings
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

vector_db = Chroma.from_documents(
    documents=pages,
    embedding=embedding,
    persist_directory=persist_directory
)

vector_db.persist()
vector_db = None

# load the persisted database from disk, and use it as normal.
vector_db = Chroma(persist_directory=persist_directory,
                   embedding_function=embedding)
print(f"{'*'*3} Loaded data into vector db")

retriever = vector_db.as_retriever()
question = "Может ли юридическое лицо быть признано потребителем для целей закона о защите прав потребителей?"
relevant_docs = retriever.get_relevant_documents(question)

print(relevant_docs)
# print(len(relevant_docs))
# print(retriever.search_type)

# create the chain to answer questions
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(api_key=openai_api_key),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)


def process_llm_response(llm_response):
    print(llm_response['result'])
    print('\n\nSources:')
    for source in llm_response["source_documents"]:
        print(source.metadata['source'])


# query = "How much money did Pando raise?"
llm_response = qa_chain(question)
process_llm_response(llm_response)

print("\nEnd Of File!")

# def load_docs(dir_path: str):
#     loader = DirectoryLoader(dir_path)
#     documents = loader.load()
#     return documents

if __name__ == "__main__":
    pass
