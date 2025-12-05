from ..utils import format_date, format_currency

def parse_850_po(segments):
    data = {"doc_type": "850 Purchase Order", "po_number": "Unknown", "items": []}
    for seg in segments:
        if seg.tag == "BEG":
            data["po_number"] = seg.get(3)
            data["date"] = format_date(seg.get(5))
        elif seg.tag == "N1" and seg.get(1) == "ST":
            data["ship_to"] = seg.get(2)
        elif seg.tag == "PO1":
            # --- SMART SKU EXTRACTION ---
            # Standard X12 PO1 structure is variable.
            # We look for qualifiers (VP, BP, UP, VN) to find the real Part Number.
            
            qty = int(seg.get(2) or 0)
            price = format_currency(seg.get(4))
            sku = "UNKNOWN"

            # 1. Try to find specific qualifiers (VP = Vendor Part, BP = Buyer Part, UP = UPC)
            # We scan elements 6 through 15 (typical range for IDs)
            found_sku = False
            for i in range(6, len(seg.elements)):
                val = seg.get(i)
                if val in ["VP", "VN", "BP", "UP", "IB"]:
                    # The value is immediately after the qualifier
                    sku = seg.get(i + 1)
                    found_sku = True
                    break
            
            # 2. Fallback: If no qualifier found, use standard position 7
            if not found_sku:
                sku = seg.get(7) or "MISSING"

            data["items"].append({
                "qty": qty,
                "price": price,
                "sku": sku
            })
            
    return data

def parse_855_ack(segments):
    data = {"doc_type": "855 PO Acknowledgement", "status": "Unknown"}
    for seg in segments:
        if seg.tag == "BAK":
            status_map = {"00": "Accepted", "AD": "Modified", "RD": "Rejected", "AC": "Changes"}
            data["status"] = status_map.get(seg.get(1), f"Code {seg.get(1)}")
            data["po_number"] = seg.get(3)
            data["ack_date"] = format_date(seg.get(4))
    return data