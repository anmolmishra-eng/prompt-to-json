# Test Generate Endpoint - Manual Testing Examples
# Base URL: http://localhost:8000/api/generate

# ============ MUMBAI EXAMPLES ============

# Mumbai Example 1: Modern 3BHK with marble
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_mumbai",
    "prompt": "Design a modern 3BHK apartment with marble flooring and modular kitchen",
    "city": "Mumbai",
    "style": "modern"
  }'

# Mumbai Example 2: Luxury penthouse
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_mumbai",
    "prompt": "Create a luxury penthouse with glass walls and wooden interiors",
    "city": "Mumbai",
    "style": "luxury"
  }'

# Mumbai Example 3: Compact 2BHK
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_mumbai",
    "prompt": "Design a compact 2BHK flat with space-saving furniture",
    "city": "Mumbai",
    "style": "minimalist"
  }'

# Mumbai Example 4: Commercial office
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_mumbai",
    "prompt": "Build a commercial office space with open layout and conference rooms",
    "city": "Mumbai",
    "style": "contemporary"
  }'

# ============ PUNE EXAMPLES ============

# Pune Example 1: 4BHK villa
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_pune",
    "prompt": "Design a 4BHK villa with garden and granite countertops",
    "city": "Pune",
    "style": "traditional"
  }'

# Pune Example 2: Duplex house
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_pune",
    "prompt": "Create a duplex house with wooden staircase and terrace",
    "city": "Pune",
    "style": "modern"
  }'

# Pune Example 3: Studio apartment
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_pune",
    "prompt": "Design a studio apartment with smart storage solutions",
    "city": "Pune",
    "style": "minimalist"
  }'

# Pune Example 4: Farmhouse
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_pune",
    "prompt": "Build a farmhouse with brick walls and open kitchen",
    "city": "Pune",
    "style": "rustic"
  }'

# ============ NASHIK EXAMPLES ============

# Nashik Example 1: 3BHK independent house
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_nashik",
    "prompt": "Design a 3BHK independent house with concrete structure",
    "city": "Nashik",
    "style": "modern"
  }'

# Nashik Example 2: Bungalow with garage
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_nashik",
    "prompt": "Create a bungalow with garage and quartz kitchen counters",
    "city": "Nashik",
    "style": "contemporary"
  }'

# Nashik Example 3: Row house
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_nashik",
    "prompt": "Design a row house with steel frame and glass windows",
    "city": "Nashik",
    "style": "industrial"
  }'

# Nashik Example 4: 2-story building
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_nashik",
    "prompt": "Build a 2-story building with multiple bedrooms and bathrooms",
    "city": "Nashik",
    "style": "traditional"
  }'

# ============ AHMEDABAD EXAMPLES ============

# Ahmedabad Example 1: 3BHK apartment
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_ahmedabad",
    "prompt": "Design a 3BHK apartment with marble flooring and modern kitchen",
    "city": "Ahmedabad",
    "style": "modern"
  }'

# Ahmedabad Example 2: Townhouse
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_ahmedabad",
    "prompt": "Create a townhouse with leather furniture and granite surfaces",
    "city": "Ahmedabad",
    "style": "luxury"
  }'

# Ahmedabad Example 3: Commercial showroom
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_ahmedabad",
    "prompt": "Design a commercial showroom with glass facade and steel structure",
    "city": "Ahmedabad",
    "style": "contemporary"
  }'

# Ahmedabad Example 4: Residential complex
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_ahmedabad",
    "prompt": "Build a residential complex with foundation and roof design",
    "city": "Ahmedabad",
    "style": "modern"
  }'
