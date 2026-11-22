import { useId, type ChangeEventHandler } from "react";
import { cn } from "../../lib/cn";
import { SearchIcon } from "../icons";

const fieldStyles =
  "w-full rounded-xl border border-white/10 bg-ink-900/80 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 transition focus:border-brand-400/70 focus:outline-none";

interface SearchFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function SearchField({
  label,
  value,
  onChange,
  placeholder,
  className,
}: SearchFieldProps) {
  const id = useId();
  const handleChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    onChange(event.target.value);
  };

  return (
    <div className={cn("relative", className)}>
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
      <input
        id={id}
        type="search"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className={cn(fieldStyles, "pl-9 pr-3")}
      />
    </div>
  );
}

interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps {
  label: string;
  value: string;
  options: readonly SelectOption[];
  onChange: (value: string) => void;
  className?: string;
}

export function SelectField({
  label,
  value,
  options,
  onChange,
  className,
}: SelectFieldProps) {
  const id = useId();
  const handleChange: ChangeEventHandler<HTMLSelectElement> = (event) => {
    onChange(event.target.value);
  };

  return (
    <div className={cn("relative", className)}>
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={handleChange}
        className={cn(fieldStyles, "appearance-none px-3 pr-9")}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500">
        ▾
      </span>
    </div>
  );
}
