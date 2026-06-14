import os
import chromadb
from chromadb.utils import embedding_functions
from ingest import load_and_clean_documents, chunk_documents

def setup_vector_store(chunks, db_path="./chroma_db"):
    # 1. Initialize the ChromaDB persistent client (saves data to disk)
    client = chromadb.PersistentClient(path=db_path)
    
    # 2. Set up the embedding function using all-MiniLM-L6-v2
    # This runs locally on your Mac with no API keys needed!
    model_name = "all-MiniLM-L6-v2"
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )
    
    # 3. Create or get the collection
    collection = client.get_or_create_collection(
        name="ui_student_guide",
        embedding_function=embedding_fn
    )
    
    # Prepare data arrays for ChromaDB batch insertion
    documents = []
    metadatas = []
    ids = []
    
    print(f"🧠 Generating embeddings for {len(chunks)} chunks...")
    for idx, chunk in enumerate(chunks):
        documents.append(chunk["text"])
        metadatas.append(chunk["metadata"])
        ids.append(f"chunk_{idx}")
    
    # 4. Add items to the collection
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("✅ Vector database populated successfully!")
    
    return collection

def query_vector_store(collection, query_text, k=2):
    # 5. Query the database for top-k nearest matches
    results = collection.query(
        query_texts=[query_text],
        n_results=k
    )
    return results

if __name__ == "__main__":
    DOCS_DIR = "documents"
    
    # Reuse your pipeline from Milestone 3
    raw_docs = load_and_clean_documents(DOCS_DIR)
    chunks = chunk_documents(raw_docs)
    
    # Setup and populate database
    collection = setup_vector_store(chunks)
    
    # 6. RETRIEVAL TEST: Let's test a sample search query from your evaluation plan
    test_query = "What are the hacks for eating at Idaho Eats?"
    print(f"\n🔍 Testing retrieval query: '{test_query}'")
    
    search_results = query_vector_store(collection, test_query, k=2)
    
    # Print the matching chunks and their distance scores
    print("\n📦 RETRIEVED CHUNKS:")
    print("=" * 60)
    for i in range(len(search_results['documents'][0])):
        text = search_results['documents'][0][i]
        source = search_results['metadatas'][0][i]['source']
        distance = search_results['distances'][0][i]
        
        print(f"🔹 Match #{i+1} | Source: {source} | Distance Score: {distance:.4f}")
        print(f"Content: {text}\n")
    print("=" * 60)