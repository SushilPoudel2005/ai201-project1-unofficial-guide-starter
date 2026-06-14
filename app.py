import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import gradio as gr

# Load environment variables from the .env file
load_dotenv()

# Initialize the Groq Client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ ERROR: GROQ_API_KEY not found in .env file!")

groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize ChromaDB Client pointing to your existing saved data
chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_collection(name="ui_student_guide", embedding_function=embedding_fn)

def ask_unofficial_guide(question):
    # 1. Retrieve the top 4 matching chunks from your local database
    results = collection.query(query_texts=[question], n_results=4)
    
    retrieved_chunks = results['documents'][0]
    metadata_list = results['metadatas'][0]
    
    # Format the chunks into a single string block for the AI to read
    context_block = ""
    sources_used = set()
    
    for i, chunk_text in enumerate(retrieved_chunks):
        source_name = metadata_list[i]['source']
        sources_used.add(source_name)
        context_block += f"--- Context Snippet #{i+1} (Source: {source_name}) ---\n{chunk_text}\n\n"
        
    # 2. Define the strict grounding system prompt
    system_prompt = (
        "You are the Unofficial University of Idaho Student Assistant. You answer student questions "
        "STRICTLY using only the provided text context snippets. Follow these rules explicitly:\n"
        "1. Answer the question completely based *only* on the text snippets provided.\n"
        "2. Do NOT use outside knowledge, general assumptions, or facts not present in the context.\n"
        "3. If the context does not contain enough data to confidently answer the question, you must reply "
        "exactly with: 'I am sorry, but I don't have enough student-generated data to answer that question safely.'\n"
        "4. Do not mention the text snippets directly as 'Snippet #1', instead summarize the information cleanly."
    )
    
    user_prompt = f"Context Data:\n{context_block}\n\nQuestion: {question}"
    
    try:
        # 3. Call the Groq LLM API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0 # Strict accuracy, no creative hallucination
        )
        
        answer = chat_completion.choices[0].message.content
        
        # If the model refused to answer based on grounding rules, clear out the source panel
        if "don't have enough student-generated data" in answer:
            sources_output = "None - Out of Scope"
        else:
            sources_output = "\n".join(f"• {s}" for s in sources_used)
            
        return answer, sources_output

    except Exception as e:
        return f"❌ API Error: {str(e)}", "None"

# 4. Build the Gradio Web Interface Dashboard
with gr.Blocks(title="The Unofficial U-Idaho Student Guide") as demo:
    gr.Markdown("# 🌲 The Unofficial Guide to U-Idaho Student Life")
    gr.Markdown("An AI Assistant grounded strictly in student-generated crowdsourced experiences.")
    
    with gr.Row():
        with gr.Column():
            inp = gr.Textbox(label="Ask a campus question:", placeholder="e.g., What are the hacks for eating at Idaho Eats?")
            btn = gr.Button("Submit Query", variant="primary")
        with gr.Column():
            answer = gr.Textbox(label="Grounded AI Answer", lines=8, interactive=False)
            sources = gr.Textbox(label="Verified Source References Used", lines=3, interactive=False)
            
    # Connect both button clicks and pressing 'Enter' inside the text box
    btn.click(ask_unofficial_guide, inputs=inp, outputs=[answer, sources])
    inp.submit(ask_unofficial_guide, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    # Launch the local web server
    demo.launch()