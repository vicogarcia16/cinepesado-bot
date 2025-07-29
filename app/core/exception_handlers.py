from fastapi import Request, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from .exceptions import JsonInvalidException, DataRequiredException, LLMApiError, YouTubeSearchError

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(JsonInvalidException)
    async def json_invalid_exception_handler(request: Request, exc: JsonInvalidException):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.detail})

    @app.exception_handler(DataRequiredException)
    async def data_required_exception_handler(request: Request, exc: DataRequiredException):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.detail})

    @app.exception_handler(LLMApiError)
    async def llm_api_error_handler(request: Request, exc: LLMApiError):
        # Aquí podrías añadir un log del error si quisieras
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(YouTubeSearchError)
    async def youtube_search_error_handler(request: Request, exc: YouTubeSearchError):
        # Aquí podrías añadir un log del error si quisieras
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail or "HTTP error"}
        )

    @app.exception_handler(Exception)
    async def handle_general_exception(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected internal server error occurred."}
        )