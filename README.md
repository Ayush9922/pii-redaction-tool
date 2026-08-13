# PII Redaction Tool

A Python-based tool that reads a customer-support ticket log, detects **Personally Identifiable Information (PII)**, replaces every occurrence with realistic fake alternatives, and writes a fully redacted output both as a plain-text file and a formatted **Microsoft Word (.docx)** document.

---

## Features

| PII Category | Detection Method | Example |
|:---|:---|:---|
| **Full Name** | Regex (two title-case words) + blocklist filter | `Rashi Patil` |
| **Email Address** | Regex | `rashhi.patil@gmail.com` |
| **Phone Number** | Regex (supports `+91` Indian format) | `+91 9876543210` |
| **Company Name** | Regex (title-case + corporate suffix) | `Patil Biotech Ltd.` |
| **Physical Address** | Regex (India 6-digit PIN + US ZIP) | `45, Park Street, ... 700016, India` |
| **Social Security Number (SSN)** | Regex `XXX-XX-XXXX` | `666-23-9874` |
| **Credit Card Number** | Regex (16 digits, optional separators) | `4532-8827-1100-3456` |
| **Date of Birth (DOB)** | Regex (YYYY-MM-DD / DD-MM-YYYY, pre-2010) | `1994-11-23` |
| **IP Address** | Regex | `192.168.4.15` |

### Key Design Decisions

- **Consistent mapping**: The same original value always maps to the same fake replacement throughout the document (e.g., every mention of `Rashi Patil` becomes the same fake name everywhere).
- **No third-party NER required**: The tool uses pure regex + a curated blocklist, making it lightweight and dependency-minimal.
- **Fake-but-realistic replacements**: [`Faker`](https://faker.readthedocs.io/) generates plausible names, emails, addresses, SSNs, and phone numbers rather than generic `[REDACTED]` placeholders.
- **Seeded randomness**: `Faker.seed(42)` ensures reproducible output.
- **Overlap resolution**: When two patterns overlap (e.g., a name inside an address), the earlier/longer span wins.
- **Audit trail**: A `redaction_mappings.json` log records every detected PII entity, its type, character span, original value, and replacement.

---

## Project Structure

```
pii-redaction-tool/
├── ticket_log.txt            # Input: realistic support-ticket log (with PII)
├── ground_truth.json         # Annotated PII labels for evaluation
├── redact_pii.py             # Main redaction script
├── evaluate_redaction.py     # Evaluation script (Precision / Recall / F1)
├── redacted_ticket_log.txt   # Output: plain-text redacted version
├── redacted_ticket_log.docx  # Output: formatted Word document
├── redaction_mappings.json   # Audit log of all replacements
├── evaluation_report.md      # Auto-generated evaluation report
└── README.md                 # This file
```

---

## Requirements

```
python >= 3.9
faker
python-docx
```

Install dependencies:

```bash
pip install faker python-docx
```

---

## Usage

### 1. Run the Redaction Script

```bash
python redact_pii.py
```

**Inputs:**
- `ticket_log.txt` — the raw ticket log to redact

**Outputs:**
- `redacted_ticket_log.txt` — plain-text redacted log
- `redacted_ticket_log.docx` — formatted Word document
- `redaction_mappings.json` — full audit log of replacements

### 2. Run the Evaluation Script

```bash
python evaluate_redaction.py
```

**Inputs:**
- `ground_truth.json` — annotated ground-truth PII labels
- `redaction_mappings.json` — output from redact_pii.py

**Output:**
- Terminal: Accuracy, Precision, Recall, F1-Score
- `evaluation_report.md` — detailed markdown report with category-wise breakdown, false positives, and false negatives

---

## Evaluation Results (on included sample dataset)

| Metric | Score |
|:---|:---:|
| Accuracy | **96.67%** |
| Precision | **96.67%** |
| Recall | **96.67%** |
| F1-Score | **96.67%** |

29 out of 30 ground-truth PII entities were correctly detected and redacted.

---

## Known Edge Cases & Limitations

| Limitation | Notes |
|:---|:---|
| Names inside `[Customer Name (...)]` headers | Not redacted — these are log-format structural labels |
| Single-word names / initials | Only two-word `FirstName LastName` patterns are detected |
| Non-Indian phone formats | Non-`+91` international numbers not fully covered |
| Ambiguous dates | Dates in 2010+ are not treated as DOBs to avoid false positives on ticket dates |
| Addresses not matching the regex | Freeform or abbreviated addresses may be missed |
| Multi-line addresses | Only single-line address detection is supported |

---

## Potential Enhancements

- Add **spaCy NER** for more robust name and organisation detection
- Integrate **Microsoft Presidio** for enterprise-grade PII detection with more categories (passport numbers, Aadhaar, PAN, etc.)
- Support **PDF** and **HTML** input formats
- Add a **confidence score** alongside each detected entity
