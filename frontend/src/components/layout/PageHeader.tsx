interface PageHeaderProps {
  eyebrow: string;
  title: string;
  description: string;
}

export function PageHeader({ eyebrow, title, description }: PageHeaderProps) {
  return (
    <div className="mb-10 max-w-3xl">
      <p className="mb-3 text-xs font-bold uppercase tracking-[0.24em] text-brand-300">
        {eyebrow}
      </p>
      <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl lg:text-5xl">
        {title}
      </h1>
      <p className="mt-4 text-base leading-relaxed text-slate-400">{description}</p>
    </div>
  );
}
