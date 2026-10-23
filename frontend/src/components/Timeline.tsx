import { drillColor } from '../colors'
import { formatMinutes } from '../format'

type Segment = { key: number | string; drillId: number; name: string; minutes: number }

type Props = {
  segments: Segment[]
  sessionMinutes: number
}

// A bar showing how the practice is split up: one colored block per drill, sized by its minutes.
function Timeline({ segments, sessionMinutes }: Props) {
  const planned = segments.reduce((total, s) => total + s.minutes, 0)
  // If the drills go over the session length, the bar stretches to fit them and marks where the session ends.
  const scale = Math.max(planned, sessionMinutes, 1)
  const freePercent = Math.max(sessionMinutes - planned, 0) / scale * 100
  const endPercent = sessionMinutes / scale * 100

  return (
    <div className="timeline" aria-label={`${formatMinutes(planned)} planned of ${formatMinutes(sessionMinutes)}`}>
      {segments.map((segment) => (
        <div
          key={segment.key}
          className="timeline-segment"
          style={{ width: `${segment.minutes / scale * 100}%`, background: drillColor(segment.drillId) }}
          title={`${segment.name} · ${formatMinutes(segment.minutes)}`}
        >
          <span>{segment.minutes}′</span>
        </div>
      ))}
      {freePercent > 0 && <div className="timeline-free" style={{ width: `${freePercent}%` }} />}
      {planned > sessionMinutes && <div className="timeline-end" style={{ left: `${endPercent}%` }} />}
    </div>
  )
}

export default Timeline
