import streamlit as st

from langchain_openai import (
    OpenAI, OpenAIEmbeddings
)
from langchain_community.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, DirectoryLoader
)
from langchain.chains import RetrievalQA


openai_api_key = st.secrets.api_credentials.api_key

dir_path = 'content/docs'
file_name = "RussianConsumerLaws.pdf"

# print(f"{dir_path}/{file_name}")

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

persist_directory = 'db'
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

if not (vector_db := Chroma(persist_directory=persist_directory, embedding_function=embeddings)):
    # Embed and store the pages on disk
    # using OpenAI embeddings for now but in future we will use local embeddings
    vector_db = Chroma.from_documents(
        documents=pages,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vector_db.persist()
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


llm_response = qa_chain(question)
process_llm_response(llm_response)

print("\nEnd Of File!")

# def load_docs(dir_path: str):
#     loader = DirectoryLoader(dir_path)
#     documents = loader.load()
#     return documents

if __name__ == "__main__":
    pass
