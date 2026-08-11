import logging
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

# Enable CORS for Next.js web application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Next.js web UI from any host/port
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
        "docs": "/docs",
        "version": "1.0.0-MCP"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
