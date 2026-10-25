# 14. Deployment

The app runs in three places, and each one is someone else's computer:

| Piece | Host | What it is there |
|---|---|---|
| Frontend (React) | **Vercel** | Plain files (HTML, JS, CSS) from `npm run build`, served from a CDN |
| Backend (FastAPI) | **Render** | A Python process that's always waiting for requests (or asleep, on the free plan) |
| Database + logins | **Supabase** | Already hosted; nothing changes |

## Terms

- **Deploy:** copy the code to the host, build it, and start it. Both hosts deploy by themselves on every push to `main`. That's the "CD" (continuous deployment) half of CI/CD.
- **Environment variables in production:** `.env` files are gitignored, so they never reach the host. You type the same values into each host's dashboard instead. `render.yaml` lists them with `sync: false`, which means "ask in the dashboard; never put the value in git".
- **Build time vs run time (Vite):** `VITE_...` variables are pasted into the JavaScript *when it's built*. After changing one on Vercel you must redeploy, or the old value stays in the files.
- **Blueprint (`render.yaml`):** infrastructure as code: the service's settings live in the repo instead of only in dashboard clicks, so they're reviewed and versioned like code.
- **Health check:** Render calls `/health` after starting the new version. Only when it answers does traffic switch over, so a broken deploy never replaces a working one.
- **Cold start:** free Render services sleep after 15 minutes without requests. The first request afterwards waits about a minute while it wakes.
- **SPA rewrite (`frontend/vercel.json`):** there is only one real page, `index.html`; React Router draws `/teams/3` in the browser. Opening `/join/abc` directly would ask Vercel for a file that doesn't exist (404). The rewrite answers every path with `index.html`. Real files like `/assets/index-x1.js` are still served first.
- **Redirect allow-list (Supabase):** after a Google login or an email confirmation, Supabase only sends people back to addresses on its list. That stops an attacker from sending a login link that returns the token to their own site.

## Why migrations run in the build

`alembic upgrade head` needs to run before the new code starts, or the code might ask for a column that doesn't exist yet. Render's "pre-deploy command" is made for that, but free services don't have it, so it runs at the end of the build. Migrations here only ever add, so the old code keeps working for the minute until the new one takes over.
