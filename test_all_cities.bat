@echo off
REM Test Generate Endpoint - All Cities (Windows)

echo Getting auth token...
curl -s -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=bhiv2024" > token.json
echo.

REM Note: You'll need to manually extract token from token.json and set it below
set TOKEN=YOUR_TOKEN_HERE

echo ========== MUMBAI TESTS ==========
echo.

echo Mumbai Test 1: Modern 3BHK apartment
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_mumbai_1\",\"prompt\":\"Design a modern 3BHK apartment with marble flooring and modular kitchen\",\"city\":\"Mumbai\",\"style\":\"modern\"}"
echo.

echo Mumbai Test 2: Luxury penthouse
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_mumbai_2\",\"prompt\":\"Create a luxury penthouse with glass walls and wooden interiors\",\"city\":\"Mumbai\",\"style\":\"luxury\"}"
echo.

echo Mumbai Test 3: Compact 2BHK
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_mumbai_3\",\"prompt\":\"Design a compact 2BHK flat with space-saving furniture\",\"city\":\"Mumbai\",\"style\":\"minimalist\"}"
echo.

echo Mumbai Test 4: Commercial office
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_mumbai_4\",\"prompt\":\"Build a commercial office space with open layout and conference rooms\",\"city\":\"Mumbai\",\"style\":\"contemporary\"}"
echo.

echo ========== PUNE TESTS ==========
echo.

echo Pune Test 1: 4BHK villa
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_pune_1\",\"prompt\":\"Design a 4BHK villa with garden and granite countertops\",\"city\":\"Pune\",\"style\":\"traditional\"}"
echo.

echo Pune Test 2: Duplex house
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_pune_2\",\"prompt\":\"Create a duplex house with wooden staircase and terrace\",\"city\":\"Pune\",\"style\":\"modern\"}"
echo.

echo Pune Test 3: Studio apartment
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_pune_3\",\"prompt\":\"Design a studio apartment with smart storage solutions\",\"city\":\"Pune\",\"style\":\"minimalist\"}"
echo.

echo Pune Test 4: Farmhouse
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_pune_4\",\"prompt\":\"Build a farmhouse with brick walls and open kitchen\",\"city\":\"Pune\",\"style\":\"rustic\"}"
echo.

echo ========== NASHIK TESTS ==========
echo.

echo Nashik Test 1: 3BHK independent house
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_nashik_1\",\"prompt\":\"Design a 3BHK independent house with concrete structure\",\"city\":\"Nashik\",\"style\":\"modern\"}"
echo.

echo Nashik Test 2: Bungalow with garage
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_nashik_2\",\"prompt\":\"Create a bungalow with garage and quartz kitchen counters\",\"city\":\"Nashik\",\"style\":\"contemporary\"}"
echo.

echo Nashik Test 3: Row house
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_nashik_3\",\"prompt\":\"Design a row house with steel frame and glass windows\",\"city\":\"Nashik\",\"style\":\"industrial\"}"
echo.

echo Nashik Test 4: 2-story building
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_nashik_4\",\"prompt\":\"Build a 2-story building with multiple bedrooms and bathrooms\",\"city\":\"Nashik\",\"style\":\"traditional\"}"
echo.

echo ========== AHMEDABAD TESTS ==========
echo.

echo Ahmedabad Test 1: 3BHK apartment
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_ahmedabad_1\",\"prompt\":\"Design a 3BHK apartment with marble flooring and modern kitchen\",\"city\":\"Ahmedabad\",\"style\":\"modern\"}"
echo.

echo Ahmedabad Test 2: Townhouse
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_ahmedabad_2\",\"prompt\":\"Create a townhouse with leather furniture and granite surfaces\",\"city\":\"Ahmedabad\",\"style\":\"luxury\"}"
echo.

echo Ahmedabad Test 3: Commercial showroom
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_ahmedabad_3\",\"prompt\":\"Design a commercial showroom with glass facade and steel structure\",\"city\":\"Ahmedabad\",\"style\":\"contemporary\"}"
echo.

echo Ahmedabad Test 4: Residential complex
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_ahmedabad_4\",\"prompt\":\"Build a residential complex with foundation and roof design\",\"city\":\"Ahmedabad\",\"style\":\"modern\"}"
echo.

echo ========== BANGALORE TESTS ==========
echo.

echo Bangalore Test 1: Modern 2BHK
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_bangalore_1\",\"prompt\":\"Design a modern 2BHK apartment with wooden flooring and balcony\",\"city\":\"Bangalore\",\"style\":\"modern\"}"
echo.

echo Bangalore Test 2: Tech startup office
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_bangalore_2\",\"prompt\":\"Create a tech startup office with open workspace and meeting pods\",\"city\":\"Bangalore\",\"style\":\"contemporary\"}"
echo.

echo Bangalore Test 3: Villa with pool
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_bangalore_3\",\"prompt\":\"Design a villa with swimming pool and landscaped garden\",\"city\":\"Bangalore\",\"style\":\"luxury\"}"
echo.

echo Bangalore Test 4: Co-working space
curl -X POST "http://localhost:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"user_id\":\"test_bangalore_4\",\"prompt\":\"Build a co-working space with ergonomic furniture and lounge area\",\"city\":\"Bangalore\",\"style\":\"industrial\"}"
echo.

echo ========== ALL TESTS COMPLETED ==========
del token.json
