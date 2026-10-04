import Link from "next/link";
import { getViewer, toClientViewer } from "@/lib/access";
import { getCourse } from "@/lib/content";
import { SITE_NAME } from "@/lib/config";
import AccountBadge from "@/components/AccountBadge";
import BuyButton from "@/components/BuyButton";

export const dynamic = "force-dynamic";

const AUDIENCE = [
  ["Software engineers", "moving into Forward Deployed, solutions or customer-facing engineering roles."],
  ["Solutions engineers & consultants", "who want to build and ship the systems, not just design them."],
  ["AI engineers", "who can build a demo and now need to get it working inside an enterprise, safely."],
];

const ENGAGEMENTS = [
  ["Cobalt Supply", "Profile, clean and reconcile messy CRM and billing exports", "Data wrangling"],
  ["Northwind Freight", "Integrate a paginated, rate-limited partner API and webhooks", "APIs"],
  ["Pinecrest Fitness", "Answer the COO's questions with SQL, cohorts and a metrics layer", "SQL"],
  ["Harbor Bank", "Build an injection-resistant ticket classifier with Claude", "Anthropic SDK"],
  ["Brightway Retail", "Ship a support agent with RAG, approvals, evals and production monitoring", "Agents & evals"],
  ["NorthStar Logistics", "Capstone: scope, build, evaluate and present an exception-triage agent", "Capstone"],
];

const STEPS = [
  ["Read", "Detailed written lessons built from real deployment patterns: discovery calls, messy data, flaky APIs, LLM evals, production incidents."],
  ["Code", "A full Python editor runs in your browser, including a simulated Anthropic SDK. No installs, no API key, no setup."],
  ["Get graded", "Every exercise has automatic checks and step-by-step hints, plus an AI tutor powered by Claude when you're stuck."],
];

const FAQ = [
  ["Do I need to install anything?", "No. Lessons, the code editor and the Python runtime all run in your browser. The code you write uses the same Anthropic SDK calls you'd use in production."],
  ["How much Python do I need?", "Comfort with functions, lists and dictionaries is enough to start. Module 3 strengthens the data-wrangling skills the rest of the course relies on."],
  ["Do I need an Anthropic API key?", "Not for the course. Exercises run against a built-in simulator of the SDK, so you can learn without paying for API calls. Your code works against the real API unchanged."],
  ["How long does it take?", "About 40 hours of lessons and exercises. Most people finish in 4 to 8 weeks at a few hours a week. Access never expires."],
  ["Can I try it before buying?", "Yes. Module 1 is free, with no credit card needed."],
];

function Check() {
  return (
    <svg viewBox="0 0 20 20" className="mt-0.5 h-4 w-4 shrink-0 text-accent" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0Z" clipRule="evenodd" />
    </svg>
  );
}

function Logo() {
  return (
    <span className="flex items-center gap-2 font-semibold text-white">
      <svg viewBox="0 0 64 64" className="h-7 w-7" aria-hidden="true">
        <rect width="64" height="64" rx="14" fill="#111827" />
        <path d="M18 44 L32 16 L46 44" fill="none" stroke="#34d399" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="32" cy="38" r="4" fill="#60a5fa" />
      </svg>
      {SITE_NAME}
    </span>
  );
}

/** A static picture of the lesson workspace: reading on the left, code and output on the right. */
function WorkspacePreview() {
  return (
    <div className="relative min-w-0 overflow-hidden rounded-2xl border border-line bg-panel shadow-2xl shadow-accent/5">
      <div className="flex items-center gap-1.5 border-b border-line px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-amber-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/70" />
        <span className="ml-3 truncate text-xs text-gray-500">Module 7 · Exercise: Human-in-the-Loop Approval Gates</span>
      </div>
      <div className="grid sm:grid-cols-5">
        <div className="hidden space-y-3 border-r border-line p-4 sm:col-span-2 sm:block">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-accent">Exercise · 30 min</div>
          <div className="h-2.5 w-11/12 rounded bg-gray-600/60" />
          <div className="h-2 w-full rounded bg-gray-700/70" />
          <div className="h-2 w-10/12 rounded bg-gray-700/70" />
          <div className="h-2 w-9/12 rounded bg-gray-700/70" />
          <div className="mt-4 rounded-lg border border-accent/30 bg-accent/5 p-3">
            <div className="h-2 w-8/12 rounded bg-accent/40" />
            <div className="mt-2 h-2 w-10/12 rounded bg-gray-700/70" />
          </div>
          <div className="h-2 w-full rounded bg-gray-700/70" />
          <div className="h-2 w-7/12 rounded bg-gray-700/70" />
        </div>
        <div className="min-w-0 sm:col-span-3">
          <pre className="overflow-hidden p-4 font-mono text-[11px] leading-5 text-gray-300">
            <span className="text-violet-300">def</span> <span className="text-sky-300">guarded_execute</span>(block, approver, audit):{"\n"}
            {"    "}<span className="text-violet-300">if</span> needs_approval(block.name, block.input):{"\n"}
            {"        "}request = {"{"}<span className="text-amber-200">&quot;summary&quot;</span>: describe_action(...){"}"}{"\n"}
            {"        "}<span className="text-violet-300">try</span>:{"\n"}
            {"            "}approved = approver(request) <span className="text-violet-300">is True</span>{"\n"}
            {"        "}<span className="text-violet-300">except</span> Exception:{"\n"}
            {"            "}approved = <span className="text-violet-300">False</span>  <span className="text-gray-500"># fail closed</span>
          </pre>
          <div className="border-t border-line bg-ink/60 p-4 font-mono text-[11px] leading-5">
            <div className="text-gray-500">OUTPUT</div>
            <div className="text-gray-300">REVIEWER SEES: Issue $75.00 store credit to Rosa Silva...</div>
            <div className="mt-1 text-accent">✓ 8 of 8 checks passed · Exercise complete</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default async function Home() {
  const course = getCourse();
  const viewer = toClientViewer(await getViewer());
  const totalMinutes = course.modules.reduce((s, m) => s + m.minutes, 0);
  const hours = Math.floor(totalMinutes / 60);
  const lessons = course.modules.reduce((s, m) => s + m.lessons.length, 0);
  const exercises = course.modules.reduce((s, m) => s + m.lessons.filter((l) => l.type === "exercise").length, 0);
  const price = course.priceUsd;
  const navLinks = [["#how", "How it works"], ["#syllabus", "Syllabus"], ["#instructor", "Instructor"], ["#pricing", "Pricing"], ["#faq", "FAQ"]];

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-line/60 bg-ink/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3 sm:px-6">
          <Link href="/" aria-label={`${SITE_NAME} home`}><Logo /></Link>
          <nav className="ml-auto hidden items-center gap-6 text-sm text-gray-400 md:flex">
            {navLinks.map(([href, label]) => (
              <a key={href} href={href} className="hover:text-white">{label}</a>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3 md:ml-0">
            {viewer.signedIn || viewer.mode === "dev" ? (
              <Link href="/learn" className="rounded-lg bg-accent px-3 py-1.5 text-sm font-semibold text-ink hover:opacity-90">My course</Link>
            ) : (
              <>
                <AccountBadge viewer={viewer} />
                <Link href="/learn" className="rounded-lg bg-accent px-3 py-1.5 text-sm font-semibold text-ink hover:opacity-90">Start free</Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute -top-40 left-1/2 h-[480px] w-[880px] -translate-x-1/2 rounded-full bg-accent/10 blur-3xl" />
        <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 pb-16 pt-14 sm:px-6 lg:grid-cols-2 lg:pt-24">
          <div className="min-w-0">
            <p className="inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
              The hands-on course for Forward Deployed Engineers
            </p>
            <h1 className="mt-5 text-4xl font-bold leading-[1.1] tracking-tight text-white sm:text-5xl">
              Learn to ship AI that works <span className="text-accent">inside your customer&apos;s world.</span>
            </h1>
            <p className="mt-6 max-w-xl text-lg text-gray-400">
              Discovery calls, messy data, flaky APIs, Claude-powered agents, evals and production incidents. Practice every part of the
              job through six realistic customer engagements, writing real Python in your browser.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/learn" className="rounded-lg bg-accent px-6 py-3 font-semibold text-ink hover:opacity-90">Start Module 1 free →</Link>
              <a href="#pricing" className="rounded-lg border border-line px-6 py-3 font-semibold text-gray-200 hover:bg-line">Full access · ${price}</a>
            </div>
            <p className="mt-4 text-sm text-gray-500">No installs · No API key needed · Lifetime access</p>
          </div>
          <WorkspacePreview />
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-line bg-panel-2">
        <dl className="mx-auto grid max-w-6xl grid-cols-2 gap-6 px-4 py-10 text-center sm:px-6 md:grid-cols-4">
          {[[`${hours}+`, "hours of content"], [String(lessons), "lessons"], [String(exercises), "graded coding exercises"], [String(course.modules.length), "modules, one capstone"]].map(([n, l]) => (
            <div key={l}>
              <dt className="text-3xl font-bold text-white">{n}</dt>
              <dd className="mt-1 text-sm text-gray-500">{l}</dd>
            </div>
          ))}
        </dl>
      </section>

      {/* Audience */}
      <section className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <h2 className="text-3xl font-bold text-white">Who it&apos;s for</h2>
        <p className="mt-2 max-w-2xl text-gray-400">
          Forward Deployed Engineers sit between the customer and the code. They find the real problem, build the solution in the
          customer&apos;s environment, and own it until it works. This course teaches that job end to end.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {AUDIENCE.map(([who, what]) => (
            <div key={who} className="rounded-xl border border-line bg-panel p-6">
              <h3 className="font-semibold text-white">{who}</h3>
              <p className="mt-2 text-sm text-gray-400">{what}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Engagements */}
      <section className="border-y border-line bg-panel-2">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <h2 className="text-3xl font-bold text-white">Six customer engagements, not toy examples</h2>
          <p className="mt-2 max-w-2xl text-gray-400">
            Each module puts you inside a realistic customer with real constraints, messy data and a stakeholder waiting for results.
          </p>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {ENGAGEMENTS.map(([name, task, tag]) => (
              <div key={name} className="rounded-xl border border-line bg-panel p-6">
                <span className="rounded-full bg-accent-2/10 px-2.5 py-1 text-xs font-medium text-accent-2">{tag}</span>
                <h3 className="mt-4 font-semibold text-white">{name}</h3>
                <p className="mt-1 text-sm text-gray-400">{task}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20 sm:px-6">
        <h2 className="text-3xl font-bold text-white">How it works</h2>
        <p className="mt-2 text-gray-400">Lesson on the left, code on the right, instant feedback.</p>
        <ol className="mt-8 grid gap-6 md:grid-cols-3">
          {STEPS.map(([title, text], i) => (
            <li key={title} className="rounded-xl border border-line bg-panel p-6">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 font-mono text-sm font-semibold text-accent">{i + 1}</span>
              <h3 className="mt-4 font-semibold text-white">{title}</h3>
              <p className="mt-2 text-sm text-gray-400">{text}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* Syllabus */}
      <section id="syllabus" className="scroll-mt-20 border-y border-line bg-panel-2">
        <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
          <h2 className="text-3xl font-bold text-white">Syllabus</h2>
          <p className="mt-2 text-gray-400">From your first customer call to running Claude-powered systems in production. Module 1 is free.</p>
          <div className="mt-8 space-y-3">
            {course.modules.map((m) => (
              <details key={m.slug} className="group rounded-xl border border-line bg-panel open:border-accent/40">
                <summary className="flex cursor-pointer list-none items-center gap-4 p-5">
                  <span className="font-mono text-sm text-gray-500">{String(m.number).padStart(2, "0")}</span>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-white">{m.title}</h3>
                    <p className="mt-0.5 text-xs text-gray-500">
                      {m.lessons.length} lessons · {Math.round(m.minutes / 6) / 10} hours{m.number === 1 ? " · Free" : ""}
                    </p>
                  </div>
                  <span className="text-gray-500 transition group-open:rotate-45" aria-hidden="true">+</span>
                </summary>
                <div className="grid gap-6 border-t border-line p-5 md:grid-cols-2">
                  <div>
                    <p className="text-sm text-gray-400">{m.summary}</p>
                    <ul className="mt-4 space-y-2 text-sm text-gray-300">
                      {m.outcomes.map((o) => (
                        <li key={o} className="flex gap-2"><Check />{o}</li>
                      ))}
                    </ul>
                  </div>
                  <ol className="space-y-1.5 text-sm">
                    {m.lessons.map((l) => (
                      <li key={l.slug} className="flex items-center gap-3 text-gray-400">
                        <span className="w-16 shrink-0 text-[10px] uppercase tracking-wider text-gray-600">{l.type}</span>
                        <span className="flex-1">{l.title}</span>
                        <span className="text-xs text-gray-600">{l.minutes}m</span>
                      </li>
                    ))}
                  </ol>
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Instructor */}
      <section id="instructor" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20 sm:px-6">
        <div className="grid items-start gap-10 rounded-2xl border border-line bg-panel p-8 md:grid-cols-3 md:p-10">
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-accent">Who I am</p>
            <div className="mt-6 flex h-24 w-24 items-center justify-center rounded-2xl bg-accent/10 text-accent" aria-hidden="true">
              <svg viewBox="0 0 24 24" className="h-12 w-12" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="8" r="4" />
                <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" strokeLinecap="round" />
              </svg>
            </div>
            <div className="mt-6 flex flex-wrap gap-2">
              {["AI Architect", "Ex-Amazon", "FDE Architect at an AI startup", "Enterprise AI delivery"].map((t) => (
                <span key={t} className="rounded-full border border-line px-3 py-1 text-xs text-gray-300">{t}</span>
              ))}
            </div>
          </div>
          <div className="md:col-span-2">
            <h2 className="text-2xl font-bold text-white sm:text-3xl">A seasoned AI architect who does this job every day.</h2>
            <div className="mt-5 space-y-4 text-gray-400">
              <p>
                I&apos;m a seasoned AI architect. I worked at Amazon, and today I&apos;m an FDE Architect at an AI startup, working in the
                Forward Deployed Engineering model: embedded with customers, from the first discovery call to the system running in
                their production environment.
              </p>
              <p>
                I&apos;ve shipped AI-based solutions to enterprise customers, and I&apos;ve learned that the hard parts are rarely the
                model. They&apos;re the messy data, the integration nobody documented, the security review, the evaluation that proves
                it works, and the readout that earns the next phase.
              </p>
              <p>
                I built {SITE_NAME} to teach exactly those parts, the way I wish I&apos;d learned them: through realistic customer
                engagements and code you write yourself.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="scroll-mt-20 border-y border-line bg-panel-2">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center sm:px-6">
          <h2 className="text-3xl font-bold text-white">One price. Lifetime access.</h2>
          <p className="mt-2 text-gray-400">Start free. Upgrade when you&apos;re ready.</p>
          <div className="mx-auto mt-10 max-w-md rounded-2xl border border-accent/40 bg-panel p-8 text-left shadow-2xl shadow-accent/5">
            <div className="flex items-baseline justify-center gap-2">
              <span className="text-5xl font-bold text-white">${price}</span>
              <span className="text-sm text-gray-500">one-time</span>
            </div>
            <ul className="mt-8 space-y-3 text-sm text-gray-300">
              {[
                `All ${course.modules.length} modules: ${lessons} lessons, ${hours}+ hours`,
                `${exercises} hands-on Python exercises with instant grading`,
                "Build with the Anthropic SDK: tool use, RAG, agents and evals",
                "Production skills: config, logging, alerts, incidents, handoff",
                "A full capstone engagement, from scoping to executive readout",
                "AI tutor on every exercise",
                "All future updates included",
              ].map((f) => (
                <li key={f} className="flex gap-2"><Check />{f}</li>
              ))}
            </ul>
            <BuyButton viewer={viewer} price={price} className="mt-8 block w-full text-center" />
            <p className="mt-3 text-center text-xs text-gray-500">Module 1 is free. No credit card needed to start.</p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-3xl scroll-mt-20 px-4 py-20 sm:px-6">
        <h2 className="text-center text-3xl font-bold text-white">Questions</h2>
        <div className="mt-8 divide-y divide-line rounded-xl border border-line bg-panel">
          {FAQ.map(([q, a]) => (
            <details key={q} className="group p-5">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium text-white">
                {q}
                <span className="text-gray-500 transition group-open:rotate-45" aria-hidden="true">+</span>
              </summary>
              <p className="mt-3 text-sm text-gray-400">{a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-4 pb-20 sm:px-6">
        <div className="rounded-2xl border border-accent/30 bg-gradient-to-br from-accent/15 to-accent-2/10 p-10 text-center">
          <h2 className="text-3xl font-bold text-white">Your first customer engagement starts now.</h2>
          <p className="mx-auto mt-3 max-w-xl text-gray-300">Module 1 is free and takes about two hours. No setup, no credit card.</p>
          <Link href="/learn" className="mt-8 inline-block rounded-lg bg-accent px-6 py-3 font-semibold text-ink hover:opacity-90">Start Module 1 free →</Link>
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-4 py-8 text-sm text-gray-500 sm:flex-row sm:px-6">
          <Logo />
          <span className="sm:ml-auto">© {new Date().getFullYear()} {SITE_NAME}. Not affiliated with Anthropic.</span>
        </div>
      </footer>
    </div>
  );
}
