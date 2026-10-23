import { createContext, useContext } from 'react'

// A small message at the bottom of the screen, like "Drill archived · Undo".
export type Toast = { message: string; action?: { label: string; run: () => void } }

export const ToastContext = createContext<(toast: Toast) => void>(() => {})

// Any component can call `const showToast = useToast()` and then `showToast({ message: '...' })`.
export const useToast = () => useContext(ToastContext)
