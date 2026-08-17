# ADR-0001: Architektur und Stack

- **Status:** vorgeschlagen (beim Ableiten eines Projekts ausfüllen und akzeptieren)
- **Datum:** YYYY-MM-DD
- **Entscheider:** <Name>
- **Skill-Stand:** ai-app-architecture v1.0.0 (Recherche 2026-08)

## Kontext

<Wofür ist das Projekt, wer nutzt es, wie viele Mandanten jetzt/später, welche Daten, welche
Vorgaben (Cloud, Datenschutz, Team)?>

## Optionen

1. Blueprint A – Python-Backend als API + optionales Next.js-Frontend (dieses Template)
2. Blueprint B – TypeScript-Full-Stack
3. Blueprint C/D – Managed-Plattform (AWS AgentCore / Azure Foundry)
4. Blueprint E – self-hosted / maximal DSGVO

## Entscheidung

Blueprint A mit diesem Template, weil <Gründe>. Mandantenfähig ab Tag 1, ein Mandant angelegt.

## Konsequenzen

- Positiv: portabel, keine Plattformbindung, Umzug auf C/D/E möglich.
- Negativ: Betrieb selbst; zwei Sprachen, sobald ein Frontend dazukommt.

## Überprüfen, wenn …

- ein Kunde physische Datentrennung oder eigenes Cloud-Konto verlangt
- Enterprise-Anforderungen (Identity, Session-Isolation, viele langlaufende Agents) kommen
- die Recherche älter als sechs Monate ist
