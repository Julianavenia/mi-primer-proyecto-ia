# mi-primer-proyecto-ia

Agente con *tool use* construido sobre la API de Anthropic (Claude), expuesto como una app web (FastAPI + frontend).

El modelo decide cuándo invocar herramientas (funciones Python) para completar una tarea, en vez de limitarse a responder texto. Este repo se está construyendo por fases: primero el agente por terminal, después el backend HTTP, y por último la interfaz web.

## Requisitos

- Python 3.13 (ver `.python-version`)
- [uv](https://docs.astral.sh/uv/) como gestor de dependencias y entornos
- Una API key de Anthropic ([console.anthropic.com](https://console.anthropic.com))

## Configuración

1. Instala las dependencias:
   ```bash
   uv sync
   ```
2. Copia `.env.example` a `.env` y añade tu API key:
   ```bash
   cp .env.example .env
   ```

## Desarrollo

```bash
uv run pytest        # tests
uv run ruff check .  # lint
uv run ruff format .  # formato
```

## Estado del proyecto

En construcción por fases. Ver el plan de desarrollo para el detalle de cada fase (agente mínimo → tool use → backend FastAPI → frontend → pulido).
