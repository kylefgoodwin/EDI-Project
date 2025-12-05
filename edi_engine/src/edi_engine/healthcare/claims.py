from ..utils import format_date, format_currency, mask_pii

def parse_837_claim(segments):
    data = {"doc_type": "837 Medical Claim", "claims": []}
    current_claim = None
    
    for seg in segments:
        if seg.tag == "BHT":
            data["creation_date"] = format_date(seg.get(4))
        elif seg.tag == "NM1":
            role = seg.get(1)
            if role == "85": # Billing Provider
                if current_claim: current_claim["provider"] = seg.get(3)
            elif role == "IL": # Insured/Subscriber
                if current_claim: current_claim["patient_id_masked"] = mask_pii(seg.get(9))
        elif seg.tag == "CLM":
            current_claim = {
                "claim_id": seg.get(1),
                "amount": format_currency(seg.get(2)),
                "diagnoses": [],
                "provider": "Unknown",
                "patient_id_masked": "Unknown"
            }
            data["claims"].append(current_claim)
        elif seg.tag == "HI":
            raw_codes = seg.elements[1:]
            codes = []
            for c in raw_codes:
                parts = c.split(':')
                if len(parts) > 1: codes.append(parts[1])
            if current_claim:
                current_claim["diagnoses"] = codes
    return data

def parse_835_payment(segments):
    data = {"doc_type": "835 Payment", "payments": []}
    for seg in segments:
        if seg.tag == "TRN": data["check_number"] = seg.get(2)
        elif seg.tag == "BPR": data["total_paid"] = format_currency(seg.get(2))
        elif seg.tag == "CLP":
            data["payments"].append({
                "claim_id": seg.get(1),
                "status": seg.get(2),
                "paid": format_currency(seg.get(4))
            })
    return data