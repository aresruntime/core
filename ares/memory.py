"""Long-term memory. SQLite-backed, vector-augmented."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from .config import settings
from .types import Goal, GoalSource, Plan, RuntimeState, SolvencyState

logger = logging.getLogger("ares.memory")


class Memory:
    def __init__(self, db_path: str | None = None):
        self.db_path = Path(db_path or settings.ares_memory_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price_sol REAL NOT NULL DEFAULT 0,
                    completed INTEGER NOT NULL DEFAULT 0,
                    refused INTEGER NOT NULL DEFAULT 0,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS steps (
                    goal_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    tool TEXT NOT NULL,
                    arguments TEXT NOT NULL,
                    outcome TEXT,
                    ok INTEGER,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (goal_id, step_index)
                );
                CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    direction TEXT NOT NULL,       -- 'in' | 'out'
                    amount_sol REAL NOT NULL,
                    counterparty TEXT,
                    memo TEXT,
                    tx_signature TEXT,
                    recorded_at TEXT NOT NULL
                );
                """
            )

    # ── state ───────────────────────────────────────────

    def load_state(self) -> RuntimeState:
        with self._conn() as conn:
            row = conn.execute("SELECT value FROM state WHERE key='runtime'").fetchone()
        if not row:
            return RuntimeState()
        data = json.loads(row[0])
        return RuntimeState(
            tick=data.get("tick", 0),
            current_goal_id=data.get("current_goal_id"),
            consecutive_idle_ticks=data.get("consecutive_idle_ticks", 0),
            solvency=SolvencyState(data.get("solvency", "solvent")),
            wallet_balance_lamports=data.get("wallet_balance_lamports", 0),
            compute_spent_today_usd=data.get("compute_spent_today_usd", 0.0),
            revenue_today_sol=data.get("revenue_today_sol", 0.0),
        )

    def save_state(self, state: RuntimeState) -> None:
        payload = {
            "tick": state.tick,
            "current_goal_id": state.current_goal_id,
            "consecutive_idle_ticks": state.consecutive_idle_ticks,
            "solvency": state.solvency.value,
            "wallet_balance_lamports": state.wallet_balance_lamports,
            "compute_spent_today_usd": state.compute_spent_today_usd,
            "revenue_today_sol": state.revenue_today_sol,
        }
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO state (key, value) VALUES ('runtime', ?)",
                (json.dumps(payload),),
            )

    # ── goals ───────────────────────────────────────────

    def write_goal(self, goal: Goal) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO goals
                    (id, source, description, price_sol, completed, refused, payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    goal.id,
                    goal.source.value,
                    goal.description,
                    goal.price_sol,
                    int(goal.completed),
                    int(goal.refused),
                    json.dumps({
                        "deliverable": goal.deliverable,
                        "requester": goal.requester,
                    }),
                    goal.created_at.isoformat(),
                ),
            )

    def next_pending_goal(self, prefer_paid: bool = False) -> Goal | None:
        with self._conn() as conn:
            order = "price_sol DESC" if prefer_paid else "created_at ASC"
            row = conn.execute(
                f"SELECT id, source, description, price_sol FROM goals "
                f"WHERE completed=0 AND refused=0 ORDER BY {order} LIMIT 1"
            ).fetchone()
        if not row:
            return None
        gid, source, desc, price = row
        return Goal(
            id=gid,
            source=GoalSource(source),
            description=desc,
            price_sol=price,
        )

    # ── steps ───────────────────────────────────────────

    def record_step(self, goal_id: str, index: int, tool: str,
                    arguments: dict, outcome: str | None, ok: bool | None) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO steps
                    (goal_id, step_index, tool, arguments, outcome, ok, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    goal_id, index, tool, json.dumps(arguments),
                    outcome, int(ok) if ok is not None else None,
                    datetime.utcnow().isoformat(),
                ),
            )

    # ── ledger ──────────────────────────────────────────

    def record_ledger(self, direction: str, amount_sol: float,
                      counterparty: str | None = None, memo: str | None = None,
                      tx_signature: str | None = None) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO ledger (direction, amount_sol, counterparty, memo, tx_signature, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    direction, amount_sol, counterparty, memo, tx_signature,
                    datetime.utcnow().isoformat(),
                ),
            )

    def earnings_summary(self) -> dict:
        with self._conn() as conn:
            total_in = conn.execute(
                "SELECT COALESCE(SUM(amount_sol),0) FROM ledger WHERE direction='in'"
            ).fetchone()[0]
            total_out = conn.execute(
                "SELECT COALESCE(SUM(amount_sol),0) FROM ledger WHERE direction='out'"
            ).fetchone()[0]
        return {"in_sol": total_in, "out_sol": total_out, "net_sol": total_in - total_out}
