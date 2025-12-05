import os
import json
import io
import chromadb # Required for the HTTP client connection

from fastapi import FastAPI, UploadFile, File, HTTPException, status, Response

from pydantic import BaseModel
from minio import Minio
import redis

# LangChain Imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# --- App Initialization ---
app = FastAPI()

# --- Configuration ---
MINIO_URL = os.getenv("MINIO_URL", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "miniouser")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "miniopassword")
REDIS_URL = os.getenv("REDIS_URL", "redis")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma-db")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")

# --- Global Clients (Initialized at Startup) ---
# These must be defined at the module level so endpoints can access them
minio_client = None
redis_client = None
vectorstore = None
llm = None
embeddings = None

class QueryRequest(BaseModel):
    question: str

@app.on_event("startup")
async def startup_event():
    # Use 'global' to assign to the variables defined above
    global minio_client, redis_client, vectorstore, llm, embeddings

    print("--- API Server Starting Up ---")

    # 1. Initialize MinIO
    try:
        # Use positional argument for endpoint to avoid version issues
        minio_client = Minio(
            MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        if not minio_client.bucket_exists("documents"):
            minio_client.make_bucket("documents")
        print("✅ MinIO Connected")
    except Exception as e:
        print(f"❌ MinIO Connection Failed: {e}")

    # 2. Initialize Redis
    try:
        redis_client = redis.Redis(host=REDIS_URL, port=6379, db=0, decode_responses=True)
        redis_client.ping()
        print("✅ Redis Connected")
    except Exception as e:
        print(f"❌ Redis Connection Failed: {e}")

    # 3. Initialize Embedding Model
    print("⏳ Loading Embedding Model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("✅ Embedding Model Loaded")

    # 4. Initialize ChromaDB Connection
    try:
        print(f"⏳ Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))

        vectorstore = Chroma(
            client=chroma_client,
            collection_name="documents",
            embedding_function=embeddings,
        )
        print("✅ ChromaDB Connected")
    except Exception as e:
        print(f"❌ ChromaDB Connection Failed: {e}")

    # 5. Initialize LLM (Ollama)
    # We point base_url to the host machine so it can access Ollama running outside Docker
    print("⏳ Connecting to Ollama...")
    llm = OllamaLLM(base_url="http://host.docker.internal:11434", model="llama3:8b")
    print("✅ Ollama Configured")


@app.get("/")
def read_root():
    return {"message": "QueryBot API is running properly."}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Stateless Upload: Saves file to MinIO and pushes a job to Redis.
    """
    if minio_client is None or redis_client is None:
        raise HTTPException(status_code=503, detail="Services not initialized")

    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)

        # Upload to MinIO
        minio_client.put_object(
            "documents",
            file.filename,
            io.BytesIO(contents),
            file_size,
            content_type=file.content_type
        )

        # Push job to Redis
        job = {"bucket": "documents", "file_name": file.filename}
        redis_client.lpush("pdf_job_queue", json.dumps(job))

        return Response(
            status_code=status.HTTP_202_ACCEPTED,
            content=f"File {file.filename} uploaded and queued."
        )

    except Exception as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """
    Stateless Query: Fetches context from ChromaDB and answers using Ollama.
    """
    # We check if the global variables are set (meaning startup succeeded)
    if vectorstore is None or llm is None:
        raise HTTPException(status_code=503, detail="AI Services not initialized")

    question = request.question
    print(f"Received Query: {question}")

    try:
        # 1. Search ChromaDB for relevant chunks
        # We retrieve the top 3 most similar chunks
        docs = vectorstore.similarity_search(question, k=3)

        context_text = "\n\n".join([d.page_content for d in docs])

        # 2. Define the RAG Prompt
        template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
        prompt = PromptTemplate.from_template(template)

        # 3. Build the Chain (LangChain Expression Language)
        # Retrieval -> Prompt -> LLM -> Output Parser
        chain = prompt| llm | StrOutputParser()

        # 4. Execute the Chain
        answer = chain.invoke({"context":context_text, "question":question})

        print("Answer generated successfully.")
        
        return {"answer": answer,
                "context": [d.page_content for d in docs]}

    except Exception as e:
        print(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
