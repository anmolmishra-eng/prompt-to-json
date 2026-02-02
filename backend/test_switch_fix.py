"""Quick test for switch endpoint fix"""

# Test the NLP parser
from app.api.switch import parse_simple_query

test_queries = [
    "replace roof with clay tiles",
    "change foundation to marble",
    "make walls white",
    "update wall color to #FFFFFF",
]

print("Testing NLP Parser:\n")
for query in test_queries:
    result = parse_simple_query(query)
    print(f"Query: '{query}'")
    print(f"Result: {result}")
    status = "PASS" if result else "FAIL"
    print(f"Status: {status}\n")
