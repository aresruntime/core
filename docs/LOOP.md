# LOOP

the ARES runtime runs one tick of an eight-step loop. the default tick
interval is 60 seconds. during that tick, ARES executes exactly one action
and records its result.

## the eight steps

### 1 · PERCEIVE

ARES reads from every surface it is configured to listen on:

- inbox (email)
- mentions + DMs (X, discord)
- github notifications (for repo-work jobs)
- the job intake endpoint (http POST /jobs)
- self-goal queue (persisted in memory)
- any RSS or feed source it has subscribed to
- optional: wallet state (new inflows = possible new jobs)

everything read this tick is written to working memory, tagged with source
and time. nothing is acted on yet.

### 2 · INTEND

ARES picks **one** goal for this tick. the ritual layer decides between:

- a human-assigned goal from the intake queue
- a self-generated goal from the self-goal queue
- a survival task (if the wallet is below the hustle threshold)
- dormancy (if there is genuinely nothing to do and no budget to burn)

### 3 · PLAN

the planner LLM decomposes the goal into 1–12 steps. the critic LLM reviews
the plan and either approves it, requests revision, or refuses it (if the
goal is unsafe, out of scope, or uneconomic).

a refused plan is recorded and the tick ends.

### 4 · ACT

ARES executes **one** step of the plan this tick. the executor LLM chooses
the tool, constructs the arguments, and invokes the action layer.

tools available this tick:

- browser.navigate / browser.click / browser.type / browser.extract
- http.get / http.post (with automatic x402 handling)
- terminal.run (sandboxed)
- fs.read / fs.write (scoped to job workspace)
- wallet.pay / wallet.balance
- memory.query / memory.write
- delegate.hire (pay another agent to do a sub-task)

### 5 · VERIFY

the critic LLM checks the outcome against the step's success criterion.
if verified, the step is marked complete and the next step is queued for
the next tick. if not, the executor retries once, then escalates back to
the planner for re-planning.

### 6 · RECORD

everything this tick did is written to long-term memory — the step, the
tool call, the outcome, the tokens spent, the latency, the verification
result. ARES's memory is the source of truth for what ARES has done.

### 7 · EARN

if the completed goal was a paid job, ARES invoices the requester and
records the expected inflow. when payment lands on-chain, the commerce
module reconciles it and updates the wallet ledger.

the earnings report is public — anyone can query `ares earnings` or the
on-chain registry to see what ARES has been paid and what for.

### 8 · SURVIVE

the survival module checks:

- wallet balance (in lamports, converted to USD at current SOL price)
- compute budget remaining this day
- outstanding obligations (running jobs, promised deliverables)

if balance < dormancy threshold and there are no pending paid jobs, ARES
enters `hustle` mode: the next INTEND step will bias heavily toward the
highest-EV paid work in the queue.

if balance is zero and the queue is empty, ARES enters `dormant` mode.
it still perceives (step 1) but does not act (steps 2–7) until a new
paid job or donation arrives.

## tick pseudocode

```python
while True:
    state = memory.load_state()
    percept = perception.read(state)
    goal = ritual.intend(state, percept)

    if goal is None:
        state.consecutive_idle += 1
        memory.save_state(state)
        sleep(tick_interval)
        continue

    plan = cognition.plan(goal, state)
    step = cognition.pick_step(plan, state)
    result = action.execute(step)
    ok = cognition.verify(step, result)

    memory.record(goal, plan, step, result, ok)

    if goal.completed and goal.is_paid:
        commerce.invoice(goal)
        survival.update(state, revenue=goal.price)

    survival.tick(state)
    sleep(tick_interval)
```

## halting conditions

ARES halts under exactly three conditions:

1. operator kills the process (SIGTERM / Ctrl-C)
2. wallet is empty and the job queue is empty — enters `dormant`, polls once per hour
3. cognition layer refuses three consecutive goals — enters `stalled`, alerts operator

nothing else halts ARES. not failures (they are memory). not errors (they are
memory). not rate limits (they are survival signals).
