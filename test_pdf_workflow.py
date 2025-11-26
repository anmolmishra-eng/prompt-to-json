"""
Test PDF to MCP Workflow for bugs
"""
import re

def test_fsi_bug():
    """Test the FSI parsing bug"""
    text_content = "FSI: 2.5 for residential areas"

    # Original buggy code
    fsi_pattern = r'FSI[:\s]+(\d+\.?\d*)'
    fsi_matches = re.findall(fsi_pattern, text_content, re.IGNORECASE)

    print(f"FSI matches found: {fsi_matches}")
    print(f"Type of fsi_matches: {type(fsi_matches)}")

    # This will fail - trying to convert list to float
    try:
        value = float(fsi_matches)  # BUG: This will crash
        print(f"Converted value: {value}")
    except Exception as e:
        print(f"❌ FSI BUG CONFIRMED: {e}")

    # Fixed version
    print("\n✅ FIXED VERSION:")
    for fsi_value in fsi_matches:
        value = float(fsi_value)
        print(f"FSI value: {value}")

def test_error_handling():
    """Test missing error handling in MCP send"""
    print("\n❌ MISSING ERROR HANDLING:")
    print("The send_rules_to_mcp function has no try-catch block")
    print("If MCP service is down, the entire workflow will crash")

if __name__ == "__main__":
    test_fsi_bug()
    test_error_handling()
