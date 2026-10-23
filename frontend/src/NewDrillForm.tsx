import { useState, type FormEvent } from 'react'
import { createDrill, type Drill } from './api'

type Props = {
  // The parent passes this in, so it can refresh its list when a drill is added.
  onCreated: (drill: Drill) => void
}

function NewDrillForm({ onCreated }: Props) {
  const [name, setName] = useState('')
  const [objective, setObjective] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault() // Stop the browser from reloading the page, its default for forms.
    try {
      const drill = await createDrill({ name, objective, description })
      setName('')
      setObjective('')
      setDescription('')
      setError(null)
      onCreated(drill)
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <form className="card new-drill" onSubmit={handleSubmit}>
      <h2>New drill</h2>
      <label>
        Name
        <input value={name} onChange={(e) => setName(e.target.value)} maxLength={100} required />
      </label>
      <label>
        Objective
        <input value={objective} onChange={(e) => setObjective(e.target.value)} />
      </label>
      <label>
        Description
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
      </label>
      {error && <p className="error">{error}</p>}
      <button type="submit">Add drill</button>
    </form>
  )
}

export default NewDrillForm
