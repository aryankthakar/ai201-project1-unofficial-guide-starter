# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

University View is one of the main off-campus housing options for UMD students,
but reliable information about it is scattered: official listing pages sell the
upside, while honest accounts of fees, maintenance, and day-to-day living are
spread across Reddit threads, Yelp, Facebook groups, and aggregator sites. This
project pulls those sources into one place so a prospective renter can ask a
direct question ("Is it worth it?", "What are the downsides?") and get a
grounded, cited answer that reflects multiple perspectives. The knowledge is valuable precisely because no single official
channel gives an unbiased, consolidated view.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

11 sources spanning official listings, third-party aggregators, and
student-generated reviews:

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Apartments.com | Listing + reviews | https://www.apartments.com/university-view-college-park-md/jtb8837/ |
| 2 | ForRent | Listing + reviews | https://www.forrent.com/md/college-park/university-view/4tb8g3l |
| 3 | Kato Housing | Aggregator listing | https://katohousing.org/apartment/university-view |
| 4 | OCH Database (UMD) | University listing | https://ochdatabase.umd.edu/housing/property/university-view/2sbyc3c |
| 5 | Reddit r/UMD — UView housing review | Forum thread | https://www.reddit.com/r/UMD/comments/1cg5mg6/uview_housing_review/ |
| 6 | University View Official FAQ | Official | https://live-theview.com/faqs/ |
| 7 | Reddit r/UMD — View vs Varsity | Forum thread | https://www.reddit.com/r/UMD/comments/q5e4we/view_vs_varsity_any_advice/ |
| 8 | Reddit r/UMD — red flags about new apartments | Forum thread | https://www.reddit.com/r/UMD/comments/12js4z9/red_flags_about_new_apartments_coming_to_college/ |
| 9 | Yelp | Reviews | https://www.yelp.com/biz/university-view-college-park-2 |
| 10 | AmberStudent | Aggregator listing | https://amberstudent.com/places/university-view-college-park-college-park-2411237089448 |
| 11 | Facebook (student housing post) | Social/forum | `documents/raw/FacebookUView.html` |

Sources behind bot walls or login (Apartments.com, ForRent, Yelp, the 3 Reddit threads, Facebook, Kato, OCH Database) were saved manually as HTML into `documents/raw/`; the official FAQ and AmberStudent were scraped live. All flow
through the same HTML→Markdown cleaning path (see `scrape.py`).


---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 400 characters

**Overlap:** 75 characters (minimum chunk length 50; shorter fragments discarded)

**Preprocessing Steps** Each source is converted from HTML to Markdown with BeautifulSoup (stripping `script`, `style`, `nav`, `header`, `footer`, `aside`, forms, etc.) and `markdownify`, then whitespace is collapsed before chunking.

**Why these choices fit your documents:** A major part of the document are reviews or responses. REddit, comments, Yelp reviews, and FAQ answers each contain one opinion or fact that's often self-contained. Small chunks make the retrieved units focused on a single perspective, rather than blurring several unrelated perspectives together. Additionally, the 400 characters stays under the `all-MiniLM-L6-v2's ~256-token (~1000-char)` input limit, so no chunk is silently truncated at embed time. The 75-char overlap is used to protect facts that straddle a boundary. 

**Final chunk count:** 356 chunks across 11 documents (avg ~394 chars/chunk).

---

### Sample chunks (5, each labeled with its source)

**1 — `apartments_com_6` (source: Apartments.com)** — per-person pricing:
```
TOWER 2  $1,249 / Person  4 Beds 2 Baths 1,352–1,408 Sq Ft  Available Now
4 BEDROOM, 4 BATH TOWER 1  $1,269 / Person  4 Beds 4 Baths 1,284–1,376 Sq Ft  Available Now
STUDIO TOWER 2  $2,299 / Person  1 Bed 1 Bath 509 Sq Ft  Not Available
2 BEDROOM, 2 BATH TOWER 1  $1,369 / Person  2 Beds 2 Baths 708–1,360 Sq Ft  Not Available
```

**2 — `ochdatabase_18` (source: OCH Database (UMD))** — what's included:
```
Washer/Dryer in Unit
### Unique Features
* 24-hour security  * 50" 1080p led tv  * barre + yoga studio
* enclosed bike storage  * free cable  * free high-speed internet
* game room w pool tables  * garage + surface parking available
* in-unit washer + dryer  * Individual + Group Study Rooms
* instructor led fitness classes  * limited entry + electronic key access
```

**3 — `forrent_28` (source: ForRent)** — negative resident review:
```
...the elevators are always down, utilities are not included, and don't come to
your account on the 1st of the month it's after.. and they are always adding
random fees. Lastly, it cost an additional $125 to park WHERE YOU LIVE.
Review from Apartments.com — 5 People Found This Helpful
### "PER PERSON" IS CRAZYYYY  It should be illegal
```

**4 — `facebook_2` (source: Facebook student housing post)** — mixed resident comments:
```
Emma Baczuk Davenport: its a great place to live, the shuttle is so nice to
have in the winter and i love having so much storage space in the bedrooms
Rachel Moffat Housley: Personally liked the living space a lot. Lots of space.
Windows are very leaky. When I was there managers made a lot of promises they
didn't [keep]
```

**5 — `forrent_21` (source: ForRent)** — campus proximity:
```
### Colleges and Universities
School  Commute Time (Distance)
University of Maryland   Walk: 12 min (0.6 mi)
Montgomery Coll., Takoma Park   Drive: 17 min (6.5 mi)
Catholic University   Drive: 16 min (6.6 mi)
```

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (384-dimensional embeddings), stored in a persistent ChromaDB collection using cosine distance. It runs locally with no API key, no cost, and no rate limits — appropriate for a small 11-document corpus where state-of-the-art accuracy isn't required.

**Production tradeoff reflection:** If this were deployed for real users and cost weren't a constraint, I'd weigh:
- **Accuracy on domain text**: a larger model (e.g. `bge-large-en` or OpenAI
  `text-embedding-3-large`) captures nuance in informal review language better,
  which matters for subjective queries like "is it worth it?".
- **Context length**: MiniLM truncates at ~256 tokens, which is the main reason
  chunks are kept small here; a longer-context model would let me embed larger,
  more self-contained chunks (e.g. a whole Reddit comment) without truncation.
- **Latency / local vs. API**: local MiniLM has zero network latency and keeps
  data private; an API model adds per-query latency and cost but offloads
  compute. Embeddings are computed once at ingest, so this mostly affects
  query-time encoding.
- **Multilingual support**: irrelevant for this English-only corpus, but would
  matter if expanded to international-student forums.


---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

> You are The Unofficial Guide to University View… You answer questions using
> ONLY the CONTEXT passages provided below, which come from reviews, listings,
> and the official FAQ.
>
> Rules:
> - Answer strictly from the CONTEXT. Do NOT use any outside knowledge about \ University View or apartments in general.
> - If the CONTEXT does not contain the answer, say so plainly — do not guess. \ An honest "the sources don't cover that" is better than a confident guess.
> - For subjective questions (e.g. "is it worth it?", "what are the downsides?"), \ synthesize a balanced view across the different sources rather than quoting one. Note when sources disagree.
> - Be concise and specific. Quote concrete figures (prices, distances, dates) when the context provides them.
> - Do not invent URLs or sources. The interface appends citations for you.
> - If there's a generic question about prices, clearly state that it varies but give a reference point for what a normal apartment would cost given x and y  number of beds and baths.
> - If the question feels vague, then ask 2 clarifying questions before giving a response.

**How source attribution is surfaced in the response:** every response ends with a deduplicated
`Sources:` list of `source name — url`, derived from the metadata of the chunks actually used.
---




## Retrieval Test Results

Three evaluation queries, showing the chunks returned (cosine distance; lower =
closer). Retrieval uses top-k=4 with a 0.7 distance filter.

**Query: "How close is it to campus?"**
| Source | Distance | Chunk (excerpt) |
|---|---|---|
| ForRent | 0.348 | "…University View proximity to Campus Village, College Park Center…" |
| Apartments.com | 0.398 | "University View is within 12 minutes or 0.6 mile from University of Maryland" |
| Reddit — View vs Varsity | 0.408 | "…it's right across from the view so it's still pretty close to campus" |
| ForRent | 0.417 | "University of Maryland — Walk: 12 min (0.6 mi)" |

*Why these are relevant:* all four directly address physical distance/commute to
UMD. The top two independently confirm the same "0.6 mi / 12-minute walk" figure
from different sources — exactly the corroboration a grounded answer wants (one
from a listing, one from a student).

**Query: "What's included?"**
| Source | Distance | Chunk (excerpt) |
|---|---|---|
| OCH Database (UMD) | 0.600 | "Washer/Dryer in Unit … 24-hour security, free cable, free high-speed internet…" |
| Apartments.com | 0.627 | "Gameroom, Individual Locking Bedrooms, Roommate Matching, Shuttle…" |
| ForRent | 0.637 | "enclosed bike storage, free cable, free high-speed internet, game room…" |
| Apartments.com | 0.650 | "Picnic Area … Individual Locking Bedrooms…" |

*Why these are relevant:* every chunk is an amenities/features list. Three
different sources overlap on the same inclusions (free internet/cable, in-unit
laundry, study rooms), so the generated answer can state them with confidence.

**Query: "Is it worth it?"** (subjective — see Evaluation Report)
| Source | Distance | Chunk (excerpt) |
|---|---|---|
| Apartments.com | 0.637 | "NOT worth it. The elevators are always down, utilities are not included…" |
| Reddit — View vs Varsity | 0.697 | "…I am very happy with the view… If you can afford it it is worth it" |


---

## Example Responses

**1 — Grounded, balanced (subjective):**
> **Q: Is it worth it?**
> According to the context, opinions on whether University View is worth it are
> mixed. One reviewer on Apartments.com states it's "NOT worth it" due to issues
> with elevators, utilities, and fees. In contrast, a Reddit user (jms4607) says
> "If you can afford it, it is worth it" and is happy with their experience.
> Another suggests The Alloy as a cheaper alternative. Overall, it depends on
> individual priorities and budget.
> **Sources:** Apartments.com; Reddit r/UMD — View vs Varsity

**2 — Grounded, factual:**
> **Q: How close is it to campus?**
> University View is within a 12-minute walk (0.6 miles) of the University of
> Maryland campus. It's also near Montgomery College and Catholic University
> (16–17 min by car).
> **Sources:** ForRent; Apartments.com; Reddit r/UMD — View vs Varsity

**3 — Out-of-scope refusal (no fabrication):**
> **Q: What's the best pizza in New York City?**
> The sources don't cover that. There is no mention of New York City or pizza in
> the provided context. The context only discusses University View and its
> surrounding area in College Park, Maryland.

---

## Query Interface

A Gradio `ChatInterface` (`app.py`), launched with `python app.py` at
`http://localhost:7860`. The user types a question; the system retrieves
relevant chunks, generates a grounded answer, and displays it with its
`Sources:` list. The five evaluation questions are wired in as one-click
examples, and the corpus is auto-indexed on first launch.

**Sample interaction:**
```
You:  What are the downsides?
Bot:  According to the provided context from Yelp, one downside is that dealing
      with University View is described as a "NIGHTMARE" — they allegedly don't
      care about residents, viewing them as just a source of income.

      Sources:
      - Yelp — https://www.yelp.com/biz/university-view-college-park-2
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What are the monthly costs and fees? | Pricing varies by floor plan/term; 4bd/4ba Tower 1 ~$1,269; plus fees | Gave $125 parking fee, admin fee (reduced w/ guarantor), 12-installment lease; did **not** surface the base per-bedroom rents | Partially relevant | Partially accurate |
| 2 | Is it worth it? | Mixed; convenience praised, value/fees/service criticized | Balanced synthesis: Apartments.com "NOT worth it" vs Reddit "worth it if affordable" + Alloy alternative | Relevant | Accurate |
| 3 | How close is it to campus? | Very close; ~0.6 mi / short walk to UMD | "12-minute walk (0.6 mi)" + nearby colleges | Relevant | Accurate |
| 4 | What are the downsides? | Noise, fees, maintenance, inconsistent service | Only customer service ("NIGHTMARE") — missed fees/maintenance/noise | Partially relevant | Partially accurate |
| 5 | What's included? | Furnished units, utilities, amenities, contract details | Comprehensive list: laundry, free internet/cable, security, study rooms, shuttle, amenities | Relevant | Accurate |

**Retrieval quality:** Relevant
**Response accuracy:** Accurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "What are the downsides?" (partially accurate)

**What the system returned:** Only one downside — that customer service is a "NIGHTMARE" (from a single Yelp chunk). It missed the other well-documented
complaints in the corpus: the $125 parking fee and "random fees" (ForRent review), elevator outages and repeated maintenance failures (Kato), and the price/value criticism (Reddit).

**Root cause (tied to a specific pipeline stage):**This is *not* a missing data problem; the relevant chunks exist. Probing retrieval unfiltered shows the other downside chunks sit *just above* the 0.7 distance cutoff: the Reddit price complaint at 0.710, Kato's elevator/maintenance chunk at 0.753. The query
*"what are the downsides?"* is short and abstract, so it embeds relatively far from concrete complaint text. Only the single strongest match (Yelp, 0.688) passes the filter, and the LLM can only synthesize from what retrieval hands it.

**What you would change to fix it:** Three options, in order of preference:
1. Raise `MAX_DISTANCE` to ~0.77 — recovers the excluded complaint chunks while a
   cleanly off-topic query (e.g. "pizza in NYC") still returns nothing useful.
2. Add a "floor" so at least 3 chunks are always passed when *any* match exists,
   regardless of distance, letting the grounding prompt judge relevance.
3. Use MMR (max-marginal-relevance) retrieval to pull *diverse* complaint chunks
   rather than several near-duplicates of the same one.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

I think the mental exercise of figuring out what the intended inputs and outputs are and justifying the choices of specs gave a sense of clarity. This is because AI can make the lower-level decisions on how to build/code the chatbot, but the planning.md gave a helpful exercise on what to build. 

**One way your implementation diverged from the spec, and why:** This is *not* a missing data problem; the relevant chunks exist. Probing retrieval unfiltered shows the other downside chunks sit *just above* the 0.7 distance cutoff: the Reddit price complaint at 0.710, Kato's elevator/maintenance chunk at 0.753. The query *"what are the downsides?"* is short and abstract, so it embeds relatively far from concrete complaint text. Only the single strongest match (Yelp, 0.688) passes the filter, and the LLM can only synthesize from what retrieval hands it.



---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* Instructions to build boilerplate programs for converting websites into markdown either by webscraping or including the HTML file in a file directory. 
- *What it produced:* It gave me the boilerplate code and stated the instances in which it couldn't access through webscraping. 
- *What I changed or overrode:* I downloaded those websites at HTML files and then asked it to convert the websites again. 

**Instance 2**

- *What I gave the AI:* I suggested context-aware design over uniform sliding window, and my reasoning was that it would be more flexible in terms of allowing for reviews of different sizes. I asked the AI for feedback on my thought process. 
- *What it produced:* The AI acknowledged that that may be the case, but pointed out that using small chunks in uniform sliding window may be more effective in terms of avoiding clashing perspectives. 
- *What I changed or overrode:* I changed the splitting mechanism to uniform sliding window. 
