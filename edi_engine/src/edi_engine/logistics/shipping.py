from ..utils import format_date

def parse_856_asn(segments):
    data = {"doc_type": "856 ASN", "shipment_id": None, "structure": []}
    current_level = "Unknown"
    for seg in segments:
        if seg.tag == "BSN":
            data["shipment_id"] = seg.get(2)
            data["ship_date"] = format_date(seg.get(3))
        elif seg.tag == "HL":
            current_level = seg.get(3) # S, O, I
        elif seg.tag == "LIN" and current_level == "I":
            data["structure"].append({"type": "Item", "sku": seg.get(3)})
        elif seg.tag == "SN1" and data["structure"] and current_level == "I":
            data["structure"][-1]["qty"] = seg.get(2)
    return data

def parse_214_status(segments):
    data = {"doc_type": "214 Carrier Status", "updates": []}
    for seg in segments:
        if seg.tag == "B10":
            data["tracking_number"] = seg.get(1)
        elif seg.tag == "AT7":
            status_map = {"AF": "Departed", "X1": "Arrived", "D1": "Delivered", "X6": "En Route"}
            data["updates"].append({
                "status": status_map.get(seg.get(1), seg.get(1)),
                "date": format_date(seg.get(5)),
                "time": seg.get(6)
            })
    return data

def parse_940_warehouse_order(segments):
    """
    Parses a 940 Warehouse Shipping Order.
    Commonly used to tell a 3PL or Warehouse what to ship.
    """
    data = {"doc_type": "940 Warehouse Order", "depositor_order": "Unknown", "items": []}
    
    for seg in segments:
        # W05 is the Header for 940s
        if seg.tag == "W05":
            data["depositor_order"] = seg.get(2) # Order #
            data["po_number"] = seg.get(3)       # PO Link
            
        elif seg.tag == "N1" and seg.get(1) == "ST":
            data["ship_to"] = seg.get(2)
            
        # W01 is the Line Item (Similar to PO1 but for Warehouses)
        elif seg.tag == "W01":
            qty = int(seg.get(1) or 0)
            
            # Smart SKU extraction for W01
            # Format: W01 * Qty * Units * UPC? * Qual * SKU
            sku = "UNKNOWN"
            
            # Try to grab the item from common positions
            # In your sample: W01*..*..*..*VN*ITEM-ABC
            # Element 4 is Qualifier, Element 5 is Value
            if seg.get(4) in ["VN", "VP", "UP", "BP"]:
                sku = seg.get(5)
            # Or fallback to element 3 (often UPC) if it looks like a code
            elif seg.get(3) and len(seg.get(3)) > 6:
                sku = seg.get(3)
                
            data["items"].append({
                "qty": qty,
                "unit": seg.get(2),
                "sku": sku
            })
            
    return data