"use client";

// Five-minute daily review: Leitner boxes over quiz questions and number cards (prices, cache rules,
// effort defaults). Boxes live in this browser (localStorage "fde-review-v1").

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

export interface ClientCard {
  id: string;
  kind: "quiz" | "number";
  deck: string;
  front: string;
  back: string;
  explain?: string;
  href?: string;
}

const KEY = "fde-review-v1";
const SESSION_MS = 5 * 60_000;
const NEW_PER_DAY = 12;
/** Days until the next review, by box (1 to 5). */
const INTERVAL = [0, 1, 2, 4, 8, 16];

interface Store {
  boxes: Record<string, { box: number; due: string }>;
  newOn: Record<string, number>;
  sessions: Record<string, number>;
}

const today = () => {
  const n = new Date();
  return `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, "0")}-${String(n.getDate()).padStart(2, "0")}`;
};
const addDays = (n: number) => {
  const d = new Date();
  d.setDate(d.getDate() + n);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

function load(): Store {
  try {
    const raw = window.localStorage.getItem(KEY);
    const s = raw ? (JSON.parse(raw) as Partial<Store>) : {};
    return { boxes: s.boxes ?? {}, newOn: s.newOn ?? {}, sessions: s.sessions ?? {} };
  } catch {
    return { boxes: {}, newOn: {}, sessions: {} };
  }
}

function persist(s: Store) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    // Storage blocked: boxes last for this visit.
  }
}

type Deck = "all" | "number" | "quiz";

export default function SiteReview({ cards, lockedNote }: { cards: ClientCard[]; lockedNote: boolean }) {
  const [store, setStore] = useState<Store | null>(null);
  const [deck, setDeck] = useState<Deck>("all");
  const [queue, setQueue] = useState<string[] | null>(null);
  const [flipped, setFlipped] = useState(false);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [stats, setStats] = useState({ right: 0, wrong: 0 });
  const [repeated, setRepeated] = useState<Set<string>>(new Set());

  useEffect(() => setStore(load()), []);
  useEffect(() => {
    if (startedAt === null) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [startedAt]);

  const byId = useMemo(() => new Map(cards.map((c) => [c.id, c])), [cards]);
  const pool = useMemo(() => cards.filter((c) => deck === "all" || c.kind === deck), [cards, deck]);

  const counts = useMemo(() => {
    if (!store) return { due: 0, fresh: 0, learned: 0 };
    const t = today();
    let due = 0;
    let fresh = 0;
    let learned = 0;
    for (const c of pool) {
      const b = store.boxes[c.id];
      if (!b) fresh++;
      else {
        if (b.due <= t) due++;
        if (b.box >= 4) learned++;
      }
    }
    return { due, fresh, learned };
  }, [pool, store]);

  const start = useCallback(() => {
    if (!store) return;
    const t = today();
    const due = pool
      .filter((c) => store.boxes[c.id] && store.boxes[c.id].due <= t)
      .sort((a, b) => store.boxes[a.id].box - store.boxes[b.id].box || store.boxes[a.id].due.localeCompare(store.boxes[b.id].due))
      .map((c) => c.id);
    const newLeft = Math.max(0, NEW_PER_DAY - (store.newOn[t] ?? 0));
    // New cards in a shuffled order so numbers and quiz questions mix.
    const fresh = pool.filter((c) => !store.boxes[c.id]).map((c) => c.id);
    for (let i = fresh.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [fresh[i], fresh[j]] = [fresh[j], fresh[i]];
    }
    setQueue([...due, ...fresh.slice(0, newLeft)]);
    setStats({ right: 0, wrong: 0 });
    setRepeated(new Set());
    setFlipped(false);
    setStartedAt(Date.now());
    setNow(Date.now());
  }, [pool, store]);

  const timeUp = startedAt !== null && now - startedAt >= SESSION_MS;
  const current = queue && queue.length && !timeUp ? byId.get(queue[0]) : undefined;

  const grade = useCallback(
    (knew: boolean) => {
      if (!store || !queue || !current) return;
      const t = today();
      const prev = store.boxes[current.id];
      const box = knew ? Math.min(5, (prev?.box ?? 0) + 1) : 1;
      const next: Store = {
        boxes: { ...store.boxes, [current.id]: { box, due: addDays(INTERVAL[box]) } },
        newOn: prev ? store.newOn : { ...store.newOn, [t]: (store.newOn[t] ?? 0) + 1 },
        sessions: { ...store.sessions, [t]: (store.sessions[t] ?? 0) + 1 },
      };
      persist(next);
      setStore(next);
      setStats((s) => (knew ? { ...s, right: s.right + 1 } : { ...s, wrong: s.wrong + 1 }));
      // A missed card comes back once at the end of this session.
      const rest = queue.slice(1);
      if (!knew && !repeated.has(current.id)) {
        setRepeated(new Set(repeated).add(current.id));
        rest.push(current.id);
      }
      setQueue(rest);
      setFlipped(false);
    },
    [store, queue, current, repeated],
  );

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!current || (e.target as HTMLElement)?.tagName === "INPUT") return;
      if (e.key === " " && !flipped) {
        e.preventDefault();
        setFlipped(true);
      } else if (flipped && (e.key === "1" || e.key === "ArrowLeft")) grade(false);
      else if (flipped && (e.key === "2" || e.key === "ArrowRight")) grade(true);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [current, flipped, grade]);

  if (!store) return <p className="text-sm text-graphite-3">Loading your boxes…</p>;

  const remaining = startedAt === null ? SESSION_MS : Math.max(0, SESSION_MS - (now - startedAt));
  const clock = `${Math.floor(remaining / 60000)}:${String(Math.floor((remaining % 60000) / 1000)).padStart(2, "0")}`;

  if (queue === null) {
    return (
      <div className="space-y-5">
        <div role="group" aria-label="Deck" className="flex flex-wrap gap-2">
          {(
            [
              ["all", "Everything"],
              ["number", "Numbers"],
              ["quiz", "Quiz questions"],
            ] as [Deck, string][]
          ).map(([v, label]) => (
            <button
              key={v}
              type="button"
              aria-pressed={deck === v}
              onClick={() => setDeck(v)}
              className={`rounded-full px-4 py-1.5 text-sm ${deck === v ? "bg-graphite text-paper" : "border border-rule text-graphite-2 hover:bg-paper-2"}`}
            >
              {label}
            </button>
          ))}
        </div>
        <dl className="grid grid-cols-3 gap-3">
          {[
            [counts.due, "due today"],
            [Math.min(counts.fresh, Math.max(0, NEW_PER_DAY - (store.newOn[today()] ?? 0))), "new today"],
            [counts.learned, "learned"],
          ].map(([n, l]) => (
            <div key={l} className="rounded-2xl border border-rule bg-white/70 px-4 py-3">
              <dt className="font-serif text-3xl font-semibold text-graphite">{n}</dt>
              <dd className="text-xs text-graphite-3">{l}</dd>
            </div>
          ))}
        </dl>
        <button type="button" onClick={start} className="w-full rounded-full bg-graphite px-6 py-4 text-lg font-semibold text-paper hover:bg-black sm:w-auto">
          Start my 5 minutes →
        </button>
        <p className="text-xs text-graphite-3">
          {pool.length} cards in this deck. Cards you know move up a box and come back less often (1, 2, 4, 8, then 16 days); a miss sends a card back to box
          1. Boxes are kept in this browser.
          {lockedNote && " Quiz cards from the paid modules appear once you have full access."}
        </p>
      </div>
    );
  }

  if (!current) {
    return (
      <div className="rounded-3xl bg-forest p-6 text-white" role="status">
        <p className="font-serif text-3xl">{timeUp ? "Time's up. Nice work." : "All done for today."}</p>
        <p className="mt-2 text-white/85">
          {stats.right} known · {stats.wrong} to see again. Come back tomorrow: five minutes a day beats an hour on the weekend.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <button type="button" onClick={() => setQueue(null)} className="rounded-full bg-white px-5 py-2 font-semibold text-forest">
            Back to decks
          </button>
          <Link href="/learn/progress" className="rounded-full border border-white/50 px-5 py-2 font-semibold text-white">
            My scorecard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl">
      <div className="mb-3 flex items-center justify-between text-sm text-graphite-3">
        <span>
          {queue.length} left · {stats.right} known
        </span>
        <span className="font-mono tabular-nums text-graphite" aria-label={`Time left ${clock}`}>
          {clock}
        </span>
      </div>
      <article className="flex min-h-[18rem] flex-col rounded-3xl border border-rule bg-white p-6 shadow-[0_30px_60px_-40px_rgba(29,27,22,0.6)]" aria-live="polite">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-vermilion">
          {current.kind === "number" ? "Number" : `${current.deck} quiz`} · box {store.boxes[current.id]?.box ?? "new"}
        </p>
        <p className="mt-3 font-serif text-xl leading-snug text-graphite">{current.front}</p>
        {flipped ? (
          <div className="mt-5 border-t border-rule pt-4">
            <p className="font-semibold text-forest">{current.back}</p>
            {current.explain && <p className="mt-2 text-sm leading-relaxed text-graphite-2">{current.explain}</p>}
            {current.href && (
              <Link href={current.href} className="mt-2 inline-block text-xs text-graphite-3 underline decoration-rule underline-offset-2 hover:text-graphite">
                From the lesson
              </Link>
            )}
          </div>
        ) : null}
      </article>
      <div className="sticky bottom-4 mt-4 grid grid-cols-2 gap-3">
        {flipped ? (
          <>
            <button type="button" onClick={() => grade(false)} className="rounded-full border border-vermilion/40 bg-paper px-4 py-3.5 font-semibold text-vermilion hover:bg-vermilion/10">
              Not yet
            </button>
            <button type="button" onClick={() => grade(true)} className="rounded-full bg-forest px-4 py-3.5 font-semibold text-white hover:bg-forest-2">
              I knew it
            </button>
          </>
        ) : (
          <button type="button" onClick={() => setFlipped(true)} className="col-span-2 rounded-full bg-graphite px-4 py-3.5 font-semibold text-paper hover:bg-black">
            Show answer
          </button>
        )}
      </div>
      <p className="mt-3 hidden text-center text-xs text-graphite-3 sm:block">Space shows the answer · 1 not yet · 2 I knew it</p>
    </div>
  );
}
