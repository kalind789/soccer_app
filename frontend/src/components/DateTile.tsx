// A small calendar-page tile: "TUE / 3 / NOV".
function DateTile({ date, muted = false }: { date: string; muted?: boolean }) {
  const [year, month, day] = date.split('-').map(Number)
  const value = new Date(year, month - 1, day)
  return (
    <div className={muted ? 'date-tile muted' : 'date-tile'} aria-hidden="true">
      <span className="date-tile-weekday">{value.toLocaleDateString(undefined, { weekday: 'short' })}</span>
      <span className="date-tile-day">{day}</span>
      <span className="date-tile-month">{value.toLocaleDateString(undefined, { month: 'short' })}</span>
    </div>
  )
}

export default DateTile
