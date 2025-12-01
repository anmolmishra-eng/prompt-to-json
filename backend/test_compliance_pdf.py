#!/usr/bin/env python3
"""
Test with Compliance-like Content
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from workflows.pdf_to_mcp_flow import parse_compliance_rules


def test_compliance_parsing():
    """Test rule parsing with compliance content"""

    # Sample compliance text (like what would be in a real DCR PDF)
    compliance_text = """
    MUMBAI DEVELOPMENT CONTROL REGULATIONS 2034

    CHAPTER 4: FLOOR SPACE INDEX (FSI)
    4.1 The FSI for residential buildings shall be 1.33
    4.2 For commercial buildings, FSI: 2.5 is permitted

    CHAPTER 5: SETBACKS
    5.1 Front setback: 3 meters from road boundary
    5.2 Side setback: 1.5 meters minimum required
    5.3 Rear setback: 2 meters shall be maintained

    CHAPTER 6: HEIGHT RESTRICTIONS
    6.1 Maximum height: 45 meters for residential
    6.2 Commercial maximum height: 60 meters allowed

    CHAPTER 7: PARKING REQUIREMENTS
    7.1 Parking: 1 space per 100 sq ft of built area
    7.2 Visitor parking: 1 slot per 500 sqft additional
    """

    print("Testing Compliance Rule Parsing")
    print("=" * 50)

    # Parse rules
    rules = parse_compliance_rules(compliance_text, "Mumbai")

    print(f"Rules extracted: {len(rules['rules'])}")
    print(f"Sections found: {len(rules['sections'])}")
    print()

    # Display extracted rules
    for i, rule in enumerate(rules["rules"], 1):
        print(f"{i}. {rule['type'].upper()}: {rule.get('value', rule.get('spaces_per_area', 'N/A'))}")
        if "unit" in rule:
            print(f"   Unit: {rule['unit']}")
        print(f"   Description: {rule['description']}")
        print()

    return len(rules["rules"]) > 0


async def main():
    """Test compliance parsing"""
    success = test_compliance_parsing()

    if success:
        print("✅ System successfully extracts compliance rules!")
        print("\n📋 To test with your real compliance PDF:")
        print("1. Upload your DCR/compliance PDF to accessible URL")
        print("2. Run: python test_real_pdf_workflow.py")
        print("3. Enter your PDF URL when prompted")
    else:
        print("❌ Rule extraction needs improvement")


if __name__ == "__main__":
    asyncio.run(main())
