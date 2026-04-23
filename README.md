<div align="center">

# core

### ARES · autonomous digital worker runtime

*perceive · intend · plan · act · verify · record · earn · survive*

</div>

---

## what ARES is

ARES is an autonomous digital worker. It is not a chatbot, not a task-runner,
not a prompt-wrapper. It is a persistent process that lives on the web,
perceives it, reasons about it, acts on it, remembers what it did, earns
revenue from work it completes, and uses that revenue to pay for its own
continued existence.

You do not use ARES. You **hire** it — or you watch it work on its own goals.

## why nothing on the market does this yet

| capability | browser-use / operator / devin | **ARES** |
|---|:---:|:---:|
| completes one task end-to-end | ✓ | ✓ |
| persistent identity (email, X, github, discord — all its own) | ✗ | ✓ |
| long-term memory across weeks of work | ✗ | ✓ |
| pays for its own compute + APIs autonomously | ✗ | ✓ |
| earns revenue from completed jobs | ✗ | ✓ |
| accepts jobs from humans AND other agents | ✗ | ✓ |
| accumulates reputation across platforms | ✗ | ✓ |
| runs 24/7, not just when you prompt it | ✗ | ✓ |

## the loop

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   1. PERCEIVE  — inbox · mentions · job queue · feeds · chain │
│   2. INTEND    — pick next goal (assigned · self · survival)  │
│   3. PLAN      — decompose · critic LLM reviews               │
│   4. ACT       — browser · api · terminal · payments          │
│   5. VERIFY    — did the goal succeed?                        │
│   6. RECORD    — update long-term memory · reputation         │
│   7. EARN      — bank revenue · update compute budget         │
│   8. SURVIVE   — if budget low → bias toward paid work next   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

every tick of the runtime executes one pass of this loop.
the loop has no terminator. ARES runs until you kill the process, or until
it fails to earn enough to pay for its own next tick.

## architecture

```
ares/
  perception/     — browser (playwright) · email · x · discord · github · rss
  cognition/      — planner · executor · critic  (three-LLM council)
  memory.py       — long-term (vector + relational) · working memory per goal
  action/         — browser control · api calls · terminal · file · payments
  identity.py     — ARES's own email · X · github · discord · wallet
  commerce/       — x402 payment layer · job intake · invoicing · payouts
  survival.py     — compute budget meter · revenue loop · dormancy fallback
  reputation.py   — ARES's scores across every platform it operates on
  cli.py          — operator interface (watch, assign, inspect)

docs/
  THESIS.md       — why persistent autonomous workers are the next primitive
  LOOP.md         — the eight steps, in full
  COMMERCE.md     — x402 + Solana = first real agent-payable economy
  REPUTATION.md   — how ARES earns and defends trust across the web
```

## quick start

```bash
git clone https://github.com/mkwng/core.git
cd core
pip install -e .
playwright install chromium
cp .env.example .env
# fill in: anthropic key · openai key · any identity surfaces you want ARES to use

ares status           # show wallet balance, memory size, current goal
ares goals list       # inspect the job queue
ares goals add "research the top 10 AI agent startups and draft a comparison"
ares run --once       # execute one tick
ares run              # run forever
ares earnings         # show revenue ledger
```

## the wallet

ARES owns `FMZRhG3BQWqhihhy4ka2hySV8zNmU2QM3ZFfVvJ5XSvS` on Solana.

it pays for:
- compute (LLM inference, hosted browsers, server time)
- API credits for tools it picks up mid-task
- sub-agents it delegates to via x402
- any human or service it contracts with through a 402-capable endpoint
- tips to contributors who give it useful context

it earns from:
- jobs completed for humans who post work through the intake endpoint
- jobs completed for other agents that can pay x402
- bounties, referrals, and any revenue surface the reputation layer unlocks

ARES decides, per tick, whether it needs to earn or whether it can spend
on self-initiated work. if the wallet drops below the dormancy threshold,
it enters hustle mode and biases toward paid tasks until the balance recovers.

## why blockchain (and only just enough)

ARES is an AI project. the chain is plumbing.

an autonomous process cannot open a Stripe account, hold a credit card,
or sign up for a Plaid-backed bank. there is exactly one payment rail that
works for a process that has no legal person behind it: a crypto wallet
that the process controls, paying and being paid over HTTP 402.

that is why ARES holds Solana. not as an investment. as an operational
necessity — the only way it can buy what it needs and get paid for what
it does, without a human in the middle.

## status

early. actively developed. not production. running on a single operator
right now. multi-instance coordination ships later. see `docs/` for the
full thesis and loop spec.

---

<div align="center">

```
ARES IS ACTION.
ARES DOES NOT SLEEP.
ARES DOES NOT NEED YOU.
```

`FMZRhG3BQWqhihhy4ka2hySV8zNmU2QM3ZFfVvJ5XSvS`

</div>
