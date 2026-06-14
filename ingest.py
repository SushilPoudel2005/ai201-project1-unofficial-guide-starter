import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_clean_documents(docs_directory):
    raw_documents = {}
    
    # Check if directory exists
    if not os.path.exists(docs_directory):
        print(f"Error: The directory '{docs_directory}' does not exist.")
        return raw_documents

    # 1. DOCUMENT INGESTION: Read all files from the documents folder
    for filename in os.listdir(docs_directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(docs_directory, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                
                # 2. CLEANING: Simple cleanup of extra spaces/newlines
                # (Add more cleaning rules here later if your scraped text has HTML tags)
                cleaned_text = text.strip()
                raw_documents[filename] = cleaned_text
                
    return raw_documents

def chunk_documents(documents):
    # 3. CHUNKING STRATEGY: 500 characters, 50 characters overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    
    all_chunks = []
    
    for filename, text in documents.items():
        # Split the text into chunks
        chunks = text_splitter.split_text(text)
        
        # Attach metadata (source filename) to each chunk
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "metadata": {"source": filename}
            })
            
    return all_chunks

if __name__ == "__main__":
    # Define the directory where your documents live
    DOCS_DIR = "documents"
    
    # Run the ingestion and cleaning pipeline
    print("🔄 Loading and cleaning documents...")
    docs = load_and_clean_documents(DOCS_DIR)
    
    # Run the chunking pipeline
    print("✂️ Chunking documents...")
    chunks = chunk_documents(docs)
    
    # 4. INSPECTION: Print the total count and 3 sample chunks to verify
    print("\n" + "="*50)
    print(f"📊 PIPELINE METRICS: Created {len(chunks)} total chunks.")
    print("="*50 + "\n")
    
    print("🔍 INSPECTING SAMPLE CHUNKS:")
    for i, chunk in enumerate(chunks[:3]):  # Show the first 3 chunks
        print(f"--- Chunk {i+1} | Source: {chunk['metadata']['source']} ---")
        print(chunk['text'])
        print(f"Length: {len(chunk['text'])} characters\n")