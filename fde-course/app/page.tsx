import Link from "next/link";
import { getViewer, toClientViewer } from "@/lib/access";
import { getCourse, FDE_TRACK } from "@/lib/content";
import { SITE_NAME, tracksEnabled } from "@/lib/config";
import AccountBadge from "@/components/AccountBadge";
import BuyButton from "@/components/BuyButton";
import TracksHome from "@/components/TracksHome";
import { Avatar, Mark } from "@/components/Playbook";

export const dynamic = "force-dynamic";

const AUDIENCE = [
  ["Software engineers", "moving into Forward Deployed, solutions or customer-facing engineering roles."],
  ["Solutions engineers & consultants", "who want to build and ship the systems, not just design them."],
  ["AI engineers", "who can build a demo and now need to get it working inside an enterprise, safely."],
];

// What you do at each customer (keyed by company; contacts come from course.json).
const TASKS: Record<string, [string, string]> = {
  "Brightline Health": ["Run your first week: prioritize the backlog and brief the VP", "The FDE role"],
  "Lumen Insurance": ["Run discovery, map stakeholders and measure an honest baseline", "Discovery"],
  "Cobalt Supply": ["Profile, clean and reconcile messy CRM and billing exports", "Data wrangling"],
  "Northwind Freight": ["Integrate a paginated, rate-limited partner API and webhooks", "APIs"],
  "Pinecrest Fitness": ["Answer the COO's questions with SQL, cohorts and a metrics layer", "SQL"],
  "Harbor Bank": ["Build an injection-resistant ticket classifier with Claude", "Anthropic SDK"],
  "Brightway Retail": ["Ship a support agent with RAG, approvals, evals and monitoring", "Agents · Evals · Prod"],
  "NorthStar Logistics": ["Capstone: scope, build, evaluate and present a triage agent", "Capstone"],
};

const STEPS = [
  ["Read the field guide", "Detailed written lessons built from real deployment patterns: discovery calls, messy data, flaky APIs, LLM evals, production incidents."],
  ["Take the case", "Each exercise is a request from a customer contact. Write real Python in the browser, including the Anthropic SDK. No installs, no API key."],
  ["Resolve it", "Automatic checks light up one by one, hints arrive when you need them, and an AI tutor nudges you when you're stuck."],
];

const FAQ = [
  ["Do I need to install anything?", "No. Lessons, the code editor and the Python runtime all run in your browser. The code you write uses the same Anthropic SDK calls you'd use in production."],
  ["How much Python do I need?", "Comfort with functions, lists and dictionaries is enough to start. Module 3 strengthens the data-wrangling skills the rest of the course relies on."],
  ["Do I need an Anthropic API key?", "Not for the course. Exercises run against a built-in simulator of the SDK, so you can learn without paying for API calls. Your code works against the real API unchanged."],
  ["How long does it take?", "About 40 hours of lessons and exercises. Most people finish in 4 to 8 weeks at a few hours a week. Access never expires."],
  ["Can I try it before buying?", "Yes. Module 1 is free, with no credit card needed."],
];

function Tick({ className = "text-forest" }: { className?: string }) {
  return (
    <svg viewBox="0 0 20 20" className={`mt-1 h-4 w-4 shrink-0 ${className}`} fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M16.7 5.3a1 1 0 0 1 0 1.4l-8 8a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.4L8 12.6l7.3-7.3a1 1 0 0 1 1.4 0Z" clipRule="evenodd" />
    </svg>
  );
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-vermilion">{children}</p>;
}

/** The product in one picture: a customer's case file, the console, and the case being resolved. */
function HeroComposition() {
  return (
    <div className="relative mx-auto w-full max-w-xl lg:max-w-none">
      {/* Case file */}
      <div className="relative z-10 rotate-[-1.5deg] rounded-2xl border border-rule bg-white shadow-[0_30px_60px_-35px_rgba(29,27,22,0.6)] sm:w-[82%]">
        <div className="flex items-center gap-2 border-b border-rule bg-paper-2/70 px-4 py-2 font-mono text-[10px] uppercase tracking-[0.14em] text-graphite-3">
          <span className="font-semibold text-vermilion">Case file</span>
          <span>·</span>
          <span>NorthStar Logistics</span>
          <span className="ml-auto flex items-center gap-1 rounded-full bg-vermilion/10 px-2 py-0.5 text-vermilion">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-vermilion" /> Open
          </span>
        </div>
        <div className="p-4">
          <div className="flex items-center gap-2.5">
            <Avatar name="Dana Whitfield" size="sm" />
            <div className="leading-tight">
              <div className="text-sm font-semibold text-graphite">Dana Whitfield</div>
              <div className="text-[11px] text-graphite-3">VP Operations · Freight</div>
            </div>
          </div>
          <p className="mt-3 font-serif text-[15px] leading-relaxed text-graphite-2">
            &ldquo;My coordinators spend their whole day on carrier messages, and we&apos;re breaching SLAs with our best customers. Can Claude triage
            exceptions so my team handles the hard cases?&rdquo;
          </p>
        </div>
      </div>

      {/* Console */}
      <div className="relative -mt-2 ml-auto rotate-[1deg] overflow-hidden rounded-2xl bg-console text-gray-200 shadow-[0_40px_80px_-30px_rgba(13,17,23,0.75)] sm:-mt-3 sm:w-[86%]">
        <div className="flex items-center gap-2 border-b border-console-line px-3 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <span className="ml-2 rounded bg-console-2 px-2 py-0.5 font-mono text-[11px] text-gray-400">triage_agent.py</span>
          <span className="ml-auto flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider text-gray-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Runtime ready
          </span>
        </div>
        <pre className="overflow-hidden px-4 py-3 font-mono text-[11.5px] leading-5 text-gray-300">
          <span className="text-[#ff7b72]">def</span> <span className="text-[#d2a8ff]">guarded_execute</span>(block, approver, audit):{"\n"}
          {"    "}<span className="text-[#ff7b72]">if</span> block.name <span className="text-[#ff7b72]">in</span> NEEDS_APPROVAL:{"\n"}
          {"        "}approved = approver(request) <span className="text-[#ff7b72]">is True</span>{"\n"}
          {"        "}<span className="text-[#ff7b72]">if not</span> approved:  <span className="italic text-gray-500"># fail closed</span>{"\n"}
          {"            "}<span className="text-[#ff7b72]">return</span> declined(block)
        </pre>
        <div className="border-t border-console-line px-4 py-3">
          <div className="flex gap-1">
            {Array.from({ length: 7 }).map((_, i) => (
              <span key={i} className="bar-fill h-1.5 flex-1 rounded-full bg-emerald-400" style={{ animationDelay: `${300 + i * 120}ms` }} />
            ))}
          </div>
          <div className="check-in mt-3 flex gap-2.5 rounded-lg border border-emerald-400/20 bg-emerald-400/[0.06] p-3" style={{ animationDelay: "1300ms" }}>
            <Avatar name="Dana Whitfield" size="sm" dark />
            <div>
              <div className="font-mono text-[10px] uppercase tracking-wider text-emerald-300">Case resolved · 7/7 checks</div>
              <p className="mt-1 font-serif text-sm text-gray-100">&ldquo;My coordinators can finally focus on the hard cases.&rdquo;</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default async function Home() {
  // The three-track home page once tracks are live; the original FDE page until then.
  if (tracksEnabled()) return <TracksHome course={getCourse()} viewer={toClientViewer(await getViewer())} />;
  return <FdeHome />;
}

async function FdeHome() {
  const full = getCourse();
  const course = { ...full, modules: full.modules.filter((m) => m.track === FDE_TRACK) };
  const viewer = toClientViewer(await getViewer());
  const totalMinutes = course.modules.reduce((s, m) => s + m.minutes, 0);
  const hours = Math.floor(totalMinutes / 60);
  const lessons = course.modules.reduce((s, m) => s + m.lessons.length, 0);
  const exercises = course.modules.reduce((s, m) => s + m.lessons.filter((l) => l.type === "exercise").length, 0);
  const price = course.priceUsd;
  const customers = course.modules
    .map((m) => ({ ...m.customer, modules: course.modules.filter((x) => x.customer.company === m.customer.company).map((x) => x.number) }))
    .filter((c, i, all) => all.findIndex((x) => x.company === c.company) === i);
  const navLinks = [["#how", "How it works"], ["#customers", "Customers"], ["#syllabus", "Syllabus"], ["#instructor", "Instructor"], ["#pricing", "Pricing"]];

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
            <Eyebrow>The field manual for Forward Deployed Engineers</Eyebrow>
            <h1 className="mt-5 font-serif text-[2.75rem] font-semibold leading-[1.04] tracking-[-0.025em] text-graphite sm:text-6xl">
              Learn to ship AI inside your{" "}
              <span className="relative inline-block italic">
                customer&apos;s world.
                <svg viewBox="0 0 300 14" preserveAspectRatio="none" className="absolute -bottom-2 left-0 h-3 w-full text-vermilion" aria-hidden="true">
                  <path d="M2 10 C 70 2, 150 2, 298 8" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                </svg>
              </span>
            </h1>
            <p className="mt-7 max-w-xl text-lg leading-relaxed text-graphite-2">
              Discovery calls, messy data, flaky APIs, Claude-powered agents, evals and production incidents. Work through {customers.length} realistic
              customer engagements, writing real Python in your browser.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <Link
                href="/learn"
                className="rounded-full bg-graphite px-6 py-3 font-semibold text-paper shadow-[0_14px_30px_-16px_rgba(29,27,22,0.8)] hover:bg-black"
              >
                Start Module 1 free →
              </Link>
              <a href="#pricing" className="rounded-full border border-graphite/20 px-6 py-3 font-semibold text-graphite hover:border-graphite/50">
                Full access · ${price}
              </a>
            </div>
            <p className="mt-5 text-sm text-graphite-3">No installs · No API key needed · Lifetime access</p>
          </div>
          <HeroComposition />
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-rule bg-paper-2/60">
        <dl className="mx-auto grid max-w-6xl grid-cols-2 px-4 sm:px-6 md:grid-cols-4">
          {[[`${hours}+`, "hours of content"], [String(lessons), "lessons"], [String(exercises), "graded engagement tasks"], [String(customers.length), "customers, one capstone"]].map(
            ([n, l], i) => (
              <div key={l} className={`px-4 py-9 text-center ${i > 0 ? "md:border-l md:border-rule" : ""} ${i % 2 ? "border-l border-rule md:border-l" : ""}`}>
                <dt className="font-serif text-4xl font-semibold text-graphite">{n}</dt>
                <dd className="mt-1 text-sm text-graphite-3">{l}</dd>
              </div>
            ),
          )}
        </dl>
      </section>

      {/* Audience */}
      <section className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
        <div className="grid gap-12 lg:grid-cols-[1fr_1.4fr]">
          <div>
            <Eyebrow>Who it&apos;s for</Eyebrow>
            <h2 className="mt-4 font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">
              The job between the customer and the code.
            </h2>
            <p className="mt-5 leading-relaxed text-graphite-2">
              Forward Deployed Engineers find the real problem, build the solution inside the customer&apos;s environment, and own it until it works.
              This course teaches that job end to end.
            </p>
          </div>
          <ol className="divide-y divide-rule border-y border-rule">
            {AUDIENCE.map(([who, what], i) => (
              <li key={who} className="flex gap-6 py-6">
                <span className="font-serif text-3xl text-vermilion">{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <h3 className="font-serif text-xl font-semibold text-graphite">{who}</h3>
                  <p className="mt-1 text-graphite-2">{what}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Customers */}
      <section id="customers" className="scroll-mt-20 bg-graphite text-paper">
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-emerald-300">Your client list</p>
          <h2 className="mt-4 max-w-2xl font-serif text-4xl font-semibold leading-tight tracking-[-0.015em]">
            {customers.length} customers, not toy examples.
          </h2>
          <p className="mt-4 max-w-2xl text-paper-3">
            Every module puts you inside a realistic company, with messy data, real constraints and a named stakeholder waiting for results.
          </p>
          <ol className="mt-12 grid gap-px overflow-hidden rounded-3xl border border-white/10 bg-white/10 sm:grid-cols-2 lg:grid-cols-4">
            {customers.map((c) => (
              <li key={c.company} className="flex flex-col bg-graphite p-6 transition hover:bg-[#25221c]">
                <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.14em] text-paper-3">
                  <span>{c.modules.length > 1 ? `Modules ${c.modules[0]}–${c.modules[c.modules.length - 1]}` : `Module ${c.modules[0]}`}</span>
                  <span className="text-emerald-300">{TASKS[c.company]?.[1]}</span>
                </div>
                <h3 className="mt-5 font-serif text-2xl font-semibold">{c.company}</h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-paper-3">{TASKS[c.company]?.[0] ?? c.sector}</p>
                <div className="mt-6 flex items-center gap-2.5 border-t border-white/10 pt-4 text-xs text-paper-3">
                  <Avatar name={c.contact} size="sm" dark />
                  <span>
                    <span className="text-paper">{c.contact}</span>
                    <br />
                    {c.role}
                  </span>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-24 sm:px-6">
        <Eyebrow>How it works</Eyebrow>
        <h2 className="mt-4 font-serif text-4xl font-semibold tracking-[-0.015em] text-graphite">Read. Take the case. Resolve it.</h2>
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

      {/* Syllabus */}
      <section id="syllabus" className="scroll-mt-20 border-y border-rule bg-paper-2/60">
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <Eyebrow>Syllabus</Eyebrow>
              <h2 className="mt-4 font-serif text-4xl font-semibold tracking-[-0.015em] text-graphite">From first call to production.</h2>
            </div>
            <p className="text-graphite-3">Module 1 is free.</p>
          </div>
          <div className="mt-10 space-y-3">
            {course.modules.map((m) => (
              <details key={m.slug} className="group rounded-2xl border border-rule bg-white/70 open:shadow-[0_24px_50px_-36px_rgba(29,27,22,0.7)]">
                <summary className="flex cursor-pointer list-none items-center gap-5 p-5 sm:p-6">
                  <span className="font-serif text-2xl text-vermilion">{String(m.number).padStart(2, "0")}</span>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-serif text-xl font-semibold text-graphite">{m.title}</h3>
                    <p className="mt-0.5 text-xs text-graphite-3">
                      {m.customer.company} · {m.lessons.length} lessons · {Math.round(m.minutes / 6) / 10} hours{m.number === 1 ? " · Free" : ""}
                    </p>
                  </div>
                  <span
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-rule text-graphite-2 transition group-open:rotate-45 group-open:bg-graphite group-open:text-paper"
                    aria-hidden="true"
                  >
                    +
                  </span>
                </summary>
                <div className="grid gap-8 border-t border-rule p-5 sm:p-6 md:grid-cols-2">
                  <div>
                    <p className="leading-relaxed text-graphite-2">{m.summary}</p>
                    <ul className="mt-4 space-y-2 text-sm text-graphite-2">
                      {m.outcomes.map((o) => (
                        <li key={o} className="flex gap-2">
                          <Tick />
                          {o}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <ol className="space-y-1.5 text-sm">
                    {m.lessons.map((l) => (
                      <li key={l.slug} className="flex items-center gap-3 text-graphite-2">
                        <span className={`w-10 shrink-0 font-mono text-[10px] uppercase tracking-wider ${l.type === "exercise" ? "text-vermilion" : "text-graphite-3"}`}>
                          {{ reading: "Read", exercise: "Task", quiz: "Quiz", drill: "Drill", written: "Write", roleplay: "Talk" }[l.type]}
                        </span>
                        <span className="flex-1">{l.title.replace(/^Exercise:\s*/, "")}</span>
                        <span className="text-xs text-graphite-3">{l.minutes}m</span>
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
      <section id="instructor" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-24 sm:px-6">
        <div className="grid items-center gap-12 lg:grid-cols-[0.9fr_1.4fr]">
          <div className="relative">
            <div className="rotate-[-2deg] rounded-3xl border border-rule bg-white/80 p-8 shadow-[0_30px_60px_-40px_rgba(29,27,22,0.6)]">
              <Eyebrow>Who I am</Eyebrow>
              <div className="mt-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-graphite text-emerald-300" aria-hidden="true">
                <svg viewBox="0 0 24 24" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="8" r="4" />
                  <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" strokeLinecap="round" />
                </svg>
              </div>
              <ul className="mt-6 space-y-2 text-sm text-graphite-2">
                {["AI Architect", "Ex-Amazon", "FDE Architect at an AI startup", "Ships AI to enterprise customers"].map((t) => (
                  <li key={t} className="flex gap-2">
                    <Tick />
                    {t}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div>
            <h2 className="font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">
              A seasoned AI architect who does this job every day.
            </h2>
            <div className="mt-6 space-y-4 text-lg leading-relaxed text-graphite-2">
              <p>
                I&apos;m a seasoned AI architect. I worked at Amazon, and today I&apos;m an FDE Architect at an AI startup, working in the Forward
                Deployed Engineering model: embedded with customers, from the first discovery call to the system running in their production
                environment.
              </p>
              <p>
                I&apos;ve shipped AI-based solutions to enterprise customers, and I&apos;ve learned that the hard parts are rarely the model.
                They&apos;re the messy data, the integration nobody documented, the security review, the evaluation that proves it works, and the
                readout that earns the next phase.
              </p>
              <p className="border-l-4 border-vermilion pl-5 font-serif text-xl italic text-graphite">
                I built {SITE_NAME} to teach exactly those parts, the way I wish I&apos;d learned them.
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
            <h2 className="mt-4 font-serif text-4xl font-semibold leading-tight tracking-[-0.015em] text-graphite">One price. Lifetime access.</h2>
            <p className="mt-4 max-w-md text-lg leading-relaxed text-graphite-2">
              Start with Module 1 for free. Upgrade when you&apos;re ready to take on every customer.
            </p>
          </div>
          <div className="rounded-3xl bg-graphite p-8 text-paper shadow-[0_40px_80px_-40px_rgba(29,27,22,0.9)] sm:p-10">
            <div className="flex items-baseline gap-2">
              <span className="font-serif text-6xl font-semibold">${price}</span>
              <span className="text-paper-3">one-time</span>
            </div>
            <ul className="mt-8 space-y-3 text-[15px] text-paper-3">
              {[
                `All ${course.modules.length} modules: ${lessons} lessons, ${hours}+ hours`,
                `${exercises} hands-on Python tasks with instant grading`,
                "Build with the Anthropic SDK: tool use, RAG, agents and evals",
                "Production skills: config, logging, alerts, incidents, handoff",
                "A full capstone engagement, from scoping to executive readout",
                "AI tutor on every exercise, and all future updates",
              ].map((f) => (
                <li key={f} className="flex gap-2.5">
                  <Tick className="text-emerald-300" />
                  {f}
                </li>
              ))}
            </ul>
            <BuyButton viewer={viewer} price={price} className="mt-9 block w-full rounded-full text-center" />
            <p className="mt-3 text-center text-xs text-paper-3">Module 1 is free. No credit card needed to start.</p>
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
          <p className="relative font-mono text-[11px] uppercase tracking-[0.18em] text-emerald-300">Case file · Brightline Health · Open</p>
          <h2 className="relative mt-4 font-serif text-4xl font-semibold leading-tight sm:text-5xl">Your first customer is waiting.</h2>
          <p className="relative mx-auto mt-4 max-w-xl text-paper-3">Module 1 is free and takes about two hours. No setup, no credit card.</p>
          <Link href="/learn" className="relative mt-9 inline-block rounded-full bg-emerald-400 px-7 py-3 font-semibold text-graphite hover:bg-emerald-300">
            Start Module 1 free →
          </Link>
        </div>
      </section>

      <footer className="border-t border-rule">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-4 px-4 py-8 text-sm text-graphite-3 sm:flex-row sm:px-6">
          <span className="flex items-center gap-2 font-serif font-semibold text-graphite">
            <Mark className="h-6 w-6" />
            {SITE_NAME}
          </span>
          <span className="sm:ml-auto">
            © {new Date().getFullYear()} {SITE_NAME}. Not affiliated with Anthropic.
          </span>
        </div>
      </footer>
    </div>
  );
}
