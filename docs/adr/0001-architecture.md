# ADR-0001: Architecture and stack

- **Status:** proposed (fill in and accept when deriving a project)
- **Date:** YYYY-MM-DD
- **Deciders:** <name>
- **Skill version:** ai-app-blueprints v2.0.0 (research 2026-08)

## Context

<What is the project for, who uses it, how many tenants now/later, which data, which
constraints (cloud, data protection, team)?>

## Options

1. Blueprint A — Python backend as an API + optional Next.js frontend (this starter)
2. Blueprint B — TypeScript full-stack
3. Blueprint C/D — managed platform (AWS AgentCore / Azure Foundry)
4. Blueprint E — self-hosted / maximum data sovereignty

## Decision

Blueprint A with this starter, because <reasons>. Multi-tenant from day one, one tenant created.

## Consequences

- Positive: portable, no platform binding, a move to C/D/E stays possible.
- Negative: operations are on us; two languages once a frontend is added.

## Revisit when …

- a customer demands physical data separation or their own cloud account
- enterprise requirements arrive (identity, session isolation, many long-running agents)
- the research is older than six months
