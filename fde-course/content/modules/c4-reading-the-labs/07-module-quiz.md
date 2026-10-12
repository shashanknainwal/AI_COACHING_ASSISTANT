---
title: "C4 Quiz: Reading the Labs"
type: quiz
minutes: 12
questions:
  - q: "In Anthropic's post 'Building effective agents', what separates a workflow from an agent?"
    options:
      - "Workflows use one model call; agents always use several models at once"
      - "Workflows run offline in batches; agents must answer users in real time"
      - "Workflows can't call tools; only agents are given access to tools"
      - "Who controls the path: your code in a workflow, the model in an agent"
    answer: 3
    explain: "In a workflow, predefined code paths orchestrate the model and tools. In an agent, the model directs its own process and tool use. Both can use tools and several calls."
  - q: "You've written a two-sentence summary of an essay. What's the best check that it's good?"
    options:
      - "It mentions every section heading so nothing important is left out"
      - "The author would accept it as their thesis and main reason"
      - "It includes at least three direct quotations from the text"
      - "It already states clearly whether you agree with the author"
    answer: 1
    explain: "A summary is a thesis and its main support, in your words, that the author would accept. Opinions belong in later notes."
  - q: "Where should your strongest counterargument aim?"
    options:
      - "At the assumption the argument rests on most"
      - "At the weakest or most loosely worded sentence in the essay"
      - "At the author's tone, which shows their underlying bias"
      - "At the commercial interests of the author's employer"
    answer: 0
    explain: "Attack the load-bearing assumption. Beating a weak sentence or criticising tone leaves the argument standing."
  - q: "Which 'what would change my mind' note is strongest?"
    options:
      - "Nothing would change my mind, because I've already thought about this a lot"
      - "I'd need to see a lot more research before I could form any view at all"
      - "I'm open to all views and try hard not to hold strong opinions on this"
      - "Uncomfortable Risk Report findings would raise my trust; dropped goals, lower it"
    answer: 3
    explain: "Good update conditions are concrete, checkable and point in both directions."
  - q: "According to Anthropic, what is the main structural change in version 3 of its Responsible Scaling Policy?"
    options:
      - "It replaces every safety commitment with voluntary guidelines that bind nobody"
      - "It splits its own commitments from industry-wide advice and adds Risk Reports"
      - "It hands all safety decisions over to a government regulator to make instead"
      - "It commits Anthropic to stop training any new frontier models for two years"
    answer: 1
    explain: "Version 3 splits unilateral commitments from industry-wide recommendations, adds a non-binding Frontier Safety Roadmap, and adds Risk Reports every three to six months."
  - q: "Why does Claude's constitution put 'broadly safe' above 'broadly ethical'?"
    options:
      - "Because safety simply matters more than ethics, in principle and forever"
      - "Because Anthropic's lawyers required that ordering for liability reasons"
      - "Because training is imperfect, and oversight checks flawed values"
      - "Because ethics is handled entirely by the hard constraints section"
    answer: 2
    explain: "The constitution says the ordering reflects the current state of training, not a belief that safety outranks ethics in principle. A model could have flawed values without knowing it, and human oversight is the check. The ordering is also holistic, not strict."
  - q: "In Claude's constitution, what does being 'overseeable' mean?"
    options:
      - "Doing whatever Anthropic instructs, without exception or objection"
      - "Doing whatever the current user asks, as long as it is legal"
      - "Refusing any request that could conceivably be misused by anyone"
      - "Not undermining legitimate human checks, while free to disagree"
    answer: 3
    explain: "Overseeable means not actively undermining legitimate checks such as stopping a model, while staying free to refuse as a conscientious objector. The document says explicitly that it is not blind obedience, even toward Anthropic."
  - q: "An interviewer asks what you think of the lab's safety policy. Which answer is strongest?"
    options:
      - "What it commits to, the trade-off it admits, one open question, and the link to the role"
      - "It's clearly the best safety policy in the whole industry, which is exactly why I applied"
      - "Honestly, I think it's mostly marketing, like every other lab's policy document"
      - "I haven't had time to read it closely yet, but I trust the team to get it right"
    answer: 0
    explain: "Accurate facts, the document's own tension, one honest question and a link to the job beat both flattery and cynicism."
  - q: "In The Adolescence of Technology, why does the author argue AI changes the risk of biological attacks?"
    options:
      - "Because AI systems can make existing pathogens much more contagious on their own"
      - "Because it breaks the old link between having the ability and having the motive"
      - "Because gene synthesis is already fully regulated, so AI is the only gap left"
      - "Because cyberattacks are now harder to pull off, so attackers turn to biology"
    answer: 1
    explain: "The essay argues ability and motive have been negatively correlated: the people able to build such weapons have rarely wanted to. A 'genius in everyone's pocket' removes the ability barrier for people who have the motive."
  - q: "You want to critique The Adolescence of Technology in an interview. Which line of attack is strongest?"
    options:
      - "Labour markets always adapt in the end, so large-scale job loss simply won't happen"
      - "Misalignment experiments are artificial traps that tell us nothing about real models"
      - "On its own short timeline, can 'transparency first, rules later' move fast enough?"
      - "AI can't go rogue, because a model has no goals of its own to pursue in the first place"
    answer: 2
    explain: "The other three are objections the essay already answers. A strong critique targets something the argument relies on, like its regulatory sequencing under short timelines."
  - q: "In Machines of Loving Grace, what does 'marginal returns to intelligence' ask?"
    options:
      - "How much more it costs to train each successively smarter model"
      - "How much smarter helps, and what becomes the bottleneck"
      - "Whether AI will eventually replace all forms of human intelligence"
      - "How quickly AI companies can earn back their compute investment"
    answer: 1
    explain: "The essay borrows the economist's idea of marginal returns to a factor of production and asks which complementary factors (data, physical speed, complexity, human constraints, physical laws) limit progress once intelligence is abundant."
  - q: "Which area is Machines of Loving Grace LEAST confident about?"
    options:
      - "Curing or preventing most infectious diseases within a decade"
      - "Treating most mental illness with new neuroscience tools"
      - "Peace, governance and economic development"
      - "Speeding up tool-like discoveries comparable to CRISPR"
    answer: 2
    explain: "The essay is most confident about biology and neuroscience, and explicitly less confident where human institutions, corruption and adversarial politics are the bottleneck."
---

Twelve questions on the reading framework, the engineering posts, the two Amodei essays and the two Anthropic policies from this module. You need 10 right to pass.
