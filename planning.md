# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

The chosen domain is **The Unofficial Guide to University of Idaho Student Life**. This knowledge base focuses on authentic, peer-generated student experiences regarding campus dining insights (such as maximizing meal plans at Idaho Eats and Chartwells locations), student residential housing feedback, academic navigation (such as student reviews of the Mathematics and Computer Science departments), and local Moscow commuting hacks. 

This knowledge is incredibly valuable because official university channels provide heavily polished marketing material rather than the practical reality. Official sites won't tell students which dining hall lines move the slowest during peak hours, which specific residential dorms have thin walls, or how difficult it is to travel to the Spokane airport without a car. Gathering this crowdsourced data into a RAG system provides an honest, centralized survival guide for incoming and current students.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/UniversityOfIdaho (Housing) | Crowdsourced student threads detailing pros and cons of campus dorms and off-campus housing. | `documents/reddit_ui_housing.txt` |
| 2 | r/UniversityOfIdaho (Dining)  | Student complaints, recommendations, and hacks regarding Idaho Eats meal plan values. | `documents/reddit_ui_dining.txt` |
| 3 | Rate My Professors (Math)     | Collected text reviews of introductory and advanced Math professors at UI. | `documents/rmp_ui_math.txt` |
| 4 | Rate My Professors (CS)       | Student reviews focusing on workload and pacing in the Computer Science department. | `documents/rmp_ui_cs.txt` |
| 5 | Moscow Student Forum (Living) | Local discussion threads about living in the city of Moscow, Idaho, utilities, and landlords. | `documents/forum_moscow_living.txt` |
| 6 | Crowdsourced Dining Guide     | Self-submitted text tips from students working or eating at Chartwells campus dining locations. | `documents/student_dining_tips.txt` |
| 7 | UI Student Discord Archives   | Anonymized and cleaned text chat logs containing academic tips and general campus hacks. | `documents/discord_campus_hacks.txt` |
| 8 | UI On-Campus Job Reviews      | Student evaluations of different campus employment positions, flexible scheduling, and work environments. | `documents/student_job_reviews.txt` |
| 9 | r/UniversityOfIdaho (Freshman)| Advice megathreads targeted at incoming freshmen preparing for their first semester. | `documents/reddit_freshman_tips.txt` |
| 10| Moscow Transit Student Guide   | Local transit feedback, rideshare availability, and regional shuttle options to Spokane airport. | `documents/student_transit_guide.txt` |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**  500 characters

**Overlap:**  50 characters

**Reasoning:**  Student forum entries, Reddit comments, and professor reviews are traditionally short, informal, and highly conversational paragraph units. Setting a chunk size of 500 characters prevents distinct pieces of advice from merging together while keeping individual thoughts completely intact. A 50-character overlap ensures that crucial text strings—like specific professor names, class codes, or dining venues—are not accidentally cleaved in half at a boundary line, preserving semantic continuity during retrieval.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` (via sentence-transformers)

**Top-k:**  4 chunks

**Production tradeoff reflection:**
   
   The `all-MiniLM-L6-v2` model is optimal for local execution on a standard laptop. It features a lightweight architecture with low computational latency, requiring no remote API overhead or hosting expenses. However, if deploying a production system for thousands of daily active campus users, we would need to weigh several production tradeoffs:
* **Context Length vs. Latency:** Standard local models limit sequences to 256 or 512 tokens. Upgrading to a model like `text-embedding-3-large` via OpenAI extends the context window significantly, letting us pass larger chunks without losing structure, though it introduces network latency.
* **Domain Specificity vs. Cost:** Crowdsourced student data is filled with casual text, abbreviations, and hyper-local slang (e.g., "The Hub", "Idaho Eats"). Commercial embedding endpoints process multi-billion parameter relationship maps that capture contextual nuances better than small local models, but introduce ongoing financial dependencies via API volume billing.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What are the best food options or student hacks for eating at Idaho Eats / Chartwells dining locations? | Students emphasize specific time hacks to avoid lines and call out specific menu items or flexible swapping methods to maximize value. |
| 2 | Which housing options or dorms do students recommend avoiding, and why? | The response should mention specific dorm complexes criticized by students for infrastructure complaints, noise issues, or outdated amenities. |
| 3 | What do students say about the workload in introductory math or data science courses? | The system should pull reviews highlighting regular homework pacing, difficult exam weights, or helpful professor study habits. |
| 4 | Is it easy to get around Moscow or travel to nearby airports like Spokane without a car? | Expected output should list alternative shuttle options, bus links, or ridesharing realities for regional travel out of Moscow. |
| 5 | What are the best on-campus jobs for students looking for flexible hours? | The response should identify departments highlighted by students for being accommodating of student class schedules and offering good work environments. |

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Noisy Text Inputs and Formatting Clutter:** Crowdsourced forum text and web-scraped inputs naturally contain conversational noise, excessive emojis, web links, or messy markdown text. If left untreated, this noise will pollute the vector space and distort semantic search rankings.

2. **Context Fragmentation Over Structural Boundaries:** If a student posts a comprehensive review covering housing pros *and* housing cons sequentially, a fixed-size text splitting function could slice the text right in the middle. This would detach the negative warnings from their primary subject context, creating fragmented chunks that result in incomplete LLM responses.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```text
========================================================================================
1. DOCUMENT INGESTION
   - Raw data: .txt files stored in documents/ directory
   - Cleaned via custom Python scripts (removing URLs, emojis, and web formatting noise)
========================================================================================
                                   │
                                   ▼
========================================================================================
2. CHUNKING
   - Library: RecursiveCharacterTextSplitter (LangChain)
   - Parameters: chunk_size = 500 characters, chunk_overlap = 50 characters
========================================================================================
                                   │
                                   ▼
========================================================================================
3. EMBEDDING + VECTOR STORE
   - Embedding Tool: sentence-transformers (all-MiniLM-L6-v2)
   - Storage Database: ChromaDB (Local Persistent Client)
   - Metadata Saved: {"source": "filename.txt"}
========================================================================================
                                   │
                                   ▼
========================================================================================
4. RETRIEVAL
   - Process: ChromaDB semantic vector query matching
   - Input: User query string  --->  Output: top_k = 4 most matching text context chunks
========================================================================================
                                   │
                                   ▼
========================================================================================
5. GENERATION + INTERFACE
   - LLM Orchestration: Groq API client running llama-3.3-70b-versatile
   - UI Interface: Gradio web application for input query and source display
========================================================================================
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
AI Tool: Claude

Input Context: Provide Claude with the Domain, Documents table, and Chunking Strategy sections from this planning.md file, along with the requirement to keep chunks clean.

Expected Output: A Python script utilizing standard file operations to ingest raw text data from the documents/ folder, scrub irrelevant textual syntax, split strings via RecursiveCharacterTextSplitter into chunks of 500 characters with an overlap of 50, and count total chunks.

Verification Method: Run the resulting script locally and print out sample text outputs alongside the final chunk count to manually verify that text segments match boundaries properly.

**Milestone 4 — Embedding and retrieval:**


AI Tool: GitHub Copilot / Claude

Input Context: Provide the Embedding Model and Retrieval Approach specifications from this document, alongside a structural outline of a target ChromaDB setup.

Expected Output: Integration code that instantiates ChromaDB, iterates over generated document chunks to assign vector values with all-MiniLM-L6-v2, stores the result to a disk partition, and exposes a clean query_database(text, k=4) collection search function.

Verification Method: Pass a diagnostic test query manually into the query function and confirm that the returned array matches the expected top-4 schema object structure along with associated source keys.

**Milestone 5 — Generation and interface:**
AI Tool: Claude

Input Context: Provide the Grounded Generation instructions, the Evaluation Plan list of test questions, and the structural design layout of the RAG pipeline.

Expected Output: A unified production file containing a strict system prompt wrapping the Groq API call, an append function that handles source metadata listings, and a simple gradio.Interface web presentation block.

Verification Method: Launch the local web server dashboard, input the evaluation questions, and verify that the app blocks any off-topic queries while correctly rendering numbered citations at the base of the text window.