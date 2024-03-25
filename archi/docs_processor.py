from langchain.document_loaders import DirectoryLoader

dir_path = 'content/data'

def load_docs(dir_path: str):
    loader = DirectoryLoader(dir_path)
    documents = loader.load()
    return documents

