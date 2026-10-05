// Small visual building blocks shared by the Playbook pages.

const AVATAR_TONES = ["bg-vermilion", "bg-forest", "bg-[#7c3aed]", "bg-[#b45309]", "bg-[#0e7490]", "bg-[#be185d]"];

export function initials(name: string) {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function Avatar({ name, dark = false, size = "md" }: { name: string; dark?: boolean; size?: "sm" | "md" }) {
  const tone = AVATAR_TONES[[...name].reduce((s, c) => s + c.charCodeAt(0), 0) % AVATAR_TONES.length];
  const dims = size === "sm" ? "h-7 w-7 text-[10px]" : "h-10 w-10 text-xs";
  return (
    <span
      className={`flex shrink-0 items-center justify-center rounded-full font-semibold tracking-wide text-white ${dims} ${tone} ${
        dark ? "ring-2 ring-white/10" : "ring-2 ring-white"
      }`}
      aria-hidden="true"
    >
      {initials(name)}
    </span>
  );
}

export function Mark({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden="true">
      <rect width="64" height="64" rx="14" fill="#1d1b16" />
      <path d="M18 44 L32 16 L46 44" fill="none" stroke="#6ee7b7" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="32" cy="38" r="4" fill="#fb923c" />
    </svg>
  );
}

/** A circular progress ring. */
export function Ring({ value, size = 44, stroke = 4, children }: { value: number; size?: number; stroke?: number; children?: React.ReactNode }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  return (
    <span className="relative inline-flex shrink-0 items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="currentColor" strokeWidth={stroke} className="text-paper-3" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="currentColor"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - Math.min(1, Math.max(0, value)))}
          className="text-forest transition-[stroke-dashoffset] duration-700"
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center">{children}</span>
    </span>
  );
}
