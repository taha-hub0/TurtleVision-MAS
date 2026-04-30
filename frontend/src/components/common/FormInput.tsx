import React from 'react'

interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

const FormInput: React.FC<FormInputProps> = ({ label, error, className, ...props }) => (
  <div className="flex flex-col">
    {label && <label className="text-sm font-medium text-slate-700 mb-2">{label}</label>}
    <input
      {...props}
      className={`border border-slate-300 rounded-lg px-4 py-2 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all ${error ? 'border-red-500' : ''} ${className || ''}`}
    />
    {error && <span className="text-red-500 text-xs mt-1">{error}</span>}
  </div>
)

export default FormInput
