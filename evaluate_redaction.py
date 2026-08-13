import json
import os

def main():
    ground_truth_path = "ground_truth.json"
    mappings_path     = "redaction_mappings.json"
    report_path       = "evaluation_report.md"

    if not os.path.exists(ground_truth_path):
        print(f"Error: {ground_truth_path} not found.")
        return
    if not os.path.exists(mappings_path):
        print(f"Error: {mappings_path} not found. Run redact_pii.py first.")
        return

    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        gt = json.load(f)

    with open(mappings_path, 'r', encoding='utf-8') as f:
        audit = json.load(f)

    # audit["mappings"] keys are like "Rashi Patil [name]"
    # Extract just the original string (everything before " [<type>]")
    redacted_originals = set()
    for key in audit.get("mappings", {}).keys():
        # Strip " [type]" suffix
        if " [" in key:
            original = key[:key.rfind(" [")]
            redacted_originals.add(original.lower())
        else:
            redacted_originals.add(key.lower())

    # Build ground-truth flat lookup: value_lower -> category
    gt_lookup = {}
    category_totals = {}
    for category, values in gt.items():
        category_totals[category] = len(values)
        for val in values:
            gt_lookup[val.lower()] = category

    gt_total = len(gt_lookup)

    # True Positives: GT entities that were actually redacted
    tp_by_category = {cat: 0 for cat in gt.keys()}
    tp = 0
    fn_details = []

    for val_lower, category in gt_lookup.items():
        if val_lower in redacted_originals:
            tp += 1
            tp_by_category[category] += 1
        else:
            # Find original case
            for val in gt[category]:
                if val.lower() == val_lower:
                    fn_details.append((val, category))
                    break

    # False Positives: things we redacted that are NOT in ground truth
    fp_details = []
    for key in audit.get("mappings", {}).keys():
        if " [" in key:
            original = key[:key.rfind(" [")]
        else:
            original = key
        if original.lower() not in gt_lookup:
            fp_details.append((original, audit["mappings"][key]))

    fp = len(fp_details)
    fn = len(fn_details)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy  = tp / gt_total if gt_total > 0 else 0.0

    print("=" * 40)
    print("EVALUATION RESULTS")
    print("=" * 40)
    print(f"Total Ground Truth PII : {gt_total}")
    print(f"True Positives  (TP)   : {tp}")
    print(f"False Positives (FP)   : {fp}")
    print(f"False Negatives (FN)   : {fn}")
    print("-" * 40)
    print(f"Accuracy  : {accuracy:.2%}")
    print(f"Precision : {precision:.2%}")
    print(f"Recall    : {recall:.2%}")
    print(f"F1-Score  : {f1:.2%}")
    print("=" * 40)

    # --- Build Markdown Report ---
    report = f"""# PII Redaction Evaluation Report

This report summarises the performance of the PII Redaction script against
the annotated ground-truth labels from `ground_truth.json`.

## Summary Metrics

| Metric | Value | Description |
|:---|:---:|:---|
| Total Ground-Truth PII | {gt_total} | Expected entities to redact |
| True Positives (TP) | {tp} | GT entities correctly redacted |
| False Positives (FP) | {fp} | Non-GT text incorrectly redacted |
| False Negatives (FN) | {fn} | GT entities missed by the tool |
| **Accuracy** | **{accuracy:.2%}** | TP / Total Expected |
| **Precision** | **{precision:.2%}** | TP / (TP + FP) |
| **Recall** | **{recall:.2%}** | TP / (TP + FN) |
| **F1-Score** | **{f1:.2%}** | Harmonic mean of Precision & Recall |

---

## Category-wise Breakdown

| Category | Expected | Detected (TP) | Recall |
|:---|:---:|:---:|:---:|
"""
    for cat in sorted(gt.keys()):
        exp = category_totals[cat]
        hits = tp_by_category[cat]
        rec  = hits / exp if exp > 0 else 0.0
        report += f"| {cat.upper()} | {exp} | {hits} | {rec:.0%} |\n"

    report += "\n---\n\n## False Positives (non-PII elements redacted)\n\n"
    if fp_details:
        report += "| Original | Replaced With |\n|:---|:---|\n"
        for orig, repl in fp_details:
            report += f"| `{orig}` | `{repl}` |\n"
    else:
        report += "_None — no false positives detected._\n"

    report += "\n## False Negatives (PII elements missed)\n\n"
    if fn_details:
        report += "| Original | Category |\n|:---|:---|\n"
        for orig, cat in fn_details:
            report += f"| `{orig}` | {cat.upper()} |\n"
    else:
        report += "_None — all ground-truth PII entities were successfully redacted!_\n"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"[+] Saved evaluation report -> {report_path}")


if __name__ == '__main__':
    main()
