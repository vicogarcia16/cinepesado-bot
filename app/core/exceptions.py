from fastapi import HTTPException, status

class JsonInvalidException(HTTPException):
    def __init__(self, detail: str = "Invalid JSON"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        
class DataRequiredException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
