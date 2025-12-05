# 📄 QueryBot: Distributed AI Data Platform

QueryBot is a production-ready, distributed Retrieval-Augmented Generation (RAG) platform. Unlike simple scripts or prototypes, QueryBot implements an asynchronous, event-driven architecture that decouples data ingestion from user querying, ensuring high availability and scalability.

It features a full ingestion pipeline, a persistent vector database, and an automated quality evaluation harness using "LLM-as-a-Judge."

## ✨ Key Features

* **🚀 Asynchronous Ingestion Pipeline**: Uploads are handled instantly via a Redis job queue. Heavy processing (chunking, embedding) happens in a background worker without blocking the API.
* **🗄️ Persistent Data Layer**:
  * **MinIO**: S3-compatible object storage for raw PDF files.
  * **ChromaDB**: Persistent, Dockerized vector database for embedding storage.
* **⚡ Stateless API**: The FastAPI backend is completely stateless, allowing for horizontal scaling.
* **🧠 Automated Evaluation**: Includes a built-in harness using **Ragas** to quantitatively score the pipeline on *Faithfulness* and *Answer Relevancy*.
* **🐳 Fully Containerized**: The entire stack (API, Worker, Frontend, Redis, MinIO, ChromaDB) is orchestrated via Docker Compose.

## 🛠️ Tech Stack

**Core Infrastructure:**
* **Orchestration**: Docker Compose
* **Queue**: Redis
* **Object Storage**: MinIO
* **Vector Database**: ChromaDB

**Application Layer:**
* **Backend API**: FastAPI
* **Background Worker**: Python (custom script)
* **Frontend**: Streamlit
* **LLM Integration**: LangChain
* **Local LLM**: Ollama (Llama 3)
* **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)

**Quality Assurance:**
* **Evaluation Framework**: Ragas (Retrieval Augmented Generation Assessment)
* **Synthetic Data**: LangChain + Ollama

## 📂 Project Structure

```text
querybot/
├── backend/
│   ├── main.py               # Stateless FastAPI server (Query Engine)
│   ├── worker.py             # Background Worker (Ingestion Engine)
│   ├── preload.py            # Model pre-loader for Docker build
│   ├── Dockerfile            # Shared Docker image for API and Worker
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── app.py                # Streamlit Dashboard
│   ├── Dockerfile            # Frontend Docker image
│   └── requirements.txt      # Frontend dependencies
├── evaluation/               # QA & Testing Harness
│   ├── gen_testset.py        # Generates synthetic test questions from PDFs
│   ├── evaluate.py           # Runs Ragas metrics using "LLM-as-a-Judge"
│   └── transformer.pdf       # Document for testing
├── docker-compose.yml        # Defines the 6-container cluster
├── .gitignore
└── README.md
````

## 🚀 Getting Started

### Prerequisites

1.  **Docker Desktop**: Installed and running.
2.  **Ollama**: Installed on your host machine with the Llama 3 model pulled.
    ```bash
    ollama run llama3:8b
    ```
3.  **Python 3.10+**: (Optional) Required only if you want to run the local evaluation scripts.

### Running the Platform

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd querybot
    ```

2.  **Launch the Cluster:**
    This command builds the images and starts all services (API, Worker, Frontend, Database, Queue, Storage).

    ```bash
    docker-compose up --build
    ```

3.  **Access the Services:**

      * **User Interface**: http://localhost:8501
      * **MinIO Console**: http://localhost:9001 (User: `miniouser`, Pass: `miniopassword`)
      * **API Docs**: http://localhost:8001/docs

## 📝 Usage

### 1\. Ingestion (Upload)

  * Go to the Streamlit UI.
  * Upload a PDF document.
  * **What happens:** The API uploads the file to MinIO and pushes a job to Redis. The UI returns "Accepted" immediately.
  * **Background:** The Worker wakes up, processes the PDF, and saves vectors to ChromaDB. Watch the Docker logs to see this happen in real-time\!

### 2\. Querying

  * Type a question in the UI.
  * **What happens:** The API searches ChromaDB for relevant context and sends it to Ollama to generate an answer.

### 3\. Quality Evaluation (Local)

To rigorously test the bot's accuracy, you can run the evaluation suite locally.

1.  **Install Dev Dependencies:**

    ```bash
    pip install langchain langchain-community langchain-ollama pypdf ragas pandas
    ```

2.  **Generate Test Data:**
    Place your PDF (e.g., `transformer.pdf`) inside the `evaluation/` folder and run:

    ```bash
    cd evaluation
    python gen_testset.py
    ```

    This creates `testset.json` with synthetic questions.

3.  **Run the Grader:**

    ```bash
    python evaluate.py
    ```

    This runs your test set against the running API and uses a local LLM judge to score Faithfulness and Relevancy.

## ⚙️ API Endpoints

  * **POST `/upload`**: Asynchronous endpoint. Uploads file to storage and queues processing job. Returns `202 Accepted`.
  * **POST `/query`**: Synchronous endpoint. Accepts `{question: str}`, performs vector search, and returns `{answer: str, context: list}`.
