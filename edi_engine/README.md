# EDI Engine: The Universal X12 Parser

**Stop manually reading EDI files.** EDI Engine is a production-grade Python library designed to parse cryptic ANSI X12 files into clean, semantic JSON that AI Agents and humans can actually understand.

Built for the **Model Context Protocol (MCP)**, allowing you to connect Supply Chain or Healthcare data directly to Claude, Cursor, or Azure AI Agents.

## Supported Transactions

### Logistics & Supply Chain
- **850 Purchase Order:** PO Numbers, Dates, SKUs, Pricing.
- **855 Acknowledgement:** Order acceptance/rejection status.
- **856 Advance Ship Notice (ASN):** Hierarchical shipment structures (Shipment -> Order -> Item).
- **214 Carrier Status:** Shipment milestones (Arrived, Departed).
- **810 Invoice:** Billing details and line items.
- **997 Functional Ack:** File processing status.

### Healthcare (HIPAA Ready)
- **837 Medical Claim:** Claims data with PII masking.
- **835 Payment Advice:** Remittance details and denial codes.
- **270/271 Eligibility:** Coverage verification.

## Installation & Usage

### 1. Install the Library

pip install -e .



Python Usage
from edi_engine import parse_edi

# Raw, ugly EDI data from an email or FTP
raw_data = "ISA*00* *00* *ZZ*SENDERID..."

# Clean, beautiful JSON
result = parse_edi(raw_data)
print(result)



MCP Server Usage
Run this to expose EDI tools to your local AI agent.
python server.py

### Desktop App (Pro)

We provide a secure, offline-first Desktop Application for Windows and Mac.

**Zero Data Exfiltration:** Files are parsed locally on your machine.

**HIPAA Compliant:** No data is ever sent to the cloud.

**Visual Debugger:** See raw segments side-by-side with parsed JSON.

### License 

MIT License - Free for personal and commercial use