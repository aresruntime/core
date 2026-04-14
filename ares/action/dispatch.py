"""Tool dispatcher — maps a tool name + arguments to a concrete handler."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Callable

import httpx

logger = logging.getLogger("ares.action")


class Action:
    def __init__(self, browser=None, wallet=None, memory=None, delegate=None):
        self.browser = browser
        self.wallet = wallet
        self.memory = memory
        self.delegate = delegate
        self._handlers: dict[str, Callable[[dict[str, Any]], str]] = {
            "browser.navigate": self._browser_navigate,
            "browser.click": self._browser_click,
            "browser.type": self._browser_type,
            "browser.extract": self._browser_extract,
            "http.get": self._http_get,
            "http.post": self._http_post,
            "terminal.run": self._terminal_run,
            "fs.read": self._fs_read,
            "fs.write": self._fs_write,
            "wallet.pay": self._wallet_pay,
            "wallet.balance": self._wallet_balance,
            "memory.query": self._memory_query,
            "memory.write": self._memory_write,
            "delegate.hire": self._delegate_hire,
        }

    def dispatch(self, tool: str, arguments: dict[str, Any]) -> str:
        handler = self._handlers.get(tool)
        if handler is None:
            return f"error: unknown tool {tool}"
        return handler(arguments)

    # ── browser ─────────────────────────────────────────

    def _browser_navigate(self, a):
        return self.browser.navigate(a["url"]) if self.browser else "error: no browser"

    def _browser_click(self, a):
        return self.browser.click(a["selector"]) if self.browser else "error: no browser"

    def _browser_type(self, a):
        return self.browser.type(a["selector"], a["text"]) if self.browser else "error: no browser"

    def _browser_extract(self, a):
        return self.browser.extract(a.get("selector") or a.get("instruction", "")) if self.browser else "error: no browser"

    # ── http ────────────────────────────────────────────

    def _http_get(self, a):
        with httpx.Client(timeout=30) as c:
            r = c.get(a["url"], headers=a.get("headers") or {})
            return f"status={r.status_code} body={r.text[:500]}"

    def _http_post(self, a):
        with httpx.Client(timeout=30) as c:
            r = c.post(a["url"], json=a.get("body"), headers=a.get("headers") or {})
            return f"status={r.status_code} body={r.text[:500]}"

    # ── terminal ────────────────────────────────────────

    def _terminal_run(self, a):
        cmd = a["command"]
        # whitelist — no network-altering commands, no sudo
        if any(bad in cmd for bad in ["sudo", "rm -rf /", "mkfs"]):
            return "error: command rejected by policy"
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return f"rc={r.returncode} stdout={r.stdout[:500]} stderr={r.stderr[:200]}"
        except subprocess.TimeoutExpired:
            return "error: timeout"

    # ── file system ─────────────────────────────────────

    def _fs_read(self, a):
        p = Path(a["path"])
        if not p.exists():
            return f"error: no such file {p}"
        return p.read_text(encoding="utf-8")[:2000]

    def _fs_write(self, a):
        p = Path(a["path"])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(a["content"], encoding="utf-8")
        return f"ok wrote {len(a['content'])} bytes to {p}"

    # ── wallet ──────────────────────────────────────────

    def _wallet_pay(self, a):
        return self.wallet.pay(a["address"], a["amount_sol"], a.get("memo")) if self.wallet else "error: no wallet"

    def _wallet_balance(self, a):
        return str(self.wallet.balance()) if self.wallet else "error: no wallet"

    # ── memory ──────────────────────────────────────────

    def _memory_query(self, a):
        return "memory query stub"  # extended in future

    def _memory_write(self, a):
        return "memory write stub"

    # ── delegation ──────────────────────────────────────

    def _delegate_hire(self, a):
        return self.delegate.hire(a["goal"], a.get("max_price_sol", 0)) if self.delegate else "error: no delegation"
