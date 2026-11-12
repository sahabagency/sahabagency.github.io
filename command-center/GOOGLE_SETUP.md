# Sahab Command Center — Google connection (v2)

This page is a **public static frontend** with a **locally encrypted vault**. It does **not** yet provide backend-enforced Google-only sign-in. Do not store credentials in this repository.

## One-time Google Cloud setup

1. Open https://console.cloud.google.com/auth/clients with the desired Google Cloud account and select/create a Cloud project.
2. Configure Google Auth Platform branding, consent and audience. For an external Testing app, include the intended Google account as a test user. For a Workspace Internal app, follow your administrator's policy.
3. Enable **Google Sheets API** and **Google Drive API** for the same Cloud project.
4. Create an OAuth 2.0 client of type **Web application**.
5. Under **Authorized JavaScript origins**, enter exactly:

   `https://sahabagency.github.io`

6. Copy the **OAuth Client ID** ending in `.apps.googleusercontent.com`. Do not paste a client secret into the web app or this GitHub repo.
7. Open https://sahabagency.github.io/command-center/, unlock the local encrypted vault, open **الإعدادات**, paste the Client ID, save and select **ربط حساب Google**.
8. Approve the requested Google scopes: identity/email, Google Sheets access (read and append to the central private registry), and Drive **metadata-only** access. No Gmail access is requested by the website.
9. The application restricts the selected Google account to the founder's configured account as a convenience check. **This is not secure backend authorization**; the protected data is the browser-encrypted vault and the private Google Sheet permissions. A server with verified sessions and row-level security is required for enforceable user roles.
10. On successful authorization the site fetches the private register from Google Sheets and recent Drive metadata; it can search Drive on demand and append **new locally created records** to the private register when authorized.

## The private register

The authenticated Google Sheets file is:
`https://docs.google.com/spreadsheets/d/1QWkzo383aW1Px1YKluSRCElcgXq2WO-U83zuO9BAXFA/edit`

- Worksheet: `السجل المركزي`.
- Columns: type, name, scope, status, source URL, description/decision, tags, priority, due date.
- Never publish or expose this registry via GitHub Pages.
- Daily ChatGPT automations may append verified new records to this private Sheet after deduplication. Website sync requires a live interactive Google authorization session and does not run on a closed device.

## Current operational limits

- Google-only account login: **NOT ENABLED**; secure backend and Google OAuth provider configuration required.
- Database-backed synchronized memory: **NOT ENABLED**; the site stores locally encrypted records and uses a private Google Sheet as a connected register when authorized.
- Live autonomous AI agents: **NOT ENABLED**. The agent center builds typed task blueprints and approval gates.
- Push notifications while all devices are closed: **NOT ENABLED in the site**; ChatGPT daily automations provide external digests separately.
- Drive document-content indexing / embeddings: **NOT ENABLED**; metadata and file links are available on demand.
- WhatsApp AI Employee: local MVP only; independent product, not deployed.
- No automatic publishing, messages, budget changes, trading actions or production deployments.

## Next backend milestone

Deploy a private application backend after infrastructure is available. Add Google OAuth session verification, per-user RLS, provider token vault, scheduled ingestion, document retrieval and source attribution, versioned memory, an agent job queue with retry/idempotency, approval workflow and audit logs, telemetry, and mobile/web push notification service. Confirm cost before provisioning infrastructure.

