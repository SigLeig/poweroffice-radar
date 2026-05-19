"""Read-only PowerOffice Go API client (OAuth2 client credentials)."""

from __future__ import annotations

import base64
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx

from config import PowerOfficeConfig, load_config


class PowerOfficeClient:
    def __init__(self, config: PowerOfficeConfig | None = None) -> None:
        self.config = config or load_config()
        self._token: str | None = None
        self._token_expires: datetime | None = None

    def _auth_headers(self) -> dict[str, str]:
        pair = f"{self.config.application_key}:{self.config.client_key}"
        encoded = base64.b64encode(pair.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Ocp-Apim-Subscription-Key": self.config.subscription_key,
        }

    def _ensure_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._token and self._token_expires and now < self._token_expires:
            return self._token

        with httpx.Client(timeout=60.0) as http:
            resp = http.post(
                self.config.token_url,
                headers={
                    **self._auth_headers(),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={"grant_type": "client_credentials"},
            )
            resp.raise_for_status()
            data = resp.json()

        self._token = data["access_token"]
        expires_in = int(data.get("expires_in", 1200))
        # Refresh a little before expiry
        self._token_expires = now + timedelta(seconds=expires_in - 60)
        return self._token

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET relative to API base, e.g. path='/TrialBalance'."""
        token = self._ensure_token()
        url = f"{self.config.api_base}{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Ocp-Apim-Subscription-Key": self.config.subscription_key,
        }
        with httpx.Client(timeout=120.0) as http:
            resp = http.get(url, headers=headers, params=params)
            resp.raise_for_status()
            if resp.status_code == 204 or not resp.content:
                return None
            return resp.json()

    def get_trial_balance(self, as_of: date | None = None) -> Any:
        d = as_of or date.today()
        return self.get("/TrialBalance", params={"date": d.isoformat()})

    def get_outgoing_invoices(self) -> Any:
        return self.get("/OutgoingInvoices")

    def get_projects(self) -> Any:
        return self.get("/Projects")

    def get_financial_settings(self) -> Any:
        return self.get("/FinancialSettings")

    def get_general_ledger_accounts(self) -> Any:
        return self.get("/GeneralLedgerAccounts")
