import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class PowerOfficeConfig:
    application_key: str
    client_key: str
    subscription_key: str
    env: str  # "demo" | "production"

    @property
    def token_url(self) -> str:
        if self.env == "demo":
            return "https://goapi.poweroffice.net/Demo/OAuth/Token"
        return "https://goapi.poweroffice.net/OAuth/Token"

    @property
    def api_base(self) -> str:
        if self.env == "demo":
            return "https://goapi.poweroffice.net/Demo/v2"
        return "https://goapi.poweroffice.net/v2"


def load_config() -> PowerOfficeConfig:
    env = os.getenv("POWEROFFICE_ENV", "demo").lower()
    app = os.getenv("POWEROFFICE_APPLICATION_KEY", "").strip()
    client = os.getenv("POWEROFFICE_CLIENT_KEY", "").strip()
    sub = os.getenv("POWEROFFICE_SUBSCRIPTION_KEY", "").strip()

    missing = [
        name
        for name, val in [
            ("POWEROFFICE_APPLICATION_KEY", app),
            ("POWEROFFICE_CLIENT_KEY", client),
            ("POWEROFFICE_SUBSCRIPTION_KEY", sub),
        ]
        if not val
    ]
    if missing:
        raise ValueError(
            "Mangler i .env: "
            + ", ".join(missing)
            + ". Kopier .env.example til .env og fyll inn nøklene fra PowerOffice."
        )

    return PowerOfficeConfig(
        application_key=app,
        client_key=client,
        subscription_key=sub,
        env=env,
    )
