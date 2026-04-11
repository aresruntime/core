"""Runtime configuration. All secrets + addresses live in .env."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # identity / wallet — read from .env
    ares_sol_wallet: str = ""
    ares_sol_keypair_path: str = ".keys/ares.json"
    solana_rpc_url: str = "https://api.mainnet-beta.solana.com"

    # cognition
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # identity surfaces
    ares_email: str = ""
    ares_x_handle: str = ""
    ares_x_bearer: str = ""
    ares_github_token: str = ""
    ares_discord_token: str = ""

    # x402
    x402_facilitator_url: str = "https://x402.org/facilitator"
    x402_max_payment_lamports: int = 1_000_000

    # runtime
    ares_tick_interval: int = 60
    ares_compute_budget_usd: float = 50.0
    ares_dormancy_threshold_usd: float = 5.0
    ares_memory_path: str = "data/memory/ares.sqlite"
    ares_jobs_path: str = "data/jobs"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
