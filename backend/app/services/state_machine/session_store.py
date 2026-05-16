from app.services.state_machine.session_context import SessionContext


class InMemorySessionStore:
    def __init__(self) -> None:
        self._store: dict[str, SessionContext] = {}

    def get(self, session_id: str) -> SessionContext | None:
        return self._store.get(session_id)

    def set(self, session_id: str, context: SessionContext) -> None:
        self._store[session_id] = context
