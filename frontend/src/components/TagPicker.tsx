type Option<T> = { value: T; label: string }

type Props<T extends string> = {
  label: string
  options: readonly Option<T>[]
  selected: T[]
  onChange: (selected: T[]) => void
}

// A row of toggle chips. Click to add a tag, click again to remove it.
function TagPicker<T extends string>({ label, options, selected, onChange }: Props<T>) {
  function toggle(value: T) {
    // Keep the options' order, whatever order they were clicked in.
    const next = selected.includes(value) ? selected.filter((v) => v !== value) : [...selected, value]
    onChange(options.map((option) => option.value).filter((v) => next.includes(v)))
  }

  return (
    <fieldset className="tag-picker">
      <legend>{label}</legend>
      <div className="chips">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            className="chip"
            aria-pressed={selected.includes(option.value)}
            onClick={() => toggle(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </fieldset>
  )
}

export default TagPicker
