"use client";

// A plain-text whiteboard for design answers: Mermaid, ASCII boxes-and-arrows or a component list.
// It is sent to the interviewer with every reply and to the grader with the final score, so the
// diagram is judged as text. No drawing library and no CDN: what you type is what gets graded.

export const DIAGRAM_MAX = 8000;

const MERMAID = `flowchart LR
  user[Client] -->|HTTPS| api[API gateway]
  api --> svc[Service]
  svc --> db[(Store)]
`;

const ASCII = `[Client] --HTTPS--> [API gateway] --> [Service] --> (Store)
                                         |
                                         +--> [Queue] --> [Worker]
`;

export default function DesignBoard({
  value,
  onChange,
  readOnly = false,
  constraints = [],
  rows = 12,
  id = "design-board",
}: {
  value: string;
  onChange: (v: string) => void;
  readOnly?: boolean;
  /** Constraints the interviewer has introduced so far, pinned above the board. */
  constraints?: string[];
  rows?: number;
  id?: string;
}) {
  const insert = (snippet: string) => onChange((value.trim() ? `${value.replace(/\s+$/, "")}\n\n` : "") + snippet);
  const over = value.length > DIAGRAM_MAX;
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex flex-wrap items-center gap-2 px-4 pt-3">
        <label htmlFor={id} className="font-mono text-xs uppercase tracking-wider text-gray-300">
          Whiteboard
        </label>
        <span className="text-[11px] text-console-muted">Mermaid, ASCII or a component list. Sent with every reply.</span>
        {!readOnly && (
          <span className="ml-auto flex gap-1.5">
            <button type="button" onClick={() => insert(MERMAID)} className="rounded-md border border-console-line px-2 py-0.5 text-[11px] text-gray-300 hover:bg-console-2">
              + Mermaid
            </button>
            <button type="button" onClick={() => insert(ASCII)} className="rounded-md border border-console-line px-2 py-0.5 text-[11px] text-gray-300 hover:bg-console-2">
              + ASCII
            </button>
          </span>
        )}
      </div>
      {constraints.length > 0 && (
        <ul className="mx-4 mt-2 space-y-1 rounded-lg border border-amber-400/30 bg-amber-400/5 px-3 py-2" aria-label="Constraints so far">
          {constraints.map((c, i) => (
            <li key={i} className="flex gap-2 text-[12px] leading-snug text-amber-100">
              <span className="shrink-0 font-mono text-[10px] uppercase tracking-wider text-amber-300">Constraint {i + 1}</span>
              <span>{c}</span>
            </li>
          ))}
        </ul>
      )}
      <textarea
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        readOnly={readOnly}
        rows={rows}
        spellCheck={false}
        wrap="off"
        aria-describedby={`${id}-count`}
        placeholder={"flowchart LR\n  client --> gateway --> service --> store"}
        className="mx-4 mt-2 min-h-[9rem] flex-1 resize-y overflow-auto whitespace-pre rounded-lg border border-console-line bg-console-2 p-3 font-mono text-[13px] leading-relaxed text-gray-100 placeholder:text-console-muted focus:border-emerald-400/60 focus:outline-none"
      />
      <p id={`${id}-count`} className={`px-4 pb-3 pt-1 text-right font-mono text-[11px] ${over ? "text-amber-300" : "text-console-muted"}`}>
        {value.length} / {DIAGRAM_MAX} characters{over ? " · only the first 8,000 are sent" : ""}
      </p>
    </div>
  );
}
