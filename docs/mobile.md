# Mobile-App anbinden (Android/iOS)

Die App ist ein weiterer Client derselben API – Agent-Logik, Tools, RLS und Modell-Zugang bleiben
unverändert. Entscheidung und Optionen: Skill `ai-app-architecture`, Abschnitt "Mobile Clients"
und ADR-Vorlage `0005-mobile.md`.

## Wege (in dieser Reihenfolge prüfen)

1. **PWA / verpackte Web-App** (Capacitor, Trusted Web Activity): das Next.js-Frontend als
   installierbare App – billigster Test, für interne Tools oft genug.
2. **Expo / React Native**: gleiche Sprache wie das Web-Frontend; das Vercel AI SDK läuft auch in
   React Native und spricht gegen `POST /api/chat`. Monorepo mit geteiltem Paket (Typen, Hooks,
   API-Client aus dem OpenAPI-Schema unter `/openapi.json`).
3. **Nativ (Kotlin/Compose)**: nur mit Grund – tiefe OS-Integration, natives Team.

## Backend-Pflichten vor der ersten App-Version

- `AUTH_MODE=jwt` in `app/deps.py` implementieren: OIDC + PKCE mit einem Identity-Provider,
  kurzlebige Access-Tokens, Refresh-Tokens, Widerruf. Die Dev-Header sind auf dem Gerät tabu.
- API-Verträge einfrieren: `/v1/`-Präfix, keine Breaking Changes, `/openapi.json` als Vertrag,
  Client generieren (z. B. `openapi-typescript`), Deprecation-Fenster.
- Lange Agent-Läufe als Jobs: `POST /v1/jobs` → Status-Endpunkt oder Push → Ergebnis in der DB
  (Tabelle mit `tenant_id` + RLS). SSE-Stream nur für den Chat.
- Uploads über signierte URLs auf den Objektspeicher (Tenant-Prefix), Verarbeitung serverseitig.
- Push (FCM/APNs): Gerätetokens pro Nutzer mit `tenant_id`; keine Inhalte im Payload.
- Rate-Limits pro Nutzer; Play Integrity / App Attest nur bei Bedarf.

## Was nicht nötig ist

KI auf dem Gerät. Modelle bleiben hinter der API; On-Device-Modelle sind höchstens später eine
Ergänzung für Offline-Kleinkram.
