import os
import shutil
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional

from config.settings import settings
from utils.logger import app_logger
from utils.exceptions import AppError, DatabaseError, RAGPipelineError
from models.pydantic_models import (
    ChatRequest, ChatResponse, Citation, ChatMessage,
    FeedbackRequest, FeedbackResponse,
    CampusVisitRequest, CampusVisitResponse, HealthResponse
)
from database.sqlite_db import SchoolERPDatabase
from rag.pipeline import RAGPipeline
from services.gemini_service import GeminiLLMService
from prompts.templates import SYSTEM_PROMPT_TEMPLATE, QUERY_REWRITE_PROMPT

router = APIRouter()

# Initialize core singletons
db = SchoolERPDatabase()
rag_pipeline = RAGPipeline(db_helper=db)
llm_service = GeminiLLMService()

# Ensure uploads directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/chat", response_model=ChatResponse, summary="Enquiry chatbot endpoint")
async def chat_endpoint(request: ChatRequest):
    """
    Core Q&A chat endpoint that executes the full RAG workflow:
    1. Query Preprocessing / Query Rewriting
    2. Context Retrieval (Hybrid: relational data + semantic document chunks)
    3. LLM Response Generation (Grounding prompt structure)
    4. Citation Mapping and Metadata aggregation
    """
    try:
        user_query = request.question
        app_logger.info(f"Received query in session '{request.session_id}': {user_query}")
        
        # 1. Compile conversation history
        chat_history_str = ""
        for msg in request.history:
            chat_history_str += f"{msg.role.capitalize()}: {msg.content}\n"
            
        # 2. Query Rewriting if history is present
        query_for_search = user_query
        if request.history:
            rewrite_prompt = QUERY_REWRITE_PROMPT.format(
                chat_history=chat_history_str,
                question=user_query
            )
            try:
                rewritten = llm_service.call_llm(rewrite_prompt, temperature=0.1)
                if rewritten and len(rewritten.strip()) > 5:
                    query_for_search = rewritten.strip().replace('"', '')
                    app_logger.info(f"Query rewritten from '{user_query}' to '{query_for_search}'")
            except Exception as e:
                app_logger.warning(f"Query rewrite failed, defaulting to original query. Error: {str(e)}")

        # 3. Hybrid Retrieval
        retrieved = rag_pipeline.retrieve(query_for_search, k=4)
        
        # Compile context paragraphs & citations
        context_parts = []
        citations = []
        scores = []
        
        for idx, (chunk, score) in enumerate(retrieved):
            source = chunk["metadata"]["source"]
            content = chunk["content"]
            context_parts.append(f"[{source}]: {content}")
            citations.append(Citation(source=source, chunk_text=content, score=score))
            scores.append(score)
            
        context_str = "\n\n".join(context_parts)
        mean_score = sum(scores) / len(scores) if scores else 0.8
        
        # 4. Generate grounded answer
        system_instruction = "You are a professional Admissions Enquiry Chatbot for Greenwood School. Ground all responses strictly."
        qa_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            context=context_str if context_str else "No relevant documents found. Rely on general school admissions knowledge.",
            chat_history=chat_history_str if chat_history_str else "No previous conversation.",
            question=user_query
        )
        
        answer = llm_service.call_llm(qa_prompt, system_instruction=system_instruction)
        
        return ChatResponse(
            answer=answer,
            confidence_score=round(mean_score, 2),
            citations=citations,
            query_rewritten=query_for_search if query_for_search != user_query else None
        )
        
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        app_logger.critical(f"Unhandled exception in /chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/upload", summary="Upload a physical document")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a file (PDF, DOCX, TXT, CSV, JSON) and saves it to local disk storage."""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        app_logger.info(f"File uploaded successfully to {file_path}")
        return {"success": True, "filename": file.filename, "file_path": file_path}
    except Exception as e:
        app_logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/index", summary="Parse and chunk document files into RAG")
async def index_document(filename: str = Query(..., description="The name of the uploaded file to parse")):
    """Triggers parsing, splitting, embedding generation, and indexing for an uploaded file."""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Uploaded file '{filename}' not found.")
            
        chunks_count = rag_pipeline.index_file(file_path)
        return {
            "success": True,
            "filename": filename,
            "chunks_indexed": chunks_count,
            "message": f"Successfully parsed and loaded {chunks_count} vector records."
        }
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.get("/search", summary="Run a dry-run similarity search")
async def search_endpoint(query: str = Query(..., description="Query string to find similarity records for")):
    """Directly queries the similarity search vector index to inspect chunks and confidence scoring."""
    try:
        retrieved = rag_pipeline.retrieve(query, k=4)
        results = []
        for chunk, score in retrieved:
            results.append({
                "source": chunk["metadata"]["source"],
                "text": chunk["content"],
                "score": round(score, 3)
            })
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/documents", summary="List all indexed document files")
async def get_indexed_documents():
    """Lists the names of all files successfully loaded into the vector index database."""
    try:
        docs = rag_pipeline.get_indexed_documents()
        return {"documents": docs, "total_count": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")


@router.post("/reload", summary="Reload vector storage & re-index database")
async def reload_pipeline():
    """Re-syncs SQLite structures and clears/re-builds the vector index database."""
    try:
        global rag_pipeline
        rag_pipeline = RAGPipeline(db_helper=db)
        # Re-index all uploaded files
        uploaded_files = os.listdir(UPLOAD_DIR)
        reindexed_count = 0
        for f in uploaded_files:
            if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and not f.startswith('.'):
                try:
                    rag_pipeline.index_file(os.path.join(UPLOAD_DIR, f))
                    reindexed_count += 1
                except Exception:
                    pass
        return {
            "success": True, 
            "message": f"Pipeline re-initialized. DB re-synced and {reindexed_count} upload files re-indexed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline reload failed: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse, summary="Submit parent feedback")
async def submit_feedback(request: FeedbackRequest):
    """Saves user rating and comment directly into the main School ERP relational database."""
    try:
        sql = "INSERT INTO Feedback (user_email, rating, comment) VALUES (?, ?, ?)"
        feedback_id = db.execute(sql, (request.user_email, request.rating, request.comment))
        app_logger.info(f"Feedback {feedback_id} recorded for {request.user_email} with rating {request.rating}")
        return FeedbackResponse(success=True, feedback_id=feedback_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/visit", response_model=CampusVisitResponse, summary="Schedule a campus visit")
async def schedule_visit(request: CampusVisitRequest):
    """Saves a scheduled parent-student visit details to the database."""
    try:
        sql = """
        INSERT INTO CampusVisits (parent_name, parent_email, parent_phone, visit_date, visit_time, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        visit_id = db.execute(sql, (
            request.parent_name, request.parent_email, request.parent_phone,
            request.visit_date, request.visit_time, request.notes
        ))
        app_logger.info(f"Campus visit {visit_id} scheduled for {request.parent_name} on {request.visit_date}")
        return CampusVisitResponse(success=True, visit_id=visit_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/health", response_model=HealthResponse, summary="API Health status")
async def health_endpoint():
    """Returns status metrics of the server, SQLite connectivity, and current vector search sizes."""
    db_connected = False
    vector_size = 0
    try:
        # Check SQLite connectivity
        test_query = db.query("SELECT 1")
        if test_query:
            db_connected = True
            
        # Check vector DB size
        if rag_pipeline and rag_pipeline.vector_store:
            vector_size = len(rag_pipeline.vector_store.chunks)
            
        return HealthResponse(
            status="healthy",
            db_connected=db_connected,
            vector_db_size=vector_size
        )
    except Exception as e:
        app_logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            db_connected=db_connected,
            vector_db_size=vector_size
        )
