# Reports Directory

## RULE: NO MANUAL REPORTS ALLOWED

All reports must be generated from `run_production_validation.py` output.

Source of truth: `backend/production_validation_results/validation_summary.json`

To generate reports:
```bash
cd backend
python run_production_validation.py  # Creates validation_summary.json
python generate_validation_report.py  # Reads validation_summary.json
```

Do not create manual summary files here.
