from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

print("--- Loading PDF ---")

loader = PyPDFLoader("attention.pdf")
documents = loader.load()

print(f"Loaded {len(documents)} pages.")

print("\n--- Splitting document into chunks ---")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                chunk_overlap = 200)
texts = text_splitter.split_documents(documents)
print(f"Split into {len(texts)} chunks.")

print("\n--- Loading embedding model ---")
model_name = "all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)
print("Embedding model loaded.")

print("\n--- Creating FAISS vectore store ---")
vectorstore = FAISS.from_documents(texts, embeddings)
print("Vector stores created.")

print("\n--- Saving vector store locally ---")
vectorstore.save_local("faiss_index")
print("Vector store saved to 'faiss_index' folder.")
