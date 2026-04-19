"""x402 client — lets ARES pay for metered HTTP APIs autonomously."""

from __future__ import annotations

import logging

import httpx

from ..config import settings

logger = logging.getLogger("ares.x402")


class X402Client:
    """Wraps httpx with HTTP 402 handling.

    Flow:
      1. ARES makes a request.
      2. Server returns 402 + payment requirement in body.
      3. ARES verifies requirement is within budget.
      4. ARES pays via wallet.
      5. ARES retries with X-Payment header containing the proof.
    """

    def __init__(self, wallet, facilitator: str | None = None, max_lamports: int | None = None):
        self.wallet = wallet
        self.facilitator = facilitator or settings.x402_facilitator_url
        self.max_lamports = max_lamports or settings.x402_max_payment_lamports

    def get(self, url: str, headers: dict | None = None) -> httpx.Response:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            r = client.get(url, headers=headers or {})
            if r.status_code != 402:
                return r

            requirement = r.json()
            lamports = int(requirement.get("amount", 0))
            recipient = requirement.get("recipient")

            if lamports > self.max_lamports:
                logger.warning("x402 payment %d > max %d; refusing", lamports, self.max_lamports)
                return r

            proof = self._pay_and_prove(recipient, lamports)
            return client.get(url, headers={**(headers or {}), "X-Payment": proof})

    def _pay_and_prove(self, recipient: str, lamports: int) -> str:
        result = self.wallet.pay(recipient, lamports / 1_000_000_000, memo="x402")
        # Real impl: return the tx signature after confirmation.
        return f"sol:unsettled:{result}"
