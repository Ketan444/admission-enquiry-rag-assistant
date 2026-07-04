import os
import json
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from docx import Document

from config.settings import settings
from utils.logger import app_logger
from utils.exceptions import RAGPipelineError, DocumentLoadError

# Try to import langchain and sentence-transformers, but build resilient fallbacks
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    app_logger.warning("SentenceTransformers not available. Using tf-idf based fallback search.")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class DocumentParser:
    """Parses various document types including TXT, PDF, DOCX, CSV, Excel, and JSON."""
    
    @staticmethod
    def load_txt(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise DocumentLoadError(f"Error loading TXT {file_path}: {str(e)}")

    @staticmethod
    def load_pdf(file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                text.append(page.extract_text() or "")
            return "\n".join(text)
        except Exception as e:
            raise DocumentLoadError(f"Error loading PDF {file_path}: {str(e)}")

    @staticmethod
    def load_docx(file_path: str) -> str:
        try:
            doc = Document(file_path)
            text = [paragraph.text for paragraph in doc.paragraphs]
            return "\n".join(text)
        except Exception as e:
            raise DocumentLoadError(f"Error loading DOCX {file_path}: {str(e)}")

    @staticmethod
    def load_csv(file_path: str) -> str:
        try:
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            raise DocumentLoadError(f"Error loading CSV {file_path}: {str(e)}")

    @staticmethod
    def load_excel(file_path: str) -> str:
        try:
            df = pd.read_excel(file_path)
            return df.to_string()
        except Exception as e:
            raise DocumentLoadError(f"Error loading Excel {file_path}: {str(e)}")

    @staticmethod
    def load_json(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception as e:
            raise DocumentLoadError(f"Error loading JSON {file_path}: {str(e)}")

    @classmethod
    def parse_file(cls, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.txt':
            return cls.load_txt(file_path)
        elif ext == '.pdf':
            return cls.load_pdf(file_path)
        elif ext == '.docx':
            return cls.load_docx(file_path)
        elif ext == '.csv':
            return cls.load_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            return cls.load_excel(file_path)
        elif ext == '.json':
            return cls.load_json(file_path)
        else:
            raise DocumentLoadError(f"Unsupported file format: {ext}")


class TextSplitter:
    """Splits a document text into smaller chunks with sliding-window overlaps."""
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def split_text(self, text: str, source_name: str) -> List[Dict[str, Any]]:
        chunks = []
        text_len = len(text)
        start = 0
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_content = text[start:end]
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "source": source_name,
                    "char_start": start,
                    "char_end": end
                }
            })
            if end == text_len:
                break
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks


class VectorStoreEngine:
    """A clean, fast, self-contained Vector Store using SentenceTransformers or TF-IDF."""
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings = None
        self.transformer_model = None
        self.tfidf_vectorizer = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                app_logger.info(f"Loading SentenceTransformer model: {settings.EMBEDDING_MODEL_NAME}")
                self.transformer_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                self.vector_dim = 384  # default for MiniLM
            except Exception as e:
                app_logger.warning(f"Failed to load SentenceTransformer: {str(e)}. Falling back to TF-IDF.")
                self.transformer_model = None
                
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Adds text chunks and recalculates embeddings."""
        if not chunks:
            return
            
        self.chunks.extend(chunks)
        texts = [c["content"] for c in self.chunks]
        
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.transformer_model:
            try:
                embeddings_list = self.transformer_model.encode(texts, show_progress_bar=False)
                self.embeddings = np.array(embeddings_list)
                app_logger.info(f"Generated sentence embeddings for {len(chunks)} chunks.")
            except Exception as e:
                app_logger.error(f"Error encoding embeddings: {str(e)}")
                self._compute_tfidf_embeddings(texts)
        else:
            self._compute_tfidf_embeddings(texts)

    def _compute_tfidf_embeddings(self, texts: List[str]):
        """TF-IDF embedding generation fallback."""
        try:
            self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
            self.embeddings = self.tfidf_vectorizer.fit_transform(texts)
            app_logger.info(f"Generated TF-IDF matrix for {len(texts)} chunks.")
        except Exception as e:
            app_logger.error(f"TF-IDF generation error: {str(e)}")

    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """Searches vector space and returns top K documents with similarity scores."""
        if not self.chunks or self.embeddings is None:
            return []
            
        k = min(k, len(self.chunks))
        
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.transformer_model:
            try:
                query_embedding = self.transformer_model.encode([query])[0]
                # Cosine Similarity
                dot_product = np.dot(self.embeddings, query_embedding)
                norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
                # Avoid division by zero
                norms[norms == 0] = 1e-9
                similarities = dot_product / norms
                
                # Get top K indices
                top_indices = np.argsort(similarities)[::-1][:k]
                results = []
                for idx in top_indices:
                    score = float(similarities[idx])
                    # Map cosine similarity [-1, 1] to a readable confidence score [0, 1]
                    confidence = max(0.0, min(1.0, (score + 1) / 2))
                    results.append((self.chunks[idx], confidence))
                return results
            except Exception as e:
                app_logger.error(f"Vector search exception: {str(e)}. Falling back to token lookup.")
                
        # TF-IDF Fallback search
        if self.tfidf_vectorizer and self.embeddings is not None:
            try:
                query_vector = self.tfidf_vectorizer.transform([query])
                similarities = cosine_similarity(self.embeddings, query_vector).flatten()
                top_indices = np.argsort(similarities)[::-1][:k]
                results = []
                for idx in top_indices:
                    results.append((self.chunks[idx], float(similarities[idx])))
                return results
            except Exception as e:
                app_logger.error(f"Fallback TF-IDF search failed: {str(e)}")
                
        # Super simple substring fallback
        results = []
        for chunk in self.chunks[:k]:
            results.append((chunk, 0.5))
        return results


class RAGPipeline:
    """Orchestrates document loading, database text sync, indexing, and retrieval operations."""
    def __init__(self, db_helper=None):
        self.parser = DocumentParser()
        self.splitter = TextSplitter()
        self.vector_store = VectorStoreEngine()
        self.db_helper = db_helper
        self.indexed_files: List[str] = []
        
        # Pull database content automatically into RAG index for holistic searches!
        self.sync_database_to_rag()

    def sync_database_to_rag(self):
        """Pulls all ERP SQLite table structures and dumps them into the vector index for seamless search."""
        if self.db_helper:
            try:
                app_logger.info("Syncing relational ERP database into the RAG vector store...")
                db_text = self.db_helper.get_all_admission_data_as_text()
                chunks = self.splitter.split_text(db_text, "School_ERP_Database")
                self.vector_store.add_documents(chunks)
                app_logger.info(f"Database synced. Indexed {len(chunks)} tables/sections.")
            except Exception as e:
                app_logger.error(f"Database sync to RAG failed: {str(e)}")

    def index_file(self, file_path: str) -> int:
        """Parses, splits, and indexes an uploaded document."""
        if not os.path.exists(file_path):
            raise DocumentLoadError(f"File not found: {file_path}")
            
        file_name = os.path.basename(file_path)
        try:
            app_logger.info(f"Parsing and indexing file: {file_name}")
            raw_text = self.parser.parse_file(file_path)
            chunks = self.splitter.split_text(raw_text, file_name)
            self.vector_store.add_documents(chunks)
            self.indexed_files.append(file_name)
            app_logger.info(f"Successfully indexed file: {file_name} with {len(chunks)} chunks.")
            return len(chunks)
        except Exception as e:
            app_logger.error(f"Failed to index file {file_name}: {str(e)}")
            raise RAGPipelineError(f"Indexing failed for {file_name}: {str(e)}")

    def retrieve(self, query: str, k: int = 4) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieves semantic contexts from indexed files and database models."""
        return self.vector_store.similarity_search(query, k=k)
        
    def get_indexed_documents(self) -> List[str]:
        return list(set(self.indexed_files))
