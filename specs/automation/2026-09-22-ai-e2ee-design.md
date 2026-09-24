<!--
SPDX-FileCopyrightText: 2026 openEDU Contributors
SPDX-License-Identifier: Apache-2.0
-->

# openEDU Workspace: Agentic AI + Unified Search + Optional E2EE

> **Design Doc** — 2026-09-22
> **Status:** Approved (Ansatz C, E2EE = Toggle-Modus)
> **Project:** openEDU extension: ai-e2ee-workspace
> **Entscheidungen:** Auf bestehende OSS aufbauen (kein Greenfield) · Connector-Manifest-Ökosystem (YAML ≠ Code) · E2EE als User-Toggle, nicht always-on

## 1. Overview

openEDU ist eine Kubernetes-basierte, quelloffene digitale Arbeitsplatz-Plattform für Bildung. Sie bietet SSO-föderierte Apps (SOGo Mail, OpenProject, OpenCloud/Nextcloud, XWiki, ILIAS, Element) sowie AI-Bausteine (Open WebUI + Ollama, n8n Automation). Es fehlt:

1. **Agentische AI eingebettet in Alltagsworkflows** — eine Such-Engine kombiniert mit agentischen AI-Fähigkeiten: komplexe Aktionen automatisieren, Informationen app-übergreifend abrufen, repetitive Aufgaben per Klick erledigen — ohne die Arbeitsumgebung zu verlassen, auch in Partner-Apps.
2. **Native E2EE-Option** — User können Daten und Kommunikation verschlüsseln (Opt-in). Ist Verschlüsselung aktiv, laufen Suche und agentische AI **direkt auf dem Gerät des Users** (Browser), sensible Daten werden lokal verarbeitet.

Dieser Spec definiert die Architektur als **Connector-Manifest-Ökosystem** (Ansatz C): Partner/Betreiber tragen deklarative YAML-Manifeste bei (kein Code), eine generische Runtime exponiert diese als LLM-Tools. Zwei Tier-Modi, durch einen E2EE-Toggle gesteuert.

### Goals

1. Unified Search über alle SSO-föderierten Apps (SOGo, OpenProject, Nextcloud, XWiki, ILIAS, …) — ohne die Arbeitsumgebung zu verlassen
2. Agentische AI (Function-Calling) die Aktionen in und über Apps ausführt (lesen, suchen, schreiben, repetitiv automatisieren)
3. Ökosystem-Interface: Partner tragen **deklarative YAML-Manifeste** bei, kein Code, kein Deployment
4. E2EE-Modus (Toggle): Suche + AI laufen im Browser, Master-Key verlässt das Gerät nie
5. Auf bestehende OSS aufbauen: Open WebUI, Ollama, n8n, Keycloak, Web Crypto, WebLLM — kein Greenfield

### Non-Goals

- Kein eigenes Agent-Framework — Open-WebUI Function-Calling nutzen
- Kein zentraler Such-Index — federated Query an native App-Suchen
- Kein Plugin-Code-Execution — Manifeste sind rein deklarativ
- Kein Custom-Crypto — Web Crypto (SubtleCrypto, AES-GCM, PBKDF2)
- Keine vollautonomen Multi-Step-Agents im E2EE-Modus (Browser-LLMs zu schwach) — ehrliche Limitierung
- Nicht die Partner-Apps selbst E2EE-fähig machen (SOGo/OpenProject/Nextcloud müssen Klartext lesen um zu funktionieren) — E2EE deckt den Workspace-Intelligence-Layer ab, nicht die App-Daten-at-rest

## 2. Architektur (Two-Tier + Toggle)

```
                    ┌──────────────────────────────────────┐
                    │        Open WebUI (existiert)         │
                    │   ai.openedusuite.example.org            │
                    │   Function Calling via Ollama          │
                    └───────────┬──────────────┬────────────┘
                        E2EE OFF│              │E2EE ON
                                ▼              ▼
┌───────────────────────────────┐  ┌──────────────────────────────┐
│ TIER 1: Server (Default)      │  │ TIER 2: Browser (E2EE)       │
│                               │  │                              │
│ Connector Runtime (neu)       │  │ WebLLM via WebGPU            │
│ ├ liest Connector-Manifeste    │  │ ├ Qwen-2.5-1.5B/Phi-3.5-mini │
│ ├ exponiert als OWUI-Tools     │  │ ├ Encrypted IndexedDB (OPFS) │
│ ├ federated search (parallel)  │  │ │ AES-GCM, PBKDF2-Master-Key │
│ └ SSO-Token-Forwarding         │  │ ├ Connector-Manifeste direkt │
│                               │  │ │ aus Browser (SSO-Cookie)    │
│ Ollama (existiert)             │  │ └ Federated Search (lokal)   │
│ n8n (existiert, SSO)           │  │                              │
│ Keycloak (existiert)           │  │ Master-Key verlässt Gerät    │
│                               │  │ nie                          │
└──────────────┬────────────────┘  └──────────────┬───────────────┘
               │                                  │
               └──────────── both call ────────────┘
                          App APIs
                 (SOGo/JMAP, OP/REST, NC/WebDAV,
                  XWiki/REST, ILIAS/REST, OCS)
```

**Toggle-Verhalten:** E2EE aus (Default) → Agent läuft server-seitig (Open WebUI + Connector Runtime + Ollama). E2EE an → server-seitige Agent-Tools für diesen User deaktiviert, Browser-Companion übernimmt. State im Keycloak-User-Property oder OWUI-User-Preference.

### E2EE-Bedrohungsmodell-Grenze (ehrlich, bindend für den Spec)

E2EE deckt den **Workspace-Intelligence-Layer** ab:
- ✅ Such-Index (IndexedDB, verschlüsselt-at-rest)
- ✅ Agent-Memory / Konversations-Historie / Notizen / Entwürfe
- ✅ LLM-Inferenz (WebGPU im Browser)
- ✅ App-API-Reads: Browser → App direkt, Ergebnis wird lokal entschlüsselt verarbeitet, verschlüsselt indexiert

NICHT abgedeckt (architektonisch unmöglich ohne App-Kern-Änderungen):
- ❌ App-Daten-at-rest (SOGo muss Mails im Klartext zustellen, Nextcloud Files serven, OpenProject Tasks queryn)
- ❌ Schreib-Aktionen in Partner-Apps (gehen durch die normale App-Verschlüsselung)

Diese Grenze ist ein Feature, kein Bug — sie ist im Threat-Model die korrekte Trennlinie.

## 3. Connector-Manifest (das Ökosystem-Interface)

**Das ist der Kern des Ansatzes C**: Partner contributing „Kuchen" = **ein YAML-Manifest, kein Code**. Niedrigster Beitrittspunkt, keine Code-Review-Security werklast, kein Deployment.

```yaml
apiVersion: opendesk.edu/v1alpha1
kind: Connector
metadata:
  name: sogo-mail
spec:
  displayName: SOGo Mail
  category: communication        # communication | productivity | knowledge | development
  endpoint: https://mail.openedusuite.example.org
  auth:
    type: oidc                    # nutzt SSO-Token aus Keycloak
  search:
    method: jmap                  # jmap | rest | webdav | ocs | custom
    path: /jmap/search
    queryParam: filter
    resultMapping:                # JSONPath → einheitliches Such-Schema
      id: $.id
      title: $.subject
      snippet: $.preview
      date: $.receivedAt
      source: sogo-mail
  actions:
    - name: send-mail
      method: POST
      path: /jmap/api/call
      params: { to: string, subject: string, body: string }
      description: Send an email via SOGo
    - name: read-mail
      method: GET
      path: /jmap/api/messages/{id}
      params: { id: string }
      description: Read a single email by id
  entities:
    - name: message
      schema: { id: string, subject: string, from: string, date: string }
```

**Manifest-Kontrakt (v1alpha1):**

| Feld | Pflicht | Beschreibung |
|---|---|---|
| `spec.endpoint` | ja | Basis-URL der App-API |
| `spec.auth.type` | ja | `oidc` (Bearer-Token) vorerst einziger Typ |
| `spec.search.method` | ja | API-Stil: `jmap` \| `rest` \| `webdav` \| `ocs` \| `custom` |
| `spec.search.path` | ja | Query-Pfad relativ zum Endpoint |
| `spec.search.queryParam` | nein | Name des Query-Parameters (rest/webdav-typisch) |
| `spec.search.resultMapping` | ja | JSONPath-Expressions → einheitliches `{id,title,snippet,date,source}` |
| `spec.search.customUrl` | nein | Voll-URL-Template für `custom`-method mit `{query}`-Platzhalter |
| `spec.actions[]` | nein | Aktionen (CRUD/Send/…), `name/method/path/params/description` |
| `spec.entities[]` | nein | Entity-Schemas für LLM-Context |

**Programmatische Validierung:** Manifeste werden beim Laden gegen ein JSON-Schema validiert (unbekannte `method`-Werte → Reject mit Fehlermeldung). Manifest mit Syntaxv/Validierungsfehlern werden einzeln übersprungen, nicht das ganze Set.

## 4. Connector Runtime (Tier 1, Server)

Neuer Service (Node.js 20+, im ns `opendesk-edu`), ~300–500 Zeilen.

### Komponenten

1. **Manifest-Loading** — liest alle `Connector`-Manifeste aus einem ConfigMap-Volume (`/etc/connectors/*.yaml`). Neue Manifeste = ConfigMap-Eintrag + Volume-Rollout, kein Code-Deploy. Webhook/Reload bei ConfigMap-Änderung (optional; initial: Start + `SIGHUP`).
2. **OWUI-Tool-Adapter** — für jedes Manifest wird eine Open-WebUI-Tool-Funktion generiert (Python mit Type-Hints). Open WebUI's native Tool-API (SQLite-gespeicherte Python-Funktionen) registriert diese beim LLM mit Function-Calling.
   - `search_<name>(query)` → federated search
   - `<action>_<name>(params…)` → einzelne Aktionen (z.B. `send_mail`, `read_mail`)
   - Jede Tool-Funktion bekommt eine Auto-Generated-Beschreibung aus dem Manifest (für LLM-Tool-Selektion).
3. **SSO-Token-Forwarding** — Erster Design-Entscheid: OWUI übergibt den User-Context an Tools; verifizieren ob das OIDC-Token weiterleitbar ist. Fallback: Runtime wird selbst OIDC-Client (Service-Account) und tauscht für den eingeloggten User einen Impersonation-Shortcut — siehe §8. Offene Fragen.
4. **Federated Search** — Query → parallele `fetch`-Calls an alle Connector-`search`-Endpoints (Promise.allSettled) → Merge nach Score → einheitliches Ergebnis-Schema `{id,title,snippet,date,source,score}`. Timeout je Connector (3s), Fehler einzelner Connectors werden als `{source, error}` markiert, nicht fatal.

### Deployment-Artefakte

```
opendesk-edu/k8s/ai-e2ee/
├── deploy-connector-runtime.yaml   # Deployment + ConfigMap-Volume /etc/connectors
├── service-connector-runtime.yaml  # ClusterIP
├── cm-connectors.yaml              # 3 Seed-Manifeste (SOGo, OpenProject, Nextcloud)
├── kustomization.yaml
```

## 5. E2EE-Modus (Tier 2, Browser)

### Browser-Companion-SPA

Neue SPA (Vite + TS), eingebettet in/trotz Open WebUI als eigener Route oder iframe. Bausteine:

1. **Master-Key** — PBKDF2 (600k Iterationen, SHA-256) aus User-Passwort + Salt, client-side. Salt persistiert (Server kann er nicht nutzen — Key bleibt lokal). Web Crypto `crypto.subtle`.
2. **Encrypted Vault** — IndexedDB via OPFS, AES-GCM (256-bit), Encrypted-At-Rest für: Such-Index, Agent-Memory, Konversations-Historie, Notizen/Entwürfe. Key-Wrapping: Master-Key dekryptiert Storage-Wrap-Key.
3. **Lokales LLM** — `@mlc-ai/web-llm` (WebGPU). Modell: Qwen-2.5-1.5B (klein/schnell) oder Phi-3.5-mini. Download ~1–3 GB, gecacht in OPFS (einmalig, offenbarungs-frei — Modell ist Public-OSS).
4. **Browser-Connector-Runtime** — gleiche Manifest-Spec wie Tier 1, aber im Browser. Fetcht App-APIs direkt mit SSO-Cookie (SameSite/HttpOnly) bzw. Keycloak-Token aus SessionStorage. Kein Server-Proxy für die Intelligence-Layer.
5. **Federated Search (lokal)** — parallele API-Calls aus dem Browser, Ergebnisse werden lokal entschlüsselt verarbeitet, in den verschlüsselten Index geschrieben. Re-Search bei Bedarf (kein persistenter Cross-App-Crawl — Kachel-Fetch on-demand, YAGNI).

**Ehrliche Limitierung (bindend):** Browser-LLMs (1.5–3.8B) sind bei Function-Calling unzuverlässig. E2EE-Modus = **Search + Summarize + Draft** (User bestätigt Aktionen). **Keine** vollautonomen Multi-Step-Workflows im E2EE-Modus. Das ist ein dokumentierter Trade-off: volle Agent-Kraft (Tier 1) vs. Datenschutz (Tier 2).

### E2EE-Toggle

- **Ort:** Open-WebUI-Settings (User-Preference) oder Keycloak-User-Attribut. Initial: OWUI-Preference (schnellster Weg).
- **Effekt:** an → `ai.mode=e2ee` im Profil; OWUI-Function-Calling für diesen User deaktiviert; Browser-Companion lädt. aus → Default-Tier-1.

## 6. Was ich NICHT baue (YAGNI)

| Versuchung | Entscheidung | Begründung |
|---|---|---|
| Eigenes Agent-Framework | ❌ Open-WebUI Function-Calling | OWUI hat das bereits mit Ollama |
| Zentraler Such-Index (Meilisearch/es) | ❌ Federated Query an native App-Suchen | Jede App hat bereits Search; Index = Duplikat + Sync-Problem |
| Plugin-Code-Execution | ❌ Manifeste rein deklarativ (YAML) | Partner nie Code auf unserem Server |
| Custom Crypto | ❌ Web Crypto (SubtleCrypto, AES-GCM, PBKDF2) | Browser-native, auditiert |
| Vollautonome E2EE-Agents | ❌ Ehrliche Limitierung | Kleine Modelle, kein zuverlässiges FC |
| Persistentes Cross-App-Crawling | ❌ Kachel-Fetch on-demand | Kein Backfill-Index nötig |

## 7. Bauphasen (minimum viable → vollständig)

**Phase 1 — Tier 1 (Server, kein E2EE)**
1. Connector-Manifest-Spec (`v1alpha1`, YAML + JSON-Schema) + Validator
2. Connector Runtime (Node.js: Manifest-Loading, HTTP-Client, OWUI-Tool-Adapter, Federated Search)
3. 3 Referenz-Connectors: SOGo/JMAP, OpenProject/REST, Nextcloud/WebDAV
4. Open-WebUI-Integration: Tools registrieren, Function-Calling mit Ollama konfigurieren
5. E2E-Test: „Suche über Mail+Projekt+Files, result in OWUI-Chart"

**Phase 2 — Tier 2 (E2EE)**
6. Browser-Companion-SPA (WebLLM + Web Crypto + encrypted IndexedDB)
7. E2EE-Toggle in OWUI-Settings + Mode-Branch
8. Federated Search im Browser (direkte API-Calls, verschlüsselter Index)
9. E2E-Test: „Toggle an → Browser-Modus, Key verlässt Gerät nie; Toggle aus → Server-Modus"

**Phase 3 — Ökosystem**
10. Manifest-Registry als Git-Repo (`opendesk-edu-connectors`) mit PR-Workflow + CI-Validierung
11. Contributor-Doku (Spec-Beispiel, Best Practices)
12. Weitere Connectors: XWiki/REST, ILIAS/REST, Element/Matrix, n8n

## 8. Offene Design-Fragen (vor Phase-1-Start zu beantworten)

1. **Token-Passthrough**: Kann OWUI's Tool-API das User-OIDC-Token an Tools weitergeben? Falls nein → Runtime wird eigenständiger OIDC-Client (Service-Account + User-Impersonation-Shortcut via Keycloak) oder App-zu-App-Token. **Blockiert den Architektur-Scouting-Start.**
2. **Ranking**: Einfaches `score`-Feld pro Connector (z.B.: betreff-Worttreffer × App-Priorität) vs. Reciprocal-Rank-Fusion — Fusions ist nur wenige Zeilen mehr, Qualität deutlich besser. Tendenz: RRF.
3. **WebLLM-Modell**: Qwen-2.5-1.5B (schnell, ~1 GB) vs Phi-3.5-mini (besser, ~2.3 GB) — OPFS-Cache vs. Qualität. Entscheid nach Load-Test in Phase 2.
4. **Manifest-Versionierung**: `v1alpha1` → `v1` — Breaking-Change-Policy (Version im `apiVersion`, Runtime validiert bekannte Versionen).
5. **OWUI-Tool-Registrierung**: OWUI speichert Tools in seiner SQLite-DB (UI-administered) — technisch kann die Runtime `POST /api/v1/tools` (Admin) nutzen, oder OWUI-Pipelines (Sidecar) erweitert werden. Verifizieren welcher Weg administrativ niedrigsten Footprint hat.

## 9. Referenzen

- Bestehend: Open WebUI (ns `llm`, `ai.openedusuite.example.org`, OWUI-Tools/Functions in SQLite, kein Pipelines-Sidecar)
- Bestehend: Ollama (ns `llm`, 2× StatefulSet, `172.17.0.6:5001/ollama:0.32.13-nix`, aktiv)
- Bestehend: n8n (ns `opendesk-edu`, SSO, `n8n.openedusuite.example.org`) — für Multi-Step-Automation (Tier 1)
- Bestehend: Keycloak (ns `home`-Eco, `id.openedusuite.example.org`, Realm `opendesk`)
- Bestehend: App-APIs — SOGo/JMAP, OpenProject/REST, Nextcloud/WebDAV+OCS, XWiki/REST, ILIAS/REST, Element/Matrix
- Neu: Connector Runtime (Node.js, ns `opendesk-edu`), Browser-Companion-SPA, Manifest-Spec
- OSS-Bausteine: `@mlc-ai/web-llm`, Web Crypto (native), `ajv` (JSON-Schema-Validierung)
