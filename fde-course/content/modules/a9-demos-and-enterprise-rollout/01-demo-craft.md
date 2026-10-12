---
title: "Demo Craft: Build a Demo That Survives Questions"
type: reading
minutes: 15
---

> **By the end of this lesson you will be able to:**
> - Build a customer demo on the customer's own data, inside a two-hour budget.
> - Put an eval next to the "wow" and show a failure on purpose.
> - Make a demo resettable, and recover when it breaks live.
> - Explain why you never fake a demo, and what to do instead.

A demo is the first time a customer sees their own problem solved. For an architect it does two jobs at once: it creates belief, and it sets expectations you'll be held to for the rest of the deal. A demo that only does the first job wins the meeting and loses the pilot.

Demos come up in architect and solutions-engineering loops at the labs this course covers, usually as a "walk us through something you built" or a live presentation round (**Reported**; see module C1 and A7/09). The rules below are practice habits, not any lab's rubric.

## Rule 1: Use the customer's own data

A demo on your sample data proves the model can read your sample data. A demo on twenty of the customer's real documents proves something they care about. Ask for the data in discovery ("Can you send twenty real examples, with the answer your team gave?"). Anonymise if you must, but keep the mess: scans, odd layouts, the second language, the one with a handwritten note.

If you can't get their data in time, say so on the first slide: "This runs on public examples that look like yours. Here's what we'd need to run it on yours." Never pass synthetic data off as theirs.

## Rule 2: Show the eval next to the "wow"

The "wow" is the moment the extracted fields light up with citations. The eval is the line under it: "17 of 20 correct on your auditors' answers. Here are the three it got wrong." Putting both on one screen changes the conversation. The customer stops asking "Is it magic?" and starts asking "Which three, and why?", which is the question a pilot answers.

Report honest denominators. Refusals, errors and abstains stay in. If you quote precision when it answers, quote coverage too. The exercise in this module builds exactly that scoreboard.

## Rule 3: Show a failure, and its handling

Pick one failure and show it on purpose. Good choices:

- **An abstain.** The scan is damaged and the system says "I can't read the total" instead of guessing. This is the most persuasive thing a regulated buyer will see all day.
- **A grounding catch.** The model proposes a value, code checks it against the document, and the check fails loudly.
- **A real miss**, with the fix you'd make. "It read the subtotal as the total. In a pilot we'd add a check that line items sum to the total."

A demo with no failures looks rehearsed. Experienced buyers know the failure rate isn't zero; they want to see that you know where it is.

## Rule 4: Make it resettable

You will run the demo more than once: rehearsal, the meeting, the follow-up with the CISO. Build a reset:

- Fixed inputs in a folder, never "whatever is in the inbox today".
- A cached run of every case, so you can switch to "here's the recorded run" if the network fails. Say that you've switched.
- One command or button that puts everything back to the starting state.
- Know your latency. Current models think by default and thinking sits inside time to first token. Set `effort` explicitly so the wait is a choice you made, not a surprise.

## Rule 5: Two hours, then stop

Most demos need two hours of build, not two weeks. A sensible budget:

| Minutes | Work |
|---|---|
| 20 | Pick 15 to 25 real cases and write down the expected answer for each |
| 40 | The narrow pipeline: one prompt, structured output, grounding in code, citations |
| 30 | The scoreboard over every case, and one deliberate failure to show |
| 20 | Reset, cached fallback run, a one-line headline |
| 10 | Rehearse once, out loud, against a clock |

If it needs more than that, the scope is too wide. Cut a field, a document type or a system, not the eval.

## Rule 6: Never fake it

No hard-coded answers behind a real-looking interface. No "Wizard of Oz" without saying so. No cherry-picked runs presented as typical. A faked demo turns every later conversation (security review, pilot criteria, the go/no-go) into damage control, and it is the fastest way for a customer to stop trusting you.

What to do instead:

- **Say what's real.** "The extraction is live. The ERP write-back is mocked; here's the API we'd call."
- **Label recordings.** "This is yesterday's run, because the venue Wi-Fi is down."
- **Show the variance.** If you ran it three times, show that the third run differed on one case.

## When it breaks live

It will. A good recovery takes under a minute:

1. **Name it.** "That's a timeout on our side." Don't pretend it didn't happen.
2. **Switch to the fallback.** The cached run, with the same cases.
3. **Turn it into evidence.** "This is why the pilot design has a retry queue and a manual path."
4. **Write it down** and follow up in writing with what caused it.

The live demo role-play in lesson 03 practises this.

> **Key takeaways**
> - Demo on the customer's own data, with the answers their team gave.
> - Put the scoreboard next to the "wow", with honest denominators.
> - Show one failure on purpose, and how the system handles it.
> - Build a reset and a cached fallback; set effort so latency is a choice.
> - Two hours of build is enough. Never fake it; say what's live and what's mocked.
