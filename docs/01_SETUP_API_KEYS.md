# API keys and accounts — set up in this order

**None of this is needed to tailor resumes.** The core kit (template,
`build_resume.py`, `verify_resume.py`, `compile_pdf.py`) works with zero
keys. Do these steps only if you also want a phone digest, outreach email
drafts, or a hosted approval dashboard.

Every service has a free tier that covers a personal job search. Do them
one at a time and test each before moving on. Secrets live in `config/`
and are git-ignored — never commit them.

---

## Step 1 — Telegram bot (phone digest of your review queue)

1. Open Telegram, message **@BotFather**, send `/newbot`. Follow the
   prompts (any name; username must end in `bot`). It replies with a token
   like `123456789:AAExampleTokenText`.
2. Put the token in `config/profile.json`:
   ```json
   "messaging": { "channel": "telegram", "bot_token": "PASTE_HERE", "chat_id": "" }
   ```
3. Send your new bot any message ("hi") in Telegram.
4. Get your chat id (writes it back into `profile.json`):
   ```bash
   python scripts/telegram_setup.py chat_id
   ```
5. Test:
   ```bash
   python scripts/telegram_setup.py test
   ```
6. Send yourself the current review queue any time:
   ```bash
   python scripts/telegram_setup.py digest
   ```
   Schedule that daily with your OS scheduler for a morning digest. An
   always-on Approve/Pass listener is **not** in this kit — use the
   dashboard (Step 5).

**Secret:** `config/profile.json` (contains `bot_token`) — git-ignored.

---

## Step 2 — Gmail API (draft recruiter emails)

The OAuth scope is `gmail.compose` — **drafts only. No code path sends
mail. You send from your Drafts folder yourself.**

1. Go to <https://console.cloud.google.com/> and create a project (free).
2. **APIs & Services → Library** → search **Gmail API** → Enable.
3. **APIs & Services → OAuth consent screen** → User type **External** →
   fill app name + your email → **Add users** → add your own Gmail address
   as a test user → Save.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   → Application type **Desktop app** → Create.
5. **Download JSON** → save it as `config/gmail_client_secret.json`.
6. Run the consent flow (caches a refresh token to `config/gmail_token.json`):
   ```bash
   python scripts/gmail_auth.py
   ```
7. Test with a draft to yourself:
   ```bash
   python scripts/gmail_auth.py --test-draft you@example.com
   ```

**Secrets:** `config/gmail_client_secret.json`, `config/gmail_token.json`
— both git-ignored.

---

## Step 3 — SerpAPI (Google Jobs search) — optional

1. Sign up at <https://serpapi.com/> (free plan: 250 searches/month).
2. Save your key as a single line in `config/serpapi_key.txt`.
3. Set `discovery.serpapi.enabled` to `true` in `config/profile.json`.

This kit has no built-in Google Jobs poller — the key is here so your own
discovery scripts can use it. A country code (`gl`) is mandatory or Google
returns HTTP 200 with zero results.

**Secret:** `config/serpapi_key.txt` — git-ignored.

---

## Step 4 — Supabase (hosted database for the dashboard) — optional

1. Create an account and a project at <https://supabase.com/> (free tier).
2. **SQL Editor → New query** → paste the contents of
   `dashboard_app/schema.sql` → **Run**. Creates the `jobs` table.
3. **Project Settings → API** — copy these into
   `config/supabase_project.json` (copy the `.example.json` first):
   - `project_ref` — the subdomain in your project URL
   - `anon` public key
   - `service_role` secret key
4. Push your local tracker up / pull dashboard decisions down:
   ```bash
   python scripts/sync_supabase.py pull    # hosted -> local   (run FIRST)
   python scripts/sync_supabase.py push    # local  -> hosted  (run LAST)
   ```

**Secret:** `config/supabase_project.json` (contains the service_role key
— it bypasses row-level security; never put it in the browser bundle) —
git-ignored.

---

## Step 5 — Vercel (host the dashboard) — optional

1. Create an account at <https://vercel.com/> (free "Hobby" tier).
2. Install the CLI and log in:
   ```bash
   npm i -g vercel
   vercel login
   ```
3. Deploy from the dashboard folder:
   ```bash
   cd dashboard_app
   vercel            # first run: accept the defaults, link/create the project
   ```
4. Set environment variables on the Vercel project
   (**Project → Settings → Environment Variables**):
   | Name | Value |
   |---|---|
   | `SUPABASE_URL` | `https://<project_ref>.supabase.co` |
   | `SUPABASE_SERVICE_KEY` | your Supabase `service_role` key |
   | `DASHBOARD_PASSCODE` | any passphrase you choose |
5. Redeploy so the env vars take effect:
   ```bash
   vercel --prod
   ```
6. Open `https://<your-project>.vercel.app/?pass=<DASHBOARD_PASSCODE>` and
   confirm you see your jobs. Put the base URL in `config/profile.json` →
   `dashboard_url`.

The Supabase service key lives **only** in Vercel's env vars and
`config/supabase_project.json`, never in `dashboard_app/index.html`.

---

## Every secret file (all git-ignored)

```
config/profile.json                (bot_token, chat_id)
config/gmail_client_secret.json
config/gmail_token.json
config/serpapi_key.txt
config/supabase_project.json       (service_role key)
```

The repo ships `*.example.*` templates for the ones with a safe shape.
Before pushing, run `git status` and confirm none of the real files are
staged.
