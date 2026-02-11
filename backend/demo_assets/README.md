# Demo Assets

## Overview
12 demo prompts (3 per city) for testing and demonstration.

## Cities Covered
- **Mumbai**: Apartment, Office, Tower
- **Pune**: Villa, Tech Park, Row Houses
- **Ahmedabad**: Traditional House, Commercial Complex, Residential Building
- **Nashik**: Resort, School, Hospital

## Generated Files
- `demo_summary.json` - Complete summary with all specs
- `demo_<city>_<n>.json` - Individual spec files (12 total)

## Usage

### Generate Demo Assets
```bash
cd backend
python generate_demo.py
```

### View Summary
```bash
cat demo_assets/demo_summary.json
```

## Prompts

### Mumbai
1. Design a 3BHK apartment with modern kitchen and balcony
2. Create a commercial office space with parking for 20 cars
3. Build a residential tower with 15 floors and rooftop amenities

### Pune
1. Design a villa with garden, swimming pool, and 4 bedrooms
2. Create a tech park with open workspace and cafeteria
3. Build a row house complex with 8 units and common parking

### Ahmedabad
1. Design a traditional house with courtyard and 3 bedrooms
2. Create a commercial complex with retail shops and offices
3. Build a residential building with 6 floors and lift

### Nashik
1. Design a vineyard resort with 10 cottages and restaurant
2. Create a school building with playground and 20 classrooms
3. Build a hospital with emergency wing and 50 beds
