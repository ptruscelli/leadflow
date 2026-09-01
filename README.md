# Leadflow


Leadflow is a small CRM for a fictional agency Brightline Studios. Visitors send an enquiry on a public form. Staff sign in with a magic link and manage those enquiries as leads, in the staff portal.

The frontend is Next.js (live at [https://leadflow-iota-one.vercel.app](https://leadflow-iota-one.vercel.app)), but will not be functional until the backend is also running. The backend is FastAPI in Docker, with SQLite and Alembic. The live site talks to a backend on your machine at `http://localhost:8000`.

[Architecture diagram at the bottom of the page](#architecture-diagram)


## Getting it running


You need Docker, Node.js, uv for testing, and a Resend API key (free tier). The sender `noreply@auth.workwithvika.com` is already verified, so mail can go to any address.

To clone the repo:

```bash
git clone https://github.com/ptruscelli/leadflow.git
cd leadflow
```

### 1. Backend

```bash
cd backend
cp .env.example .env
```
NOTE: copy command on windows terminal is `copy` not `cp`

Edit `.env`:

- Put your Resend API key in `RESEND_API_KEY`.
- Add your email to `STAFF_ALLOWLIST` (comma-separated).

From the **repo root**:  

```bash
docker compose up --build
```

This runs migrations, starts the API on port 8000, and seeds demo leads if the database is empty. SQLite is stored in a Docker volume. 

The app should now be up and running !

 [https://leadflow-iota-one.vercel.app](https://leadflow-iota-one.vercel.app)

### 2. Sign in

1. Open staff login and enter an email that is on `STAFF_ALLOWLIST`.
2.  Check your email inbox for the link, **or** if `LOG_MAGIC_LINKS=True`, the full URL is printed to the logs as a fallback
3. Open the link. It is valid for 10 minutes and can only be used once.

The API never says whether an email is on the allowlist.

### 3. Local Frontend

To run Next locally instead of using the live Vercel app linked at the top:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Note that for a local frontend, FRONTEND_DOMAIN in backend/.env.example needs to be changed.

Local UI: [http://localhost:3000](http://localhost:3000).

### Tests

```bash
cd backend
uv sync
uv run pytest
```

GitHub Actions runs pytest and `docker compose build` on each push to `main`.

## Some design decisions

**Magic links last 10 minutes.** They should die in the inbox if unused.

**Sessions last 8 hours.** That covers a working day unless staff log out earlier.

**Tokens are stored as SHA-256 hashes and raw tokens are never stored in a db.** The raw value is only in the email, the logs, and the cookie.

**Staff live in `STAFF_ALLOWLIST`, not a users table.** A reviewer can be added from env. Sessions are checked against that list on each request, so removing an email ends access.

**Leads are soft-deleted** (`deleted_at`). They leave the main list and show up under Archive.

**Offset pagination** chosen over cursor, as offset seems better choice for admin tables, search results, and ability to jump to arbitrary page if needed.  Default page size is 10, max 50.

**Search** is `ILIKE` (SQL LIKE) on name, email, phone, and company. No index on those columns as a contains-search cannot use a normal B-tree. Token hashes already have unique indexes. `leads.status` is indexed for filtering. Uses escape_wildcards function to escape ILIKE wildcards.

**Cookies** are `HttpOnly`, `Secure` (when `SECURE_COOKIES=True`), and `SameSite=None` so the Vercel frontend can call the local API. That is a cross-site setup. CORS only allows the configured frontend origin and `http://localhost:3000`.

**Naive SQLite datetimes** are labelled UTC when the API returns them, so the UI shows the right local time.


### Summary of login flow

- Staff submit email; browser `POST /auth/magic-link`.
- If the email is on `STAFF_ALLOWLIST`, create a raw token, store only SHA-256, email `/auth/login?token=...` (and log it when the fallback is on). Always return the same 200 either way.
- Click loads the frontend; it `POST /auth/login` with `{ raw_token }`.
- API hashes the token, loads that row, rejects if missing, used, or past 10 minutes, then sets `used_at`.
- API creates a new session token, stores its hash, returns `Set-Cookie` (`HttpOnly`, 8 hours).
- Frontend sends the user to `/leads`; later requests send the cookie and `require_session` checks it.

## With more time

- Add playwright UI tests covering the login flow, enquiry form submission etc
- Add periodic or startup job to remove expired magic links and sessions from db 
- Composite index `(deleted_at`, `status)`
- GET /health endpoint ?
- Metrics/monitoring
- Index `created_at` / `updated_at` so staff can sort by date.
- Rate-limiting for `POST /auth/magic-link`.
- SQLite FTS5 for faster text search.
- Typescript

#### AI tools

This project was built using cursor. After setting up the NextJS structure and desired pages, a lot of the frontend react and tailwind code was AI generated with my direction and constraints.



### Architecture Diagram

[Architecture diagram](docs/architecture.html)