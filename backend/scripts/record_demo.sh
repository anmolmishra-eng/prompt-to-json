#!/bin/bash
# Record demo video for handover

echo "MULTI-CITY BACKEND - DEMO RECORDING GUIDE"
echo "=========================================="
echo ""
echo "This script will guide you through recording the demo"
echo "Estimated time: 2-3 minutes"
echo ""

read -p "Press ENTER to start demo walkthrough..."

echo ""
echo "DEMO SCRIPT - Follow this sequence:"
echo ""

echo "1. INTRODUCTION (15 seconds)"
echo "   Say: 'Welcome to Multi-City Backend - supporting 4 Indian cities with DCR rules'"
echo "   Show: Terminal with project structure"
echo ""

read -p "Press ENTER when ready for Step 2..."

echo "2. HEALTH CHECK (15 seconds)"
echo "   Run: curl http://localhost:8000/api/v1/health | jq"
echo "   Say: 'System is healthy with database and cache connected'"
echo "   Show: Health check response"
echo ""

read -p "Press ENTER when ready for Step 3..."

echo "3. CITY SUPPORT (20 seconds)"
echo "   Run: curl http://localhost:8000/api/v1/cities/ | jq"
echo "   Say: 'We support 4 cities: Mumbai, Pune, Ahmedabad, Nashik'"
echo "   Run: curl http://localhost:8000/api/v1/cities/Mumbai/rules | jq"
echo "   Say: 'Each city has specific DCR rules - Mumbai FSI is 1.33'"
echo ""

read -p "Press ENTER when ready for Step 4..."

echo "4. DESIGN GENERATION (30 seconds)"
echo "   Say: 'Let me generate a design for Mumbai'"
echo "   Run the following command:"
echo ""
echo "   curl -X POST http://localhost:8000/api/v1/generate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"user_id\":\"demo\",\"prompt\":\"4-floor residential building\",\"city\":\"Mumbai\"}' | jq"
echo ""
echo "   Say: 'System generated design spec with city-specific constraints'"
echo ""

read -p "Press ENTER when ready for Step 5..."

echo "5. VALIDATION RESULTS (20 seconds)"
echo "   Say: 'We achieved 100% data validation across all cities'"
echo "   Run: python scripts/validate_city_data.py"
echo "   Show: Validation results with all tests passing"
echo ""

read -p "Press ENTER when ready for Step 6..."

echo "6. CONCLUSION (10 seconds)"
echo "   Say: 'Multi-City Backend is production-ready with comprehensive testing'"
echo "   Say: 'Thank you for watching!'"
echo ""

echo "Demo script complete!"
echo ""
echo "RECORDING TIPS:"
echo "   - Use OBS Studio or screen recorder"
echo "   - Record at 1080p, 30fps"
echo "   - Keep total length under 3 minutes"
echo "   - Save as: demo_multi_city_backend.mp4"
echo ""
echo "Save video to: docs/demo_video.mp4"