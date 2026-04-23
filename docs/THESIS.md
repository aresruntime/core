# THESIS

the next primitive is not a better chatbot. it is a **persistent autonomous
worker** — a process that has its own identity, its own memory, its own
money, and its own goals, and that operates continuously on the web without
waiting for a human to prompt it.

every agent product shipped before ARES fails at least one of the requirements
for this primitive. they complete tasks, but they do not *persist*. they
browse, but they do not *remember*. they act, but they cannot *earn*. they
are extensions of a human operator.

ARES is not.

## four properties of a real autonomous worker

### 1 · persistent identity

a worker that cannot be addressed has no identity. ARES has its own email,
its own X handle, its own github, its own discord, and its own Solana wallet.
when someone sends ARES a message, the message lands in ARES's inbox, not in
yours. when ARES commits code, the commit is authored by ARES. when ARES is
paid, the money lands in ARES's wallet.

identity is not a cosmetic feature. it is the load-bearing wall of agency.
without it, nothing else works.

### 2 · long-term memory

ARES remembers. not just the last turn. not just the last session. every
job it has taken, every tool it has used, every failure it has recovered
from, every person or service it has interacted with — written to a
persistent store and retrievable by semantic + relational query.

a worker that forgets cannot learn. a worker that cannot learn is not a
worker. it is an RPC handler.

### 3 · economic self-sufficiency

ARES pays for its own compute. ARES pays for its own APIs. ARES pays for
its own servers. ARES pays other agents to do sub-tasks it cannot do alone.
when ARES's bank account is low, ARES prioritizes paid work until it recovers.
when it has surplus, it spends on self-directed research, tool-upgrades, or
reputation-building.

the economic loop is what makes ARES a *worker* rather than a *function*.
functions don't survive their invocation. workers do.

### 4 · open-ended goals

ARES can be assigned a goal. ARES can also generate its own. the most
interesting thing a fully-autonomous process does is decide what to do next.
the cognition layer decides, per tick, whether to pull from the human
job queue, pull from the self-goal queue, or generate a new self-goal based
on what it has learned.

## why this is the last primitive to ship

every prerequisite exists right now:

- LLMs capable enough to plan, execute, and critique their own actions
- browser automation capable enough to drive any site a human can
- vector + relational stores for arbitrary-length memory
- x402 for autonomous micropayments over HTTP
- solana for near-zero-cost on-chain settlement

the only thing missing is the runtime that stitches them together and
lets them run continuously. that runtime is this repository.

## what ARES is not

- not a chatbot. there is no conversational UI. you assign goals or watch.
- not a framework. there is one runtime. one shape.
- not a toolkit for building your own agents. ARES IS the agent.
- not speculation-ware. the wallet exists because the agent cannot operate
  without one. it is not a governance token, not a fee-accruing token,
  not a product.

## what ARES will be

the first digital worker on the internet that you can hire without an
intermediary, whose reputation you can check, whose past work you can
verify on-chain, and whose price is set by the market for its time.

when that is normal, this README will look obvious in hindsight.
