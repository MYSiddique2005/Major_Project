interface FilterDropdownProps {
  label: string
  value: string
  options: readonly string[]
  onChange: (value: string) => void
  formatOption?: (option: string) => string
}

/** A select with an "All" option; the empty string means no filter. */
export function FilterDropdown({ label, value, options, onChange, formatOption }: FilterDropdownProps) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      aria-label={`Filter by ${label.toLowerCase()}`}
      className="field w-full sm:w-auto"
    >
      <option value="">All {label.toLowerCase()}</option>
      {options.map((option) => (
        <option key={option} value={option}>
          {formatOption ? formatOption(option) : option}
        </option>
      ))}
    </select>
  )
}
