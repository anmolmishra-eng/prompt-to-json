import requests
import json

BASE_URL = "http://localhost:8000/api/generate"

test_cases = {
    "Mumbai": [
        {"user_id": "test_user_mumbai", "prompt": "Design a modern 3BHK apartment with marble flooring and modular kitchen", "city": "Mumbai", "style": "modern"},
        {"user_id": "test_user_mumbai", "prompt": "Create a luxury penthouse with glass walls and wooden interiors", "city": "Mumbai", "style": "luxury"},
        {"user_id": "test_user_mumbai", "prompt": "Design a compact 2BHK flat with space-saving furniture", "city": "Mumbai", "style": "minimalist"},
        {"user_id": "test_user_mumbai", "prompt": "Build a commercial office space with open layout and conference rooms", "city": "Mumbai", "style": "contemporary"}
    ],
    "Pune": [
        {"user_id": "test_user_pune", "prompt": "Design a 4BHK villa with garden and granite countertops", "city": "Pune", "style": "traditional"},
        {"user_id": "test_user_pune", "prompt": "Create a duplex house with wooden staircase and terrace", "city": "Pune", "style": "modern"},
        {"user_id": "test_user_pune", "prompt": "Design a studio apartment with smart storage solutions", "city": "Pune", "style": "minimalist"},
        {"user_id": "test_user_pune", "prompt": "Build a farmhouse with brick walls and open kitchen", "city": "Pune", "style": "rustic"}
    ],
    "Nashik": [
        {"user_id": "test_user_nashik", "prompt": "Design a 3BHK independent house with concrete structure", "city": "Nashik", "style": "modern"},
        {"user_id": "test_user_nashik", "prompt": "Create a bungalow with garage and quartz kitchen counters", "city": "Nashik", "style": "contemporary"},
        {"user_id": "test_user_nashik", "prompt": "Design a row house with steel frame and glass windows", "city": "Nashik", "style": "industrial"},
        {"user_id": "test_user_nashik", "prompt": "Build a 2-story building with multiple bedrooms and bathrooms", "city": "Nashik", "style": "traditional"}
    ],
    "Ahmedabad": [
        {"user_id": "test_user_ahmedabad", "prompt": "Design a 3BHK apartment with marble flooring and modern kitchen", "city": "Ahmedabad", "style": "modern"},
        {"user_id": "test_user_ahmedabad", "prompt": "Create a townhouse with leather furniture and granite surfaces", "city": "Ahmedabad", "style": "luxury"},
        {"user_id": "test_user_ahmedabad", "prompt": "Design a commercial showroom with glass facade and steel structure", "city": "Ahmedabad", "style": "contemporary"},
        {"user_id": "test_user_ahmedabad", "prompt": "Build a residential complex with foundation and roof design", "city": "Ahmedabad", "style": "modern"}
    ]
}

def test_generate_endpoint(city, test_data):
    print(f"\n{'='*60}")
    print(f"Testing {city} - {test_data['style']}")
    print(f"Prompt: {test_data['prompt'][:50]}...")
    print(f"{'='*60}")

    try:
        response = requests.post(BASE_URL, json=test_data, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 201:
            data = response.json()
            print(f"✓ Success!")
            print(f"  Spec ID: {data.get('spec_id')}")
            print(f"  Cost: ₹{data.get('estimated_cost', 0):,.0f}")
            print(f"  Objects: {len(data.get('spec_json', {}).get('objects', []))}")
            return True
        else:
            print(f"✗ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Generate Endpoint Tests")
    print("="*60)

    results = {"passed": 0, "failed": 0}

    for city, tests in test_cases.items():
        for i, test_data in enumerate(tests, 1):
            print(f"\n[{city} Test {i}/4]")
            if test_generate_endpoint(city, test_data):
                results["passed"] += 1
            else:
                results["failed"] += 1

    print(f"\n{'='*60}")
    print(f"SUMMARY: {results['passed']} passed, {results['failed']} failed")
    print(f"{'='*60}")
