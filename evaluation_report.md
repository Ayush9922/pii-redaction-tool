# PII Redaction Evaluation Report

This report summarises the performance of the PII Redaction script against
the annotated ground-truth labels from `ground_truth.json`.

## Summary Metrics

| Metric | Value | Description |
|:---|:---:|:---|
| Total Ground-Truth PII | 30 | Expected entities to redact |
| True Positives (TP) | 29 | GT entities correctly redacted |
| False Positives (FP) | 1 | Non-GT text incorrectly redacted |
| False Negatives (FN) | 1 | GT entities missed by the tool |
| **Accuracy** | **96.67%** | TP / Total Expected |
| **Precision** | **96.67%** | TP / (TP + FP) |
| **Recall** | **96.67%** | TP / (TP + FN) |
| **F1-Score** | **96.67%** | Harmonic mean of Precision & Recall |

---

## Category-wise Breakdown

| Category | Expected | Detected (TP) | Recall |
|:---|:---:|:---:|:---:|
| ADDRESSES | 3 | 3 | 100% |
| COMPANIES | 4 | 3 | 75% |
| CREDIT_CARDS | 2 | 2 | 100% |
| DOBS | 2 | 2 | 100% |
| EMAILS | 6 | 6 | 100% |
| IPS | 4 | 4 | 100% |
| NAMES | 6 | 6 | 100% |
| PHONES | 2 | 2 | 100% |
| SSNS | 1 | 1 | 100% |

---

## False Positives (non-PII elements redacted)

| Original | Replaced With |
|:---|:---|
| `Patil Biotech` | `Henderson, Lewis and Ryan` |

## False Negatives (PII elements missed)

| Original | Category |
|:---|:---|
| `Patil Biotech Ltd.` | COMPANIES |
