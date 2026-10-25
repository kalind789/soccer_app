// Turn the backend's raw values into what a coach wants to read.

// "2026-11-03" → "Tue, Nov 3, 2026"
export function formatDate(date: string): string {
  // Build the date from its parts. new Date("2026-11-03") would mean midnight UTC,
  // which is the evening before in US time zones.
  const [year, month, day] = date.split('-').map(Number)
  return new Date(year, month - 1, day).toLocaleDateString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

// "18:00:00" → "6:00 PM"
export function formatTime(time: string): string {
  const [hours, minutes] = time.split(':').map(Number)
  return new Date(2000, 0, 1, hours, minutes).toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  })
}

// 90 → "1 h 30 min"
export function formatMinutes(total: number): string {
  const hours = Math.floor(total / 60)
  const minutes = total % 60
  if (hours === 0) return `${minutes} min`
  if (minutes === 0) return `${hours} h`
  return `${hours} h ${minutes} min`
}

// "18:00:00" → "18:00", the format <input type="time"> wants.
export function toTimeInput(time: string): string {
  return time.slice(0, 5)
}

// The letter on a team's badge: the first word that isn't an age group or a year, so "U12 Eagles 2027" → "E".
export function teamInitial(name: string): string {
  const words = name.trim().split(/\s+/)
  const word = words.find((w) => !/^(u\d+|\d+)$/i.test(w)) ?? words[0] ?? '?'
  return word.charAt(0).toUpperCase()
}
