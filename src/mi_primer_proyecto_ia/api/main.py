from fastapi import FastAPI

from mi_primer_proyecto_ia.api.routers import chat, health

app = FastAPI(title="mi-primer-proyecto-ia")
app.include_router(health.router)
app.include_router(chat.router)
