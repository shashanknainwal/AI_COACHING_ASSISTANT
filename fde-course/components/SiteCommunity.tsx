"use client";

// Peer-mock kit: pick a role-play lesson and print an interviewer script built from the lesson's
// public text and rubric. The AI persona's private brief and grader notes are never included.

import { useMemo, useState } from "react";

export interface ClientPeerScript {
  id: string;
  track: string;
  moduleCode: string;
  title: string;
  minutes: number;
  timeLimit: number;
  maxTurns: number;
  design: boolean;
  persona: { name: string; role: string; company: string } | null;
  opening: string;
  setup: string;
  rubric: { name: string; points: number; lookFor: string }[];
  passScore: number;
  free: boolean;
}

const TRACK_LABEL: Record<string, string> = { core: "Foundations", engineer: "Applied AI Engineer", architect: "Applied AI Architect", fde: "Forward Deployed Engineer" };

export default function SiteCommunity({ scripts }: { scripts: ClientPeerScript[] }) {
  const [id, setId] = useState(scripts.find((s) => s.free)?.id ?? scripts[0]?.id ?? "");
  const s = useMemo(() => scripts.find((x) => x.id === id), [scripts, id]);
  const total = s ? s.rubric.reduce((n, r) => n + r.points, 0) : 0;
  const minutes = s ? s.timeLimit || Math.max(20, Math.min(45, s.maxTurns * 4)) : 0;

  if (!scripts.length) return <p className="text-sm text-graphite-2">No role-play lessons are open to you yet.</p>;

  return (
    <div>
      <label className="block text-sm print:hidden">
        <span className="text-graphite-2">Choose a round</span>
        <select value={id} onChange={(e) => setId(e.target.value)} className="mt-1 w-full rounded-xl border border-rule bg-white px-3 py-2">
          {Object.entries(
            scripts.reduce<Record<string, ClientPeerScript[]>>((acc, x) => {
              (acc[x.track] ??= []).push(x);
              return acc;
            }, {}),
          ).map(([track, list]) => (
            <optgroup key={track} label={TRACK_LABEL[track] ?? track}>
              {list.map((x) => (
                <option key={x.id} value={x.id}>
                  {x.moduleCode} · {x.title}
                  {x.free ? " (free)" : ""}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </label>

      {s && (
        <article className="peer-script mt-5 rounded-3xl border border-rule bg-white p-5 sm:p-7 print:mt-0 print:rounded-none print:border-0 print:p-0">
          <div className="flex flex-wrap items-start gap-3">
            <div className="min-w-0 flex-1">
              <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-vermilion">Interviewer script · {s.moduleCode}</p>
              <h3 className="mt-1 font-serif text-2xl font-semibold leading-snug text-graphite">{s.title}</h3>
              <p className="mt-1 text-sm text-graphite-3">
                About {minutes} minutes{s.design ? " · design interview: the candidate draws as they talk" : ""} · pass mark {s.passScore}%
              </p>
            </div>
            <button type="button" onClick={() => window.print()} className="shrink-0 rounded-full bg-graphite px-4 py-2 text-sm font-semibold text-paper hover:bg-black print:hidden">
              Print script
            </button>
          </div>

          <h4 className="mt-6 font-serif text-lg font-semibold text-graphite">Your part</h4>
          {s.persona ? (
            <p className="mt-1 text-sm text-graphite-2">
              You play <strong className="text-graphite">{s.persona.name}</strong>, {s.persona.role} at {s.persona.company}. Stay in character for the whole
              session.
            </p>
          ) : (
            <p className="mt-1 text-sm text-graphite-2">You play the interviewer described in the brief below.</p>
          )}
          {s.opening && (
            <blockquote className="mt-3 border-l-4 border-vermilion pl-4 font-serif text-base italic text-graphite">&ldquo;{s.opening}&rdquo;</blockquote>
          )}
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-graphite-2">
            <li>Open with the line above, word for word, then let the candidate lead.</li>
            <li>Ask one follow-up at a time: &ldquo;Why that?&rdquo;, &ldquo;What would you measure?&rdquo;, &ldquo;What if that fails?&rdquo;</li>
            <li>Push back once on their main decision and see if they defend it with reasons or numbers.</li>
            <li>Don&apos;t coach or hint during the session. If they ask for a fact the brief doesn&apos;t give, say &ldquo;I&apos;d have to check&rdquo;.</li>
            <li>Keep time. Give a two-minute warning and stop on time.</li>
          </ul>

          <h4 className="mt-6 font-serif text-lg font-semibold text-graphite">What the candidate has read</h4>
          <p className="mt-1 text-xs text-graphite-3">The lesson&apos;s own text. Read it before the session so you know the scenario.</p>
          <div className="mt-2 max-h-80 overflow-y-auto whitespace-pre-line rounded-2xl bg-paper-2/60 p-4 text-sm leading-relaxed text-graphite-2 print:max-h-none print:overflow-visible">
            {s.setup}
          </div>

          <h4 className="mt-6 font-serif text-lg font-semibold text-graphite">Score sheet</h4>
          <p className="mt-1 text-xs text-graphite-3">Score each line after the session, then add them up. {total} points in all.</p>
          <table className="mt-2 w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-graphite-3">
              <tr>
                <th scope="col" className="py-2 pr-2 font-semibold">Rubric line</th>
                <th scope="col" className="w-20 px-2 py-2 text-right font-semibold">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-rule align-top">
              {s.rubric.map((r) => (
                <tr key={r.name}>
                  <td className="py-2 pr-2">
                    <p className="font-semibold text-graphite">{r.name}</p>
                    <p className="text-xs leading-relaxed text-graphite-2">{r.lookFor}</p>
                  </td>
                  <td className="whitespace-nowrap px-2 py-2 text-right font-mono text-graphite-2">___ / {r.points}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <h4 className="mt-6 font-serif text-lg font-semibold text-graphite">Debrief (10 minutes)</h4>
          <ol className="mt-1 list-decimal space-y-1 pl-5 text-sm text-graphite-2">
            <li>The candidate says how they think it went, first.</li>
            <li>You give the total and the two lowest lines, each with one moment from the session.</li>
            <li>One thing to keep, one thing to fix first. Then swap roles.</li>
          </ol>
          <p className="mt-4 text-xs text-graphite-3">
            Want the AI-graded version too? The candidate can run the same lesson on the site afterwards and compare the scores.
          </p>
        </article>
      )}
    </div>
  );
}
