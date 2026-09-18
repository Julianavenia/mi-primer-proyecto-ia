from typing import Annotated

from fastapi import APIRouter, Depends

from mi_primer_proyecto_ia.api.deps import get_settings
from mi_primer_proyecto_ia.api.schemas import HealthResponse
from mi_primer_proyecto_ia.config import Settings

router = APIRouter()


@router.get("/health")
def get_health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(status="ok", llm_backend=settings.llm_backend)
