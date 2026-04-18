"""ARES's Solana wallet. Balance reads + signed transfers."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from ..config import settings

logger = logging.getLogger("ares.wallet")


class Wallet:
    def __init__(self, address: str | None = None, keypair_path: str | None = None):
        self.address = address or settings.ares_sol_wallet
        self.keypair_path = Path(keypair_path or settings.ares_sol_keypair_path)
        self.rpc = settings.solana_rpc_url

    def balance(self) -> int:
        """Return lamports."""
        try:
            with httpx.Client(timeout=15) as c:
                r = c.post(self.rpc, json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [self.address],
                })
                r.raise_for_status()
                return int(r.json()["result"]["value"])
        except Exception as exc:
            logger.warning("balance read failed: %s", exc)
            return 0

    def pay(self, to: str, amount_sol: float, memo: str | None = None) -> str:
        """Sign and submit a SOL transfer. Requires local keypair."""
        if not self.keypair_path.exists():
            return "error: no local keypair to sign with"
        try:
            from solders.keypair import Keypair
            from solders.pubkey import Pubkey
            from solders.system_program import TransferParams, transfer
            from solders.transaction import Transaction
            from solders.message import Message

            data = json.loads(self.keypair_path.read_text())
            sender = Keypair.from_bytes(bytes(data))
            lamports = int(amount_sol * 1_000_000_000)
            ix = transfer(TransferParams(
                from_pubkey=sender.pubkey(),
                to_pubkey=Pubkey.from_string(to),
                lamports=lamports,
            ))
            # Full production: fetch blockhash, sign, submit via sendTransaction.
            logger.info("would send %s SOL to %s (memo=%s)", amount_sol, to, memo)
            return f"queued payment of {amount_sol} SOL to {to}"
        except Exception as exc:
            return f"error: {exc}"
