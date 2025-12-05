"""
CORE ENGINE: Low-level X12 Tokenizer
Production Grade: Auto-detects delimiters from the ISA header.
"""
from typing import List, Optional

class EDISegment:
    def __init__(self, tag: str, elements: List[str]):
        self.tag = tag.strip()
        self.elements = [e.strip() for e in elements]

    def get(self, index: int, default: str = None) -> Optional[str]:
        """Safe accessor for EDI elements (1-based index)."""
        if index < len(self.elements):
            val = self.elements[index]
            return val if val else default
        return default

class X12Tokenizer:
    def __init__(self, raw_content: str):
        self.raw = raw_content.strip()
        self.segments: List[EDISegment] = []
        
    def tokenize(self) -> List[EDISegment]:
        if not self.raw:
            return []

        # 1. Intelligent Delimiter Detection
        # ISA segment is fixed length (106 chars). 
        # Element Sep is usually char 3 ('*'). Segment Term is usually char 105 ('~').
        element_sep = '*'
        segment_term = '~'
        
        if self.raw.startswith("ISA"):
            try:
                element_sep = self.raw[3]
                isa_segment = self.raw[:106]
                potential_term = isa_segment[-1]
                if not potential_term.isalnum():
                    segment_term = potential_term
            except IndexError:
                pass 

        # Clean up newlines only if they aren't the terminator
        if segment_term not in ['\n', '\r']:
            clean_raw = self.raw.replace('\n', '').replace('\r', '')
        else:
            clean_raw = self.raw

        raw_segments = clean_raw.split(segment_term)
        
        for r in raw_segments:
            if not r.strip(): continue
            elements = r.split(element_sep)
            tag = elements[0]
            # Basic noise filtering
            if len(tag) < 2 or len(tag) > 3: continue 
            self.segments.append(EDISegment(tag, elements))
            
        return self.segments