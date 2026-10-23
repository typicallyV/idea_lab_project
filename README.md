# LiveLegal AI ⚖️🤖

> **Intelligent, Grounded Legal Document Analysis & Conversational Intelligence Platform**  
> Built for the IDEA LAB project • Hosted at [typicallyV/idea_lab_project](https://github.com/typicallyV/idea_lab_project)

[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016%20(React%2019)-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/RAG%20Service-FastAPI%20(Python%203.11+)-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Express.js](https://img.shields.io/badge/API%20Gateway-Express.js%20(Node%2020)-000000?style=for-the-badge&logo=express)](https://expressjs.com/)
[![FAISS](https://img.shields.io/badge/Vector%20Store-FAISS-blue?style=for-the-badge)](https://github.com/facebookresearch/faiss)
[![Docker](https://img.shields.io/badge/Deploy-Docker%20%26%20Caddy%20v2-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?style=for-the-badge&logo=mongodb)](https://www.mongodb.com/)

---

## 📌 Executive Summary

**LiveLegal AI** is an enterprise-ready, document-grounded legal assistant and risk analysis platform powered by Retrieval-Augmented Generation (RAG). Designed to bridge the gap between complex legal jargon and rapid decision-making, LiveLegal AI empowers legal practitioners, enterprises, and individuals to dissect intricate contracts, non-disclosure agreements (NDAs), petitions, and regulatory filings in seconds.

Unlike generic chatbots prone to hallucinations, LiveLegal AI guarantees strictly grounded responses backed by exact clause citations, automated risk severity scoring (0–100), and on-demand professional PDF briefing reports.

---

## 🌟 Key Features

- 📑 **Dual-Format Document Ingestion & Parsing**
  - High-precision extraction for `.pdf` and `.docx` legal documents via PyMuPDF/PyPDF and python-docx.
  - Automatic structure normalization, headers/footers cleaning, and noise removal.

- 🔍 **Isolated Per-Document FAISS Vector Storage**
  - Each uploaded legal document maintains its own dedicated vector index, preventing cross-tenant document bleeding and maintaining surgical precision.
  - Sliding-window chunking (500 tokens with 50-token overlap) with normalized vector embeddings (HuggingFace `all-MiniLM-L6-v2` or OpenAI `text-embedding-3-small`).

- ⚖️ **Heuristic & LLM Legal Severity Scoring (0–100)**
  - Rule-based risk engine that flags indemnification clauses, uncapped liabilities, non-compete traps, jurisdiction vulnerabilities, and termination penalties.
  - Categorizes risk into Low (0–30), Moderate (31–70), and Critical (71–100) tiers.

- 💬 **Grounded Multi-Turn Legal Chat with Source Attributions**
  - Conversational AI powered by Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o / Google Gemini.
  - Every answer includes verbatim excerpts, chunk coordinates, and clause references from the original contract.

- 📄 **Executive PDF Briefing Report Generation**
  - Server-side PDF generation engine powered by PDFKit.
  - Automatically compiles key terms, obligations, identified risks, and AI recommendations into downloadable, presentation-ready legal memos.

- 🛡️ **Production-Hardened Security & Defenses**
  - **NoSQL Operator Injection Prevention**: Strict regex validation (`^[A-Za-z0-9_-]{1,64}$`) on all document identifiers at route and repository layers.
  - **Path Traversal Shield**: File operations guarded against directory traversal attempts (`../../etc/passwd`).
  - **Dual Authentication**: NextAuth session gateway with Google OAuth SSO + Express bcrypt JWT verification (12 rounds) with IP rate limiting.
  - **Zero Public Exposure for RAG**: Python microservice stays isolated inside an internal Docker bridge network without direct host port exposure.

- 🎓 **Viva Voce & Technical Defense Blueprint**
  - Comes bundled with an automated 2-pass ReportLab PDF generation blueprint (`generate_viva_guide.py`) producing the complete examination preparation manual (`LiveLegalAI_Viva_Preparation_Guide.pdf`).

---

## 🏗️ System Architecture

```
                                      [ HTTPS / Port 443 ]
                                                │
                                                ▼
                             ┌─────────────────────────────────────┐
                             │       Caddy Reverse Proxy (v2)      │
                             │   (Auto Let's Encrypt SSL / TLS)    │
                             └──────────┬───────────────┬──────────┘
                                        │               │
                 Route: /* (HTML / Next.js)             │ Route: /api/*, /health, /docs
                                        │               │
                                        ▼               ▼
                       ┌──────────────────────┐   ┌────────────────────────┐
                       │   Frontend (Next 16) │   │ Backend API (Express)  │
                       │   React 19 / Tailwind│   │ Auth, JWT, Mongo, S3   │
                       │   Port: 3000 (Docker)│   │ Port: 5000 (Docker)    │
                       └──────────┬───────────┘   └──────────┬─────────────┘
                                  │                          │
                                  └─────────► JSON ◄─────────┘
                                                │
                                                ▼ (Internal Docker Network only)
                                  ┌───────────────────────────┐
                                  │   Python RAG Microservice │
                                  │   FastAPI (Port: 8000)    │
                                  └─────────────┬─────────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    ▼                           ▼                           ▼
         ┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
         │ Isolated FAISS Store│     │ Document Ingestion  │     │ LLM Inference Engine│
         │ Per-doc .index files│     │ PyPDF / python-docx │     │ Claude / OpenAI /   │
         │ Local Vector Cache  │     │ Text Normalization  │     │ Gemini 3.1 Flash    │
         └─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

---

## 📁 Repository Structure

```tree
LiveLegalAI/
├── .env.example                       # Root configuration for Caddy & Docker Compose
├── .gitignore                         # Comprehensive ignore rules (Node, Python, OS)
├── Caddyfile                          # Production reverse-proxy rules & SSL automation
├── Decisions.md                       # Architectural Decision Records (ADRs) & security audit
├── docker-compose.yaml                # Orchestration for full 4-tier stack (Caddy + 3 apps)
├── generate_viva_guide.py             # ReportLab script generating academic defense guide
├── LiveLegalAI_Viva_Preparation_Guide.pdf # Project examination & viva preparation blueprint
├── README.md                          # Root project documentation
│
├── frontend/                          # Next.js 16 Web Application
│   ├── src/
│   │   ├── app/                       # App Router pages (auth, dashboard, analyze, chat)
│   │   ├── components/                # UI components (Radix, Lucide, Tailwind v4)
│   │   ├── features/                  # Domain-driven features (document viewer, chat, risk)
│   │   ├── hooks/                     # Custom React hooks
│   │   └── lib/                       # NextAuth config, API client, utils
│   ├── Dockerfile                     # Multi-stage optimized Node.js builder
│   ├── package.json
│   └── .env.example
│
└── backend/
    ├── docker-compose.yaml            # Backend-only Docker compose (Render / Cloud deploy)
    │
    ├── api_express/                   # Node.js Express REST API Gateway
    │   ├── config/                    # MongoDB, Cloudinary, Winston logger configs
    │   ├── controllers/               # Auth, Document, Chat, and User controllers
    │   ├── middleware/                # JWT verification, upload limits, error handler
    │   ├── models/                    # Mongoose schemas (User, Document, ChatHistory)
    │   ├── repositories/              # Scoped database access layer (NoSQL-safe)
    │   ├── routes/                    # API route definitions
    │   ├── services/                  # RAG proxy, PDFKit summary generator, Cloudinary
    │   ├── validators/                # Input validation schemas & regex guards
    │   ├── swagger.json               # OpenAPI 3.0 API specifications
    │   ├── Dockerfile
    │   ├── package.json
    │   └── .env.example
    │
    └── rag-api_python/                # FastAPI Retrieval-Augmented Generation Microservice
        ├── api/                       # Endpoint routers (/ingest, /analyze, /chat, /health)
        ├── core/                      # RAG pipeline implementation
        │   ├── rag_pipeline.py        # Pipeline orchestrator
        │   ├── document_parser.py     # PDF & DOCX text extraction
        │   ├── text_cleaner.py        # Noise elimination & formatting normalization
        │   ├── chunker.py             # Sliding-window text chunker
        │   ├── embeddings.py          # SentenceTransformers / OpenAI vector generator
        │   ├── vector_store.py        # Per-document FAISS index manager
        │   ├── retriever.py           # Cosine similarity context retrieval
        │   └── severity_scoring.py    # 0–100 legal risk & liability scoring engine
        ├── models/                    # Pydantic schemas with regex parameter validation
        ├── config.py                  # Service configuration & environment bounds
        ├── main.py                    # FastAPI application initialization
        ├── requirements.txt           # Python dependency manifest
        ├── Dockerfile
        └── .env.example
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | [Next.js 16](https://nextjs.org/) (App Router), [React 19](https://react.dev/), [TypeScript 5](https://www.typescriptlang.org/), [Tailwind CSS v4](https://tailwindcss.com/), [NextAuth.js](https://next-auth.js.org/), [Framer Motion](https://www.framer.com/motion/), [Sonner](https://sonner.emilkowal.ski/) |
| **API Gateway** | [Node.js 20](https://nodejs.org/), [Express.js 4](https://expressjs.com/), [Mongoose 9](https://mongoosejs.com/), [JWT](https://jwt.io/), [PDFKit](https://pdfkit.org/), [Winston](https://github.com/winstonjs/winston), [Helmet](https://helmetjs.github.io/) |
| **RAG Microservice** | [Python 3.11+](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Pydantic v2](https://docs.pydantic.dev/) |
| **AI / NLP & Vectors** | [Anthropic Claude 3.5 Sonnet](https://www.anthropic.com/), [OpenAI GPT-4o](https://openai.com/), [Google Gemini](https://ai.google.dev/), [SentenceTransformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`), [Meta FAISS](https://github.com/facebookresearch/faiss) |
| **Database & Storage** | [MongoDB Atlas](https://www.mongodb.com/atlas), [Cloudinary](https://cloudinary.com/) (Document storage) |
| **DevOps & Proxy** | [Docker](https://www.docker.com/), [Docker Compose v2](https://docs.docker.com/compose/), [Caddy v2](https://caddyserver.com/) (Automatic Let's Encrypt SSL/TLS) |

---

## 🚀 Quick Start & Installation

You can run LiveLegal AI either via **Docker Compose** (recommended for production and all-in-one testing) or by running each microservice independently in **Local Development Mode**.

### Option A: Running via Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/typicallyV/idea_lab_project.git
   cd idea_lab_project
   ```

2. **Configure Environment Files:**
   Copy the example environment files for each tier:
   ```bash
   # Root (Caddy & public URL)
   cp .env.example .env

   # Frontend
   cp frontend/.env.example frontend/.env.local

   # Express API
   cp backend/api_express/.env.example backend/api_express/.env

   # Python RAG Microservice
   cp backend/rag-api_python/.env.example backend/rag-api_python/.env
   ```

3. **Populate Key Environment Variables:**
   - In `backend/api_express/.env`: add your `MONGODB_URI`, `JWT_SECRET`, `CLOUDINARY_*` credentials.
   - In `backend/rag-api_python/.env`: add your `ANTHROPIC_API_KEY` (and optional `OPENAI_API_KEY` or `GEMINI_API_KEY`).
   - In `frontend/.env.local`: set `NEXTAUTH_SECRET` (`openssl rand -base64 32`) and optional Google OAuth credentials.

4. **Launch the Stack:**
   ```bash
   docker compose up -d --build
   ```
   - **Frontend UI**: `http://localhost:3000` (or your domain via Caddy)
   - **Express API Docs**: `http://localhost:5000/api-docs`
   - **Python RAG Docs**: `http://localhost:8000/docs`

---

### Option B: Local Development Mode (3 Independent Terminals)

#### 1. Python RAG Microservice
```bash
cd backend/rag-api_python

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Set ANTHROPIC_API_KEY and MASTER_BACKEND_URL=http://localhost:5000 in .env

# Run server
python main.py
# Running on http://localhost:8000
```

#### 2. Express.js API Gateway
```bash
cd backend/api_express

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Configure MONGODB_URI, JWT_SECRET, RAG_SERVICE_URL=http://localhost:8000

# Start development server
npm run dev
# Running on http://localhost:5000
```

#### 3. Next.js Frontend
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Set NEXT_PUBLIC_BACKEND_URL=http://localhost:5000 and NEXTAUTH_URL=http://localhost:3000

# Launch Next.js dev server
npm run dev
# Running on http://localhost:3000
```

---

## 📡 API Reference

### Express API Gateway (`/api/*`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Email/password login with JWT token issuance | No |
| `POST` | `/api/auth/google` | Google OAuth token verification & session creation | No |
| `GET` | `/api/auth/me` | Fetch active user credentials and preferences | Yes (Bearer JWT) |
| `POST` | `/api/document/upload` | Multipart upload of legal document (PDF/DOCX) | Yes |
| `GET` | `/api/document/history` | List user's analyzed legal documents | Yes |
| `GET` | `/api/document/:id` | Retrieve metadata, severity score & summary | Yes |
| `GET` | `/api/document/:id/report` | Download generated PDF briefing memo | Yes |
| `POST` | `/api/chat/analyze` | Request comprehensive clause risk analysis | Yes |
| `POST` | `/api/chat/chat` | Conversational Q&A grounded in document chunks | Yes |
| `GET` | `/api/chat/history` | Retrieve chat message history for document | Yes |
| `GET` | `/health` | System liveness probe & dependency status | No |

### Python RAG Service (`http://localhost:8000`)

| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| `POST` | `/ingest` | Parses document, creates embeddings & saves FAISS index | `multipart/form-data` |
| `POST` | `/analyze` | Generates overall summary, clauses & 0–100 severity score | `{"document_id": "..."}` |
| `POST` | `/chat` | Contextual semantic retrieval + LLM synthesis | `{"document_id": "...", "question": "..."}` |
| `GET` | `/health` | Strict readiness check (writable storage + LLM keys) | None |

---

## 🔒 Security Architecture Highlights

As documented in [Decisions.md](./Decisions.md):
1. **Zero-Trust Network Perimeter**: In production Docker deployments, the Python RAG microservice is strictly non-routable from the public internet. Only the internal Express backend can invoke it.
2. **NoSQL Injection Defenses**: All incoming `document_id` parameters are validated against strict alphanumeric regex patterns (`^[A-Za-z0-9_-]{1,64}$`), neutralizing Mongo operator injection (`{"$ne": null}`).
3. **Path Traversal Guards**: Filenames and document identifiers are sanitized before any filesystem interaction in both Node.js and Python.
4. **Header Injection Hardening**: `Content-Disposition` download headers sanitize client file names to prevent quote-breakout vulnerabilities.

---

## 🎓 Academic Defense & Viva Voce Blueprint

This repository includes a dedicated viva examination and presentation preparation guide:
- 📜 **`generate_viva_guide.py`**: A standalone Python script utilizing ReportLab to generate a publication-quality examination blueprint with custom page canvas numbering, risk flowcharts, architecture tables, and expected defense questions.
- 📘 **`LiveLegalAI_Viva_Preparation_Guide.pdf`**: The compiled, comprehensive viva preparation guide ready for academic defense and committee evaluation.

To recompile the PDF guide:
```bash
pip install reportlab
python generate_viva_guide.py
```

---

## 🤝 Contributing & License

Developed with passion for **IDEA LAB**. Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/LegalInnovation`)
3. Commit your Changes (`git commit -m 'feat: Add legal clause comparator'`)
4. Push to the Branch (`git push origin feature/LegalInnovation`)
5. Open a Pull Request

---

*Repository maintained at [typicallyV/idea_lab_project](https://github.com/typicallyV/idea_lab_project)*