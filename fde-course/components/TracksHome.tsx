import Link from "next/link";
import type { ClientViewer } from "@/lib/access";
import type { Course } from "@/lib/content";
import { SITE_NAME } from "@/lib/config";
import testimonials from "@/content/testimonials.json";
import AccountBadge from "./AccountBadge";
import BuyButton from "./BuyButton";
import { Avatar, Mark } from "./Playbook";

// The home page once the three tracks are live (tracksEnabled()). The original FDE-only
// home page in app/page.tsx is still served until then.

const GRADED = new Set(["exercise", "drill", "written", "roleplay"]);

const ROUNDS: [string, string, string][] = [
  [
    "Practical coding",
    "Timed, multi-level Python problems in the progressive format candidates describe: build it, then extend it as the requirements change.",
    "Timed drills",
  ],
  [
    "LLM system design",
    "Scope an ambiguous product, choose models and retrieval, set an eval gate, and do the cost and latency math out loud.",
    "Graded design answers",
  ],
  [
    "Project deep dive",
    "Defend something you built while an interviewer pushes on your decisions, your failures and your numbers.",
    "Live role-play",
  ],
  [
    "Values and motivation",
    "Mission, safety and money questions, answered with true stories and a real reading of what the labs publish.",
    "Mock values interview",
  ],
];

const STEPS: [string, string][] = [
  ["Learn what's tested", "Written lessons on how frontier labs hire, the fundamentals every round assumes, and the work each role does day to day."],
  ["Practice it for real", "Python in your browser with a simulated Claude SDK, timed coding drills, and customer and executive conversations."],
  ["Get graded like the loop", "Hidden tests check your code. Claude grades written answers and live sessions against interviewer-style rubrics."],
];

const FAQ: [string, string][] = [
  [
    "Are these real interview questions?",
    "No. Every question is original, written in the style candidates publicly describe. We never use leaked or confidential material, and every claim about a hiring process is labelled official, reported or anecdotal.",
  ],
  ["Is this affiliated with Anthropic, OpenAI or Perplexity?", "No. It's an independent course. Labs are named only as factual references."],
  [
    "Which track should I take?",
    "Everyone starts with Foundations. Then pick the role you're applying for: Applied AI Engineer if you build systems, Applied AI Architect if you design and sell them, Forward Deployed Engineer if you ship them inside customers.",
  ],
  [
    "Do I need an API key or any installs?",
    "No. Everything runs in your browser. Coding exercises use a built-in simulator of the Anthropic SDK that uses the same calls as the real SDK for the features taught; your capstone runs against the real API with your own key.",
  ],
  ["Can I try it before buying?", "Yes. The first Foundations module, the first lesson of every track and FDE Module 1 are free, with no credit card."],
  ["Does it follow the labs' AI-use rules?", "Yes. Timed drills switch the AI tutor off, the same as real assessments, and the written lessons teach Anthropic's published candidate guidance."],
];

const FEATURES: [string, string][] = [
  ["Voice mock interviews", "Talk to the interviewer out loud with your microphone, hear the replies, and see a timer on every answer. Or type, if you prefer."],
  ["Interactive design rounds", "The interviewer reveals requirements only when you ask, adds a new constraint mid-round, and grades the diagram you draw as you talk."],
  ["Progress dashboard", "Your loop scorecard builds itself: every round's score, your weakest rubric lines, drill times, and the module to fix next."],
  ["A plan to your date", "Set your interview date and hours, take a ten-question self-check, and get a week-by-week plan with a countdown."],
  ["Portfolio capstone", "Build a project against the real API with your own key, then defend it in the deep-dive rounds and link it from a public record of verified results."],
  ["Peer mocks and daily review", "Printable interviewer scripts to practise with a partner, plus five-minute spaced-repetition flashcards for the numbers."],
];

function Tick({ className = "text-forest" }: { className?: string }) {
  return (
    <svg viewBox="0 0 20 20" className={`mt-1 h-4 w-4 shrink-0 ${className}`} fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0Z" clipRule="evenodd" />
    </svg>
  );
}

function Eyebrow({ children, className = "text-vermilion" }: { children: React.ReactNode; className?: string }) {
  return <p className={`text-[11px] font-semibold uppercase tracking-[0.18em] ${className}`}>{children}</p>;
}

/** The product in one picture: the progress dashboard's loop scorecard, and a live session being graded. Example numbers. */
function LoopComposition() {
  const rounds: [string, string, number, "pass" | "close"][] = [
    ["Coding drill", "3 of 4 levels in time", 85, "pass"],
    ["Design, live", "first attempt", 78, "pass"],
    ["Technical deep dive", "first attempt", 64, "close"],
    ["Experiences and goals", "first attempt", 81, "pass"],
  ];
  return (
    <div className="relative mx-auto w-full max-w-xl lg:max-w-none" role="img" aria-label="Example of the progress dashboard: a mock-loop scorecard with a score and pass or close status for each round, and a live interview answer being graded against a rubric line.">
      <div className="relative z-10 rotate-[-1.5deg] rounded-2xl border border-rule bg-white shadow-[0_30px_60px_-35px_rgba(29,27,22,0.6)] sm:w-[84%]">
        <div className="flex items-center gap-2 border-b border-rule bg-paper-2/70 px-4 py-2 font-mono text-[10px] uppercase tracking-[0.14em] text-graphite-3">
          <span className="font-semibold text-vermilion">Loop scorecard</span>
          <span>·</span>
          <span>Applied AI Engineer</span>
          <span className="ml-auto normal-case tracking-normal">example</span>
        </div>
        <ol className="divide-y divide-rule px-4">
          {rounds.map(([name, meta, score, state]) => (
            <li key={name} className="flex items-center gap-3 py-2.5">
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold text-graphite">{name}</span>
                <span className="block font-mono text-[10px] text-graphite-3">{meta}</span>
              </span>
              <span className="font-mono text-sm font-semibold tabular-nums text-graphite">{score}</span>
              <span className={`w-12 rounded-full px-2 py-0.5 text-center text-[10px] font-semibold ${state === "pass" ? "bg-forest text-white" : "bg-amber-100 text-amber-900"}`}>
                {state === "pass" ? "Pass" : "Close"}
              </span>
            </li>
          ))}
        </ol>
        <div className="border-t border-rule px-4 py-3 text-[12px] text-graphite-2">
          <span className="font-semibold text-graphite">Readiness: close.</span> Weakest round 64; lowest line &ldquo;Depth on one decision&rdquo;.{" "}
          <span className="text-forest">Next: E4 Evals as Engineering →</span>
        </div>
      </div>

      <div className="relative -mt-2 ml-auto rotate-[1deg] overflow-hidden rounded-2xl bg-console text-gray-200 shadow-[0_40px_80px_-30px_rgba(13,17,23,0.75)] sm:-mt-3 sm:w-[86%]">
        <div className="flex items-center gap-2 border-b border-console-line px-3 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <span className="ml-2 rounded bg-console-2 px-2 py-0.5 font-mono text-[11px] text-gray-400">live session · voice on</span>
        </div>
        <div className="space-y-3 p-4">
          <div className="flex gap-2.5">
            <Avatar name="Sam Okoye" size="sm" dark />
            <p className="rounded-xl rounded-tl-sm bg-console-2 px-3 py-2 text-[13px] leading-relaxed text-gray-100">
              Tell me about a time you slowed down a launch because it wasn&apos;t ready. What did <em>you</em> do?
            </p>
          </div>
          <div className="flex justify-end">
            <p className="max-w-[85%] rounded-xl rounded-tr-sm bg-emerald-500/15 px-3 py-2 text-[13px] leading-relaxed text-emerald-50">
              The agent gave wrong refund answers in 4% of tests, so I proposed a 10% canary with an eval gate at 99%…
            </p>
          </div>
          <div className="check-in rounded-lg border border-emerald-400/20 bg-emerald-400/[0.06] p-3" style={{ animationDelay: "900ms" }}>
            <div className="flex items-baseline justify-between font-mono text-[10px] uppercase tracking-wider text-emerald-300">
              <span>Rubric · Specific, real examples</span>
              <span>23 / 25</span>
            </div>
            <div className="mt-2 h-1.5 rounded-full bg-console-2">
              <div className="bar-fill h-1.5 w-[92%] rounded-full bg-emerald-400" style={{ animationDelay: "1100ms" }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// A fictional sample answer and debrief for one written lesson (E7 Round 2 prep), so visitors can see what grading looks like.
const SAMPLE_LINES: [string, number, number, string][] = [
  ["Scoping with numbers", 12, 15, "Good volume and diff-size numbers. Missing: how many comments per PR reviewers will tolerate."],
  ["Context selection and architecture", 19, 25, "Diff plus touched files plus the repo's style guide is right. No plan for PRs larger than the context budget."],
  ["Evals and quality bar", 9, 20, "\u201cWe'll track thumbs-up rate\u201d isn't a gate. Needs a labelled set of past PRs and a precision target before launch."],
  ["Failure modes, security and trust", 15, 20, "Read-only token and no auto-merge: good. Prompt injection through PR text isn't mentioned."],
  ["Cost, latency and rollout", 14, 20, "The arithmetic follows, but 1.5K output ignores thinking: Sonnet 5.5 defaults to effort high, so set effort or budget more. Rollout jumps straight to every repo."],
];

function SampleDebrief() {
  const total = SAMPLE_LINES.reduce((n, l) => n + l[1], 0);
  const max = SAMPLE_LINES.reduce((n, l) => n + l[2], 0);
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
      <div className="min-w-0 rounded-3xl border border-rule bg-white/80 p-6">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-vermilion">Sample answer · fictional</p>
        <p className="mt-1 text-sm font-semibold text-graphite">E7 · Design a pull-request review assistant (excerpt)</p>
        <div className="mt-4 space-y-3 font-serif text-[15px] leading-relaxed text-graphite-2">
          <p>
            &ldquo;About 400 PRs a day, median diff around 300 lines. With the touched files and the style guide, a review request is roughly 12K input
            tokens and 1.5K output. On Sonnet 5.5 at $2 and $10 per million that&apos;s about $0.039 a review, or $16 a day.
          </p>
          <p>
            The bot gets a read-only token and posts comments only; it can never approve or merge. We&apos;ll track the thumbs-up rate on its comments and
            tune the prompt from there. Once it looks good, we turn it on for every repository.&rdquo;
          </p>
        </div>
      </div>
      <div className="min-w-0 rounded-3xl bg-graphite p-6 text-paper">
        <div className="flex items-baseline justify-between gap-3">
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-emerald-300">Sample debrief</p>
          <p className="font-serif text-3xl font-semibold">
            {total}
            <span className="text-base text-paper-3"> / {max}</span>
          </p>
        </div>
        <p className="mt-1 text-sm text-paper-3">Just under the pass mark of 70. Every line gets a score and one specific note.</p>
        <ul className="mt-5 space-y-4">
          {SAMPLE_LINES.map(([name, got, of, note]) => (
            <li key={name}>
              <div className="flex items-baseline justify-between gap-3 text-sm">
                <span className="font-semibold">{name}</span>
                <span className="shrink-0 font-mono tabular-nums text-paper-3">
                  {got} / {of}
                </span>
              </div>
              <div className="mt-1.5 h-1.5 rounded-full bg-white/10" role="img" aria-label={`${name}: ${got} of ${of}`}>
                <div className={`h-1.5 rounded-full ${got / of >= 0.7 ? "bg-emerald-400" : "bg-amber-400"}`} style={{ width: `${(got / of) * 100}%` }} />
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-paper-3">{note}</p>
            </li>
          ))}
        </ul>
        <p className="mt-5 border-t border-white/10 pt-4 text-sm">
          <span className="font-semibold text-emerald-300">Fix first:</span> <span className="text-paper-3">replace the thumbs-up metric with a release gate on 50 labelled past PRs.</span>
        </p>
      </div>
    </div>
  );
}

interface Testimonial {
  quote: string;
  name: string;
  role?: string;
}

export default function TracksHome({ course, viewer }: { course: Course; viewer: ClientViewer }) {
  const price = course.priceUsd;
  const all = course.modules.flatMap((m) => m.lessons);
  const hours = Math.floor(course.modules.reduce((s, m) => s + m.minutes, 0) / 60);
  const graded = all.filter((l) => GRADED.has(l.type)).length;
  const livePractice = all.filter((l) => l.type === "roleplay").length;
  const roleTracks = course.tracks.filter((t) => t.slug !== "core");
  const trackStats = (slug: string) => {
    const mods = course.modules.filter((m) => m.track === slug);
    return {
      mods,
      lessons: mods.reduce((s, m) => s + m.lessons.length, 0),
      hours: Math.round(mods.reduce((s, m) => s + m.minutes, 0) / 60),
    };
  };
  const navLinks = [["#tracks", "Tracks"], ["#loop", "The loop"], ["#sample", "Sample grade"], ["#syllabus", "Syllabus"], ["#pricing", "Pricing"]];
  const instructor = {
    name: process.env.NEXT_PUBLIC_INSTRUCTOR_NAME?.trim() || null,
    linkedin: process.env.NEXT_PUBLIC_INSTRUCTOR_LINKEDIN?.trim() || null,
    photo: process.env.NEXT_PUBLIC_INSTRUCTOR_PHOTO?.trim() || null,
  };
  const quotes = (Array.isArray(testimonials) ? (testimonials as Testimonial[]) : []).filter((t) => t && t.quote && t.name);

  return (
    <div className="playbook-page min-h-screen">
      <header className="sticky top-0 z-30 border-b border-rule/70 bg-paper/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 sm:px-6">
          <Link href="/" aria-label={`${SITE_NAME} home`} className="flex items-center gap-2 font-serif text-lg font-semibold text-graphite">
            <Mark />
            {SITE_NAME}
          </Link>
          <nav className="ml-auto hidden items-center gap-6 text-sm text-graphite-2 md:flex">
            {navLinks.map(([href, label]) => (
              <a key={href} href={href} className="hover:text-graphite">
                {label}
              </a>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3 md:ml-0">
            {viewer.signedIn || viewer.mode === "dev" ? (
              <Link href="/learn" className="rounded-full bg-graphite px-4 py-1.5 text-sm font-semibold text-paper hover:bg-black">
                My course
              </Link>
            ) : (
              <>
                <span className="[&_*]:!text-graphite-2 [&_a]:!border-rule">
                  <AccountBadge viewer={viewer} />
                </span>
                <Link href="/learn" className="rounded-full bg-graphite px-4 py-1.5 text-sm font-semibold text-paper hover:bg-black">
                  Start free
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="mx-auto grid max-w-6xl items-center gap-14 px-4 pb-20 pt-14 sm:px-6 lg:grid-cols-[1.05fr_1fr] lg:pt-20">
          <div className="min-w-0">
            <Eyebrow>Interview prep for applied AI roles at frontier labs</Eyebrow>
            <h1 className="mt-5 font-serif text-[2.75rem] font-semibold leading-[1.04] tracking-[-0.025em] text-graphite sm:text-6xl">
              Get hired to ship AI{" "}
              <span className="relative inline-block italic">
                at the frontier.
                <svg viewBox="0 0 300 14" preserveAspectRatio="none" className="absolute -bottom-2 left-0 h-3 w-full text-vermilion" aria-hidden="true">
                  <path d="M2 10 C 70 2, 150 2, 298 8" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                </svg>
              </span>
            </h1>
            <p className="mt-7 max-w-xl text-lg leading-relaxed text-graphite-2">
              You know the material. Then the interviewer says &ldquo;walk me through it,&rdquo; the clock starts, and your best answer comes out
              half-formed. Interviews aren&apos;t purely logical tests: pressure, nerves and a skeptical face in the room decide as much as knowledge does.
            </p>
            <p className="mt-4 max-w-xl text-lg leading-relaxed text-graphite-2">
              So rehearse under pressure. Three role tracks, for Applied AI Engineer, Applied AI Architect and Forward Deployed Engineer: timed drills,
              graded answers and live, spoken rounds with interviewers and customers who push back.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <Link
                href="/learn"
                className="rounded-full bg-graphite px-6 py-3 font-semibold text-paper shadow-[0_14px_30px_-16px_rgba(29,27,22,0.8)] hover:bg-black"
              >
                Start free →
              </Link>
              <Link href="/start" className="rounded-full border border-graphite/20 px-6 py-3 font-semibold text-graphite hover:border-graphite/50">
                Build my plan
              </Link>
              <a href="#pricing" className="px-2 py-3 font-semibold text-graphite-2 underline decoration-rule underline-offset-4 hover:text-graphite">
                All tracks · ${price}
              </a>
            </div>
            <p className="mt-5 text-sm text-graphite-3">Start with a 2-minute plan · No installs · No API key · Original questions, never leaked ones</p>
          </div>
          <LoopComposition />
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-rule bg-paper-2/60">
        <dl className="mx-auto grid max-w-6xl grid-cols-2 px-4 sm:px-6 md:grid-cols-4">
          {[[`${hours}+`, "hours of content"], [String(all.length), "lessons"], [String(graded), "graded tasks"], [String(livePractice), "live practice sessions"]].map(
            ([n, l], i) => (
              <div key={l} className={`px-4 py-9 text-center ${i > 0 ? "md:border-l md:border-rule" : ""} ${i % 2 ? "border-l border-rule md:border-l" : ""}`}>
                <dt className="font-serif text-4xl font-semibold text-graphite">{n}</dt>
                <dd className="mt-1 text-sm text-graphite-3">{l}</dd>
              </div>
            ),
          )}
        </dl>
      </section>

      {/* Why people stumble */}
      <section className="mx-auto max-w-6xl px-4 pt-24 sm:px-6">
        <Eyebrow>Why strong engineers stumble</Eyebrow>
        <h2 className="mt-4 max-w-3xl font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">
          It&apos;s rarely knowledge. It&apos;s the room.
        </h2>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {[
            [
              "You freeze, then ramble",
              "A design prompt with no numbers, a clock and a silent interviewer. Without reps, people jump to a solution and talk until time runs out.",
              "Timed design rounds with a live interviewer who changes the requirements halfway through.",
            ],
            [
              "You fold under pushback",
              "A staff engineer says \u201cI\u2019m not convinced.\u201d A CISO asks you to just confirm. Wanting to be liked makes people agree or overclaim.",
              "Personas trained to push back once, with grading that rewards holding a reasoned position.",
            ],
            [
              "You prepare for rumors",
              "Prep sites sell certainty: \u201cthey always ask X.\u201d Ten blogs copying one forum post still feel like proof when you\u2019re anxious.",
              "Every hiring claim labelled official, reported or anecdotal, with sources, so you train for what\u2019s real.",
            ],
          ].map(([title, problem, answer]) => (
            <div key={title} className="flex flex-col rounded-3xl border border-rule bg-white/70 p-6">
              <h3 className="font-serif text-2xl font-semibold text-graphite">{title}</h3>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-graphite-2">{problem}</p>
              <p className="mt-5 border-t border-rule pt-4 text-sm font-semibold leading-relaxed text-forest">{answer}</p>
            </div>
          ))}
        </div>
        <p className="mt-8 max-w-3xl text-graphite-2">
          Knowing how pressure and persuasion work doesn&apos;t only help you read a room. It also protects you from being pushed: by a customer who wants a
          promise you can&apos;t keep, an executive who wants a rounder number, or a prep course that sells fear. Every module trains both.
        </p>
      </section>

      {/* Tracks */}
      <section id="tracks" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-24 sm:px-6">
        <Eyebrow>Pick your role</Eyebrow>
        <h2 className="mt-4 max-w-3xl font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">
          One shared foundation. Three ways into the job.
        </h2>
        {(() => {
          const core = course.tracks.find((t) => t.slug === "core");
          if (!core) return null;
          const s = trackStats(core.slug);
          return (
            <Link
              href={`/learn?track=${core.slug}`}
              className="mt-10 flex flex-col gap-4 rounded-3xl bg-graphite p-6 text-paper shadow-[0_30px_60px_-36px_rgba(29,27,22,0.8)] sm:flex-row sm:items-center sm:p-8"
            >
              <div className="min-w-0 flex-1">
                <Eyebrow className="text-emerald-300">Start here · {core.title}</Eyebrow>
                <p className="mt-2 font-serif text-2xl leading-snug">{core.summary}</p>
              </div>
              <span className="shrink-0 font-mono text-xs text-paper-3">
                {s.mods.length} modules · {s.lessons} lessons · about {s.hours}h
              </span>
            </Link>
          );
        })()}
        <ol className="mt-4 grid gap-4 md:grid-cols-3">
          {roleTracks.map((t) => {
            const s = trackStats(t.slug);
            return (
              <li key={t.slug} className="flex min-w-0 flex-col rounded-3xl border border-rule bg-white/70 p-6">
                <Eyebrow>Track</Eyebrow>
                <h3 className="mt-2 font-serif text-2xl font-semibold leading-snug text-graphite">{t.short}</h3>
                <p className="mt-2 text-sm leading-relaxed text-graphite-2">{t.summary}</p>
                <p className="mt-2 text-xs text-graphite-3">For {t.audience}</p>
                <ul className="mt-5 flex-1 space-y-1.5 border-t border-rule pt-4 text-sm text-graphite-2">
                  {s.mods.slice(0, 5).map((m) => (
                    <li key={m.slug} className="flex gap-2">
                      <span className="w-7 shrink-0 font-mono text-[11px] text-vermilion">{/^\d+$/.test(m.code) ? m.code.padStart(2, "0") : m.code}</span>
                      <span className="min-w-0">{m.title}</span>
                    </li>
                  ))}
                  {s.mods.length > 5 && <li className="pl-9 text-xs text-graphite-3">+ {s.mods.length - 5} more, including a full mock loop</li>}
                </ul>
                <div className="mt-5 flex items-center justify-between">
                  <span className="font-mono text-[11px] text-graphite-3">
                    {s.lessons} lessons · about {s.hours}h
                  </span>
                  <Link href={`/learn?track=${t.slug}`} className="text-sm font-semibold text-forest hover:underline">
                    Open →
                  </Link>
                </div>
              </li>
            );
          })}
        </ol>
      </section>

      {/* The loop */}
      <section id="loop" className="scroll-mt-20 bg-graphite text-paper">
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <Eyebrow className="text-emerald-300">The loop, practiced</Eyebrow>
          <h2 className="mt-4 max-w-2xl font-serif text-4xl font-semibold leading-tight tracking-[-0.015em]">Four rounds keep coming up. Train for each one.</h2>
          <p className="mt-4 max-w-2xl text-paper-3">
            Strip away the company names and candidates describe the same four rounds again and again. Every claim in the course is labelled official,
            reported or anecdotal, so you know what to trust.
          </p>
          <ol className="mt-12 grid gap-px overflow-hidden rounded-3xl border border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-4">
            {ROUNDS.map(([round, text, feature], i) => (
              <li key={round} className="flex flex-col bg-graphite p-6">
                <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-paper-3">Round {i + 1}</span>
                <h3 className="mt-4 font-serif text-2xl font-semibold">{round}</h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-paper-3">{text}</p>
                <span className="mt-6 border-t border-white/10 pt-4 font-mono text-[11px] uppercase tracking-wider text-emerald-300">{feature}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
        <Eyebrow>How it works</Eyebrow>
        <h2 className="mt-4 font-serif text-4xl font-semibold tracking-[-0.015em] text-graphite">Learn it. Practice it. Get graded.</h2>
        <ol className="mt-12 grid gap-10 md:grid-cols-3">
          {STEPS.map(([title, text], i) => (
            <li key={title} className="relative border-t-2 border-graphite pt-6">
              <span className="absolute -top-3.5 left-0 bg-paper pr-3 font-mono text-sm font-semibold text-vermilion">0{i + 1}</span>
              <h3 className="font-serif text-2xl font-semibold text-graphite">{title}</h3>
              <p className="mt-3 leading-relaxed text-graphite-2">{text}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* What you get */}
      <section className="border-t border-rule bg-paper-2/60">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <Eyebrow>What&apos;s inside</Eyebrow>
          <ul className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(([title, text]) => (
              <li key={title} className="rounded-3xl border border-rule bg-white/70 p-6">
                <h3 className="font-serif text-xl font-semibold text-graphite">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-graphite-2">{text}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Sample graded answer */}
      <section id="sample" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-24 sm:px-6">
        <Eyebrow>Sample graded answer</Eyebrow>
        <h2 className="mt-4 max-w-3xl font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">See exactly how an answer gets graded.</h2>
        <p className="mt-4 max-w-2xl text-graphite-2">
          A fictional answer to a design round and the kind of debrief Claude returns: a score per rubric line, a note on each, and the one fix to make
          first. Your real debriefs are about your own answers.
        </p>
        <div className="mt-10">
          <SampleDebrief />
        </div>
      </section>

      {quotes.length > 0 && (
        <section aria-labelledby="quotes-title" className="border-t border-rule">
          <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
            <h2 id="quotes-title" className="font-serif text-3xl font-semibold text-graphite">
              From learners
            </h2>
            <ul className="mt-8 grid gap-4 md:grid-cols-2">
              {quotes.map((t) => (
                <li key={t.quote} className="rounded-3xl border border-rule bg-white/70 p-6">
                  <blockquote className="font-serif text-lg leading-relaxed text-graphite">&ldquo;{t.quote}&rdquo;</blockquote>
                  <p className="mt-3 text-sm text-graphite-3">
                    {t.name}
                    {t.role ? `, ${t.role}` : ""}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {/* Syllabus */}
      <section id="syllabus" className="scroll-mt-20 border-y border-rule bg-paper-2/60">
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <Eyebrow>Syllabus</Eyebrow>
          <h2 className="mt-4 font-serif text-4xl font-semibold tracking-[-0.015em] text-graphite">Every module, every track.</h2>
          <div className="mt-10 space-y-3">
            {course.tracks.map((t) => {
              const s = trackStats(t.slug);
              return (
                <details key={t.slug} className="group rounded-2xl border border-rule bg-white/70 open:shadow-[0_24px_50px_-36px_rgba(29,27,22,0.7)]">
                  <summary className="flex cursor-pointer list-none items-center gap-5 p-5 sm:p-6">
                    <div className="min-w-0 flex-1">
                      <h3 className="font-serif text-xl font-semibold text-graphite">{t.title}</h3>
                      <p className="mt-0.5 text-xs text-graphite-3">
                        {s.mods.length} modules · {s.lessons} lessons · about {s.hours} hours
                      </p>
                    </div>
                    <span
                      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-rule text-graphite-2 transition group-open:rotate-45 group-open:bg-graphite group-open:text-paper"
                      aria-hidden="true"
                    >
                      +
                    </span>
                  </summary>
                  <ol className="grid gap-x-8 gap-y-4 border-t border-rule p-5 sm:p-6 md:grid-cols-2">
                    {s.mods.map((m) => (
                      <li key={m.slug} className="flex gap-3">
                        <span className="w-8 shrink-0 font-serif text-lg text-vermilion">{/^\d+$/.test(m.code) ? m.code.padStart(2, "0") : m.code}</span>
                        <div className="min-w-0">
                          <p className="font-semibold text-graphite">{m.title}</p>
                          <p className="mt-0.5 text-sm leading-relaxed text-graphite-2">{m.summary}</p>
                          <p className="mt-1 text-xs text-graphite-3">
                            {m.lessons.length} lessons · {Math.round(m.minutes / 6) / 10}h
                          </p>
                        </div>
                      </li>
                    ))}
                  </ol>
                </details>
              );
            })}
          </div>
        </div>
      </section>

      {/* Instructor */}
      <section id="instructor" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-24 sm:px-6">
        <div className="grid items-center gap-12 lg:grid-cols-[0.9fr_1.4fr]">
          <div className="rotate-[-2deg] rounded-3xl border border-rule bg-white/80 p-8 shadow-[0_30px_60px_-40px_rgba(29,27,22,0.6)]">
            <Eyebrow>Who I am</Eyebrow>
            {instructor.photo ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={instructor.photo} alt={instructor.name ? `Photo of ${instructor.name}` : "Photo of the instructor"} className="mt-6 h-20 w-20 rounded-2xl object-cover" />
            ) : (
              <div className="mt-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-graphite text-emerald-300" aria-hidden="true">
                <svg viewBox="0 0 24 24" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" strokeLinecap="round" />
                </svg>
              </div>
            )}
            {instructor.name && <p className="mt-4 font-serif text-2xl font-semibold text-graphite">{instructor.name}</p>}
            {instructor.linkedin && (
              <a href={instructor.linkedin} target="_blank" rel="noopener noreferrer" className="mt-1 inline-block text-sm font-semibold text-forest hover:underline">
                LinkedIn profile →
              </a>
            )}
            <ul className="mt-6 space-y-2 text-sm text-graphite-2">
              {["AI Architect", "Ex-Amazon", "FDE Architect at an AI startup", "Ships AI to enterprise customers"].map((t) => (
                <li key={t} className="flex gap-2">
                  <Tick />
                  {t}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">
              Built by someone who&apos;s sat on both sides of the loop.
            </h2>
            <div className="mt-6 space-y-4 text-lg leading-relaxed text-graphite-2">
              <p>
                I&apos;m a seasoned AI architect. I worked at Amazon, and today I&apos;m an FDE Architect at an AI startup, working in the Forward
                Deployed Engineering model and shipping AI-based solutions to enterprise customers.
              </p>
              <p>
                The interviews for these roles test the job itself: scoping a messy problem, building something that works, proving it with evals, and
                explaining it to people who decide. Throughout the course you&apos;ll find &ldquo;From my loop&rdquo; notes with what I&apos;ve seen
                work, from Amazon&apos;s bar raiser round to a startup&apos;s live customer scenario.
              </p>
              <p className="border-l-4 border-vermilion pl-5 font-serif text-xl italic text-graphite">
                I built {SITE_NAME} to be the prep I wish I&apos;d had.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="scroll-mt-20 border-t border-rule bg-paper-2/60">
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 py-24 sm:px-6 lg:grid-cols-2">
          <div>
            <Eyebrow>Pricing</Eyebrow>
            <h2 className="mt-4 font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">One price. Every track. Lifetime access.</h2>
            <p className="mt-4 max-w-md text-lg leading-relaxed text-graphite-2">
              Start free with the first Foundations module, the first lesson of every track and FDE Module 1. Upgrade when you&apos;re ready to prepare
              for real.
            </p>
            <p className="mt-4 max-w-md text-graphite-2">
              For scale: a single one-hour mock with a human interviewer is reported to cost roughly $170 to $340 on popular platforms. This is one
              payment for every track, unlimited practice and lifetime updates. Human mocks are still worth doing; this is how you arrive ready for them.
            </p>
          </div>
          <div className="rounded-3xl bg-graphite p-8 text-paper shadow-[0_40px_80px_-40px_rgba(29,27,22,0.9)] sm:p-10">
            <div className="flex items-baseline gap-2">
              <span className="font-serif text-6xl font-semibold">${price}</span>
              <span className="text-paper-3">one-time</span>
            </div>
            <ul className="mt-8 space-y-3 text-[15px] text-paper-3">
              {[
                `Foundations plus all three role tracks: ${all.length} lessons, ${hours}+ hours`,
                `${graded} graded tasks: Python exercises, timed drills, written answers and live sessions`,
                "Three full mock interview loops, one per role, with an auto-built scorecard",
                "Voice mock interviews and interactive design rounds, graded by Claude",
                "Progress dashboard, week-by-week plan and daily review",
                "A portfolio capstone on the real API, and a public record of verified results",
                "AI tutor on every exercise, and all future updates",
              ].map((f) => (
                <li key={f} className="flex gap-2.5">
                  <Tick className="text-emerald-300" />
                  {f}
                </li>
              ))}
            </ul>
            <BuyButton viewer={viewer} price={price} className="mt-9 block w-full rounded-full text-center" />
            <p className="mt-3 text-center text-xs text-paper-3">Free lessons need no credit card.</p>
            <p className="mt-1 text-center text-xs text-paper-3">Refunds: email us within 14 days (reply to your receipt). A refund ends access.</p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-3xl scroll-mt-20 px-4 py-24 sm:px-6">
        <h2 className="text-center font-serif text-4xl font-semibold tracking-[-0.015em] text-graphite">Questions</h2>
        <div className="mt-10 divide-y divide-rule border-y border-rule">
          {FAQ.map(([q, a]) => (
            <details key={q} className="group py-5">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-serif text-lg font-semibold text-graphite">
                {q}
                <span className="text-graphite-3 transition group-open:rotate-45" aria-hidden="true">
                  +
                </span>
              </summary>
              <p className="mt-3 leading-relaxed text-graphite-2">{a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Final call to action */}
      <section className="mx-auto max-w-6xl px-4 pb-24 sm:px-6">
        <div className="relative overflow-hidden rounded-[2rem] bg-graphite px-8 py-16 text-center text-paper">
          <div className="pointer-events-none absolute -left-20 -top-20 h-64 w-64 rounded-full bg-emerald-400/15 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-24 -right-10 h-64 w-64 rounded-full bg-orange-400/10 blur-3xl" />
          <p className="relative font-mono text-[11px] uppercase tracking-[0.18em] text-emerald-300">Foundations · C1 · Free</p>
          <h2 className="relative mt-4 font-serif text-4xl font-semibold leading-tight sm:text-5xl">Walk into the onsite having done it before.</h2>
          <p className="relative mx-auto mt-4 max-w-xl text-paper-3">
            The best feeling in an interview is recognition: you&apos;ve heard this kind of question, you&apos;ve been pushed like this, and you know your
            next move. Start with the free module. It takes under two hours, with no setup and no credit card.
          </p>
          <Link href="/learn" className="relative mt-9 inline-block rounded-full bg-emerald-400 px-7 py-3 font-semibold text-graphite hover:bg-emerald-300">
            Start free →
          </Link>
        </div>
      </section>

      <footer className="border-t border-rule">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-4 py-8 text-sm text-graphite-3 sm:flex-row sm:px-6">
          <span className="flex items-center gap-2 font-serif font-semibold text-graphite">
            <Mark className="h-6 w-6" />
            {SITE_NAME}
          </span>
          <span className="text-center sm:ml-auto sm:text-right">
            © {new Date().getFullYear()} {SITE_NAME}. Independent course, not affiliated with Anthropic, OpenAI or Perplexity.
          </span>
        </div>
      </footer>
    </div>
  );
}
