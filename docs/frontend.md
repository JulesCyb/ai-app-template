# Frontend anbinden (Next.js + Vercel AI SDK)

Das Backend liefert unter `POST /api/chat` das Stream-Format des Vercel AI SDK (PydanticAI
`VercelAIAdapter`, `sdk_version=6`). Ein Next.js-Frontend braucht damit keinen eigenen Agent-Code.

Versionen sind schnelllebig – vor dem Start aktuelle Docs prüfen (`ai`, `@ai-sdk/react`, Next.js).

```bash
npx create-next-app@latest web --ts --app --eslint --tailwind --no-src-dir
cd web && npm i ai @ai-sdk/react
```

Minimaler Chat (`web/app/page.tsx`, Prinzip – API-Details gegen die aktuelle SDK-Doku prüfen):

```tsx
"use client";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";

export default function Page() {
  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({
      api: process.env.NEXT_PUBLIC_API_URL + "/api/chat",
      headers: {                       // dev-headers – in Produktion Session/JWT
        "X-Tenant-Id": process.env.NEXT_PUBLIC_DEV_TENANT_ID!,
        "X-User-Id": process.env.NEXT_PUBLIC_DEV_USER_ID!,
      },
    }),
  });
  // messages rendern, Formular -> sendMessage({ text })
}
```

Hinweise:
- CORS: `CORS_ORIGINS` im Backend auf die Frontend-URL setzen.
- Tool-Aufrufe (`search_documents`) kommen als Tool-Parts im Stream an – anzeigen, damit Nutzer sehen, was der Agent tut.
- In Produktion die Auth im Frontend über die Session lösen (Cookie/JWT); die dev-Header nie ausliefern.
- Alternative ohne UI-Framework-Bindung: `POST /agents/assistant/stream` (SSE, reiner Text) oder AG-UI-Adapter von PydanticAI.
