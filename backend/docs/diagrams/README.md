# Architecture Diagrams

This directory contains visual documentation for the Multi-City Backend System.

## Available Diagrams

### 1. System Overview (`system_overview.md`)
- High-level system architecture
- Component relationships
- Multi-city data flow
- User interaction flow

### 2. API Flow (`api_flow.md`)
- API request/response sequences
- Database interactions
- City data loading process
- Compliance checking flow

### 3. Deployment Architecture (`deployment.md`)
- Docker container structure
- Service dependencies
- Storage volumes
- Network configuration

### 4. Data Model (`data_model.md`)
- Database schema
- Entity relationships
- Primary/foreign keys
- Data constraints

### 5. Testing Flow (`testing_flow.md`)
- Test suite organization
- Test data structure
- Result reporting
- Test orchestration

## How to View Diagrams

### In GitHub/GitLab
The Mermaid diagrams will render automatically in most Git platforms.

### In VS Code
Install the "Mermaid Preview" extension to view diagrams locally.

### Online Mermaid Editor
Copy diagram code to https://mermaid.live/ for interactive viewing.

### Generate PNG/SVG
Use Mermaid CLI to generate image files:
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i system_overview.md -o system_overview.png
```

## Diagram Updates

To regenerate all diagrams:
```bash
python scripts/generate_architecture_diagrams.py
```

Individual diagrams can be updated by modifying the generator script and re-running it.

## Integration with Documentation

These diagrams are referenced in:
- `HANDOVER.md` - Main handover document
- `README.md` - Project overview
- API documentation - Endpoint flows
- Deployment guides - Infrastructure setup
