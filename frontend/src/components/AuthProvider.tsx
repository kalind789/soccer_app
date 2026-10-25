import type { Session } from '@supabase/supabase-js'
import { useEffect, useState, type ReactNode } from 'react'
import { AuthContext } from '../authContext'
import { supabase } from '../supabase'

// Keeps track of who is logged in and shares it with every component.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null | undefined>(undefined)

  useEffect(() => {
    // Called once right away with the saved login (or null), then on every log in, log out and token refresh.
    const { data } = supabase.auth.onAuthStateChange((_event, newSession) => setSession(newSession))
    return () => data.subscription.unsubscribe()
  }, [])

  return <AuthContext.Provider value={session}>{children}</AuthContext.Provider>
}
