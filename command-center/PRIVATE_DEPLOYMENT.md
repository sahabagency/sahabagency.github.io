# Sahab Command Center — private deployment / migration

Status: development branch, not deployed. No live account credentials or private data should be committed to GitHub. The media renderer produces silent text-card MP4 and PNG carousel ZIP files locally; live AI, avatar, footage editing, research feeds, publishing, and analytics need further integration.

## Run on an isolated Linux host with Docker
From the command-center directory:
1. Build: docker build -t sahab-command-center .
2. Set a unique CENTER_OWNER_PASSWORD of at least 24 characters in a private environment file (permissions 600; never commit it). Add OPENAI_API_KEY only if AI drafting is required.
3. Run: docker run -d --restart unless-stopped --name sahab-center --env-file /secure/path/sahab.env -p 127.0.0.1:8000:8000 -v sahab-data:/data sahab-command-center
4. Reverse proxy via HTTPS to the loopback port. Do not expose port 8000 directly. Configure HTTPS at the host before any credentials are entered.
5. The hosted HTML requires owner basic authentication; API calls require the separate generated token in /data/access (read privately on the server). Configure this token using the private server panel. Do not paste secrets into the public website.
6. Back up the complete /data volume, including encryption key, database and media, before migration. Restore it only to the private target.
7. Validate unauthenticated access is denied, then authenticated state access, AI job handling, media rendering and downloads. Test OAuth and publishing separately before enabling any external action.

## Offline smoke test
With Python and FFmpeg installed, from command-center: python -m unittest runtime.test_media

## Migration gate
Confirm hosting permits a persistent application process, private storage, HTTPS reverse proxy, FFmpeg, sufficient CPU and disk, and backups. Use a separate subdomain or virtual host; do not overwrite WordPress. Do not change DNS until the new system passes its checks. Existing static GitHub Pages is not an authenticated application host and must not be used for sensitive data.

The 14 content roles currently create draft tasks; they are not autonomous research/publishing workers. Rendering is explicit and local; public publication remains disabled. The private server is not yet verified in production.
