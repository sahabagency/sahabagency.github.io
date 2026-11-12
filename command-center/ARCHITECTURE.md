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
