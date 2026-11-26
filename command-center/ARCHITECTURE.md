# Sahab Command Center — system of record and agent orchestration

## Single inbox / intake
Input sources: founder's app notes, private Sheets registry, Drive metadata/search, existing Sahab OS CRM, GitHub/Railway inventory, daily market research, and approved inbox digests. Each fact carries its provenance, timestamp, status and account scope. Duplicate detection uses source URL and type/name. Sensitive documents remain in their original access-controlled systems.

## Project ledger
Type: product, agency operating system, client, idea, study, document, contract/proposal, task, market opportunity, decision/memory.

## Agent roster (planned, not executing)
- Market researcher: source-backed competitor/user/market research.
- Feasibility analyst: unit economics, margin, cash flow and risk.
- Product planner: scoped PRD and acceptance criteria.
- Engineering implementer: proposed implementation, test and deployment plan.
- QA/security reviewer: auth, tenant scoping, quality and regression gates.
- Launch operator: go-to-market, reporting and explicit publication approval.

## Execution contract for future server agents
1. Intake item stored with immutable source and reference.
2. Orchestrator classifies and proposes agent roles, costs and deadlines.
3. Queue jobs are idempotent, scoped to one tenant and have explicit resource budgets.
4. Agents produce artifacts and evidence; no secrets in prompt logs or public repositories.
5. Critical actions are drafts requiring founder approval: customer sends, contracts, billing, ads, deployments, trading, data deletion and access grants.
6. Store feedback, approvals, outcomes and cited decisions in versioned memory.
7. Notify through app and cross-device push once a server subscription is active.
8. Measure execution success; do not label agent tasks complete without evidence.

## Status 2026-11-12
- GitHub Pages: published source at `command-center/` with responsive RTL layout, encrypted local vault, project/client/file catalog, intake, agent blueprint generator, Google OAuth client-configuration screen, private Sheet read/append, Drive metadata search.
- Google OAuth requires one-time Google Cloud Web Client ID and user consent; Google-only app login is **not finished**.
- Google connected operations are user-browser mediated. No background web server.
- Private register contains 83 initial records in Google Sheets.
- Existing ChatGPT daily research and operations digests updated to append verified discoveries to the private register.
- Source project WhatsApp AI Employee is local Docker MVP, not live.

## Privacy
The GitHub repository is PUBLIC. Never commit internal client inventories, contracts, financial data, Gmail contents or access tokens to this source. Local vault uses Web Crypto AES-GCM+PBKDF2 and requires recovery backups. Google access tokens stay in memory. Production auth, RLS and backend audit are not provided by a static website.

## Development runtime
Serve the dashboard and API from the same origin. The static Pages deployment continues to support offline use.
On a Mac with Python 3.10+ run Start.command in Terminal and open the printed loopback address. Enter the vault passphrase, then the local server token under Portfolio. For a new encrypted bootstrap use its supplied vault passphrase.
For a hosted development instance build the command-center Dockerfile, mount a private persistent volume at /data and expose HTTPS. The single-owner access token is in /data/access. Use one replica and one Uvicorn worker. Back up the volume and both encryption keys securely. Configure OPENAI_API_KEY and optionally CENTER_MODEL in the server environment.
The browser syncs an encrypted vault snapshot every ten seconds while connected and unlocked. Divergent revisions prompt for an explicit restore after backup. A server worker processes submitted role-specific draft jobs independently of browser state, recovers interrupted jobs, and retains completed outputs for the next session. Only the selected project brief or the question context goes to the configured model. Outputs are drafts, without external research or execution privileges. Existing Google Sheets/Drive OAuth flows remain browser-based.

## GitHub scheduled execution
The existing Pages route uses scheduled-agents.js to send role/context jobs to the private registry's مهام وكلاء المركز tab through the existing Google OAuth session. The نتائج وكلاء المركز tab is an append-only execution journal. Results restore on another device after Google connection. Raw input is written with RAW mode to avoid formula execution.

The Command Center Agents workflow runs at minutes 7,22,37,52. GitHub schedules can be delayed. Configure repository secrets CENTER_GOOGLE_CREDENTIALS (Google service-account JSON with access only to the private registry), CENTER_SHEET_ID, and OPENAI_API_KEY. The existing browser still needs its Google OAuth client ID configured. Use CENTER_MODEL as an optional repository variable.

One workflow concurrency group serializes processing. Each request is content-addressed. Six attempts per cycle and 24 per rolling day cap generation. The worker persists a running event before invoking the provider. An interrupted call becomes review-required, and provider failures remain failed. To retry, edit the task context and resubmit after reviewing the private journal. Completed drafts are surfaced as completed draft tasks. This does not grant agents deployment, sending, billing, trading or external research tools.

Validation covers deduplication, failure redaction and attempt budgets. Live model generation requires the configured secrets. No private payloads or results are uploaded as Actions artifacts or logs.
