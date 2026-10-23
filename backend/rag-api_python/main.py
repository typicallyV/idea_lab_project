import os
import hmac
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routes import router
from config import APP_TITLE, APP_VERSION, APP_DESCRIPTION, FAISS_INDEX_DIR, UPLOAD_DIR
from logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        docs_url="/docs",        # Swagger UI at http://localhost:8000/docs
        redoc_url="/redoc",      # ReDoc UI at http://localhost:8000/redoc
    )

    @app.middleware("http")
    async def protect_public_rag_service(request: Request, call_next):
        # Render Free services have public URLs. Keep health probes public, but
        # require the Express service's shared secret for every RAG operation.
        if request.url.path == "/health" or request.method == "OPTIONS":
            return await call_next(request)

        expected_key = os.environ.get("INTERNAL_API_KEY", "")
        if not expected_key:
            if os.environ.get("ENVIRONMENT", "development").lower() == "production":
                return JSONResponse(
                    status_code=503,
                    content={"detail": "RAG service internal API key is not configured"},
                )
            return await call_next(request)

        supplied_key = request.headers.get("x-internal-api-key", "")
        if not hmac.compare_digest(supplied_key, expected_key):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)


    # first check if master backend is defined
    master_backend_url = os.environ.get("MASTER_BACKEND_URL")
    if not master_backend_url:
        raise RuntimeError("MASTER_BACKEND_URL is not configured")
    
    # checking health of master backend 

    # no need for cors. as we are using this microservice for server <-> server communication
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup():
        os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        logger.info(f"RAG Microservice starting up — {APP_TITLE} v{APP_VERSION}")
        logger.info(f"FAISS index directory : {FAISS_INDEX_DIR}")
        logger.info(f"Upload directory      : {UPLOAD_DIR}")
        logger.info("All systems ready. API docs available at http://localhost:8000/docs")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("RAG Microservice shutting down — goodbye!")

    return app


app = create_app()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    if(port==8000):
       logger.info("PORT not set; using default port 8000")

    # quick reload will be enabled in dev, not on production
    is_dev = os.environ.get("ENVIRONMENT", "development").lower() == "development"

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=is_dev,        
    )
