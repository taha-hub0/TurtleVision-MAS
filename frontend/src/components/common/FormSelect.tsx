import React from 'react'

interface FormSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options?: Array<{ value: string; label: string }>
}

const FormSelect: React.FC<FormSelectProps> = ({ label, error, options, className, ...props }) => (
  <div className="flex flex-col">
    {label && <label className="text-sm font-medium text-slate-700 mb-2">{label}</label>}
    <select
      {...props}
      className={`border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all ${error ? 'border-red-500' : ''} ${className || ''}`}
    >
      {props.children}
      {options?.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    {error && <span className="text-red-500 text-xs mt-1">{error}</span>}
  </div>
)

export default FormSelect
