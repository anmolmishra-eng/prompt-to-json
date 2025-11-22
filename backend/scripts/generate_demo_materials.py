"""
Generate demo materials for handover
Screenshots, sample requests, expected responses
"""

import json
from pathlib import Path
from datetime import datetime


def create_sample_requests():
    """Create sample API requests for demo"""
    
    samples = {
        "mumbai_residential": {
            "description": "Mumbai 4-floor residential building",
            "request": {
                "user_id": "demo_user",
                "prompt": "Design a 4-floor residential building with parking",
                "project_id": "demo_mumbai_001",
                "city": "Mumbai"
            },
            "curl_command": """curl -X POST http://localhost:8000/api/v1/generate \\
  -H 'Content-Type: application/json' \\
  -d '{
    "user_id": "demo_user",
    "prompt": "Design a 4-floor residential building with parking",
    "project_id": "demo_mumbai_001",
    "city": "Mumbai"
  }' | jq"""
        },
        "pune_it_park": {
            "description": "Pune IT office park",
            "request": {
                "user_id": "demo_user",
                "prompt": "Create an IT office campus with 3 buildings",
                "project_id": "demo_pune_001",
                "city": "Pune"
            },
            "curl_command": """curl -X POST http://localhost:8000/api/v1/generate \\
  -H 'Content-Type: application/json' \\
  -d '{
    "user_id": "demo_user",
    "prompt": "Create an IT office campus with 3 buildings",
    "project_id": "demo_pune_001",
    "city": "Pune"
  }' | jq"""
        },
        "city_rules": {
            "description": "Get city DCR rules",
            "curl_command": "curl http://localhost:8000/api/v1/cities/Mumbai/rules | jq"
        },
        "city_context": {
            "description": "Get city context",
            "curl_command": "curl http://localhost:8000/api/v1/cities/Ahmedabad/context | jq"
        }
    }
    
    output_path = Path("docs/demo_samples.json")
    with open(output_path, 'w') as f:
        json.dump(samples, f, indent=2)
    
    print(f"Sample requests saved to {output_path}")
    
    # Create markdown version
    md_output = Path("docs/DEMO_GUIDE.md")
    with open(md_output, 'w') as f:
        f.write("# Multi-City Backend Demo Guide\n\n")
        f.write("## Sample API Requests\n\n")
        
        for name, sample in samples.items():
            f.write(f"### {sample['description']}\n\n")
            if 'request' in sample:
                f.write("**Request:**\n```json\n")
                f.write(json.dumps(sample['request'], indent=2))
                f.write("\n```\n\n")
            f.write("**cURL Command:**\n```bash\n")
            f.write(sample['curl_command'])
            f.write("\n```\n\n")
    
    print(f"Demo guide saved to {md_output}")


def create_expected_responses():
    """Create expected response examples"""
    
    expected = {
        "generate_response": {
            "spec_id": "spec_abc123xyz",
            "spec_json": {
                "version": "1.0",
                "objects": [
                    {
                        "id": "floor_001",
                        "type": "floor",
                        "material": "concrete",
                        "level": 0
                    }
                ],
                "constraints": {
                    "city": "Mumbai",
                    "fsi_base": 1.33,
                    "setback_front": 3.0
                }
            },
            "preview_url": "https://storage.example.com/previews/spec_abc123xyz.png",
            "cost_estimate": 2500000,
            "processing_time_ms": 850
        },
        "health_response": {
            "status": "healthy",
            "database": "connected",
            "cache": "connected",
            "timestamp": "2025-11-22T14:05:30.123Z",
            "version": "1.0.0"
        },
        "cities_response": {
            "cities": ["Mumbai", "Pune", "Ahmedabad", "Nashik"],
            "count": 4
        },
        "mumbai_rules_response": {
            "city": "Mumbai",
            "dcr_version": "DCPR 2034",
            "fsi_base": 1.33,
            "setback_front": 3.0,
            "setback_rear": 3.0,
            "parking_ratio": "1 ECS per 100 sqm",
            "source_documents": ["DCPR_2034.pdf", "MCGM_Amendments.pdf"]
        }
    }
    
    output_path = Path("docs/expected_responses.json")
    with open(output_path, 'w') as f:
        json.dump(expected, f, indent=2)
    
    print(f"Expected responses saved to {output_path}")


def create_demo_checklist():
    """Create demo preparation checklist"""
    
    checklist = """# Demo Preparation Checklist

## Pre-Demo Setup
- [ ] Start the backend server: `python -m uvicorn app.main:app --reload`
- [ ] Verify health check: `curl http://localhost:8000/api/v1/health`
- [ ] Test city endpoints: `curl http://localhost:8000/api/v1/cities/`
- [ ] Prepare terminal with clear font and good contrast
- [ ] Close unnecessary applications
- [ ] Test microphone and audio levels

## Demo Flow
- [ ] Introduction (15s) - Project overview
- [ ] Health check (15s) - System status
- [ ] City support (20s) - Multi-city capabilities
- [ ] Design generation (30s) - Core functionality
- [ ] Validation results (20s) - Testing success
- [ ] Conclusion (10s) - Production readiness

## Recording Settings
- [ ] Screen resolution: 1920x1080
- [ ] Frame rate: 30fps
- [ ] Audio quality: Clear microphone
- [ ] Recording software: OBS Studio or equivalent
- [ ] Output format: MP4
- [ ] Duration target: Under 3 minutes

## Post-Recording
- [ ] Review video for clarity
- [ ] Check audio synchronization
- [ ] Trim any unnecessary parts
- [ ] Save as: `docs/demo_video.mp4`
- [ ] Create thumbnail image
- [ ] Upload to shared storage

## Backup Commands
```bash
# Health check
curl http://localhost:8000/api/v1/health | jq

# List cities
curl http://localhost:8000/api/v1/cities/ | jq

# Mumbai rules
curl http://localhost:8000/api/v1/cities/Mumbai/rules | jq

# Generate design
curl -X POST http://localhost:8000/api/v1/generate \\
  -H 'Content-Type: application/json' \\
  -d '{"user_id":"demo","prompt":"4-floor building","city":"Mumbai"}' | jq

# Run validation
python scripts/validate_city_data.py
```
"""
    
    output_path = Path("docs/DEMO_CHECKLIST.md")
    with open(output_path, 'w') as f:
        f.write(checklist)
    
    print(f"Demo checklist saved to {output_path}")


def main():
    """Generate all demo materials"""
    print("Generating demo materials...\n")
    
    create_sample_requests()
    create_expected_responses()
    create_demo_checklist()
    
    print(f"\nAll demo materials generated!")
    print(f"Location: docs/")


if __name__ == "__main__":
    main()