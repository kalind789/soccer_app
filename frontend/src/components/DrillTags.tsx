import type { Drill } from '../api'
import { ageLabel, goalLabel, isForAllAges } from '../tags'

// A drill's tags as small chips: goals first (what it works on), then who it's for.
function DrillTags({ drill }: { drill: Pick<Drill, 'age_groups' | 'goals'> }) {
  if (drill.goals.length === 0 && drill.age_groups.length === 0) return null
  return (
    <ul className="tags" aria-label="Tags">
      {drill.goals.map((goal) => (
        <li key={goal} className="tag goal">
          {goalLabel(goal)}
        </li>
      ))}
      {isForAllAges(drill.age_groups) ? (
        <li className="tag age">All ages</li>
      ) : (
        drill.age_groups.map((age) => (
          <li key={age} className="tag age">
            {ageLabel(age)}
          </li>
        ))
      )}
    </ul>
  )
}

export default DrillTags
