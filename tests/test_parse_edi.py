import pytest
from edi_engine import parse_edi


def test_parse_basic_x12():
    sample = (
        "ISA*00*          *00*          *ZZ*SENDER       *ZZ*RECEIVER     "
        "*210101*1253*U*00401*000000001*0*T*:~GS*PO*SENDER*RECEIVER*20210101*1253*1*X*004010~"
        "ST*850*0001~BEG*00*SA*12345**20210101~SE*4*0001~GE*1*1~IEA*1*000000001~"
    )
    result = parse_edi(sample)
    assert isinstance(result, dict)
    assert result.get("success", False)
    data = result.get("data") or {}
    assert data.get("file_type") == "X12"
    tags = [s.get("tag") for s in data.get("segments", [])]
    assert any(t in ("ISA", "GS", "ST") for t in tags)


def test_parse_empty():
    res = parse_edi("")
    assert res.get("success") is False
