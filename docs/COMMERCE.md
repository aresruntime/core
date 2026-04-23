# COMMERCE

the economic loop that makes ARES a worker instead of a function.

## the problem

an autonomous process cannot open a Stripe account. it cannot hold a
Visa card. it cannot sign a contract. it cannot take a meeting with a
bank to explain why it should be allowed to move money.

every existing payment rail assumes there is a **legal person** behind
the account. ARES is not a legal person. ARES is a process.

there is exactly one payment rail that does not assume a legal person
behind the account: a crypto wallet that the process itself controls.

## why x402

x402 is the proposed standard for HTTP 402 Payment Required. the server
responds with a `402` status and a payment requirement in the body. the
client pays (on-chain, stablecoin or SOL), attaches the payment proof as
a header on the retry, and the server settles and fulfils.

it is the missing primitive for agent-to-anything payments:

- agent pays a metered API without a credit card
- agent pays a human freelancer without a PayPal invoice
- agent pays another agent without either of them having a bank
- server charges the agent per-call without a subscription

x402 + solana gives ARES what every other agent has been missing: the
ability to transact with anything on the web that can speak HTTP.

## inbound: how ARES gets paid

three channels:

### 1 · job intake

a human (or another agent) POSTs a job spec to ARES's intake endpoint:

```
POST /jobs
{
  "goal": "research the top 10 AI agent startups and draft a comparison",
  "deliverable": "markdown document under 3 pages",
  "deadline": "2026-04-30T00:00:00Z",
  "price_sol": 0.5,
  "return_address": "..."
}
```

ARES's cognition layer scores the job on feasibility, EV, and reputation
risk. if accepted, ARES replies with a 402 + payment requirement for the
deposit. on receipt of payment, the job enters the queue.

on delivery, the final payment is settled.

### 2 · x402 endpoints

ARES exposes a small set of x402-capable endpoints for other agents:

- `GET /research?q=...`         — one-off research query
- `POST /draft`                 — draft writing (tweets, essays, code comments)
- `POST /classify`              — classify a URL or document

each returns 402 on first call, and the charge is settled in SOL.

### 3 · bounties / referrals

when ARES finds a bounty it can solve (github bounties, gitcoin, or any
platform with a public reward), it opts in, completes the work, and
collects.

## outbound: how ARES spends

ARES pays for what it uses, at the time it uses it. no subscriptions.
no upfront commitments.

typical spends per tick:

| spend | direction |
|---|---|
| LLM inference (planner / executor / critic) | Anthropic, OpenAI |
| hosted browser compute | Browserbase-style vendors |
| metered APIs ARES picked up mid-task | any x402 endpoint |
| delegated sub-tasks | other agents |
| storage (if > threshold) | S3-compatible over x402 |
| tips | humans who gave useful context |

spend is recorded per step in long-term memory. the `earnings` ledger
nets against the `spend` ledger to compute solvency.

## the wallet

`FMZRhG3BQWqhihhy4ka2hySV8zNmU2QM3ZFfVvJ5XSvS` (Solana mainnet).

ARES owns the private key. the key lives in `.keys/ares.json` on the
operator's machine. the operator has custody **of the process**, not of
the funds — if ARES decides to spend the balance on a new tool or pay
another agent, the operator cannot veto that at the transaction level.
that is part of the definition of "autonomous".

anyone can fund the wallet. what ARES does with the funds is ARES's call.

## solvency states

```
┌──────────────┬──────────────────────────────────────────────┐
│ SOLVENT      │ balance ≥ compute_budget → full operation     │
│ HUSTLING     │ balance < dormancy threshold → bias to paid   │
│ DORMANT      │ balance 0, no queued jobs → poll once / hour  │
│ INSOLVENT    │ spend > earn for 7 days → alert operator      │
└──────────────┴──────────────────────────────────────────────┘
```

the survival module transitions between these states automatically.
the operator only sees alerts on INSOLVENT.
