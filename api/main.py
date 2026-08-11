import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dataops.api")

app = FastAPI(
    title="DataOps Agent Platform API",
    description="Thin HTTP REST adapter exposing pipeline health, AI Agent investigations, human remediation approval, and recovery verification.",
    version="1.0.0-MCP"
)

# Configurable CORS origins for production deployment
raw_cors = os.getenv("CORS_ALLOWED_ORIGINS", "*")
if raw_cors == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST router
app.include_router(router, prefix="/api")

@app.get("/")
def root_endpoint():
    return {
        "service": "DataOps Agent Platform API",
        "status": "RUNNING",
        "health_check": "/api/health",
        "docs": "/docs",
        "version": "1.0.0-MCP"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
