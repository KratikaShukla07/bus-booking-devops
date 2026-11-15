You are helping me finish and verify my DevOps assessment project: “Cloud Deployment & CI/CD – Bus Booking Platform” (FastAPI + PostgreSQL + Docker Compose + Nginx + GitHub Actions).

Work inside the existing repository; do not replace it with an unrelated app. First inspect every file, then:
1. Run tests and fix all failures.
2. Verify SQLAlchemy partial unique index works on PostgreSQL and SQLite; add a real concurrent duplicate-booking test if practical.
3. Verify Docker Compose config, startup ordering, health checks, volume persistence, and backup/restore scripts.
4. Improve security and reproducibility without adding unnecessary complexity. Keep API non-root, DB unexposed, secrets out of Git.
5. Ensure CI runs compile/lint/tests/build/Trivy scan and tags the image with commit SHA. Do not fabricate a GitHub run, cloud URL, screenshots, TLS certificate or evidence.
6. Check every README command on Windows PowerShell and Linux/macOS; add exact commands for both where needed.
7. Make sure seed trips are valid future dates and booking validation handles route stops, travel date, seat range, cancellation and duplicate requests.
8. Add a concise demo script (3–5 minutes) and likely technical interview questions with accurate answers.
9. Report what you actually ran, exact results, remaining gaps and the next commands I must run. Never claim an external deployment or CI success unless verified.

Assessment constraints: only trip and seat reservation API; no full passenger booking product. Required evidence: green CI, image tag/digest, health/logs, duplicate seat conflict, failure/recovery, backup/restore, architecture and runbook. Be honest about local-only deployment and unfinished HTTPS if no valid cert is installed.
