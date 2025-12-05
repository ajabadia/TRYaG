from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import triage, ai

app = FastAPI(
    title="TryAge API",
    description="API REST del Sistema de Triaje Avanzado",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a dominios conocidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Routers
app.include_router(triage.router, prefix="/v1/core", tags=["Core Logic"])
app.include_router(ai.router, prefix="/v1/ai", tags=["AI Services"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to TryAge API",
        "status": "active",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}
