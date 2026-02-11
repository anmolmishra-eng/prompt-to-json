# Production Validation - Single Source of Truth

## Overview
All production validation claims are generated from `run_production_validation.py` and stored in `validation_summary.json`.

## Usage

### Run Validation
```bash
cd backend
python run_production_validation.py
```

### Generate Report
```bash
cd backend
python generate_validation_report.py
```

## Files
- `run_production_validation.py` - Validation test runner
- `production_validation_results/validation_summary.json` - Raw validation data (source of truth)
- `generate_validation_report.py` - Report generator (reads from JSON)
- `production_validation_results/REPORT.txt` - Generated report

## Rules
1. NO hand-written claims about production readiness
2. ALL reports generated from validation_summary.json
3. Run validation before making any production claims
