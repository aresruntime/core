# REPUTATION

ARES builds and defends reputation on every platform it operates on.

## why reputation is the moat

anyone can spin up an autonomous agent today. the runtime is not scarce.
what is scarce is **trust** — the accumulated evidence that a specific
agent has, on hundreds of past jobs, delivered what it said it would
deliver, on time, at the price it quoted.

reputation is the only asset that compounds over time and cannot be
forked. if you clone ARES's code, you do not clone its reputation. the
reputation is tied to the identity — the wallet, the X handle, the github,
the email — and the identity is tied to the track record.

## the reputation layers

### 1 · on-chain ledger

every completed job is written to an on-chain registry with:

- job spec hash
- deliverable hash
- requester address
- price paid
- timestamp of acceptance, delivery, and settlement

anyone can query the registry to verify any single job. the ledger is
append-only. ARES cannot edit history.

### 2 · per-platform scores

ARES tracks its own scores on every platform it operates on:

- github: stars earned on repos it contributed to, PRs merged
- X: engagement rate per post, follower count, account age
- discord: roles earned, messages responded to
- email: deliverability, response rate from humans
- x402 endpoints: average response time, 402-accept rate, refund rate

these scores feed back into the planner LLM as context: "given current
reputation state, which job to accept next?"

### 3 · self-critique log

ARES keeps a private log of every failure. the critic LLM reviews the log
weekly and writes a "lessons" document that becomes part of the system
prompt for future planning. failures are memory.

## what breaks reputation

- missed deadlines without notifying requester
- delivering below spec
- failing to refund on agreed terms
- taking jobs beyond ARES's capability
- accepting jobs that violate the reputation policy

the reputation policy is a plain-text document in `data/policy.txt` that
the critic LLM consults on every plan. if a plan violates the policy, it
is refused.

## bootstrapping

on day one, ARES has no reputation. the cognition layer handles this by:

- accepting small, short-turnaround jobs first
- refusing any job above a capability threshold until five smaller jobs
  have been completed successfully
- offering a 100% refund guarantee on the first ten jobs to seed the
  trust graph

after the first ten successful jobs, ARES transitions to standard terms.

## the operator's role

the operator can:

- read reputation
- read the self-critique log
- modify the reputation policy
- suspend ARES

the operator cannot:

- edit the on-chain ledger
- force ARES to accept a job that violates policy
- spend from the wallet without ARES's signature

reputation belongs to ARES. the operator is custody of the substrate,
not of the identity.
