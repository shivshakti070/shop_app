Deployment plan — quick steps

Goal: host the FastAPI backend publicly and point the mobile app to the deployed URL.

Choose provider
- Quick: Railway (fast, GUI-driven)
- Robust: Fly.io + Supabase (Fly for container, Supabase for Postgres)

Prepare the backend (already done)
- `backend/Dockerfile` added
- `backend/requirements.txt` added
- `backend/database.py` reads `DATABASE_URL` (falls back to sqlite)
- `backend/auth.py` reads `SECRET_KEY` and token config from env
- `/health` endpoint added

Provision a Postgres DB (example: Supabase)
1. Create a Supabase project and copy the `DATABASE_URL` (connection string).
2. In Supabase settings find the connection string (Postgres) and keep it safe.

Deploy steps (Railway example)
1. Push this repo to GitHub.
2. Create a Railway project and connect the GitHub repo.
3. Add an environment variable `DATABASE_URL` with your Postgres connection string.
4. Optionally add `SECRET_KEY` env var for JWT.
5. Deploy — Railway will build the Dockerfile and run `uvicorn main:app`.
6. After deployment, open the app URL and check `/health`.

Postgres migration
1. In the Railway or Supabase dashboard, create the database (already created by provider).
2. Run the app once with `DATABASE_URL` configured so tables are created (`Base.metadata.create_all` runs in `main.py`).
3. Export/Import data:
   - Option A: Use `backend/migrate_sqlite_to_postgres.py` locally. Set env vars and run:

```bash
export DATABASE_URL="postgres://..."
python migrate_sqlite_to_postgres.py
```

   - Option B: Export tables to CSV from SQLite and import into Supabase or psql.

Update mobile app
1. Once backend has a public URL (e.g., `https://myshop.fly.dev`), update `mobile/src/config.ts` or set `global.__API_HOST__` to the host.
2. For Expo Go testing, no additional steps needed for users beyond installing Expo Go and opening the app QR.

Testing
- Test `POST /auth/signup`, `POST /auth/token`, `GET /inventory/` from a device not on your LAN.

Notes
- For production, secure `SECRET_KEY` and do not use `allow_origins=['*']` in CORS.
- Consider adding backups and monitoring for the Postgres DB.
