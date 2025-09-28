# 1. Start with a base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy and install dependencies (optimized for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Pre-load the embedding model
COPY preload.py .
RUN python preload.py

# 5. Copy your application code
COPY . .

# 6. Expose the port the app runs on
EXPOSE 8000

# 7. Define the run command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]