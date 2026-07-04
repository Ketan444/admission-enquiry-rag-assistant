class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class DatabaseError(AppError):
    """Exception raised when an SQLite database operation fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class RAGPipelineError(AppError):
    """Exception raised when RAG document processing or retrieval fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class GeminiAPIError(AppError):
    """Exception raised when calling the Gemini API fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=502)

class DocumentLoadError(AppError):
    """Exception raised when loading document files fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
        
class InputValidationError(AppError):
    """Exception raised when custom input validation fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)
