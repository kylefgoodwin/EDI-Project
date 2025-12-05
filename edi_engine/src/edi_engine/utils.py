def format_date(edi_date: str) -> str:
    if not edi_date or len(edi_date) != 8: return edi_date or "N/A"
    return f"{edi_date[:4]}-{edi_date[4:6]}-{edi_date[6:]}"

def format_currency(amount_str: str) -> float:
    try: return float(amount_str)
    except (ValueError, TypeError): return 0.0

def mask_pii(value: str) -> str:
    if not value: return "UNKNOWN"
    if len(value) < 5: return "****"
    return f"****{value[-4:]}"