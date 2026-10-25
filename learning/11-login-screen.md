# Step 13: The login screen

- **Supabase client (`supabase-js`):** a library that talks to Supabase Auth for us: sign up, log in, log out, and keeping the login token fresh.
- **Publishable key:** a public id for the Supabase project, safe in the browser. It can't read our tables, because RLS blocks it. The *secret* key must never be in the frontend.
- **Session:** what Supabase gives you after logging in: an **access token** (the JWT our backend checks, valid about an hour) and a **refresh token** (used to get a new access token without typing your password again).
- **`onAuthStateChange`:** Supabase calls our function whenever the login changes (logged in, logged out, token refreshed). `AuthProvider` stores the session, and the app re-renders.
- **Login gate:** `LoggedInOnly` in `App.tsx` shows the login page when there's no session, and the real app when there is. Nothing else in the app needs to think about logins.
- **`Authorization: Bearer` header:** `api.ts` adds the access token to every request. On a 401 it logs out, so an expired or broken login sends you back to the login page.
- **`key` on a component:** `<TeamProvider key={user id}>`. When the key changes, React throws away the old component and starts fresh, so the next coach never sees the last coach's teams.
- **Email confirmation:** by default Supabase makes new users click a link in an email before they can log in. The link goes back to the Site URL (`http://localhost:5173`).
- **`VITE_` variables:** Vite only gives the browser code environment variables whose names start with `VITE_`, so server secrets can't leak into the frontend by accident.

My notes:
