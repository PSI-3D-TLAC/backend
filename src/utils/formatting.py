from __future__ import annotations

from datetime import datetime

def now_iso() -> str:
    return datetime.utcnow().isoformat()

def format_money(amount: float, currency: str = "€") -> str:
    return f"{float(amount):.2f} {currency}"

def format_minutes(total_min: int) -> str:
    total_min = int(total_min or 0)
    hours, minutes = divmod(total_min, 60)
    if hours and minutes:
        return f"{hours}h {minutes}m"
    if hours:
        return f"{hours}h"
    return f"{minutes}m"

def format_eta_days(days: int) -> str:
    days = int(days or 0)
    if days <= 0:
        return "Ready for pickup"
    if days == 1:
        return "1 day"
    return f"{days} days"
