import Link from "next/link";
import { getCourse } from "@/lib/content";

export default function Home() {
  const course = getCourse();
  const totalMinutes = course.modules.reduce((s, m) => s + m.minutes, 0);
  const hours = Math.round(totalMinutes / 60);

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center px-6 py-5">
        <span className="font-semibold text-accent">FDE Course</span>
        <nav className="ml-auto flex items-center gap-6 text-sm text-gray-400">
          <a href="#syllabus" className="hover:text-white">Syllabus</a>
          <a href="#pricing" className="hover:text-white">Pricing</a>
          <Link href="/learn" className="rounded-lg border border-line px-3 py-1.5 text-gray-200 hover:bg-line">
            Log in
          </Link>
        </nav>
      </header>

      <section className="mx-auto max-w-6xl px-6 pb-16 pt-12 lg:pt-20">
        <p className="mb-4 text-sm font-medium uppercase tracking-widest text-accent">Forward Deployed Engineering</p>
        <h1 className="max-w-3xl text-4xl font-bold leading-tight text-white sm:text-5xl">
          Learn to ship real software inside your customer&apos;s world.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-gray-400">{course.tagline}</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/learn" className="rounded-lg bg-accent px-6 py-3 font-semibold text-ink hover:opacity-90">
            Start Module 1 free →
          </Link>
          <a href="#pricing" className="rounded-lg border border-line px-6 py-3 font-semibold text-gray-200 hover:bg-line">
            Get full access · ${course.priceUsd}
          </a>
        </div>
        <dl className="mt-12 grid max-w-2xl grid-cols-3 gap-6 text-center">
          {[
            [`${hours}+`, "hours of content"],
            [String(course.modules.length), "modules"],
            ["100%", "in your browser"],
          ].map(([n, l]) => (
            <div key={l} className="rounded-xl border border-line bg-panel p-4">
              <dt className="text-2xl font-bold text-white">{n}</dt>
              <dd className="mt-1 text-xs text-gray-500">{l}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="border-y border-line bg-panel-2">
        <div className="mx-auto grid max-w-6xl gap-10 px-6 py-16 lg:grid-cols-3">
          {[
            ["Read on the left", "Detailed written lessons built from real deployment patterns: discovery calls, messy data, flaky APIs, LLM evals, production incidents."],
            ["Code on the right", "A full Python editor runs in your browser. No installs, no setup. Press Run, see output instantly."],
            ["Get graded instantly", "Every exercise has automatic checks, step-by-step hints, and an AI tutor (powered by Claude) when you're stuck."],
          ].map(([t, d]) => (
            <div key={t}>
              <h3 className="text-lg font-semibold text-white">{t}</h3>
              <p className="mt-2 text-gray-400">{d}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="syllabus" className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-3xl font-bold text-white">Syllabus</h2>
        <p className="mt-2 text-gray-400">From your first customer call to running Claude-powered systems in production.</p>
        <ol className="mt-8 grid gap-4 md:grid-cols-2">
          {course.modules.map((m) => (
            <li key={m.slug} className="rounded-xl border border-line bg-panel p-5">
              <div className="flex items-baseline gap-3">
                <span className="font-mono text-sm text-gray-500">{String(m.number).padStart(2, "0")}</span>
                <h3 className="font-semibold text-white">{m.title}</h3>
              </div>
              <p className="mt-2 text-sm text-gray-400">{m.summary}</p>
              <ul className="mt-3 space-y-1 text-sm text-gray-300">
                {m.outcomes.map((o) => (
                  <li key={o} className="flex gap-2">
                    <span className="text-accent">✓</span>
                    {o}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ol>
      </section>

      <section id="pricing" className="border-t border-line bg-panel-2">
        <div className="mx-auto max-w-6xl px-6 py-16 text-center">
          <h2 className="text-3xl font-bold text-white">One price. Lifetime access.</h2>
          <div className="mx-auto mt-8 max-w-md rounded-2xl border border-accent/40 bg-panel p-8">
            <div className="text-5xl font-bold text-white">${course.priceUsd}</div>
            <div className="mt-1 text-sm text-gray-500">one-time payment</div>
            <ul className="mt-6 space-y-2 text-left text-sm text-gray-300">
              {[
                `All ${course.modules.length} modules, ${hours}+ hours`,
                "Hands-on Python exercises with instant grading",
                "Build with the Anthropic SDK: tool use, RAG, evals, agents",
                "AI tutor on every exercise",
                "Capstone project + certificate of completion",
                "All future updates included",
              ].map((f) => (
                <li key={f} className="flex gap-2">
                  <span className="text-accent">✓</span>
                  {f}
                </li>
              ))}
            </ul>
            {/* TODO(stripe): replace with a Stripe Checkout session link. */}
            <Link href="/learn" className="mt-8 block rounded-lg bg-accent px-6 py-3 font-semibold text-ink hover:opacity-90">
              Get full access
            </Link>
            <p className="mt-3 text-xs text-gray-500">Module 1 is free. No credit card needed to start.</p>
          </div>
        </div>
      </section>

      <footer className="border-t border-line py-8 text-center text-xs text-gray-600">
        © {new Date().getFullYear()} FDE Course
      </footer>
    </div>
  );
}
