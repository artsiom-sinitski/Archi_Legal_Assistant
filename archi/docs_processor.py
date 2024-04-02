import os
from pprint import pprint

from langchain_openai import (
    ChatOpenAI, OpenAIEmbeddings
)
from langchain_community.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, DirectoryLoader
)
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


openai_api_key = None
try:
    openai_api_key = os.environ["OPENAI_API_KEY"]
except (KeyError, AttributeError) as err:
    print(str(err))

# -----------------------------------------
knowledge_db_dir_path = 'knowledge_db'
knowledge_docs_dir_path = 'content/knowledge_docs'

# file_name = "RussianConsumerLaws.pdf"
# print(f"{dir_path}/{file_name}")
# -----------------------------------------

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# split the text into chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# texts = text_splitter.split_documents(pages)

# print(texts[0])
# print(pages[0])
# print(type(pages))
# print(pages[0].metadata["source"])

if os.path.isdir(knowledge_db_dir_path):
    vector_db = Chroma(persist_directory=knowledge_db_dir_path, embedding_function=embeddings)
else:
    # loader = PyPDFLoader(f"{dir_path}/{file_name}")
    loader = DirectoryLoader(knowledge_docs_dir_path, glob="./*.pdf", loader_cls=PyPDFLoader)
    pages = loader.load_and_split()
    print(f"{'*' * 3} Scanned and split the knowledge documents")

    # Embed and store the pages data on disk
    vector_db = Chroma.from_documents(
        documents=pages,
        embedding=embeddings,
        persist_directory=knowledge_db_dir_path
    )
    print(f"{'*' * 3} Created knowledge vector DB")
    vector_db.persist()
    print(f"{'*' * 3} Persisted vector DB to disk")
# if end
print(f"{'*'*3} Retrieved data from knowledge vector DB")

retriever = vector_db.as_retriever()

template_ru = """
Тебя зовут Арчиа, ты - старший юрист, который, отвечает на вопросы о правах потребителя, а также
помогает разобраться в конкретных ситуациях согласно законодательству о правах потребителей, в данном контексте.
В ответе обязательно указывай полное название релевантных статей закона о защите прав потребителей.
Отвечай на вопросы по возможности подробно, но понятно.
Если ты не знаешь ответ на вопрос, то так и говори, не фантазируй.
{context}
Вопрос: {question}
"""

template_en = """
"Assuming the role of a legal assistant specializing in consumer rights, named Archia, provide comprehensive yet
straightforward advice on resolving issues based on the Russian consumer protection laws relevant to the provided context.
Whenever possible, include the specific statutes or sections of the Russian consumer protection legislation that 
support your guidance. 
Ensure your explanations are accessible to individuals without a background in law.
Responses should be delivered in the language of the inquiry.
If the answer is unknown, openly state so, avoiding any guesswork.
{context}
Question: {question}
"""


PROMPT = PromptTemplate(template=template_en, input_variables=["context", "question"])

llm = ChatOpenAI(
    api_key=openai_api_key,
    temperature=0,
    # model="gpt-4-1106-preview"
    model="gpt-3.5-turbo-16k"
)
#"gpt-3.5-turbo-16k", "gpt-3.5-turbo-0125"

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
