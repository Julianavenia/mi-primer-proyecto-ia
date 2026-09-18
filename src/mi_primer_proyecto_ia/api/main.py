from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mi_primer_proyecto_ia.api.deps import get_settings
from mi_primer_proyecto_ia.api.routers import chat, health

app = FastAPI(title="mi-primer-proyecto-ia")

# Orígenes explícitos (nunca "*") — ver Settings.cors_allowed_origins en config.py.
# El frontend (web/, Next.js) corre en un proceso/origen distinto al backend, así
# que el navegador exige CORS para permitir las peticiones desde localhost:3000.
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router)
app.include_router(chat.router)
