from langchain_huggingface import HuggingFaceEmbeddings

print("Pre-loading sentence transformer model...")

# Instantiate the model, which will trigger the download
HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print("Model pre-loading complete.")
