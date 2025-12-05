from ..utils import format_date, mask_pii

def parse_270_inquiry(segments):
    data = {"doc_type": "270 Inquiry", "patient_masked": None}
    for seg in segments:
        if seg.tag == "NM1" and seg.get(1) == "IL":
             data["patient_masked"] = mask_pii(seg.get(9))
    return data

def parse_271_eligibility(segments):
    data = {"doc_type": "271 Response", "status": "Unknown"}
    for seg in segments:
        if seg.tag == "EB":
            code = seg.get(1)
            data["status"] = "Active" if code == "1" else f"Code {code}"
            data["plan"] = seg.get(5)
    return data