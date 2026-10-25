import { createClient } from '@supabase/supabase-js'

// The Supabase client, used only for logging in. Our data still goes through our own backend (api.ts).
// Both values are public: the publishable key only identifies the project.
const url = import.meta.env.VITE_SUPABASE_URL
const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY
if (!url || !key) {
  throw new Error('Set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY in frontend/.env.local')
}

// It keeps the login in localStorage and refreshes the token before it expires.
export const supabase = createClient(url, key)
