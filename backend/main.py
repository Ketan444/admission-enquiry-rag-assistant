import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings
from backend.api import routes
from utils.logger import app_logger
from utils.exceptions import AppError

# Initialize FastAPI App with precise Metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-grade Retrieval Augmented Generation (RAG) chatbot API "
        "designed for School ERP systems. Integrates structured SQLite database tables "
        "with unstructured document indices to respond gracefully to parent enquiries using Gemini LLMs."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable Cross-Origin Resource Sharing (CORS) for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origin domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register central routing
app.include_router(routes.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    app_logger.info("==================================================")
    app_logger.info(f"Starting {settings.PROJECT_NAME} Backend API...")
    app_logger.info("Successfully loaded system parameters & configurations.")
    app_logger.info("==================================================")


@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("Shutting down Admissions Assistant Service...")


# Custom Exception Handlers for clean API Responses
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    app_logger.error(f"Application error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "detail": exc.message}
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    app_logger.critical(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "detail": "An unexpected system error occurred."}
    )


# Root landing route
@app.get("/", include_in_schema=False)
async def root_redirect():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} Service API.",
        "swagger_docs": "/docs",
        "health_check": f"{settings.API_V1_STR}/health"
    }


if __name__ == "__main__":
    # Runs the uvicorn development server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
