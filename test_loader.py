from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("attention.pdf")

pages = loader.load()

print(f"Successfully loaded {len(pages)} pages from the attenion.pdf")

print("\n--- Content of Page 1 (first 250 chars) ---")
print(pages[0].page_content[:250])

print("\n--- Metadata of Page 1 ---")
print(pages[0].metadata)
