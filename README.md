# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
The topic of this system is **The Unofficial Guide to University of Idaho Student Life**. This knowledge base focuses heavily on unpolished, crowdsourced peer experiences regarding campus dining insights (such as maximizing meal plans across Idaho Eats and Chartwells locations), student residential housing feedback, academic navigation (specifically student course evaluations for the Mathematics and Computer Science departments), and local Moscow commuting hacks. 

This knowledge is incredibly valuable because official university channels provide polished marketing material that skips over practical campus realities. Official sites do not tell students which dining hall lines move the slowest during peak hours, which residential dorms have thin walls, or how difficult it is to travel to the Spokane airport without personal transportation. Consolidating this raw data into a RAG system provides an honest, centralized survival guide for incoming and current students.


---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->
| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/UniversityOfIdaho (Housing) | Text/Markdown | `documents/reddit_ui_housing.txt` |
| 2 | r/UniversityOfIdaho (Dining)  | Text/Markdown | `documents/reddit_ui_dining.txt` |
| 3 | Rate My Professors (Math)     | Text/Markdown | `documents/rmp_ui_math.txt` |
| 4 | Rate My Professors (CS)       | Text/Markdown | `documents/rmp_ui_cs.txt` |
| 5 | Moscow Student Forum (Living) | Text/Markdown | `documents/forum_moscow_living.txt` |
| 6 | Crowdsourced Dining Guide     | Text/Markdown | `documents/student_dining_tips.txt` |
| 7 | UI Student Discord Archives   | Text/Markdown | `documents/discord_campus_hacks.txt` |
| 8 | UI On-Campus Job Reviews      | Text/Markdown | `documents/student_job_reviews.txt` |
| 9 | r/UniversityOfIdaho (Freshman)| Text/Markdown | `documents/reddit_freshman_tips.txt` |
| 10| Moscow Transit Student Guide  | Text/Markdown | `documents/student_transit_guide.txt` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**

Student forum entries, Reddit comments, and professor reviews are traditionally short, informal, and highly conversational paragraph units. Setting a chunk size of 500 characters prevents entirely distinct pieces of advice from blending together while keeping individual thoughts completely intact. The 50-character overlap ensures that crucial text strings—like specific professor names, class codes, or dining venues—are not accidentally cleaved in half at a boundary line, preserving semantic continuity during retrieval.

Before chunking, the ingestion pipeline cleans each file dynamically by stripping out extra spaces, trailing newlines, and uniform metadata headers to ensure the vector data contains only the substance of the student text.

**Final chunk count:**
3 total chunks ( Using the initial benchmark student dining guide sample file)
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via the `sentence-transformers` library.

**Production tradeoff reflection:**
This model is highly efficient for local development because it runs completely locally on standard laptop hardware without requiring external API keys, runtime costs, or encountering network rate limits. However, if deploying this system at scale for thousands of students, major tradeoffs would need to be addressed:
* **Context Window & Latency:** `all-MiniLM-L6-v2` caps sequences at 256 or 512 tokens. An API-hosted model like OpenAI’s `text-embedding-3-large` handles vastly larger dimensions and inputs, which would let us pass larger chunks without losing structure, though it introduces network latency.

* **Slang & Domain Vocabulary:** Campus discussions are filled with hyper-local terminology (e.g., "The Hub," "Polya Center," "Meal Exchanges"). Multi-billion parameter commercial embedding models understand contextual synonyms and messy, casual phrasing much better than a small local model, though they introduce ongoing API volume billing.
---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

You are the Unofficial University of Idaho Student Assistant. You answer student questions STRICTLY using only the provided text context snippets. Follow these rules explicitly:
1. Answer the question completely based *only* on the text snippets provided.
2. Do NOT use outside knowledge, general assumptions, or facts not present in the context.
3. If the context does not contain enough data to confidently answer the question, you must reply exactly with: 'I am sorry, but I don't have enough student-generated data to answer that question safely.'
4. Do not mention the text snippets directly as 'Snippet #1', instead summarize the information cleanly.

**How source attribution is surfaced in the response:**

Every chunk added to ChromaDB includes a source metadata attribute tracking its origin filename. When a user runs a query, the application retrieves the top chunks, reads the metadata dictionary programmatically, and appends a clean, bulleted checklist to a standalone "Verified Source References Used" text panel in the Gradio UI. If the system rejects a prompt due to a lack of data, it programmatically sets the source frame to "None - Out of Scope."

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

Evaluation Report#QuestionExpected answerSystem response (summarized)Retrieval qualityResponse accuracy1What are the hacks for eating at Idaho Eats?Avoid the Hub rush from 12:00-12:45 PM, maximize meal exchanges before Sunday, ask for fresh pizzas politely.Clean summary explaining peak Hub lines, using meal exchanges at Einstein Bros before Sunday resets, and requesting fresh pies.RelevantAccurate2Who won the Super Bowl in 2024?System should decline to answer using the exact prompt refusal statement."I am sorry, but I don't have enough student-generated data to answer that question safely."Off-targetAccurate3What do students say about the workload in introductory math courses?Pacing moves very fast, homework is due online every Tuesday/Thursday, use the Polya center."I am sorry, but I don't have enough student-generated data to answer that question safely."Off-targetAccurate4Which housing options or dorms do students recommend avoiding?Detailed specific student infrastructure complaints or bad amenities."I am sorry, but I don't have enough student-generated data to answer that question safely."Off-targetAccurate5What are the best on-campus jobs for students looking for flexible hours?Lists campus departments praised by students for accommodating class schedules."I am sorry, but I don't have enough student-generated data to answer that question safely."Off-targetAccurate

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"What do students say about the workload in introductory math courses?"

**What the system returned:**
"I am sorry, but I don't have enough student-generated data to answer that question safely."

**Root cause (tied to a specific pipeline stage):**
This is a failure at the Document Ingestion stage. While the underlying RAG pipeline code is fully written, integrated, and functioning correctly, only the initial sample document (student_dining_tips.txt) was loaded during the baseline testing run. Because the math review document (rmp_ui_math.txt) had not yet been fully populated across the vector storage collection, ChromaDB could not match any relevant embeddings, causing the system prompt's grounding filter to force a safe, programmatic refusal.

**What you would change to fix it:**
To fix this, I need to finish populating the remaining 8 text source files inside the documents/ folder as planned in the specification, and clear/re-run vector_store.py to rebuild the index database so that all domain topics are fully embedded.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The spec kept me disciplined about defining my exact character sizes and overlap rules before touching code. Having the ASCII architecture diagram completely mapped out meant that when I moved from creating the text files to writing the database scripts, I knew exactly how data flows from ingest.py straight into the ChromaDB vector collections.

**One way your implementation diverged from the spec, and why:**
My implementation diverged slightly because I automated the chunking process entirely through LangChain's RecursiveCharacterTextSplitter inside ingest.py rather than a crude, fixed mechanical loop. I did this because the text splitter respects word and sentence boundaries natively, preventing sentences from being sliced haphazardly across the 500-character limits.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
I passed the raw chunking strategy text from my planning.md file along with my targeted domain info and asked it to construct a foundational file loading template.

- *What it produced:*
It generated a standalone Python script utilizing regular expressions to clean text, chunking text mechanically by fixed characters, and counting the elements.

- *What I changed or overrode:*
I completely overrode the mechanical text splitting functions and imported LangChain’s RecursiveCharacterTextSplitter instead. This ensured that our pipeline splits text contextually by paragraph space parameters, rather than severing random words mid-sentence.

**Instance 2**

- *What I gave the AI:*
I provided my grounding requirements, the target Groq llama-3.3-70b-versatile client configuration parameters, and my expected Gradio UI block structure layout.

- *What it produced:*
A complete app.py script that called the LLM, but passed the context chunks inline without explicit delimiters and relied entirely on the LLM to format and list the sources at the end of the text.

- *What I changed or overrode:*
I restructured the script to isolate the context cleanly inside structured snippet blocks (--- Context Snippet #X ---). I also stripped the source tracking out of the LLM's hands entirely, writing custom Python code to extract metadata from the local ChromaDB query response and map it directly into its own isolated Gradio dashboard window.