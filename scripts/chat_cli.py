"""Prueba manual del agente por terminal. Ejecutar con: uv run python scripts/chat_cli.py"""

from anthropic.types import MessageParam

from mi_primer_proyecto_ia.agent.client import build_client
from mi_primer_proyecto_ia.agent.loop import ToolIterationLimitError, run_agent_turn
from mi_primer_proyecto_ia.config import Settings


def main() -> None:
    settings = Settings()
    client = build_client(settings)
    history: list[MessageParam] = []

    if settings.llm_backend == "fake":
        print("Modo local simulado (LLM_BACKEND=fake) — sin llamadas reales a Anthropic.")
    else:
        print(f"Hablando con {settings.model_name} vía la API real de Anthropic.")
    print("Ctrl+C o 'salir' para terminar.\n")
    while True:
        try:
            user_message = input("Tú: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if user_message.strip().lower() in {"salir", "exit", "quit"}:
            break

        try:
            reply = run_agent_turn(client, settings, history, user_message)
        except ToolIterationLimitError as exc:
            reply = f"[error] {exc}"
        print(f"Claude: {reply}\n")


if __name__ == "__main__":
    main()
