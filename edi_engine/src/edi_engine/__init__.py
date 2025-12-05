from .core import X12Tokenizer
from .logistics import orders, shipping, finance
from .healthcare import claims, eligibility
import logging

def generic_parse(segments, doc_type):
    """
    Fallback parser for unsupported transaction sets.
    Returns the raw segment structure so the user sees SOMETHING useful.
    """
    return {
        "doc_type": f"{doc_type} (Generic View)",
        "note": "No specific parser logic defined for this type yet.",
        "structure": [
            {"segment": s.tag, "elements": s.elements} for s in segments
        ]
    }

def parse_edi(raw_content: str) -> dict:
    """UNIVERSAL ENTRY POINT: Auto-detects and parses."""
    tokenizer = X12Tokenizer(raw_content)
    segments = tokenizer.tokenize()
    
    if not segments:
        return {"error": "Empty or invalid EDI content", "success": False}

    # 1. Detect Type from ST Segment
    doc_type = "Unknown"
    for seg in segments:
        if seg.tag == "ST":
            doc_type = seg.get(1)
            break
    
    # 2. Route to Specific Parsers
    parsers = {
        "850": orders.parse_850_po,
        "855": orders.parse_855_ack,
        "856": shipping.parse_856_asn,
        "214": shipping.parse_214_status,
        "940": shipping.parse_940_warehouse_order, 
        "810": finance.parse_810_invoice,
        "997": finance.parse_997_ack,
        "837": claims.parse_837_claim,
        "835": claims.parse_835_payment,
        "270": eligibility.parse_270_inquiry,
        "271": eligibility.parse_271_eligibility
    }
    
    parser_func = parsers.get(doc_type)
    
    result = {
        "success": True,
        "detected_type": doc_type,
        "segments_read": len(segments),
        "data": {}
    }

    try:
        if parser_func:
            result["data"] = parser_func(segments)
        else:
            # USE FALLBACK INSTEAD OF ERROR
            result["data"] = generic_parse(segments, doc_type)
            result["warning"] = "Using generic parser. Some fields may not be labeled."
            
    except Exception as e:
        logging.error(f"Parser Error: {e}")
        result["success"] = False
        result["error"] = f"Parsing failed: {str(e)}"

    return result