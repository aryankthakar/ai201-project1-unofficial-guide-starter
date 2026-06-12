# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

My ideas so far are UMD housing reviews (specifically of University View, so that the scope of the domain is manageable enough), since it's hard to find information on them in one reliable place, so the thought process here is to gather information from multiple sites in order to get a coherent perspective. 

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Apartments.com | | https://www.apartments.com/university-view-college-park-md/jtb8837/ |
| 2 | ForRent | | https://www.forrent.com/md/college-park/university-view/4tb8g3l |
| 3 | Kato Housing | | https://katohousing.org/apartment/university-view|
| 4 | ochdatabase | | https://ochdatabase.umd.edu/housing/property/university-view/2sbyc3c|
| 5 | Reddit r/UMD | | https://www.reddit.com/r/UMD/comments/1cg5mg6/uview_housing_review/|
| 6 | University View Website | | https://live-theview.com/faqs/ |
| 7 | Reddit r/UMD | | https://www.reddit.com/r/UMD/comments/q5e4we/view_vs_varsity_any_advice/|
| 8 | Reddit r/UMD | | https://www.reddit.com/r/UMD/comments/12js4z9/red_flags_about_new_apartments_coming_to_college/|
| 9 | Yelp | | https://www.yelp.com/biz/university-view-college-park-2|
| 10 | AmberStudent | | https://amberstudent.com/places/university-view-college-park-college-park-2411237089448|
| 11 | Facebook | https://www.facebook.com/groups/BYUI.Students/posts/5524373450942892/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 400 characters

**Overlap:** 75 characters (min chunk length 50; shorter fragments discarded)

**Reasoning:** Uniform character-based sliding window. The corpus is
review-heavy — reviews, Reddit comments, and FAQ answers each pack one opinion
or one fact into a short span, so small chunks keep every retrieved unit focused
on a single perspective instead of blurring several together. 400 chars also
stays under all-MiniLM-L6-v2's ~256-token (~1000-char) limit, so no chunk is
silently truncated at embed time. The 75-char overlap protects facts that
straddle a boundary. Result on the 6 ingested sources: 254 chunks, avg 395
chars/chunk.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** *all-MiniLM-L6-v2*, it's a small and fast model running with no API cost or rate limits. 

**Top-k:** *4* seems like a good balance, enough to cover multiple perspectives but not so many that there's redundancies. 

**Production tradeoff reflection:** If cost constraints didn't exist, I'd optimize for increasing accuracy, context length, multilingual support. 

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What are the monthly costs and fees? | Pricing depends on floor plan and lease term, and the official rates page is the best place to check current numbers. Generally, 4 bed 4 bath in tower 1 starts at $1269.|
| 2 | Is it worth it? | University View seems most worth it if campus proximity is your top priority; reviews are mixed, with convenience praised more often than value, fees, or service.|
| 3 | How close is it to campus? | Reviews and official info consistently describe it as very close to UMD and convenient for walking or getting around campus.|
| 4 | What are the downsides? | The most common complaints are noise, fees, maintenance concerns, and inconsistent service for the price.|
| 5 | What's included? | The FAQs cover furnished units, utilities, contract details, and other standard student-housing questions.|

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Noisy documents that contain information about other topics that is irrelevant to the website. This could result in tokens being expended on vectors that aren't useful. More performance and storage wasted on something unhelpful. 
2. Processing these documents may not be able to convert fully from HTML to Markdown and may lose important information. This can decrease the amount of context for the RAG chatbot. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

flowchart LR
    A["HTML Documents"]
    --> B["LangChain Ingestion<br/>HTML → Markdown"]
    --> C["Context-Aware Chunking"]
    --> D["Embeddings<br/>all-MiniLM-L6-v2"]
    --> E["ChromaDB Vector Store"]

    U["User Query"]
    --> F["Retrieval<br/>llama-3.3-70b-versatile"]

    E --> F
    F --> G["Retrieved Context"]

    G --> H["Generation<br/>llama-3.3-70b-versatile"]
    U --> H

    H --> I["Final Response"]


## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

1. I'll use Claude. 
2. I'll give the planning.md file and a prompt telling it how to utilize the document and prompt it to ask as many clarifying questions as possible. 
3. I expect it to produce one python program for each part of the programming pipeline. 
4. I'll create test cases to determine if the correct models and parameters are being used. 

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
