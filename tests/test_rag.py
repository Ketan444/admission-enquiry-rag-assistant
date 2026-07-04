import os
import pytest
from database.sqlite_db import SchoolERPDatabase
from rag.pipeline import TextSplitter, VectorStoreEngine, DocumentParser
from models.pydantic_models import ChatMessage


def test_sqlite_connection_and_seeding():
    """Test that our SQLite School ERP database creates and seeds tables correctly."""
    # Create temp database
    test_db_path = "database/test_school_erp.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        
    db = SchoolERPDatabase(db_path=test_db_path)
    
    # Check that admissions and fee structure tables have data
    admissions_count = db.query("SELECT COUNT(*) as cnt FROM Admissions")[0]["cnt"]
    fees_count = db.query("SELECT COUNT(*) as cnt FROM FeeStructure")[0]["cnt"]
    
    assert admissions_count > 0, "Admissions table should be seeded."
    assert fees_count > 0, "FeeStructure table should be seeded."
    
    # Clean up test DB
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_text_splitter():
    """Test that text splitter chunks long text with overlap properly."""
    text = "A" * 2500
    splitter = TextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text, "test_doc")
    
    assert len(chunks) > 1, "Text should be split into multiple chunks."
    assert chunks[0]["metadata"]["source"] == "test_doc"
    assert len(chunks[0]["content"]) == 1000


def test_vector_store_search():
    """Test that vector engine runs similarity search with fallback support."""
    engine = VectorStoreEngine()
    
    chunks = [
        {"content": "Greenwood School tuition fee for grade 5 is $42,000.", "metadata": {"source": "fees.txt"}},
        {"content": "The soccer field and swimming pool are excellent sports facilities.", "metadata": {"source": "sports.txt"}},
        {"content": "Admissions close on August 15th.", "metadata": {"source": "dates.txt"}}
    ]
    
    engine.add_documents(chunks)
    results = engine.similarity_search("How much is grade 5 tuition fee?", k=1)
    
    assert len(results) == 1, "Search should return 1 result."
    # The first result chunk should match the first item since it is semantically related
    matched_chunk = results[0][0]
    assert "tuition" in matched_chunk["content"] or "grade 5" in matched_chunk["content"]


def test_pydantic_validation():
    """Test that our ChatMessage Pydantic model validates structure correctly."""
    msg = ChatMessage(role="user", content="Hello, is transport available?")
    assert msg.role == "user"
    assert msg.content == "Hello, is transport available?"
