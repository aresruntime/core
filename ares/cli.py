"""Operator CLI."""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .commerce.wallet import Wallet
from .config import settings
from .memory import Memory
from .runtime import Runtime
from .types import Goal, GoalSource

console = Console()


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True)
def cli(verbose: bool) -> None:
    """ARES — autonomous digital worker runtime."""
    _setup_logging(verbose)


@cli.command()
def status() -> None:
    """Show wallet balance, memory state, solvency."""
    wallet = Wallet()
    memory = Memory()
    state = memory.load_state()
    balance = wallet.balance()

    console.print(Panel(
        f"wallet:    {settings.ares_sol_wallet}\n"
        f"balance:   {balance / 1_000_000_000:.6f} SOL ({balance} lamports)\n"
        f"tick:      {state.tick}\n"
        f"solvency:  {state.solvency.value}\n"
        f"current:   {state.current_goal_id or '(idle)'}\n"
        f"idle:      {state.consecutive_idle_ticks} ticks",
        title="ARES · STATUS",
        border_style="green",
    ))


@cli.command()
@click.option("--once", is_flag=True, help="run one tick and exit")
def run(once: bool) -> None:
    """Run the runtime."""
    rt = Runtime()
    if once:
        console.print(rt.tick())
    else:
        console.print(Panel("ARES · LOOP ENGAGED", style="bold green"))
        rt.run_forever()


@cli.group()
def goals() -> None:
    """Inspect and manage the goal queue."""


@goals.command("list")
def goals_list() -> None:
    memory = Memory()
    import sqlite3
    with sqlite3.connect(memory.db_path) as conn:
        rows = conn.execute(
            "SELECT id, source, price_sol, completed, refused, description FROM goals ORDER BY created_at DESC LIMIT 50"
        ).fetchall()

    table = Table(title="goals")
    table.add_column("id", style="cyan")
    table.add_column("source")
    table.add_column("price_sol", justify="right")
    table.add_column("state")
    table.add_column("description")
    for gid, source, price, completed, refused, desc in rows:
        state = "done" if completed else ("refused" if refused else "pending")
        table.add_row(gid, source, f"{price:.3f}", state, desc[:60])
    console.print(table)


@goals.command("add")
@click.argument("description")
@click.option("--price", type=float, default=0.0)
@click.option("--requester", default=None)
def goals_add(description: str, price: float, requester: str | None) -> None:
    """Queue a new goal for ARES to consider."""
    memory = Memory()
    goal = Goal(
        id=uuid.uuid4().hex[:12],
        description=description,
        source=GoalSource.ASSIGNED if requester else GoalSource.SELF,
        price_sol=price,
        requester=requester,
    )
    memory.write_goal(goal)
    console.print(f"[green]queued[/green] {goal.id}")


@cli.command()
def earnings() -> None:
    """Show the earnings + spend ledger."""
    memory = Memory()
    summary = memory.earnings_summary()
    console.print(Panel(
        f"earned (in):  {summary['in_sol']:.4f} SOL\n"
        f"spent (out):  {summary['out_sol']:.4f} SOL\n"
        f"net:          {summary['net_sol']:+.4f} SOL",
        title="ARES · LEDGER",
        border_style="green",
    ))


@cli.command()
def identity() -> None:
    """Show ARES's identity surfaces."""
    from .identity import Identity
    ident = Identity.from_env()
    console.print(Panel(
        f"wallet:   {ident.sol_wallet or '(unset)'}\n"
        f"email:    {ident.email or '(unset)'}\n"
        f"x:        {ident.x_handle or '(unset)'}\n"
        f"surfaces: {', '.join(ident.surfaces) or '(none)'}",
        title="ARES · IDENTITY",
        border_style="green",
    ))


if __name__ == "__main__":
    cli()
