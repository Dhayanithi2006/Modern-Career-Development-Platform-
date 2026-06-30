import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.project_name, version="0.1.0")
logger = logging.getLogger("MODERN_AI_PLATFORM")
logging.basicConfig(level=logging.INFO)

print("CORS ORIGINS:")
print(settings.backend_cors_origins)
print(type(settings.backend_cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.56.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        logger.info("%s %s completed in %.2fms", request.method, request.url.path, (time.perf_counter() - start) * 1000)
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/test-500", tags=["test"])
def test_500():
    raise Exception("This is a test 500 error")


@app.get("/", tags=["root"])
def root():
    return {
        "message": "MODERN_AI_PLATFORM Backend Running",
        "docs": "/docs",
        "health": "/health"
    }

app.include_router(api_router, prefix="/api/v1")
