"""Simple liquidity snapshot from read-only API data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


@dataclass
class LiquiditySnapshot:
    as_of: date
    bank_balance: float | None
    bank_accounts: list[tuple[str, float]]
    open_customer_total: float
    open_customer_count: int
    notes: list[str]


def _as_list(payload: Any) -> list[dict]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "value", "results"):
            if key in payload and isinstance(payload[key], list):
                return payload[key]
    return []


def _num(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _account_no(acc: dict) -> int | None:
    raw = acc.get("AccountNo") or acc.get("accountNo") or acc.get("code")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _account_name(acc: dict) -> str:
    return str(
        acc.get("AccountName")
        or acc.get("Name")
        or acc.get("name")
        or acc.get("description")
        or "?"
    )


def _account_balance(acc: dict) -> float:
    return _num(
        acc.get("Balance")
        or acc.get("balance")
        or acc.get("amount")
        or acc.get("closingBalance")
    )


def _find_bank_accounts(accounts: list[dict]) -> list[tuple[str, float]]:
    """Norwegian chart: liquidity accounts often 1900–1999 (kasse, bank)."""
    out: list[tuple[str, float]] = []
    for acc in accounts:
        name = _account_name(acc)
        no = _account_no(acc)
        name_l = name.lower()
        # NS4102: 1900–1999 = kontanter og bank (ikke kostnads-kontoer som 7770)
        is_bank = no is not None and 1900 <= no < 2000
        if not is_bank:
            continue
        out.append((f"{no} {name}" if no else name, _account_balance(acc)))
    return out


def _open_customer_amount(invoice: dict) -> float:
    for key in ("remainingAmount", "balance", "openAmount", "amountOutstanding"):
        if key in invoice and invoice[key] is not None:
            return _num(invoice[key])
    total = _num(invoice.get("totalAmount") or invoice.get("amount"))
    paid = _num(invoice.get("paidAmount"))
    return max(total - paid, 0.0)


def _is_open_invoice(inv: dict) -> bool:
    if inv.get("isPaid") is True:
        return False
    if inv.get("paid") is True:
        return False
    status = str(inv.get("status") or inv.get("invoiceStatus") or "").lower()
    if status in ("paid", "settled", "cancelled", "credited"):
        return False
    return _open_customer_amount(inv) > 0.01


def build_snapshot(
    trial_balance: Any,
    outgoing_invoices: Any,
    general_ledger_accounts: Any | None = None,
) -> LiquiditySnapshot:
    notes: list[str] = []
    as_of = date.today()

    tb_rows = _as_list(trial_balance)
    gl_rows = _as_list(general_ledger_accounts)

    bank_accounts = _find_bank_accounts(tb_rows)
    if not bank_accounts and gl_rows:
        bank_accounts = _find_bank_accounts(gl_rows)
        if bank_accounts:
            notes.append("Banksaldo hentet fra kontoplan (ikke prøvebalanse).")

    bank_balance = sum(b for _, b in bank_accounts) if bank_accounts else None
    if bank_balance is None:
        notes.append(
            "Fant ingen bankkonto automatisk. Vi finjusterer når du har kjørt første rapport."
        )

    invoices = _as_list(outgoing_invoices)
    open_invs = [i for i in invoices if _is_open_invoice(i)]
    open_total = sum(_open_customer_amount(i) for i in open_invs)

    return LiquiditySnapshot(
        as_of=as_of,
        bank_balance=bank_balance,
        bank_accounts=bank_accounts,
        open_customer_total=open_total,
        open_customer_count=len(open_invs),
        notes=notes,
    )


def format_snapshot(s: LiquiditySnapshot) -> str:
    lines = [
        f"=== Likviditetsoversikt {s.as_of.isoformat()} ===",
        "",
    ]
    if s.bank_accounts:
        lines.append("Bank / kontanter:")
        for name, bal in s.bank_accounts:
            lines.append(f"  - {name}: {bal:,.2f}".replace(",", " "))
        lines.append(f"  Sum bank: {s.bank_balance:,.2f}".replace(",", " "))
    else:
        lines.append("Bank: (ikke identifisert ennå)")

    lines.extend(
        [
            "",
            f"Utestående kundefakturaer: {s.open_customer_count} stk",
            f"Sum utestående: {s.open_customer_total:,.2f}".replace(",", " "),
            "",
            "Handling skjer i PowerOffice Go (godkjenning / faktura).",
        ]
    )
    if s.notes:
        lines.append("")
        lines.append("Merknader:")
        for n in s.notes:
            lines.append(f"  - {n}")
    return "\n".join(lines)
