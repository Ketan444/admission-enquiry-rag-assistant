# Greenwood School ERP Admissions RAG Assistant & Android App

A production-grade, highly-scalable, and enterprise-ready Retrieval Augmented Generation (RAG) assistant integrated with a relational SQLite ERP database, a real-time FastAPI backend, a Streamlit parenting desk portal, and a native Jetpack Compose Android Application with persistent Room DB hybrid context retrieval.

---

## 🏫 Project Overview

- **Title**: Admission Enquiry Assistant for School ERP
- **Goal**: Build an AI chatbot using Gemini API and Retrieval Augmented Generation (RAG) that answers admission-related questions by retrieving information from multiple structured and unstructured sources simultaneously (SQLite, PDF, DOCX, TXT, CSV, JSON).

---

## 📐 Enterprise Architecture Diagram

```
                             +---------------------------+
                             |   Parent / User Clients   |
                             +-------------+-------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
       +------------+------------+                  +-------------+-------------+
       |   Streamlit Web Portal  |                  | Native Compose Android App |
       |    (Parenting Desk)     |                  | (with Offline Room DB-RAG) |
       +------------+------------+                  +-------------+-------------+
                    |                                             |
                    | (REST API JSON)                             | (Direct Gemini REST API
                    |                                             |  grounded with local DB)
                    v                                             v
       +------------+------------+                  +-------------+-------------+
       |  FastAPI Backend Engine |                  |  Google Gemini-3.5-Flash  |
       |  (Endpoints & Routing)  |                  |       Inference API       |
       +------------+------------+                  +---------------------------+
                    |
      +-------------+-------------+
      |                           |
      v                           v
+-----+-----+               +-----+-----+
| SQL DB    |               | Vector DB |
| (SQLite)  |               | (Chroma)  |
+-----------+               +-----------+
```

---

## 📁 Complete Folder Structure

```
/
├── backend/                  # FastAPI Web Backend
│   ├── api/                  # API router & controllers
│   │   ├── __init__.py
│   │   └── routes.py         # /chat, /upload, /index, /health, /feedback
│   ├── __init__.py
│   └── main.py               # Backend server entrypoint
├── config/                   # Central Settings Management
│   └── settings.py           # Pydantic configuration and env loader
├── database/                 # Relational Database Layer
│   └── sqlite_db.py          # SQLite relational schema, seeders, and wrappers
├── prompts/                  # LLM Prompt Templates
│   └── templates.py          # Grounded prompts & query rewriters
├── models/                   # Common Validation Models
│   └── pydantic_models.py    # Request and Response schemas
├── rag/                      # RAG Engineering Pipeline
│   └── pipeline.py           # Parser, text chunker, TF-IDF/embeddings engine
├── services/                 # External Integrations
│   └── gemini_service.py     # Gemini SDK client with streaming and fallback
├── utils/                    # Utility Packages
│   ├── exceptions.py         # Standardized exception classes
│   └── logger.py             # Highly readable color logs
├── frontend/                 # Streamlit UI
│   └── app.py                # Parenting desk frontend
├── sample_data/              # Seed Policy Sheets & CSV fee metrics
│   ├── admission_policy.txt
│   └── fee_structure.csv
├── tests/                    # Testing Suites
│   └── test_rag.py           # Pytest unit & pipeline integration tests
├── scripts/                  # Shell Scripts
│   └── start.sh              # Parallel docker startup execution script
├── app/                      # Native Android Application (Kotlin / Compose)
│   ├── build.gradle.kts      # Android compilation rules
│   └── src/main/java/com/example/
│       ├── data/             # Room DB Entities, DAOs, and Offline Seeding
│       ├── network/          # Retrofit interface for Google Gemini REST API
│       └── ui/               # Compose views & MVVM MainViewModel
├── Dockerfile                # Root docker configuration
└── docker-compose.yml        # Multi-service network orchestration config
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+ installed
- Android SDK / Studio (for native mobile compilation)
- Google Gemini API Key

### Backend Setup
1. Clone the workspace files.
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file based on `.env.example`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash
   SQLITE_DB_PATH=database/school_erp.db
   ```
5. Launch the backend:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup
1. Start Streamlit:
   ```bash
   streamlit run frontend/app.py
   ```
2. Navigate to `http://localhost:8501` to use the interactive parent admissions portal.

---

## 🐋 Dockerization & Deployment

To deploy in production using Docker:
```bash
docker-compose up --build
```
This boots:
1. **FastAPI Server** on `http://localhost:8000`
2. **Streamlit Parenting Portal** on `http://localhost:8501`

---

## 🚀 API Documentation

The FastAPI backend automatically hosts an interactive Swagger documentation portal at `http://localhost:8000/docs`.

### Key Endpoints

#### 1. `POST /api/v1/chat`
Ask admission questions. Integrates relational-vector hybrid RAG and returns citations.
- **Payload**:
  ```json
  {
    "session_id": "session_abc123",
    "question": "What are the school fees for Grade 5?",
    "history": []
  }
  ```
- **Response**:
  ```json
  {
    "answer": "Grade 5 tuition fee is $42,000 per term with an admission fee of $10,000...",
    "query_rewritten": "What are the school fees for Grade 5?",
    "confidence_score": 0.95,
    "citations": [
      {
        "source": "database",
        "chunk_text": "Grade: Grade 5 -> Tuition: 42000.0, Admission Fee: 10000.0",
        "score": 1.0
      }
    ]
  }
  ```

#### 2. `POST /api/v1/upload`
Upload custom brochures, policy sheets, or schedules (PDF, TXT, DOCX, CSV, Excel, JSON).

#### 3. `POST /api/v1/index`
Trigger RAG chunking and vector index updates for the uploaded file.

#### 4. `GET /api/v1/health`
Return systems wellness status and vector size.

---

## 🧪 Testing Guidelines

We have implemented unit and pipeline validation tests using Pytest. Run the suite locally:
```bash
pytest tests/
```

---

## 📸 Suggested Screenshots to Capture

When submitting your assessment, capture these visual screens:
1. **Swagger Playground**: Open `http://localhost:8000/docs` highlighting all eight structured routes.
2. **Interactive Streamlit UI (Light Mode)**: Run a fee enquiry detailing the dynamic confidence metrics and source chunk expansions.
3. **Streamlit UI (Dark Mode)**: Contrast dark layout styling showing the structured documents list.
4. **Android Compose Chat Desk**: Highlight parent-chatbot interaction flow in the Android emulator.
5. **Android Database Table View**: Show the local seeder tables (Fees, Route status).

---

## 🎯 Top 20 Master-Level AI & RAG Interview Questions & Answers

#### Q1. What is RAG and why is it preferred over fine-tuning for structured ERP data?
RAG (Retrieval-Augmented Generation) keeps information fresh by querying a live SQL database or vector store at runtime without expensive retraining. ERP systems contain dynamic values (e.g., seat availability, fee updates) which must be 100% accurate; fine-tuning would suffer from knowledge-cutoff lag and hallucination, which RAG prevents by grounding the prompt with hard context.

#### Q2. Explain the hybrid search architecture used in this system.
This system queries a relational SQL ERP database for structured facts (like accurate fees or schedule times) and simultaneously runs semantic similarity searching on vector repositories containing policy brochures. Combining structured SQL results with unstructured vector chunks guarantees absolute factual correctness while preserving conversational elasticity.

#### Q3. Why did we implement Query Rewriting in this pipeline?
User queries can be brief or colloquial (e.g., "how much for first grade?"). Query rewriting uses the LLM to expand the query to formal terms (e.g., "Grade 1 admission fees and tuition cost") before searching, resulting in significantly higher vector and database search hit rates.

#### Q4. How do you handle sliding context windows and chunk overlap in text splitters?
We chunk raw text with a specified window size (e.g., 500 characters) and a 15% overlap. The overlap ensures semantic transitions are not severed at boundaries, preserving context across adjacent chunks.

#### Q5. What is context ranking or reranking, and why is it important?
Reranking sorts retrieved context chunks using cross-encoder relevance scores rather than simple vector distances. It ensures that the most semantically pertinent text lies closest to the prompt window boundary, increasing generation quality.

#### Q6. How does our linter/liveness engine ensure offline fallback during API degradation?
The system checks `BuildConfig.GEMINI_API_KEY`. If empty, it degrades gracefully to a pre-defined simulation handler that parses queries and returns structured ERP answers from seeded tables, ensuring zero downtime.

#### Q7. Explain the SOLID principles as implemented in this codebase.
- **Single Responsibility Principle**: `SchoolERPDatabase` solely manages SQLite, while `VectorStoreEngine` handles embeddings.
- **Open-Closed Principle**: `DocumentParser` can be extended to support more formats without rewriting the core indexing pipeline.
- **Liskov Substitution Principle**: Retrieval fallbacks behave identically to index searches.
- **Interface Segregation**: Clean DAOs in Room enforce narrow data boundaries.
- **Dependency Inversion**: Settings/Configuration is loaded via Pydantic injectors.

#### Q8. How do you prevent SQL injection in an LLM-orchestrated ERP?
We never allow the LLM to directly formulate or run raw SQL commands. Instead, queries are sanitized, mapped to prepared query patterns via structured repository functions, and parameter-bound using SQLAlchemy or parameterized SQLite placeholders.

#### Q9. Why is the Gemini API key not stored in strings.xml?
Storing keys in plain strings inside an APK leaves them exposed to extraction via basic decompilers. In accordance with the AI Studio Secrets guidelines, we inject keys securely via `BuildConfig` compiled at build-time.

#### Q10. What is a Vector Database and how does it index semantic data?
Vector databases store dense text embeddings (high-dimensional floating-point arrays) and index them using techniques like HNSW (Hierarchical Navigable Small World) to enable sub-millisecond similarity lookups.

#### Q11. Explain how Room handles database migrations in Android.
Room uses defined migration schemas. If the database schema changes, Room executes designated SQL updates sequentially. For simple prototypes, we use `fallbackToDestructiveMigration` to recreate tables cleanly.

#### Q12. Why do we utilize Flow and Coroutines in Jetpack Compose?
Jetpack Compose is highly reactive. By exposing Room updates as a `Flow<List<T>>`, Compose automatically triggers safe recompositions only when the underlying database tables change.

#### Q13. How does the system calculate confidence matching scores?
Similarity searching returns scores based on vector distances (e.g., cosine similarity). We normalize these distances into a percentage-based confidence matching score.

#### Q14. What are the benefits of using FastAPI over standard Flask?
FastAPI leverages asynchronous asyncio loops, yields automatic Swagger generation via Pydantic schemas, and is significantly faster, matching Node.js performance levels.

#### Q15. Explain chunking strategies for CSV and Excel files.
CSVs represent structured tabular data. Standard paragraph chunkers split mid-row, destroying meaning. We chunk CSVs by converting each individual row into a readable text block with headers (e.g., "The fee for Grade 1 is...").

#### Q16. How does Docker compose handle service dependencies?
We use `depends_on` with `condition: service_healthy`. This ensures the Streamlit frontend container waits to boot until the FastAPI backend passes its designated API health checks.

#### Q17. Why is `enableEdgeToEdge()` critical in Material 3 Compose?
`enableEdgeToEdge()` allows the Compose Canvas to draw underneath the status bar and system navigation pills, creating a fluid, modern layout.

#### Q18. How do we ensure that interactive targets comply with accessibility standards?
Every button, list item, or text field has a minimum touch target size of `48dp x 48dp` (Material 3 minimum interactive component size) and meaningful content descriptions.

#### Q19. What is Moshi and why is it preferred over Gson?
Moshi is modern, designed from the ground up for Kotlin, supports Kotlin null-safety natively, and uses compile-time codegen via KSP instead of expensive reflection.

#### Q20. How would you scale this RAG pipeline to support millions of school queries?
We would migrate SQLite to PostgreSQL (using pgvector), implement Redis caching for recurrent queries, move Chroma to a standalone cloud cluster, and run FastAPI on a managed Kubernetes service.
