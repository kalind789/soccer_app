import type { Session } from '@supabase/supabase-js'
import { createContext, useContext } from 'react'

// undefined = still checking, null = logged out.
export const AuthContext = createContext<Session | null | undefined>(undefined)

// Any component can call `const session = useSession()` to see who is logged in.
export const useSession = () => useContext(AuthContext)
