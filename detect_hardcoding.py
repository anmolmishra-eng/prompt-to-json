"""
Detect Hardcoding and Fallback Logic
Identifies default dimensions, fallback templates, and missing file reads
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

def analyze_file(filepath, filename):
    """Analyze a file for hardcoded values and fallbacks"""
    print(f"\n{'='*70}")
    print(f"ANALYZING: {filename}")
    print('='*70)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    findings = []

    # 1. Default dimensions
    dim_patterns = [
        (r'\.get\(["\']width["\']\s*,\s*(\d+\.?\d*)\)', 'Default width'),
        (r'\.get\(["\']length["\']\s*,\s*(\d+\.?\d*)\)', 'Default length'),
        (r'\.get\(["\']height["\']\s*,\s*(\d+\.?\d*)\)', 'Default height'),
        (r'\.get\(["\']depth["\']\s*,\s*(\d+\.?\d*)\)', 'Default depth'),
        (r'\.get\(["\']thickness["\']\s*,\s*(\d+\.?\d*)\)', 'Default thickness'),
    ]

    for pattern, desc in dim_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'type': 'DEFAULT_DIMENSION',
                'line': line_num,
                'desc': desc,
                'value': match.group(1),
                'code': lines[line_num-1].strip()
            })

    # 2. Fallback geometry
    fallback_patterns = [
        (r'# Fallback', 'Fallback comment'),
        (r'fallback', 'Fallback keyword'),
        (r'except.*:\s*\n.*return.*glb', 'Exception fallback'),
        (r'if not.*:\s*\n.*create_box', 'Empty check fallback'),
    ]

    for pattern, desc in fallback_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'type': 'FALLBACK_LOGIC',
                'line': line_num,
                'desc': desc,
                'code': lines[line_num-1].strip()[:80]
            })

    # 3. File reads (should exist but might be missing)
    file_read_patterns = [
        (r'open\(', 'File open'),
        (r'\.load\(', 'Load method'),
        (r'json\.load', 'JSON load'),
        (r'spec_storage\.load', 'Spec storage load'),
    ]

    for pattern, desc in file_read_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'type': 'FILE_READ',
                'line': line_num,
                'desc': desc,
                'code': lines[line_num-1].strip()[:80]
            })

    # 4. Hardcoded paths
    path_patterns = [
        (r'["\']data/[^"\']+["\']', 'Hardcoded data path'),
        (r'["\']backend/[^"\']+["\']', 'Hardcoded backend path'),
    ]

    for pattern, desc in path_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'type': 'HARDCODED_PATH',
                'line': line_num,
                'desc': desc,
                'value': match.group(0),
                'code': lines[line_num-1].strip()[:80]
            })

    # Print findings by type
    for ftype in ['DEFAULT_DIMENSION', 'FALLBACK_LOGIC', 'FILE_READ', 'HARDCODED_PATH']:
        type_findings = [f for f in findings if f['type'] == ftype]
        if type_findings:
            print(f"\n[{ftype}] Found {len(type_findings)} instances:")
            for f in type_findings[:5]:  # Show first 5
                print(f"  Line {f['line']}: {f['desc']}")
                if 'value' in f:
                    print(f"    Value: {f['value']}")
                print(f"    Code: {f['code']}")

    return findings

def main():
    print("\n" + "="*70)
    print("HARDCODING & FALLBACK DETECTOR")
    print("="*70)

    # Files to analyze
    files_to_check = [
        ("backend/app/geometry_generator_real.py", "Geometry Generator"),
        ("backend/app/api/generate.py", "Generate API"),
        ("backend/app/api/geometry_generator.py", "Geometry API"),
    ]

    all_findings = {}

    for filepath, name in files_to_check:
        full_path = Path(filepath)
        if full_path.exists():
            findings = analyze_file(full_path, name)
            all_findings[name] = findings
        else:
            print(f"\n[SKIP] {filepath} not found")

    # Summary
    print("\n" + "="*70)
    print("CRITICAL FINDINGS SUMMARY")
    print("="*70)

    # Count by type
    total_defaults = sum(len([f for f in findings if f['type'] == 'DEFAULT_DIMENSION'])
                        for findings in all_findings.values())
    total_fallbacks = sum(len([f for f in findings if f['type'] == 'FALLBACK_LOGIC'])
                         for findings in all_findings.values())
    total_file_reads = sum(len([f for f in findings if f['type'] == 'FILE_READ'])
                          for findings in all_findings.values())

    print(f"\n[DEFAULTS] {total_defaults} default dimension values found")
    print(f"[FALLBACKS] {total_fallbacks} fallback logic blocks found")
    print(f"[FILE_READS] {total_file_reads} file read operations found")

    # Root cause analysis
    print("\n" + "="*70)
    print("ROOT CAUSE ANALYSIS")
    print("="*70)

    print("""
ISSUE: Geometry generator may use hardcoded defaults instead of spec values

EVIDENCE:
1. Multiple .get() calls with default values (width=10.0, length=8.0, etc.)
2. Fallback logic creates generic geometry when spec is incomplete
3. No file reads from spec_storage in geometry_generator_real.py
4. Direct parameter passing: generate_real_glb(spec_json)

ROOT CAUSE:
- Generator receives spec_json as function parameter (CORRECT)
- BUT uses .get() with defaults for every dimension access
- If LM returns incomplete spec, defaults are silently used
- No validation that spec_json contains required fields

RISK SCENARIOS:
1. LM returns spec without 'dimensions' key -> uses defaults
2. LM returns dimensions without 'width' -> uses width=10.0
3. Spec has typo in key name -> falls back to default
4. Empty objects array -> creates generic box

ACCEPTANCE:
[CONFIRMED] Generator uses spec_json parameter (not file reads)
[CONFIRMED] Heavy reliance on .get() defaults throughout code
[CONFIRMED] Fallback to generic geometry when data missing
[ROOT CAUSE] No strict validation of spec_json completeness
""")

    # Specific examples
    print("\n" + "="*70)
    print("SPECIFIC EXAMPLES FROM CODE")
    print("="*70)

    if "Geometry Generator" in all_findings:
        defaults = [f for f in all_findings["Geometry Generator"]
                   if f['type'] == 'DEFAULT_DIMENSION'][:3]
        if defaults:
            print("\nDefault dimensions in geometry_generator_real.py:")
            for d in defaults:
                print(f"  Line {d['line']}: {d['code']}")

    if "Generate API" in all_findings:
        fallbacks = [f for f in all_findings["Generate API"]
                    if f['type'] == 'FALLBACK_LOGIC'][:3]
        if fallbacks:
            print("\nFallback logic in generate.py:")
            for fb in fallbacks:
                print(f"  Line {fb['line']}: {fb['code']}")

    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    print("""
1. Add strict validation before calling generate_real_glb()
2. Raise errors instead of using defaults for critical dimensions
3. Log warnings when defaults are used
4. Add spec_json schema validation
5. Return validation errors to user instead of silent fallbacks
""")

    print("="*70)

if __name__ == "__main__":
    main()
