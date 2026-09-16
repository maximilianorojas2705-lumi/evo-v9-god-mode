# Repository Notes

## General

- This repository is the OpenHands frontend.
- Frontend API adaptation lives mainly in `src/api/`:
  - `option-service` fabricates a web-client config and reads models/providers through `@openhands/typescript-client` LLM endpoints.
  - `settings-service` uses `@openhands/typescript-client` settings APIs for persistence; reads schemas from `/api/settings/agent-schema` and `/api/settings/conversation-schema`, fetches settings with optional `X-Expose-Secrets: encrypted` header for conversation start payloads, and saves settings via PATCH with diffs.
  - `agent-server-conversation-service`, `event-service`, `agent-server-git-service`, and `skills-service` route local agent-server access through `@openhands/typescript-client` rather than direct HTTP calls.
- Supported env vars for deployment:
  - `VITE_BACKEND_BASE_URL` for the agent server base URL.
  - `VITE_SESSION_API_KEY` for optional session auth.
  - `VITE_WORKING_DIR` for the default workspace path sent when starting conversations.
  - `VITE_ENABLE_BROWSER_TOOLS=false` to omit the `browser_tool_set` tool from new conversation payloads.
  - `VITE_BASE_PATH` for serving the SPA under a subpath such as `/canvas`; pair it with `scripts/static-server.mjs --base-path` at runtime.
- Public skills are loaded from the `@openhands/extensions` npm package at build time via `SKILLS_CATALOG` (exported from `@openhands/extensions/skills`). The frontend's `SkillsService` maps catalog entries to `SkillInfo` objects and merges them with user/project skills fetched from the agent-server (with `load_public: false`). Bundled catalog skills use the persisted `enabled_skills` allow-list (defaulted from `DEFAULT_ENABLED_SKILL_NAMES`); user/project skills remain enabled unless named in `disabled_skills`. Keep this logic centralized in `src/utils/skill-enablement.ts`. The agent-server no longer clones the extensions repo or uses `EXTENSIONS_REF` for public skills.
- Default working-dir fallback is now the relative path `workspace/project` (exported as `DEFAULT_WORKING_DIR` from `src/api/agent-server-config.ts`); git-path heuristics and the default PLAN preview path should reuse that constant instead of hardcoding `/workspace/project`.
- Current Cloud behavior is implemented explicitly through the backend registry, Cloud service layer, and device authorization flow.
- Primary verification commands: `npm run lint`, `npm test`, `npm run build`, and `npm run build:lib`.
- GitHub automation now includes `.github/workflows/ci.yml` for `npm ci`, `npm test`, and `npm run build`, plus `.github/dependabot.yml` with weekly npm/github-actions updates gated by a 7-day cooldown.

## Repository Map — what belongs where

This repo (`OpenHands/OpenHands`) is **only the agent-canvas frontend**. It is one
piece of a multi-repo system. Before adding code here, check the change belongs in
*this* repo — several kinds of work belong in a sibling repo instead.

| Repo | Owns | Add code here when… |
|------|------|---------------------|
| **`OpenHands/OpenHands`** (this repo) | The React/TypeScript **frontend** (agent-canvas): UI, routes, frontend services in `src/api/` that *consume* backend APIs. | You are changing UI, frontend state, or how the frontend *calls* an existing backend endpoint. |
| **`OpenHands/software-agent-sdk`** | The Python **SDK + agent-server**: agents, tools, conversations, events, and the REST/WebSocket **API surface** (`openhands-sdk`, `openhands-tools`, `openhands-agent-server`, `openhands-workspace`). | You are adding or changing a backend endpoint, agent/tool behaviour, or server-side logic. New API **endpoints** live here, not in the frontend. |
| **`OpenHands/typescript-client`** (`@openhands/typescript-client`) | The generated/maintained **TypeScript client** that mirrors the agent-server API. The frontend's *only* sanctioned way to reach the agent-server (see "API Access Rules"). | You are adding client-side **access to an agent-server endpoint** (typed client method, request/response types). API-access code belongs here, **not** re-implemented in this repo. |
| **`OpenHands/extensions`** (`@openhands/extensions`) | Public **skills, automations, and integrations** (loaded here at build time via `SKILLS_CATALOG`). | You are adding or editing a skill, automation, or MCP integration. |

Common mis-placements to avoid:

- **API endpoint access** → belongs in `typescript-client`, then consumed here. Do **not**
  add raw `axios`/`fetch` endpoint code to the frontend (CI guard:
  `src/api/no-direct-agent-server-calls.test.ts`; see "API Access Rules").
- **New server endpoints / agent or tool logic** → belongs in `software-agent-sdk`.
- **Skills / automations / integrations** → belong in `extensions`.

## Cross-Repository Boundaries

The four repositories have distinct ownership boundaries:

| Repository | Owns |
|---|---|
| [`OpenHands/OpenHands`](https://github.com/OpenHands/OpenHands) | Agent Canvas frontend, user-facing control center, backend selection, and local-stack orchestration. |
| [`OpenHands/software-agent-sdk`](https://github.com/OpenHands/software-agent-sdk) | Python SDK, Agent Server, agent/tool behavior, conversations, workspaces, events, and the canonical server API. |
| [`OpenHands/typescript-client`](https://github.com/OpenHands/typescript-client) | Browser-compatible TypeScript client and generated/maintained types for the Agent Server API. |
| [`OpenHands/automation`](https://github.com/OpenHands/automation) | Automation definitions, scheduling, webhooks, run history, and dispatching. It manages when automations run; the Agent Server/SDK executes them. |

The usual dependency direction is `software-agent-sdk` / Agent Server → OpenAPI contract → `typescript-client` → Agent Canvas. Automation scheduling and dispatching flow from Agent Canvas to `automation`, which starts work on the Agent Server/SDK. Put new server behavior and endpoints in `software-agent-sdk`, client access in `typescript-client`, UI and frontend integration in this repository, and scheduling/webhook lifecycle behavior in `automation`.

All pull requests for this repository must comply with [`.agents/skills/custom-codereview-guide.md`](.agents/skills/custom-codereview-guide.md), in addition to the general contribution requirements and CI checks.


## PR Description Human Check

The `HUMAN:` section in PR descriptions is reserved for human contributors only.
AI agents MUST NOT add to, edit, move, or remove it. If the PR description
CI fails because the section is missing or empty, stop and ask the
human user to update it in their own words. If the section was already updated
by a human, report the exact validator error rather than editing it yourself.

## Tracking / Analytics Architecture

One Canvas-owned PostHog client owns telemetry and app analytics.

- `src/services/telemetry.ts` is the only module that accesses the named `agent-canvas` PostHog client. The name isolates Canvas identity, persistence, configuration, and consent from an embedding host's default singleton. React code declares Cloud user identity and event context through the service and captures through the service; it never receives, identifies, or resets the SDK client directly.
- `TelemetryProvider` configures bootstrap/runtime options, eagerly initializes the service, and is the sole owner of the `useTelemetry()` lifecycle that emits install/session events. Do not mount that lifecycle hook separately in Canvas routes or internal components. The provider does not expose PostHog context or maintain a second client lifecycle.
- The default PostHog key and direct ingestion host live in `config/defaults.json` under `telemetry`. Local launchers (`dev-with-automation`, `dev-static`, published binary path) and Docker default `AUTOMATION_POSTHOG_API_KEY` from explicit automation env, then `VITE_POSTHOG_API_KEY`, then that shared default key, so the automation backend can emit local consent-gated telemetry without extra user config. Keep `VITE_DO_NOT_TRACK=1` disabling the zero-config default.
- Unconfigured source builds use the staging key and route through `https://z.openhands.dev`. Release workflows pass the public production key through `VITE_POSTHOG_API_KEY`. Precompiled npm consumers override `apiKey`, `apiHost`, and `uiHost` at runtime through `AgentServerUIProviders.analytics` or `configureTelemetry()`.
- `setTelemetryConsent` is the only user-consent controller; `configureTelemetry(false)` is the embedding host's hard disable. An explicit first-run browser decision remains pending across local backends until `useSyncTelemetryConsent` persists it to Cloud; a stale/default backend value must not overwrite that newer choice during login or navigation. Once Cloud confirms the choice, backend `user_consents_to_analytics` changes are authoritative and mirrored to the client. No other hook or component should call `opt_in_capturing` / `opt_out_capturing` directly.
- `subscribeTelemetryConsent` is the sole React-facing consent store. Hooks that render consent state must use `useSyncExternalStore`; do not mirror consent in component state or gate events outside `telemetry.ts`.
- `canvas_install` fires once, pre-consent, with the client's anonymous distinct ID. After consent and Cloud authentication, Canvas identifies PostHog with the stable Cloud user ID so PostHog joins the earlier anonymous activity to that person. Merely switching to a local backend clears Cloud event context without resetting the identified person; a resolved logout/account change, consent revocation, or privacy clear owns the reset. Local-only and never-authenticated traffic remains on the anonymous browser/install ID. Cloud account context (`cloud_user_id`, `cloud_user_email`, `cloud_org_id`) is attached as event properties only while a Cloud backend is active.
- `telemetry.ts` adds immutable `client_source`, `client_version`, `package_name`, and `package_version` properties in `before_send`, so reset cannot remove attribution and event producers cannot override it. Repeated business milestones use deterministic PostHog `$insert_id` values instead of process-local caches.
- `trackEvent` and `useTelemetry` remain the public library telemetry API for npm consumers (the `TelemetryConsentBanner` component was removed; hosts needing a consent UI build their own on `useTelemetry`). Non-React state machines use typed functions in `cloud-funnel-analytics.ts`; they do not call `trackEvent` directly.
- React app events use typed functions in `src/hooks/use-tracking.ts`; components never call `posthog.capture()` raw. The hook attaches `current_url` automatically and captures through the telemetry service; Cloud account email is attached centrally as `cloud_user_email` while Cloud context is active. It may read backend settings for event properties, but must never gate capture on a settings snapshot: `useSyncTelemetryConsent` has already mirrored the authoritative decision to the telemetry service, and settings can be stale during a backend transition.
- A business milestone has one canonical event capture. Do not conditionally switch between telemetry and app clients or emit duplicate events.

### Cloud funnel observability
- OAuth device authorization and Cloud conversation-start requests include the coarse `X-OpenHands-Client: agent_canvas` and `X-OpenHands-Client-Version` headers from `src/api/client-source.ts`. Never put device codes, API keys, conversation content, raw hosts, or other user data in these headers.
- Production ingress must retain those two headers as structured Datadog facets before source-specific operational queries will work.
- The consented OSS funnel uses typed `cloud_device_authorization_started`, `cloud_device_authorization_succeeded`, and `cloud_conversation_ready` events from `cloud-funnel-analytics.ts`; React emits the canonical `backend_added` event through `useTracking`.

### Adding a new event
1. Add a typed function to `useTracking` in `src/hooks/use-tracking.ts`
2