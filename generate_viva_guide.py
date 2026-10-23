import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw total page count
    along with running header and footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        w, h = A4

        # Running Header (pages 2 to end)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(HexColor("#0F172A"))
            self.drawString(36, h - 28, "LIVELEGALAI — VIVA VOCE EXAMINATION PREPARATION BLUEPRINT")
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(HexColor("#2563EB"))
            self.drawRightString(w - 36, h - 28, "PROJECT VIVA & DEFENSE GUIDE")
            self.setStrokeColor(HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, h - 33, w - 36, h - 33)

        # Running Footer (all pages)
        self.setStrokeColor(HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 32, w - 36, 32)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(HexColor("#64748B"))
        self.drawString(36, 22, "LiveLegalAI • Full-Stack Legal Document Intelligence • Express.js + FastAPI + FAISS")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(w - 36, 22, page_str)

        self.restoreState()


def build_pdf(filename="LiveLegalAI_Viva_Preparation_Guide.pdf"):
    # Margins: 36 pt (0.5 in) left/right, 38 pt top/bottom
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38,
    )

    styles = getSampleStyleSheet()

    # Color Palette
    PRIMARY = HexColor("#0F172A")    # Deep Navy
    SECONDARY = HexColor("#1E3A8A")  # Deep Blue
    ACCENT_BLUE = HexColor("#2563EB")# Brand Blue
    ACCENT_CYAN = HexColor("#0284C7")# Cyan Blue
    DARK_TEXT = HexColor("#1E293B")  # Slate 800
    MUTED_TEXT = HexColor("#475569") # Slate 600
    LIGHT_BG = HexColor("#F8FAFC")   # Slate 50
    CARD_BG = HexColor("#F1F5F9")    # Slate 100
    ALERT_BG = HexColor("#FEF2F2")   # Red 50
    ALERT_BORDER = HexColor("#EF4444")# Red 500
    SUCCESS_BG = HexColor("#F0FDF4") # Green 50
    SUCCESS_BORDER = HexColor("#22C55E") # Green 500
    TAG_BG = HexColor("#EFF6FF")     # Blue 50
    BORDER_COLOR = HexColor("#CBD5E1") # Slate 300

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=PRIMARY,
        spaceAfter=3,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=MUTED_TEXT,
        spaceAfter=8,
    )
    page_header_style = ParagraphStyle(
        "PageHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=4,
    )
    page_sub_style = ParagraphStyle(
        "PageSubHeader",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=MUTED_TEXT,
        spaceAfter=8,
    )
    sec_title_style = ParagraphStyle(
        "SecTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=ACCENT_BLUE,
        spaceAfter=3,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=DARK_TEXT,
        spaceAfter=4,
    )
    body_bold = ParagraphStyle(
        "BodyDarkBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=DARK_TEXT,
        spaceAfter=4,
    )
    q_style = ParagraphStyle(
        "QuestionStyle",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=PRIMARY,
        spaceAfter=2,
    )
    ans_style = ParagraphStyle(
        "AnswerStyle",
        fontName="Helvetica",
        fontSize=8,
        leading=10.8,
        textColor=DARK_TEXT,
        spaceAfter=4,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=DARK_TEXT,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=PRIMARY,
    )
    table_cell_header = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=HexColor("#FFFFFF"),
    )
    callout_text = ParagraphStyle(
        "CalloutText",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        textColor=DARK_TEXT,
    )

    story = []

    # Helper function for card containers
    def make_card(flowables, bg_color=LIGHT_BG, border_color=BORDER_COLOR, padding=6):
        tbl = Table([[flowables]], colWidths=[523.27])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_color),
            ("BOX", (0, 0), (-1, -1), 0.75, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), padding),
            ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
            ("LEFTPADDING", (0, 0), (-1, -1), padding + 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), padding + 2),
        ]))
        return tbl

    def make_qa_box(q_text, a_text, tag="EXAMINER QUESTION"):
        content = [
            Paragraph(f"<b><font color='#2563EB'>[{tag}]</font> {q_text}</b>", q_style),
            Paragraph(f"<b>Model Answer:</b> {a_text}", ans_style)
        ]
        tbl = Table([[content]], colWidths=[523.27])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.6, HexColor("#CBD5E1")),
            ("LINELEFT", (0, 0), (-1, -1), 2.5, ACCENT_BLUE),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return tbl

    # =========================================================================
    # PAGE 1: PROJECT OVERVIEW & BASIC TOPICS
    # =========================================================================
    # Title Block
    title_table = Table([
        [
            Paragraph("<b>LiveLegalAI — Project Viva Voce Preparation Guide</b>", title_style),
            Paragraph("<font color='#2563EB'><b>FINAL DEFENSE</b></font><br/><font color='#64748B'>Comprehensive Prep</font>", ParagraphStyle("RightHdr", fontName="Helvetica", fontSize=8, leading=10, alignment=2))
        ]
    ], colWidths=[400, 123.27])
    title_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(title_table)
    story.append(Paragraph("System Architecture, RAG Microservices, Vector Search, Security Audits & Examiner Question Bank", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceBefore=0, spaceAfter=6))

    # Meta badges table
    meta_data = [
        [
            Paragraph("<b>Architecture:</b> Multi-Service Microservices", table_cell),
            Paragraph("<b>AI Paradigm:</b> Retrieval-Augmented Generation (RAG)", table_cell),
            Paragraph("<b>Deployment:</b> Docker Compose + Caddy TLS", table_cell),
        ]
    ]
    meta_tbl = Table(meta_data, colWidths=[174, 185, 164.27])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TAG_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#BFDBFE")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6))

    # 1. Project Overview & Problem Statement
    story.append(Paragraph("1. Executive Summary & Problem-Solution Fit", sec_title_style))
    overview_p = (
        "<b>Problem:</b> Legal notices, summons, tenancy disputes, and cease-and-desist letters use complex, archaic legalese "
        "that induces anxiety and delays timely response. Consulting an attorney for basic comprehension is expensive and slow.<br/>"
        "<b>Solution:</b> <b>LiveLegalAI</b> is an end-to-end, document-grounded legal intelligence platform. Users upload PDF/DOCX "
        "contracts or notices, and the system delivers: (1) an explainable <b>0–100 Severity Score</b>, (2) an objective <b>plain-English summary</b>, "
        "(3) breakdown of <b>legal rights & obligations</b>, (4) a <b>custom suggested reply draft</b>, and (5) an interactive <b>grounded chat interface</b> "
        "with dynamic PDF export."
    )
    story.append(Paragraph(overview_p, body_style))
    story.append(Spacer(1, 4))

    # 2. Tech Stack Matrix Table
    story.append(Paragraph("2. Full Technology Stack & Architectural Roles", sec_title_style))
    stack_data = [
        [Paragraph("Tier / Layer", table_cell_header), Paragraph("Technologies Used", table_cell_header), Paragraph("Key Responsibility in LiveLegalAI", table_cell_header)],
        [Paragraph("<b>Frontend UI</b>", table_cell), Paragraph("Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, NextAuth", table_cell), Paragraph("Client portal, interactive analysis dashboard, risk gauge chart, grounded chat UI, PDF download.", table_cell)],
        [Paragraph("<b>API Gateway & Auth</b>", table_cell), Paragraph("Node.js, Express.js, MongoDB Atlas (Mongoose), JWT, Cloudinary, PDFKit", table_cell), Paragraph("Stateless JWT auth, Google OAuth ID token verification, file upload handling, async polling, PDF generation.", table_cell)],
        [Paragraph("<b>RAG Microservice</b>", table_cell), Paragraph("Python 3.11, FastAPI, FAISS, PyTorch, SentenceTransformers, Anthropic / Gemini", table_cell), Paragraph("Text extraction (pdfplumber/docx), chunking, 384-d vector embeddings, FAISS search, multi-LLM router.", table_cell)],
        [Paragraph("<b>Infrastructure</b>", table_cell), Paragraph("Docker Compose, Caddy 2 Reverse Proxy, Linux Bridge Network", table_cell), Paragraph("Single internal Docker network, automated Let's Encrypt SSL/TLS, port 80/443 mapping, service isolation.", table_cell)],
    ]
    stack_tbl = Table(stack_data, colWidths=[90, 190, 243.27])
    stack_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(stack_tbl)
    story.append(Spacer(1, 4))

    # 3. End-to-End Workflow & Data Lifecycle
    story.append(Paragraph("3. End-to-End Data Lifecycle (Upload to Insights)", sec_title_style))
    workflow_p = (
        "<b>Step 1: Upload & 202 Accepted:</b> Frontend POSTs file to Express. Express saves document record with status <i>'processing'</i> (progress: 5%), responds with HTTP 202, and kicks off asynchronous background processing.<br/>"
        "<b>Step 2: Parsing & Ingestion:</b> Express streams buffer to Python FastAPI <code>/ingest</code>. <code>pdfplumber</code> extracts text; text is cleaned and split into 500-char chunks (50-char overlap).<br/>"
        "<b>Step 3: Vector Indexing:</b> Chunks are embedded using local <code>all-MiniLM-L6-v2</code> into 384-d vectors, L2-normalized, and indexed in FAISS (<code>{document_id}.index</code>) on disk.<br/>"
        "<b>Step 4: Cloud Backup & LLM Analysis:</b> Express uploads file to Cloudinary CDN, calls FastAPI <code>/analyze</code>. The RAG engine computes the rule-based severity score, retrieves Top-5 relevant chunks, and prompts Claude/Gemini.<br/>"
        "<b>Step 5: Polling & Display:</b> Frontend polls <code>GET /api/documents/status/:documentId</code> every 1.5s until 100% completion, rendering the analysis, suggested reply, and risk graph."
    )
    story.append(Paragraph(workflow_p, body_style))
    story.append(Spacer(1, 4))

    # 4. Basic Viva Questions
    story.append(Paragraph("4. Essential Basic Viva Questions & Answers", sec_title_style))
    story.append(make_qa_box(
        "What is Retrieval-Augmented Generation (RAG) and why is it necessary in LiveLegalAI?",
        "Standard LLMs suffer from knowledge cutoff dates and hallucinate facts when asked about unseen private legal contracts. RAG solves this by decoupling knowledge storage from language reasoning. LiveLegalAI retrieves the exact, verified text passages from the user's specific document and injects them into the LLM prompt as ground truth context, ensuring 100% factual, document-grounded legal analysis.",
        "BASIC VIVA Q1"
    ))
    story.append(Spacer(1, 3))
    story.append(make_qa_box(
        "Why use a multi-service architecture (Express + FastAPI) instead of a single monolith?",
        "Separation of concerns and ecosystem specialization: Python is the undisputed leader for AI/ML pipelines (FAISS, PyTorch, SentenceTransformers), while Node.js/Express provides high-throughput, non-blocking asynchronous I/O ideal for web routing, JWT sessions, and file uploads. Isolating heavy vector operations in FastAPI prevents ML compute spikes from stalling user web requests.",
        "BASIC VIVA Q2"
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: DEEP TOPIC 1 — RAG PIPELINE, EMBEDDINGS & VECTOR SEARCH
    # =========================================================================
    story.append(Paragraph("DEEP DIVE 1: RAG Architecture, Chunking, Vector Embeddings & FAISS", page_header_style))
    story.append(Paragraph("In-depth breakdown of text ingestion, sliding-window chunking, vector spaces, indexing, and explainable risk scoring.", page_sub_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT_BLUE, spaceBefore=0, spaceAfter=5))

    # Deep Technical Breakdown
    story.append(Paragraph("1. Text Extraction & Preprocessing Pipeline", sec_title_style))
    parse_p = (
        "• <b>Parser Selection:</b> <code>document_parser.py</code> uses <code>pdfplumber</code> for PDF extraction (iterates over pages with bounding box text extraction) and <code>python-docx</code> for Microsoft Word files.<br/>"
        "• <b>Noise Cleaning:</b> <code>text_cleaner.py</code> normalizes CRLF to LF, removes unprintable ASCII control characters (<code>[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F]</code>), strips repeated whitespace, and eliminates redundant line headers while strictly preserving punctuation and paragraph breaks essential for legal syntax interpretation.<br/>"
        "• <b>Zero-Text Handling:</b> Image-only scanned PDFs yield 0 bytes of text. The pipeline detects this early and raises a descriptive <code>ValueError</code> (HTTP 400), avoiding downstream model failures or wasted embedding computation."
    )
    story.append(Paragraph(parse_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("2. Sliding-Window Text Chunking Strategy", sec_title_style))
    chunk_p = (
        "• <b>Parameters:</b> <code>CHUNK_SIZE = 500</code> characters, <code>CHUNK_OVERLAP = 50</code> characters (Cursor step: 450 characters).<br/>"
        "• <b>Why Chunking is Mandatory:</b> (1) Transformer models have strict context limits (MiniLM is capped at 512 tokens). (2) Embedding an entire 30-page document into a single vector compresses and dilutes fine-grained legal clauses. Paragraph-sized chunks maximize semantic retrieval fidelity.<br/>"
        "• <b>Overlap Rationale:</b> Legal provisions frequently span sentence boundaries (e.g., <i>'Provided however that the licensee shall...'</i>). A 50-character overlap prevents contextual severance between adjacent chunks."
    )
    story.append(Paragraph(chunk_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("3. Dense Embeddings & Vector Space Geometry", sec_title_style))
    embed_p = (
        "• <b>Default Model:</b> <code>sentence-transformers/all-MiniLM-L6-v2</code> running locally on CPU. Compact (~90 MB), fast, and outputs <b>384-dimensional dense vectors</b>. No external API key or cost required.<br/>"
        "• <b>Secondary Backend:</b> OpenAI <code>text-embedding-3-small</code> (1536 dimensions), toggleable via <code>USE_OPENAI_EMBEDDINGS=true</code>.<br/>"
        "• <b>L2 Normalization Formula:</b> Every chunk vector <i>v</i> is normalized: <b><i>v<sub>norm</sub> = v / ||v||<sub>2</sub></i></b>. Once normalized, the Inner Product (Dot Product) is mathematically identical to <b>Cosine Similarity</b>: "
        "<b><i>CosineSim(u, v) = (u · v) / (||u|| ||v||) = u<sub>norm</sub> · v<sub>norm</sub></i></b>."
    )
    story.append(Paragraph(embed_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("4. FAISS Vector Store: Per-Document vs Global Index", sec_title_style))
    faiss_p = (
        "• <b>Architecture:</b> <code>IndexFlatIP</code> (Inner Product on L2-normalized vectors). Brute-force exact search ensures 100% recall without quantization artifacts.<br/>"
        "• <b>Per-Document Indexing Strategy:</b> Instead of one massive global index with metadata filtering, LiveLegalAI creates isolated index pairs on disk: <code>{document_id}.index</code> (FAISS binary) and <code>{document_id}_chunks.json</code> (text chunk mapping).<br/>"
        "• <b>3 Major Advantages:</b> (1) <i>Absolute Tenant Isolation:</i> Document A queries can never retrieve Document B chunks. (2) <i>Instant Deletion:</i> Deleting a document is an O(1) filesystem delete, avoiding expensive FAISS index rebuilding. (3) <i>Low RAM Usage:</i> Indexes are loaded on-demand."
    )
    story.append(Paragraph(faiss_p, body_style))
    story.append(Spacer(1, 3))

    # Severity Scoring Rules Table
    story.append(Paragraph("5. Explainable Legal Risk Scoring Engine (Rule-Based)", sec_title_style))
    rules_data = [
        [Paragraph("Category", table_cell_header), Paragraph("Point Value", table_cell_header), Paragraph("Regex Trigger Pattern", table_cell_header), Paragraph("Legal Risk Rationale", table_cell_header)],
        [Paragraph("<b>Litigation / Lawsuit</b>", table_cell), Paragraph("<b>+40 pts</b>", table_cell), Paragraph("r'\\b(lawsuit|litigation|sue|court|plaintiff|summons|subpoena)\\b'", table_cell), Paragraph("Active legal dispute; imminent court appearance or civil action.", table_cell)],
        [Paragraph("<b>Deadline / Expiration</b>", table_cell), Paragraph("<b>+20 pts</b>", table_cell), Paragraph("r'\\b(deadline|due date|within \\d+ days|respond within|expire)\\b'", table_cell), Paragraph("Time-sensitive obligation; forfeiture of rights upon missed date.", table_cell)],
        [Paragraph("<b>Monetary Demand</b>", table_cell), Paragraph("<b>+15 pts</b>", table_cell), Paragraph("r'(\\$[\\d,]+|\\b\\d[\\d,]*\\s*(dollars|USD|damages|penalty|fine))'", table_cell), Paragraph("Financial claims, damages, or statutory monetary penalties.", table_cell)],
        [Paragraph("<b>Copyright / IP Strike</b>", table_cell), Paragraph("<b>+10 pts</b>", table_cell), Paragraph("r'\\b(copyright|DMCA|trademark|infringement|cease and desist)\\b'", table_cell), Paragraph("Intellectual property violation claim requiring immediate takedown.", table_cell)],
        [Paragraph("<b>Formal Warning</b>", table_cell), Paragraph("<b>+5 pts</b>", table_cell), Paragraph("r'\\b(warning|notice|notify|hereby informed|be advised)\\b'", table_cell), Paragraph("Official legal advisement putting the recipient on formal notice.", table_cell)],
    ]
    rules_tbl = Table(rules_data, colWidths=[95, 55, 175, 198.27])
    rules_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(rules_tbl)
    story.append(Paragraph("<font size='7' color='#475569'><i>*Total score is additive and capped at 100. Labels: 0–30 (Low), 31–70 (Moderate), 71–100 (High). Deterministic, transparent, and auditable.</i></font>", body_style))
    story.append(Spacer(1, 3))

    # Deep Viva Questions for Page 2
    story.append(Paragraph("6. Deep Viva Questions & Model Answers", sec_title_style))
    story.append(make_qa_box(
        "Why use IndexFlatIP over IndexFlatL2 in FAISS? Doesn't FlatL2 calculate Euclidean distance?",
        "FlatL2 measures straight-line Euclidean distance, which is sensitive to vector length. In NLP embeddings, semantic meaning is captured by the direction/angle of the vector, not its magnitude. By applying faiss.normalize_L2 to both chunk and query embeddings, all vectors lie on a unit hypersphere. On unit vectors, Inner Product (FlatIP) is mathematically identical to Cosine Similarity (u · v = cos θ), ranking chunks purely by semantic alignment.",
        "DEEP VIVA Q1"
    ))
    story.append(Spacer(1, 3))
    story.append(make_qa_box(
        "Why did you use a rule-based severity scorer instead of letting Claude or GPT calculate the score?",
        "LLMs are non-deterministic: the same legal notice prompted twice might score 65 then 85 due to sampling temperature. In legal compliance, scores must be completely deterministic, explainable, and auditable. A rule-based regex engine guarantees that the presence of 'subpoena' (+40) and 'within 10 days' (+20) always yields 60 points, allowing judges or users to trace exact causal triggers.",
        "DEEP VIVA Q2"
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: DEEP TOPIC 2 — BACKEND ARCHITECTURE & LLM FALLBACK ROUTING
    # =========================================================================
    story.append(Paragraph("DEEP DIVE 2: Backend Async Architecture, Dual Auth & LLM Fallback Routing", page_header_style))
    story.append(Paragraph("Detailed analysis of non-blocking polling, dual JWT/OAuth authentication, tri-tier LLM failover, and health monitoring.", page_sub_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT_BLUE, spaceBefore=0, spaceAfter=5))

    story.append(Paragraph("1. Asynchronous Ingestion & Non-Blocking State Machine", sec_title_style))
    async_p = (
        "• <b>The Scalability Bottleneck:</b> Ingesting a large PDF (text extraction, chunking, 384-d embedding, FAISS indexing, Cloudinary upload, and LLM analysis) takes 5–25 seconds. Blocking the HTTP connection causes client timeouts and starves the Node.js event loop.<br/>"
        "• <b>The HTTP 202 Async Solution:</b> Express immediately generates a unique <code>documentId</code> (<code>doc_&lt;uuid12&gt;</code>), writes a record to MongoDB with <code>status: 'processing'</code>, and returns <b>HTTP 202 Accepted</b> in &lt;100ms.<br/>"
        "• <b>Background Pipeline State Progression:</b> The asynchronous worker executes five discrete stages, updating MongoDB progress: "
        "<b>5%</b> (Upload initialized) → <b>20%</b> (Text parsed & cleaned) → <b>45%</b> (Cloudinary CDN upload) → <b>70%</b> (FAISS indexed & LLM analyzing) → <b>100%</b> (Completed).<br/>"
        "• <b>Client Polling Architecture:</b> The frontend polls <code>GET /api/documents/status/:documentId</code> every 1,500ms. If processing fails, it updates to <code>status: 'failed'</code> with error details, ensuring robust UX."
    )
    story.append(Paragraph(async_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("2. Dual-Layer Authentication Flow (NextAuth + Express JWT)", sec_title_style))
    auth_p = (
        "• <b>Stateless JWT Architecture:</b> The Express backend issues signed HMAC-SHA256 tokens (<code>jsonwebtoken</code>) containing the user payload (<code>sub: user._id</code>) upon register/login.<br/>"
        "• <b>Google OAuth Audience Verification:</b> NextAuth on the frontend initiates Google Sign-In and passes the Google <code>idToken</code> to Express <code>POST /api/auth/google</code>. Express uses <code>google-auth-library</code> to verify the token signature against Google's public certificates and strictly enforces <code>audience: GOOGLE_CLIENT_ID</code>. This prevents cross-client token replay attacks.<br/>"
        "• <b>Session Wrapping:</b> NextAuth never uses Google tokens for API calls; it wraps the Express-issued JWT inside its session cookie. Every protected backend route executes <code>requireAuth</code> middleware, extracting and validating <code>Authorization: Bearer &lt;token&gt;</code>.<br/>"
        "• <b>Password Security:</b> Local credentials are cryptographically hashed using <code>bcryptjs</code> with <b>12 salt rounds</b>."
    )
    story.append(Paragraph(auth_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("3. Tri-Tier LLM Fallback Routing Architecture", sec_title_style))
    llm_p = (
        "In production legal applications, an LLM API outage (500) or rate-limit spike (429) must never crash the service. "
        "<code>core/llm_provider.py</code> implements a unified sequential fallback router:<br/>"
        "<b>1. Primary Tier: Claude 3.5 Sonnet (Anthropic):</b> Configured at <code>temperature=0.3</code> with 1500 max tokens. Chosen for industry-leading nuanced reasoning and legal extraction capabilities.<br/>"
        "<b>2. Secondary Fallback: OpenAI GPT-4o-mini:</b> Activated immediately if Anthropic returns connection timeouts, quota exhaustion, or 5xx server errors.<br/>"
        "<b>3. Final Fallback: Google Gemini 2.0 Flash:</b> High-speed fallback via <code>google-generativeai</code> SDK. <i>Critical Design Nuance:</i> Safety settings for Harassment, Hate Speech, and Dangerous Content are explicitly set to <code>BLOCK_NONE</code>. "
        "Legal dispute letters contain aggressive litigation threats, repossession notices, and eviction demands; default AI safety filters would falsely flag and block legitimate legal analysis!"
    )
    story.append(Paragraph(llm_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("4. Architectural Asymmetry in Health Checks", sec_title_style))
    health_p = (
        "• <b>Express <code>GET /health</code> is a LIVENESS Check:</b> Returns HTTP 200 as long as the Express process responds. MongoDB connectivity and RAG reachability are reported in JSON as <code>status: 'ok' | 'degraded'</code>. Express intentionally does NOT crash on MongoDB disconnection so that RAG proxy routes stay functional during transient database glitches.<br/>"
        "• <b>FastAPI <code>GET /health</code> is a READINESS Check:</b> Returns <b>HTTP 503</b> if FAISS directories are not writable or if no LLM provider API key is loaded. Because RAG cannot perform any meaningful operation without storage and an LLM, blocking startup order in Docker Compose (<code>condition: service_healthy</code>) is correct."
    )
    story.append(Paragraph(health_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("5. Dynamic On-the-Fly PDF Report Streaming", sec_title_style))
    pdf_p = (
        "When the user downloads a report, Express <code>documentController.js</code> uses <code>PDFDocument</code> (PDFKit) to construct the document dynamically in memory (Times-Roman typography, structured risk sections, legal advice disclaimer) and pipes it directly to the HTTP response stream (<code>pdf.pipe(res)</code>). No temporary PDF files are stored on server disk."
    )
    story.append(Paragraph(pdf_p, body_style))
    story.append(Spacer(1, 3))

    # Deep Viva Questions for Page 3
    story.append(Paragraph("6. Deep Viva Questions & Model Answers", sec_title_style))
    story.append(make_qa_box(
        "Why wrap the Express JWT inside NextAuth rather than making API calls with the Google OAuth token?",
        "Decoupling and zero third-party lock-in: If the backend validated Google tokens on every route, it would incur network overhead contacting Google's token verification endpoints and fail for email/password users. By verifying the Google ID token once during login and issuing an internal Express JWT, all backend routes use a single, unified Authorization header format regardless of how the user authenticated.",
        "DEEP VIVA Q3"
    ))
    story.append(Spacer(1, 3))
    story.append(make_qa_box(
        "How do you handle LLM prompt context length when a user chats with a 100-page document?",
        "We never feed the full document into the LLM! In the chat pipeline (POST /chat), retriever.py converts the user's question into an embedding, searches the FAISS index, and retrieves only the Top-K (K=5) chunks (~2,500 characters / ~600 tokens). Only these 5 chunks are injected into the prompt. The LLM context window is strictly bounded, ensuring sub-second inference and low token cost.",
        "DEEP VIVA Q4"
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: DEEP TOPIC 3 — SECURITY AUDIT, VULNERABILITIES & HARDENING
    # =========================================================================
    story.append(Paragraph("DEEP DIVE 3: Security Audit, Threat Vectors & Production Hardening", page_header_style))
    story.append(Paragraph("A rigorous technical audit of vulnerabilities discovered, exploit mechanics, and applied defense-in-depth mitigations.", page_sub_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT_BLUE, spaceBefore=0, spaceAfter=5))

    story.append(Paragraph("1. Critical Vulnerability 1: NoSQL Operator Injection (Cross-Tenant Data Breach)", sec_title_style))
    sec1_p = (
        "• <b>The Flaw:</b> Endpoints <code>POST /api/chat/analyze</code> and <code>/chat</code> previously read <code>document_id</code> directly from <code>req.body</code> without schema or type validation.<br/>"
        "• <b>The Exploit:</b> An attacker submits a malicious JSON body: <code>{\"document_id\": {\"$ne\": null}, \"question\": \"Summarize\"}</code>. Mongoose accepts the query object literally: <code>Document.findOne({ documentId: { $ne: null } })</code>.<br/>"
        "• <b>The Breach Path:</b> The repository helper <code>findDocumentByDocumentId</code> (used for cache re-indexing) intentionally had no <code>userId</code> scope. The query matched the first document in MongoDB belonging to <b>any arbitrary tenant</b>, downloading and exposing private confidential legal notices server-side!<br/>"
        "• <b>The Mitigation:</b> (1) Applied <code>DOCUMENT_ID_PATTERN = /^[A-Za-z0-9_-]{1,64}$/</code> in <code>chatValidator.js</code>, rejecting non-string types and Mongo operators before hitting the controller. (2) Added defense-in-depth checks in <code>documentRepository.js</code> that throw an explicit error if <code>documentId</code> is not a non-empty string."
    )
    story.append(Paragraph(sec1_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("2. Critical Vulnerability 2: Directory Path Traversal in FAISS Store", sec_title_style))
    sec2_p = (
        "• <b>The Flaw:</b> In FastAPI, <code>document_id</code> was concatenated unsanitized via <code>os.path.join(UPLOAD_DIR, f'{document_id}.pdf')</code> and <code>os.path.join(FAISS_INDEX_DIR, f'{document_id}.index')</code>. While Pydantic enforces <code>str</code>, it does not block directory traversal sequences.<br/>"
        "• <b>The Exploit:</b> Submitting <code>document_id = '../../etc/passwd'</code> or traversal payloads allowed an attacker to overwrite host system files or manipulate FAISS storage on disk.<br/>"
        "• <b>The Mitigation:</b> (1) Implemented regex validation <code>validate_document_id()</code> enforcing <code>^[A-Za-z0-9_-]{1,64}$</code> in <code>file_utils.py</code>. (2) Added regex constraints directly to Pydantic models: <code>Field(..., pattern=r'^[A-Za-z0-9_-]{1,64}$')</code>. (3) Added runtime validation right at the filesystem boundary in <code>vector_store.py</code>'s <code>_index_path()</code>."
    )
    story.append(Paragraph(sec2_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("3. Vulnerability 3: Content-Disposition Header Injection", sec_title_style))
    sec3_p = (
        "• <b>The Flaw:</b> In <code>documentController.js</code>, the report download header was constructed using the client's raw upload name: <code>Content-Disposition: attachment; filename=\"${doc.originalName}.pdf\"</code>.<br/>"
        "• <b>The Exploit:</b> An attacker uploads a file named <code>notice\"; filename=\"malware.exe</code>. The unescaped double quote breaks out of the quoted parameter string, altering browser download handling.<br/>"
        "• <b>The Mitigation:</b> Sanitized the header string by stripping all quotes, carriage returns, and line feeds: <code>(doc.originalName || 'analysis').replace(/[\"\\r\\n]/g, '')</code>."
    )
    story.append(Paragraph(sec3_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("4. Vulnerability 4: Information Disclosure via Unhandled Error Messages", sec_title_style))
    sec4_p = (
        "• <b>The Flaw:</b> <code>errorMiddleware.js</code> previously passed raw <code>err.message</code> to client responses for all thrown errors. Mongoose <code>CastError</code> or database driver exceptions exposed internal collection names, query paths, and stack traces.<br/>"
        "• <b>The Mitigation:</b> Production error masking: only explicit instances of <code>AppError</code> (trusted operational errors) expose their messages to clients. All unexpected runtime exceptions return a generic <code>'Internal Server Error'</code> while logging the full stack trace server-side."
    )
    story.append(Paragraph(sec4_p, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("5. Architectural Finding: Unauthenticated Internal RAG Microservice", sec_title_style))
    sec5_p = (
        "• <b>The State:</b> FastAPI endpoints (<code>/ingest</code>, <code>/analyze</code>, <code>/chat</code>) enforce no request-level API key or bearer token authentication.<br/>"
        "• <b>Perimeter Defense:</b> This risk is strictly mitigated via <b>Docker Network Bridge Isolation</b>. <code>rag_service</code> only exposes port 8000 internally on the <code>livelegalai</code> bridge network; it is NEVER published on host port mappings. Caddy reverse proxy only routes <code>/api/*</code> to Express and <code>/*</code> to Next.js. The RAG service cannot be reached from the public internet."
    )
    story.append(Paragraph(sec5_p, body_style))
    story.append(Spacer(1, 3))

    # Security Summary Table
    story.append(Paragraph("6. Security Hardening Summary Matrix", sec_title_style))
    sec_data = [
        [Paragraph("Security Domain", table_cell_header), Paragraph("Identified Risk", table_cell_header), Paragraph("Applied Mitigation & Defensive Mechanism", table_cell_header)],
        [Paragraph("<b>Brute-Force Auth</b>", table_cell), Paragraph("Credential stuffing & login flooding", table_cell), Paragraph("<code>authLimiter</code>: Max 10 requests per 15 minutes per IP on auth endpoints.", table_cell)],
        [Paragraph("<b>File Uploads</b>", table_cell), Paragraph("Malicious scripts, zip bombs, oversized files", table_cell), Paragraph("Multer enforces 10MB limit and MIME/extension allowlist. FastAPI streams in 64KB chunks.", table_cell)],
        [Paragraph("<b>XSS Attacks</b>", table_cell), Paragraph("Script injection into generated reports", table_cell), Paragraph("PDFKit renders literal glyphs, not HTML markup; user strings cannot break out.", table_cell)],
        [Paragraph("<b>SSRF Exposure</b>", table_cell), Paragraph("Server fetching internal malicious IPs", table_cell), Paragraph("Express only downloads files from Cloudinary's verified CDN URL generated at upload.", table_cell)],
    ]
    sec_tbl = Table(sec_data, colWidths=[100, 150, 273.27])
    sec_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#334155")),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sec_tbl)
    story.append(Spacer(1, 3))

    # Deep Viva Questions for Page 4
    story.append(Paragraph("7. Deep Viva Questions & Model Answers", sec_title_style))
    story.append(make_qa_box(
        "What is the difference between SQL injection and NoSQL injection in Mongoose?",
        "SQL injection relies on escaping string literals to append executable SQL commands (e.g., ' OR 1=1 --). In Mongoose/MongoDB, injection occurs because MongoDB queries accept JSON objects. If an endpoint accepts raw request bodies without type checking, an attacker passes query operators like {'$ne': null} or {'$gt': ''} as object values. This alters the database query logic without any SQL keywords.",
        "DEEP VIVA Q5"
    ))
    story.append(Spacer(1, 3))
    story.append(make_qa_box(
        "If the RAG microservice has no authentication header, how is it protected against unauthorized access?",
        "By network topology isolation: In our docker-compose.yaml, the RAG container joins the internal 'livelegalai' bridge network and uses 'expose: 8000' rather than 'ports: 8000:8000'. Only Caddy publishes host ports (80/443), and Caddyfile does not route any path to rag_service. The container is completely invisible to the external internet and reachable solely by Express.",
        "DEEP VIVA Q6"
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: RAPID-FIRE VIVA CHEATSHEET & EXAMINER TRAP QUESTIONS
    # =========================================================================
    story.append(Paragraph("RAPID-FIRE VIVA CHEATSHEET & EXAMINER TRAP QUESTIONS", page_header_style))
    story.append(Paragraph("Crucial rapid-fire answers, examiner trap questions, system limitations, and high-impact presentation tips.", page_sub_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=ACCENT_BLUE, spaceBefore=0, spaceAfter=5))

    story.append(Paragraph("1. Rapid-Fire Technical Definitions (Memorize These!)", sec_title_style))
    rapid_data = [
        [Paragraph("Term / Metric", table_cell_header), Paragraph("Precise 1-Line Technical Definition for Examiners", table_cell_header)],
        [Paragraph("<b>Dense Vector</b>", table_cell), Paragraph("A continuous numerical array (384 floats in all-MiniLM-L6-v2) capturing semantic context in latent vector space.", table_cell)],
        [Paragraph("<b>Cosine Similarity</b>", table_cell), Paragraph("The cosine of the angle between two normalized vectors, measuring conceptual similarity independent of text length.", table_cell)],
        [Paragraph("<b>Sliding Window Chunking</b>", table_cell), Paragraph("Splitting text into 500-char segments with 50-char overlap to preserve contextual continuity across clause boundaries.", table_cell)],
        [Paragraph("<b>FAISS IndexFlatIP</b>", table_cell), Paragraph("Facebook AI Similarity Search inner-product index; executes exact brute-force cosine search with 100% recall.", table_cell)],
        [Paragraph("<b>Stateless JWT</b>", table_cell), Paragraph("Cryptographically signed token carrying identity claims in its payload, avoiding server-side session lookups in RAM.", table_cell)],
    ]
    rapid_tbl = Table(rapid_data, colWidths=[130, 393.27])
    rapid_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(rapid_tbl)
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. 4 Classic 'Examiner Trap Questions' (How to Ace Them)", sec_title_style))
    story.append(make_qa_box(
        "Examiner: 'What happens if a user uploads a handwritten or scanned image PDF?'",
        "Our current pipeline utilizes pdfplumber, which extracts computer-encoded font glyphs. Scanned images yield zero text. Rather than crashing or invoking the LLM with empty prompts, our text_cleaner detects zero chunks and returns an immediate HTTP 400 with a clear error: 'Scanned image-based PDF detected. OCR preprocessing required.' In future iterations, we plan to integrate Tesseract OCR.",
        "TRAP QUESTION 1"
    ))
    story.append(Spacer(1, 3))
    story.append(make_qa_box(
        "Examiner: 'Why didn't you use LangChain or LlamaIndex instead of building custom pipeline scripts?'",
        "LangChain introduces heavy abstractions, complex dependency trees, and opaque debugging chains. In a production legal context, explainability and absolute control are paramount. By writing explicit modular scripts (document_parser.py, chunker.py, retriever.py), every step is transparent, easy to unit-test, logs clear execution times, and has zero framework bloat.",
        "TRAP QUESTION 2"
    ))
    story.append(Spacer(1, 3))
    story.append(make_qa_box(
        "Examiner: 'How does FAISS scale horizontally if you deploy across multiple server instances?'",
        "In our current design, FAISS index files (.index) reside on local container storage. For a multi-node horizontal deployment, local storage would cause cache misses if instance B served a query for a doc ingested by instance A. To scale horizontally, we would either (1) mount a shared NFS / Amazon EFS volume, or (2) transition to a distributed vector database like Qdrant, Milvus, or Pgvector.",
        "TRAP QUESTION 3"
    ))
    story.append(Spacer(1, 3))
    story.append(make_qa_box(
        "Examiner: 'What prevents the LLM from fabricating legal advice or hallucinating non-existent court precedents?'",
        "Three-layer grounding defense: (1) System prompt explicitly commands: 'ONLY use information from the provided document excerpts. NEVER invent legal facts. If unknown, state clearly.' (2) The prompt injects Top-5 retrieved excerpts with strict delimiter tags. (3) The UI displays an explicit legal disclaimer that LiveLegalAI provides informational analysis, not formal attorney representation.",
        "TRAP QUESTION 4"
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3. System Limitations & Future Engineering Roadmap", sec_title_style))
    future_data = [
        [Paragraph("Current System Limitation", table_cell_bold), Paragraph("Engineered Future Solution", table_cell_bold)],
        [Paragraph("• Only parses text-based PDFs and DOCX files.", table_cell), Paragraph("• Integrate an OCR engine (Tesseract / AWS Textract) for scanned notices.", table_cell)],
        [Paragraph("• HTTP polling for background status updates.", table_cell), Paragraph("• Implement WebSockets / Server-Sent Events (SSE) for real-time progress.", table_cell)],
        [Paragraph("• FAISS stored locally on container disk.", table_cell), Paragraph("• Migrate to a distributed vector store (Qdrant / Pgvector on PostgreSQL).", table_cell)],
        [Paragraph("• Pure dense vector semantic search.", table_cell), Paragraph("• Implement Hybrid Search (BM25 keyword search + Dense FAISS via RRF).", table_cell)],
    ]
    future_tbl = Table(future_data, colWidths=[240, 283.27])
    future_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("BACKGROUND", (0, 0), (-1, 0), TAG_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(future_tbl)
    story.append(Spacer(1, 4))

    # Golden Tips Callout Box
    tips_box = [
        Paragraph("<b>GOLDEN RULES FOR ACING YOUR VIVA DEFENSE:</b>", ParagraphStyle("TipsHdr", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=SECONDARY)),
        Paragraph("1. <b>Speak in trade-offs:</b> Examiners love candidates who explain <i>why</i> an alternative was rejected (e.g., why per-document FAISS was chosen over a global index, why rule-based scoring was chosen over LLM scoring).<br/>"
                  "2. <b>Highlight the security audit:</b> Discussing the NoSQL operator injection and path traversal fixes proves production maturity beyond standard student tutorials.<br/>"
                  "3. <b>Know your numbers:</b> 384 dimensions, 500-char chunks, 50-char overlap, Top-5 chunks, 12 bcrypt salt rounds, 10 req/15 min auth rate limit.", callout_text)
    ]
    story.append(make_card(tips_box, bg_color=HexColor("#F0FDF4"), border_color=HexColor("#86EFAC"), padding=5))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    build_pdf()
