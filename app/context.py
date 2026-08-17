"""Das Kontext-Objekt: wer handelt für welchen Mandanten.

Wird einmal pro Request (app/deps.py), pro Job oder pro MCP-Verbindung erzeugt und durch
Agent-Lauf, Tools und Repositories gereicht. Nichts liest Mandant oder Nutzer aus globalem Zustand.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RequestContext:
    tenant_id: UUID
    user_id: UUID
    roles: frozenset[str] = field(default_factory=frozenset)
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def require_role(self, role: str) -> None:
        if not self.has_role(role):
            raise PermissionError(f"Rolle {role!r} erforderlich")

    def trace_attributes(self) -> dict[str, str]:
        """Attribute für Tracing/Langfuse – nie Inhalte, nur Identifikatoren."""
        return {
            "tenant_id": str(self.tenant_id),
            "user_id": str(self.user_id),
            "request_id": self.request_id,
        }
