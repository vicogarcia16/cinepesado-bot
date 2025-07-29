from fastapi import HTTPException, status

class JsonInvalidException(HTTPException):
    def __init__(self, detail: str = "Invalid JSON"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        
class DataRequiredException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class LLMApiError(HTTPException):
    def __init__(self, detail: str = "Error communicating with the LLM API"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)

class YouTubeSearchError(HTTPException):
    def __init__(self, detail: str = "Error searching for a YouTube trailer"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)