"""
Steg 1: Test at API-nøkler fungerer og skriv en enkel likviditetsoversikt.

Kjør fra prosjektmappen:
  python -m venv .venv
  .venv\\Scripts\\activate
  pip install -r requirements.txt
  copy .env.example .env
  python src/run_daily.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running as: python src/run_daily.py
sys.path.insert(0, str(Path(__file__).resolve().parent))

from liquidity_snapshot import build_snapshot, format_snapshot
from poweroffice_client import PowerOfficeClient


def main() -> int:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    client = PowerOfficeClient()

    print("Henter data fra PowerOffice (kun lesing)...")
    trial_balance = client.get_trial_balance()
    outgoing = client.get_outgoing_invoices()
    gl_accounts = client.get_general_ledger_accounts()

    # Raw JSON for debugging / mapping bank accounts in your client
    (data_dir / "trial_balance.json").write_text(
        json.dumps(trial_balance, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (data_dir / "outgoing_invoices.json").write_text(
        json.dumps(outgoing, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (data_dir / "general_ledger_accounts.json").write_text(
        json.dumps(gl_accounts, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    snapshot = build_snapshot(trial_balance, outgoing, gl_accounts)
    report = format_snapshot(snapshot)
    print()
    print(report)

    report_path = data_dir / "latest_liquidity.txt"
    report_path.write_text(report, encoding="utf-8")
    print()
    print(f"Rapport lagret: {report_path}")
    print(f"Rådata lagret i: {data_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as e:
        print(f"Konfigurasjon: {e}", file=sys.stderr)
        raise SystemExit(1) from e
    except Exception as e:
        print(f"Feil: {e}", file=sys.stderr)
        raise SystemExit(1) from e
