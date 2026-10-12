"use client";

// /start: role, interview date, hours and background; a 10-question self-check; a self-rating per
// skill area; then a week-by-week plan with a countdown. Saved to /api/profile (diagnostic jsonb),
// or to this browser when the profile service isn't available.

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AREAS, QUESTIONS, RATING_LABELS, buildPlan } from "./SiteDiagnostic";
import { countdownText, daysUntil, useProfile } from "./SiteProfile";
import { ROLE_LABEL, ROLE_TRACKS, type Diagnostic, type PlanModule, type RoleTrack } from "./SiteTypes";

const BACKGROUNDS = ["Software engineer", "ML or data engineer", "Solutions or sales engineer", "Consultant or architect", "Product or other"];

const STATUS_STYLE: Record<string, [string, string]> = {
  do: ["Do", "bg-graphite text-paper"],
  skim: ["Skim", "bg-amber-100 text-amber-900"],
  skip: ["Graded tasks only", "border border-rule text-graphite-2"],
};

function Step({ n, title, children }: { n: number; title: string; children: React.ReactNode }) {
  return (
    <section aria-labelledby={`step-${n}`} className="rounded-3xl border border-rule bg-white/70 p-5 sm:p-6">
      <p className="font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-vermilion">Step {n}</p>
      <h2 id={`step-${n}`} className="mt-1 font-serif text-2xl font-semibold text-graphite">
        {title}
      </h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

export default function SiteOnboarding({ modules, roles }: { modules: PlanModule[]; roles: RoleTrack[] }) {
  const { profile, source, save } = useProfile();
  const [role, setRole] = useState<RoleTrack | "">("");
  const [date, setDate] = useState("");
  const [hours, setHours] = useState(8);
  const [background, setBackground] = useState("");
  const [answers, setAnswers] = useState<number[]>(() => QUESTIONS.map(() => -1));
  const [ratings, setRatings] = useState<Record<string, number>>({});
  const [result, setResult] = useState<Diagnostic | null>(null);
  const [editing, setEditing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveNote, setSaveNote] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (source === "loading" || loaded) return;
    setLoaded(true);
    if (!profile) return;
    if (profile.targetRole && roles.includes(profile.targetRole)) setRole(profile.targetRole);
    if (profile.interviewDate) setDate(profile.interviewDate);
    if (profile.hoursPerWeek) setHours(profile.hoursPerWeek);
    if (profile.background) setBackground(profile.background);
    const d = profile.diagnostic;
    if (d && d.version === 1 && Array.isArray(d.plan)) {
      if (Array.isArray(d.answers) && d.answers.length === QUESTIONS.length) setAnswers(d.answers);
      if (d.ratings) setRatings(d.ratings);
      setResult(d);
      setEditing(false);
    }
  }, [source, profile, loaded, roles]);

  const today = useMemo(() => {
    const n = new Date();
    return `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, "0")}-${String(n.getDate()).padStart(2, "0")}`;
  }, []);
  const answered = answers.filter((a) => a >= 0).length;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!role) return setError("Pick the role you're preparing for.");
    if (answered < QUESTIONS.length) return setError(`Answer all ${QUESTIONS.length} questions (${QUESTIONS.length - answered} left). "Not sure" is fine: pick your best guess.`);
    setError(null);
    const diagnostic = buildPlan({ modules, role, interviewDate: date || null, hoursPerWeek: hours, answers, ratings });
    setResult(diagnostic);
    setEditing(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
    const err = await save({ targetRole: role, interviewDate: date || null, hoursPerWeek: hours, background: background || null, diagnostic });
    setSaveNote(err ? `Your plan is shown but couldn't be saved: ${err}` : null);
  };

  if (source === "loading") return <p className="text-sm text-graphite-3">Loading…</p>;

  if (result && !editing) {
    const days = daysUntil(date || null);
    const over = result.totalHours > result.capacityHours;
    const planRole = (role || profile?.targetRole) as RoleTrack | undefined;
    return (
      <div className="space-y-6">
        <section className="grid gap-4 sm:grid-cols-[1.3fr_1fr]">
          <div className="rounded-3xl bg-graphite p-6 text-paper">
            <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-emerald-300">{planRole ? ROLE_LABEL[planRole] : "Your plan"}</p>
            <p className="mt-2 font-serif text-4xl font-semibold leading-tight">{countdownText(days) ?? "No interview date yet"}</p>
            <p className="mt-2 text-sm text-paper-3">
              {result.plan.length} week{result.plan.length === 1 ? "" : "s"} · about {result.totalHours} h of work · {result.capacityHours} h available at {hours} h a week
              {!date && " (planned over 8 weeks until you set a date)"}
            </p>
          </div>
          <div className="rounded-3xl border border-rule bg-white/70 p-6">
            <p className="text-sm text-graphite-3">Fundamentals self-check</p>
            <p className="mt-1 font-serif text-3xl font-semibold text-graphite">
              {result.score} / {QUESTIONS.length}
            </p>
            <p className="mt-2 text-sm text-graphite-2">Modules where you rated yourself highly and answered correctly are marked to skim, or graded tasks only.</p>
          </div>
        </section>
        {over && (
          <p className="rounded-2xl border border-vermilion/30 bg-vermilion/5 p-4 text-sm text-graphite-2" role="status">
            The plan needs about {Math.round(result.totalHours - result.capacityHours)} more hours than you have. Add hours per week, skim the modules you know
            best, or move the interview if you can. Extra work is piled into the last study week.
          </p>
        )}
        {saveNote && (
          <p className="text-sm text-vermilion" role="alert">
            {saveNote}
          </p>
        )}
        {source === "local" && <p className="text-xs text-graphite-3">Saved in this browser. Sign in to keep your plan and get weekly reminders.</p>}
        <ol className="space-y-3">
          {result.plan.map((w) => (
            <li key={w.week} className="rounded-3xl border border-rule bg-white/70 p-5">
              <div className="flex flex-wrap items-baseline gap-x-3">
                <h3 className="font-serif text-xl font-semibold text-graphite">Week {w.week}</h3>
                <span className="text-xs text-graphite-3">
                  from {new Date(`${w.start}T12:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" })} · about {w.hours} h
                </span>
              </div>
              {w.note && <p className="mt-1 text-sm font-semibold text-vermilion">{w.note}</p>}
              {w.items.length ? (
                <ul className="mt-3 space-y-1.5 text-sm">
                  {w.items.map((it) => {
                    const href = modules.find((m) => m.slug === it.slug)?.href ?? "/learn";
                    const [label, cls] = STATUS_STYLE[it.status];
                    return (
                      <li key={it.slug} className="flex flex-wrap items-center gap-2">
                        <span className="w-9 shrink-0 font-mono text-xs text-vermilion">{it.code}</span>
                        <Link href={href} className="min-w-0 flex-1 text-graphite hover:underline">
                          {it.title}
                        </Link>
                        <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold ${cls}`}>{label}</span>
                        <span className="w-12 shrink-0 text-right text-xs tabular-nums text-graphite-3">{it.hours} h</span>
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <p className="mt-2 text-sm text-graphite-3">Catch-up and review week. Do a daily five-minute review.</p>
              )}
            </li>
          ))}
        </ol>
        <details className="rounded-3xl border border-rule bg-white/70 p-5">
          <summary className="cursor-pointer font-serif text-lg font-semibold text-graphite">Self-check answers</summary>
          <ol className="mt-3 space-y-3 text-sm">
            {QUESTIONS.map((q, i) => (
              <li key={i}>
                <p className="text-graphite">
                  {i + 1}. {q.q}
                </p>
                <p className={result.answers[i] === q.answer ? "text-forest" : "text-vermilion"}>
                  {result.answers[i] === q.answer ? "Correct" : "Not quite"}: {q.options[q.answer]}
                </p>
                <p className="text-graphite-3">{q.explain}</p>
              </li>
            ))}
          </ol>
        </details>
        <div className="flex flex-wrap gap-3">
          <Link href={planRole ? `/learn?track=core` : "/learn"} className="rounded-full bg-graphite px-5 py-2.5 font-semibold text-paper hover:bg-black">
            Start week 1 →
          </Link>
          <Link href="/learn/progress" className="rounded-full border border-rule px-5 py-2.5 font-semibold text-graphite hover:bg-paper-2">
            My scorecard
          </Link>
          <button type="button" onClick={() => setEditing(true)} className="rounded-full px-5 py-2.5 text-graphite-2 hover:bg-paper-2">
            Change my answers
          </button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-6" noValidate>
      <Step n={1} title="About you">
        <fieldset>
          <legend className="text-sm text-graphite-2">Which role are you preparing for?</legend>
          <div className="mt-2 grid gap-2 sm:grid-cols-3">
            {(roles.length ? roles : ROLE_TRACKS).map((r) => (
              <label key={r} className={`flex cursor-pointer items-center gap-2 rounded-2xl border px-4 py-3 text-sm ${role === r ? "border-graphite bg-white" : "border-rule bg-white/60"}`}>
                <input type="radio" name="role" value={r} checked={role === r} onChange={() => setRole(r)} className="accent-forest" />
                <span className="font-semibold text-graphite">{ROLE_LABEL[r]}</span>
              </label>
            ))}
          </div>
        </fieldset>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
          <label className="block text-sm">
            <span className="text-graphite-2">Interview date (if you have one)</span>
            <input type="date" min={today} value={date} onChange={(e) => setDate(e.target.value)} className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2" />
          </label>
          <label className="block text-sm">
            <span className="text-graphite-2">Hours per week you can give it</span>
            <input
              type="number"
              min={1}
              max={80}
              value={hours}
              onChange={(e) => setHours(Math.max(1, Math.min(80, Number(e.target.value) || 1)))}
              className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2"
            />
          </label>
          <label className="block text-sm">
            <span className="text-graphite-2">Your background</span>
            <select value={background} onChange={(e) => setBackground(e.target.value)} className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2">
              <option value="">Choose one</option>
              {BACKGROUNDS.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </label>
        </div>
      </Step>

      <Step n={2} title="Fundamentals self-check">
        <p className="-mt-2 mb-4 text-sm text-graphite-3">Ten quick questions, about five minutes. No penalty for guessing; it only shapes your plan.</p>
        <ol className="space-y-5">
          {QUESTIONS.map((q, i) => (
            <li key={i}>
              <fieldset>
                <legend className="text-sm font-semibold text-graphite">
                  {i + 1}. {q.q}
                </legend>
                <div className="mt-2 grid gap-1.5">
                  {q.options.map((o, j) => (
                    <label
                      key={j}
                      className={`flex cursor-pointer items-start gap-2 rounded-xl border px-3 py-2 text-sm ${answers[i] === j ? "border-graphite bg-white" : "border-rule bg-white/60"}`}
                    >
                      <input
                        type="radio"
                        name={`q${i}`}
                        checked={answers[i] === j}
                        onChange={() => setAnswers((a) => a.map((x, k) => (k === i ? j : x)))}
                        className="mt-0.5 accent-forest"
                      />
                      <span className="min-w-0">{o}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
            </li>
          ))}
        </ol>
      </Step>

      <Step n={3} title="Rate yourself">
        <p className="-mt-2 mb-4 text-sm text-graphite-3">Be honest: a high rating marks modules to skim. Unrated areas count as the middle.</p>
        <ul className="space-y-4">
          {AREAS.map((a) => (
            <li key={a.key}>
              <fieldset>
                <legend className="text-sm font-semibold text-graphite">{a.label}</legend>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {RATING_LABELS.map((label, i) => {
                    const v = i + 1;
                    const on = ratings[a.key] === v;
                    return (
                      <label key={v} className={`cursor-pointer rounded-full border px-3 py-1 text-xs ${on ? "border-graphite bg-graphite text-paper" : "border-rule bg-white/60 text-graphite-2"}`}>
                        <input
                          type="radio"
                          name={`rate-${a.key}`}
                          value={v}
                          checked={on}
                          onChange={() => setRatings((r) => ({ ...r, [a.key]: v }))}
                          className="sr-only"
                        />
                        {v} · {label}
                      </label>
                    );
                  })}
                </div>
              </fieldset>
            </li>
          ))}
        </ul>
      </Step>

      {error && (
        <p className="text-sm text-vermilion" role="alert">
          {error}
        </p>
      )}
      <div className="flex flex-wrap items-center gap-3">
        <button type="submit" className="rounded-full bg-graphite px-6 py-3 font-semibold text-paper hover:bg-black">
          Build my plan →
        </button>
        <span className="text-xs text-graphite-3">
          {answered}/{QUESTIONS.length} answered
        </span>
        {result && (
          <button type="button" onClick={() => setEditing(false)} className="text-sm text-graphite-2 hover:text-graphite">
            Back to my plan
          </button>
        )}
      </div>
    </form>
  );
}
