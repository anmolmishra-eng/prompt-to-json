"""Generate validation report from validation_summary.json - ONLY Source of Truth

This is the ONLY way to generate validation reports.
Manual summary files are NOT allowed.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

SUMMARY_FILE = "production_validation_results/validation_summary.json"


def load_validation_data():
    if not Path(SUMMARY_FILE).exists():
        print(f"ERROR: {SUMMARY_FILE} not found. Run run_production_validation.py first.")
        sys.exit(1)
    with open(SUMMARY_FILE) as f:
        return json.load(f)


def generate_report(data):
    report = []
    report.append("=" * 70)
    report.append("PRODUCTION VALIDATION REPORT")
    report.append("=" * 70)
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append(f"Source: {SUMMARY_FILE}")
    report.append(f"Validation Run: {data['timestamp']}")
    report.append(f"Total Tests: {data['total_tests']}")
    report.append("")

    # City breakdown
    cities = {}
    for r in data["results"]:
        city = r["city"]
        if city not in cities:
            cities[city] = []
        cities[city].append(r)

    report.append("CITY BREAKDOWN")
    report.append("-" * 70)
    for city, results in cities.items():
        total = len(results)
        success = sum(1 for r in results if r["success_rate"] != "0/1")
        report.append(f"{city}: {success}/{total} flows completed")

    report.append("")
    report.append("DETAILED RESULTS")
    report.append("-" * 70)
    for r in data["results"]:
        report.append(f"{r['flow_id']}: {r['success_rate']}")
        for step, status in r["steps"].items():
            report.append(f"  {step}: {status}")

    return "\n".join(report)


if __name__ == "__main__":
    data = load_validation_data()
    report = generate_report(data)
    print(report)

    output_file = "production_validation_results/REPORT.txt"
    with open(output_file, "w") as f:
        f.write(report)
    print(f"\nReport saved: {output_file}")
