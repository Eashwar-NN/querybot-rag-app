import streamlit as st
import requests
import time

# Define the base URL for the backend API
BACKEND_URL = "http://fastapi-server:8000"

st.title("📄 QueryBot Interface")
st.write("Welcome! This tool allows you to ask questions about a technical document.")

# --- File Upload Section ---
st.header("1. Upload a PDF")

# Create a file uploader widget that accepts only PDF files
uploaded_file = st.file_uploader(
    "Choose a PDF file to process",
    type="pdf"
)

# Create a button to trigger the upload process
if st.button("Upload and Process"):
    if uploaded_file is not None:
        # Prepare the file for the POST request
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}

        # Use a spinner to show that the upload is in progress
        with st.spinner(f"Uploading and processing '{uploaded_file.name}'... This may take a moment."):
            try:
                # Send the POST request to the backend's /upload endpoint
                response = requests.post(f"{BACKEND_URL}/upload", files=files)

                # Check the response from the backend
                if response.status_code in [200, 202]:
                    st.success("✅ File successfully uploaded and processed!")
                    st.info("You can now ask questions about the document below.")
                else:
                    # Show an error message if the upload failed
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                # Handle connection errors
                st.error(f"❌ Connection Error: Could not connect to the backend at {BACKEND_URL}.")
                st.error("Please ensure the backend Docker container is running.")

    else:
        # Show a warning if the user clicks the button without selecting a file
        st.warning("⚠️ Please select a PDF file first.")

# Add a visual separator
st.divider()

# --- Q&A Section ---
st.header("2. Ask a Question")

# Create a text input for the user's question
user_question = st.text_input(
    "Enter your question about the document:",
    placeholder="e.g., What is the self-attention mechanism?"
)

# Create a button to submit the question
if st.button("Ask"):
    if user_question:
        # Prepare the JSON payload for the POST request
        payload = {"question": user_question}

        # Use a spinner to show that the query is in progress
        with st.spinner("🧠 Thinking..."):
            try:
                # Send the POST request to the backend's /query endpoint
                response = requests.post(f"{BACKEND_URL}/query", json=payload)

                # Check the response from the backend
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer found.")
                    st.markdown("### Answer:")
                    st.write(answer)
                else:
                    # Show an error message if the query failed
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                # Handle connection errors
                st.error(f"❌ Connection Error: Could not connect to the backend at {BACKEND_URL}.")
                st.error("Please ensure the backend Docker container is running.")

    else:
        # Show a warning if the user clicks the button without typing a question
        st.warning("⚠️ Please enter a question first.")
