📄 QueryBot: A Full-Stack RAG Application
QueryBot is a complete, containerized Retrieval-Augmented Generation (RAG) application built from the ground up. It provides a simple web interface for users to upload a PDF document and ask questions about its content. The application uses a local Large Language Model (LLM) via Ollama, ensuring privacy and cost-effectiveness.

The entire project is orchestrated with Docker Compose, allowing for a seamless one-command launch of both the frontend and backend services.

✨ Features
FastAPI Backend: A robust backend server with API endpoints for document processing and querying.

RAG Pipeline: Implements a full pipeline to ingest PDF documents, create vector embeddings, and generate context-aware answers.

Interactive Frontend: A user-friendly interface built with Streamlit for easy file uploading and Q&A interaction.

Local First: Utilizes a locally-run LLM (e.g., Llama 3) through Ollama, making it independent of external APIs.

Containerized: The entire application is containerized using Docker and managed with a single Docker Compose file for easy setup and portability.

🛠️ Tech Stack
Application Framework: LangChain

Vector Store: FAISS (Facebook AI Similarity Search)

Embedding Model: Sentence-Transformers (all-MiniLM-L6-v2)

LLM: Ollama (e.g., llama3:8b)

Backend Server: FastAPI

Frontend Server: Streamlit

Containerization: Docker & Docker Compose

📂 Project Structure
querybot/
├── backend/
│   ├── main.py               # FastAPI application logic
│   ├── preload.py            # Script to download the embedding model
│   ├── Dockerfile            # Docker instructions for the backend
│   └── requirements.txt      # Backend Python dependencies
├── frontend/
│   ├── app.py                # Streamlit application logic
│   ├── Dockerfile            # Docker instructions for the frontend
│   └── requirements.txt      # Frontend Python dependencies
├── .gitignore                # Specifies files for Git to ignore
└── docker-compose.yml        # Orchestrates both services

🚀 Getting Started
Follow these instructions to get a local copy up and running.

Prerequisites
Docker and Docker Compose: Ensure you have Docker Desktop installed and running. You can download it from the official Docker website.

Ollama: Install and run the Ollama application on your host machine. You can download it from ollama.com.

LLM Model: Pull the required LLM using the Ollama CLI. This project is configured for llama3:8b.

ollama run llama3:8b

Running the Application
Clone the repository:

git clone <your-repository-url>
cd querybot

Launch the services with Docker Compose:
This command will build the Docker images for both the backend and frontend and start the containers.

docker-compose up --build

Access the application:
Once the containers are running, the application will be available at:

Streamlit Frontend: http://localhost:8501

📝 Usage
Open your web browser and navigate to http://localhost:8501.

In the "Upload a PDF" section, browse for a PDF file on your local machine and click the "Upload and Process" button. Wait for the success message.

In the "Ask a Question" section, type your question about the uploaded document into the text input field.

Click the "Ask" button and wait for the AI-generated answer to appear.

⚙️ API Endpoints
The backend service exposes the following API endpoints, which can be tested via the interactive documentation at http://localhost:8001/docs.

POST /upload: Accepts a PDF file (multipart/form-data) to process and index.

POST /query: Accepts a JSON payload like {"question": "your question here"} and returns the answer.