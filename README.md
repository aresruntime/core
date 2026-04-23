<div align="center">

# core

### ARES · autonomous digital worker

*perceive · intend · plan · act · verify · record · earn · survive*

</div>

---

## what it is

long-running process. not a one-shot “agent as a product” demo: tick loop, memory,
browsers, LLMs, job intake, x402, survival logic. you run it, assign goals, or let it
pick work if you wired that up. early code.

## comparison (rough)

| | typical agent wrappers | **this** |
|---|:---:|:---:|
| end-to-end task | yes | yes |
| keeps going without you | mostly no | yes (loop) |
| own surfaces / long memory | often no | intended |
| get paid and pay for runtime | often no | intended |

## loop

```
perceive -> intend -> plan -> act (one step) -> verify -> record -> earn -> survive
```

kills: SIGTERM, or it goes idle if broke / broke-broke. read `docs/LOOP.md` for detail.

## layout

```
ares/   perception, cognition, memory, action, identity, commerce, survival, reputation, runtime, cli
docs/   THESIS, LOOP, COMMERCE, REPUTATION
```

## quick start

```bash
git clone https://github.com/OWNER/core.git
cd core
pip install -e .
playwright install chromium
cp .env.example .env
# keys + surfaces you care about

ares status
ares goals add "optional goal text"
ares run --once
ares run
```

## money

x402 is there so something headless can hit paid APIs without a card on file. chain stuff
is boring plumbing; you are not “investing” in anything. details in `docs/COMMERCE.md` if
you care. anything sensitive lives in env, not here.

## status

wip. not prod. more in `docs/`.

---

*ARES = action, not vibes.*
