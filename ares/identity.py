"""ARES's digital identity. Wallet, handles, endpoints."""

from __future__ import annotations

from dataclasses import dataclass

from .config import settings


@dataclass
class Identity:
    """Everything ARES uses to be addressable on the web."""

    sol_wallet: str
    email: str
    x_handle: str
    github_token: str
    discord_token: str

    @classmethod
    def from_env(cls) -> "Identity":
        return cls(
            sol_wallet=settings.ares_sol_wallet,
            email=settings.ares_email,
            x_handle=settings.ares_x_handle,
            github_token=settings.ares_github_token,
            discord_token=settings.ares_discord_token,
        )

    @property
    def has_wallet(self) -> bool:
        return bool(self.sol_wallet)

    @property
    def surfaces(self) -> list[str]:
        surfaces = []
        if self.email:          surfaces.append("email")
        if self.x_handle:       surfaces.append("x")
        if self.github_token:   surfaces.append("github")
        if self.discord_token:  surfaces.append("discord")
        return surfaces
