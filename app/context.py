"""The context object: who is acting, for which tenant.

Created once per request (app/deps.py), per job, or per MCP connection, and passed through
agent run, tools, and repositories. Nothing reads tenant or user from global state.
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
            raise PermissionError(f"role {role!r} required")

    def trace_attributes(self) -> dict[str, str]:
        """Attributes for tracing/Langfuse — never content, identifiers only."""
        return {
            "tenant_id": str(self.tenant_id),
            "user_id": str(self.user_id),
            "request_id": self.request_id,
        }
