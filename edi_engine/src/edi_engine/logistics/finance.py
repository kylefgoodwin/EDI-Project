from ..utils import format_date, format_currency

def parse_810_invoice(segments):
    data = {"doc_type": "810 Invoice", "total": 0.0, "lines": []}
    for seg in segments:
        if seg.tag == "BIG":
            data["invoice_date"] = format_date(seg.get(1))
            data["invoice_number"] = seg.get(2)
            data["po_number"] = seg.get(4)
        elif seg.tag == "TDS":
            data["total"] = format_currency(seg.get(1)) / 100.0
        elif seg.tag == "IT1":
            data["lines"].append({
                "qty": seg.get(2),
                "price": seg.get(4),
                "sku": seg.get(7)
            })
    return data

def parse_997_ack(segments):
    data = {"doc_type": "997 Functional Ack", "status": "Unknown"}
    for seg in segments:
        if seg.tag == "AK1": data["group"] = seg.get(1)
        elif seg.tag == "AK5":
            codes = {"A": "Accepted", "R": "Rejected", "E": "Errors", "M": "Rejected, Auth Required"}
            data["status"] = codes.get(seg.get(1), seg.get(1))
    return data