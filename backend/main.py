import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from pydantic import BaseModel

# Langchain processing
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# LangChain for RAG
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# --- App Initialization & Global Variables ---
app = FastAPI()

# Global variables to hold the models and the RAG chain
# These are initialized at startup and populated by the /upload endpoint
embeddings = None
chain = None

# --- Pydantic model for the query request ---
class QueryRequest(BaseModel):
    """Defines the expected JSON structure for a query request."""
    question: str

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    Loads only the embedding model at startup.
    The full RAG chain is built by the /upload endpoint.
    """
    global embeddings
    print("--- Loading embedding model at startup ---")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("--- Embedding model loaded ---")


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to QueryBot! Upload a PDF to /upload to begin."}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global chain
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = Path(temp_dir) / file.filename

        with open(temp_file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        # 1. Load, split, and create the vector store
        print(f"Processing {temp_file_path}...")
        loader = PyPDFLoader(str(temp_file_path))
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(texts, embeddings)
        vectorstore.save_local("faiss_index")
        print("Vector store saved to 'faiss_index' folder.")

    # 2. Build the RAG chain now that the index exists
    print("Building RAG chain...")
    llm = OllamaLLM(base_url="http://host.docker.internal:11434", model="llama3:8b")
    retriever = vectorstore.as_retriever()

    template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

Context: {context}
Question: {input}
Answer:
"""
    prompt = PromptTemplate.from_template(template)
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # 3. Store the chain in the global variable
    chain = retrieval_chain
    print("--- RAG chain is now ready ---")

    return {"status": "success", "filename": file.filename}


@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Accepts a question, invokes the RAG chain, and returns the answer.
    """
    # 1. Check if the chain has been created
    if chain is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No document has been uploaded yet. Please upload a file to /upload first."
        )

    # 2. If the chain exists, proceed with the query
    try:
        response = chain.invoke({"input": request.question})
        return {"answer": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
