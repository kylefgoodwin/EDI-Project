def parse_edi(content):
    """
    A lightweight, deterministic X12 EDI Parser.
    This converts raw EDI strings into a structured JSON format 
    that is easier for the AI to read and analyze.
    """
    if not content:
        return {"success": False, "error": "Empty content"}

    try:
        # 1. basic cleanup
        content = content.strip()
        
        # 2. Detect delimiters (Simple assumption: * for elements, ~ for segments)
        # In a full production app, you would read the ISA header to find these dynamic chars.
        segment_terminator = "~"
        element_separator = "*"
        
        # 3. Split into segments
        raw_segments = content.split(segment_terminator)
        parsed_segments = []
        
        transaction_set = "Unknown"
        sender_id = "Unknown"
        receiver_id = "Unknown"

        for segment in raw_segments:
            segment = segment.strip()
            if not segment:
                continue
            
            elements = segment.split(element_separator)
            segment_id = elements[0]
            
            # Capture specific metadata for the summary
            if segment_id == "ISA":
                # ISA elements 6 and 8 are Sender/Receiver
                if len(elements) > 8:
                    sender_id = elements[6].strip()
                    receiver_id = elements[8].strip()
            
            elif segment_id == "ST":
                # ST element 1 is the Transaction Set Code (e.g., 850)
                if len(elements) > 1:
                    transaction_set = elements[1]

            # include both `id` (back-compat) and `tag` (used by tests/other code)
            parsed_segments.append({
                "id": segment_id,
                "tag": segment_id,
                "elements": elements[1:] # Store data without the ID
            })

        # 4. Construct the Final Data Structure
        return {
            "success": True,
            "data": {
                "file_type": "X12",
                "transaction_set": transaction_set,
                "sender": sender_id,
                "receiver": receiver_id,
                "segment_count": len(parsed_segments),
                # We pass the full structure so the AI can read line-by-line
                "segments": parsed_segments, 
                "raw_content": content
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}