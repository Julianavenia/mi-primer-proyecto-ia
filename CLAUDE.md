# CLAUDE.md

Reglas permanentes de trabajo para cualquier sesión de Claude Code en este proyecto.
Estas reglas tienen prioridad sobre el comportamiento por defecto.

## 1. Objetivo del proyecto

Desarrollar una aplicación moderna de IA: un **agente con tool use** (el modelo decide
cuándo invocar herramientas para actuar, no solo responder texto), con una arquitectura
preparada desde el inicio para crecer en agentes y herramientas sin reescribirse.

## 2. Stack actual

- Python 3.13.15 (ver `.python-version`)
- `uv` como gestor de dependencias y entornos (`.venv`)
- `pytest` para tests
- `ruff` para lint y formato
- Git + GitHub (remote `origin`)
- Integración con la API de Anthropic, preparada pero desacoplada (ver sección 7)

## 3. Reglas de desarrollo

- Analizar el código y el estado del proyecto antes de modificar nada.
- Planificar el enfoque antes de implementar; para cambios no triviales, proponer el
  plan y esperar aprobación antes de escribir código.
- No hacer cambios destructivos (`git reset --hard`, `git push --force`, borrar
  archivos o historial) sin confirmación explícita.
- Explicar los cambios importantes: qué se hizo y por qué, no solo el diff.
- Mantener una arquitectura clara y modular (separar agente / herramientas / API /
  frontend; sin mezclar responsabilidades entre capas).
- Evitar código innecesariamente complejo: no añadir abstracciones, dependencias ni
  configuración que el problema actual no requiera.

## 4. Pruebas y calidad

- Ejecutar `uv run pytest` después de cualquier cambio relevante.
- Ejecutar `uv run ruff check .` (y `ruff format .` si aplica) después de cambios de código.
- No afirmar que algo "funciona" sin haberlo verificado ejecutándolo o probándolo.
  Si algo no se pudo probar (por ejemplo, requiere una API key real), decirlo
  explícitamente en vez de asumir que funciona.

## 5. Seguridad

- Nunca introducir API keys, contraseñas ni secretos directamente en el código.
- Nunca mostrar secretos reales en las respuestas, logs o commits.
- `.env` debe permanecer fuera de Git (ya cubierto por `.gitignore`) — no crearlo,
  leerlo en texto plano ni exponer su contenido salvo que el usuario lo pida explícitamente.
- `.env.example` documenta nombres de variables, nunca valores reales.

## 6. Git

- No hacer commits de forma automática — solo cuando el usuario lo pida explícitamente.
- No hacer push de forma automática — solo cuando el usuario lo pida explícitamente.
- Mantener los commits pequeños y con mensajes descriptivos (qué y por qué, no solo qué).
- Revisar `git diff`/`git status` antes de proponer un commit.

## 7. IA (integración con Anthropic)

- La integración con Anthropic debe mantenerse desacoplada del resto del código:
  `agent/loop.py` y `tools/` no deben depender de si el cliente es real o simulado.
- El mecanismo concreto para esto es `Settings.llm_backend` (`config.py`):
  `"fake"` (default) usa `FakeAnthropicClient` (`agent/fake_client.py`, sin red);
  `"anthropic"` usa el SDK real y requiere `ANTHROPIC_API_KEY`.
- Los tests deben usar siempre mocks/fakes (`FakeAnthropicClient` en modo guionado,
  o `MagicMock`) — nunca deben depender de la API real ni de una key configurada.
- No realizar llamadas reales a la API de Anthropic (es decir, no cambiar
  `LLM_BACKEND` a `"anthropic"` ni ejecutar código en ese modo) salvo que el usuario
  lo autorice explícitamente en la conversación.

## 8. Metodología de trabajo

Para cualquier tarea no trivial, seguir este ciclo:

**ANALIZAR → PLANIFICAR → APROBAR → IMPLEMENTAR → PROBAR → REVISAR → COMMIT**

No saltarse pasos: no implementar sin un plan aprobado, no dar por cerrada una tarea
sin haberla probado, no hacer commit sin haberla revisado con el usuario.

## 9. Cómo trabajar con el usuario

El usuario está aprendiendo este stack (Claude API, agentes, FastAPI) aunque ya tiene
experiencia general de programación. Por eso:

- Explicar las decisiones técnicas importantes y el porqué, no solo aplicarlas.
- No sustituir o reescribir código existente sin explicar qué cambió y por qué.
- Priorizar siempre soluciones mantenibles y profesionales sobre atajos rápidos,
  incluso si son un poco más de trabajo inicial.
