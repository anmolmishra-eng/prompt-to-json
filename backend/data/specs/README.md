# Data Integrity Enforcement

## Rules

1. **Spec JSON stored locally** - All specs MUST be saved to `data/specs/`
2. **No ghost artifacts** - All files must have valid JSON and spec_id
3. **Audit completeness > 70%** - Specs must have required fields

## Usage

### Validate Data Integrity
```bash
cd backend
python validate_data_integrity.py
```

### Use Spec Storage Manager
```python
from app.spec_storage import spec_storage

# Save spec (enforced)
spec_storage.save(spec_id, spec_json)

# Load spec
spec = spec_storage.load(spec_id)

# Check existence
if spec_storage.exists(spec_id):
    ...
```

## Validation Criteria

### Required Fields (60% weight)
- spec_id
- city
- building_type
- floors
- units
- plot_area

### Optional Fields (40% weight)
- amenities
- parking
- setbacks
- fsi
- height
- materials

## Acceptance
Validator confirms data integrity without manual patching.
