"""
Generate system architecture diagrams
Creates visual documentation for handover
"""

from pathlib import Path


def generate_system_overview_diagram():
    """Generate system overview diagram in Mermaid format"""
    
    diagram = """
```mermaid
graph TB
    User[User Request<br/>Natural Language Prompt]
    
    User --> Backend[Multi-City Backend<br/>Port 8000<br/>FastAPI Application]
    
    Backend --> Generate[Generate<br/>Design Spec]
    Backend --> Evaluate[Evaluate<br/>Design Quality]
    Backend --> Iterate[Iterate<br/>Improvements]
    Backend --> Switch[Switch<br/>Components]
    
    Backend --> Cities[Multi-City Loader<br/>Mumbai, Pune<br/>Ahmedabad, Nashik]
    Backend --> Compliance[Compliance<br/>Checker]
    
    Cities --> Mumbai[Mumbai<br/>DCPR 2034<br/>FSI: 1.33]
    Cities --> Pune[Pune<br/>DCR 2017<br/>FSI: 1.5]
    Cities --> Ahmedabad[Ahmedabad<br/>AUDA DCR 2020<br/>FSI: 1.8]
    Cities --> Nashik[Nashik<br/>NMC DCR 2015<br/>FSI: 1.2]
    
    Generate --> Response[Unified Response]
    Evaluate --> Response
    Iterate --> Response
    Switch --> Response
    Compliance --> Response
    
    Response --> User
    
    style Backend fill:#32b8c6,stroke:#1d7480,stroke-width:3px,color:#fff
    style Cities fill:#5e8240,stroke:#3d5629,stroke-width:2px,color:#fff
    style Compliance fill:#a85f2f,stroke:#6b3d1f,stroke-width:2px,color:#fff
    style Response fill:#21808d,stroke:#165259,stroke-width:3px,color:#fff
```
"""

    output_path = Path("docs/diagrams/system_overview.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# System Overview Diagram\n\n")
        f.write(diagram)

    print(f"System overview diagram saved to {output_path}")


def generate_api_flow_diagram():
    """Generate API flow diagram"""
    
    diagram = """
```mermaid
sequenceDiagram
    participant User
    participant Backend
    participant CityLoader
    participant Database
    
    User->>Backend: POST /api/v1/generate
    Note over Backend: Extract city from request
    
    Backend->>CityLoader: get_city_rules(city)
    CityLoader-->>Backend: DCR rules, FSI, setbacks
    
    Backend->>Backend: Generate design spec
    Backend->>Database: Store spec
    Database-->>Backend: spec_id
    
    Backend->>Backend: Apply city constraints
    Backend->>Backend: Validate compliance
    
    Backend-->>User: Design spec + compliance
    
    User->>Backend: GET /api/v1/cities/Mumbai/rules
    Backend->>CityLoader: get_city_rules(Mumbai)
    CityLoader-->>Backend: Mumbai DCR rules
    Backend-->>User: Mumbai rules (FSI: 1.33)
    
    User->>Backend: POST /api/v1/compliance/check
    Backend->>Backend: Validate against city rules
    Backend-->>User: Compliance report
```
"""

    output_path = Path("docs/diagrams/api_flow.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# API Flow Diagram\n\n")
        f.write(diagram)

    print(f"API flow diagram saved to {output_path}")


def generate_deployment_diagram():
    """Generate deployment architecture diagram"""
    
    diagram = """
```mermaid
graph TB
    subgraph Docker Compose Stack
        Backend[Multi-City Backend<br/>Port 8000<br/>FastAPI + Multi-City]
        DB[(PostgreSQL<br/>Port 5432<br/>Data Storage)]
        Redis[(Redis<br/>Port 6379<br/>Caching)]
        Nginx[Nginx<br/>Port 80/443<br/>Reverse Proxy]
        
        Backend --> DB
        Backend --> Redis
        Nginx --> Backend
    end
    
    subgraph Multi-City Data
        Mumbai[Mumbai<br/>DCPR 2034]
        Pune[Pune<br/>DCR 2017]
        Ahmedabad[Ahmedabad<br/>AUDA DCR 2020]
        Nashik[Nashik<br/>NMC DCR 2015]
    end
    
    Backend --> Mumbai
    Backend --> Pune
    Backend --> Ahmedabad
    Backend --> Nashik
    
    subgraph Storage Volumes
        BackendData[Backend Data<br/>Specs & Reports]
        DBData[Database Data<br/>Persistent Storage]
        Logs[Application Logs<br/>Monitoring]
    end
    
    Backend -.-> BackendData
    DB -.-> DBData
    Backend -.-> Logs
    
    subgraph External Access
        Users[Users/Frontend<br/>HTTP Requests]
        API[API Consumers<br/>Third-party Apps]
    end
    
    Users --> Nginx
    API --> Nginx
    
    style Backend fill:#32b8c6,stroke:#1d7480,stroke-width:3px,color:#fff
    style DB fill:#c01f2f,stroke:#801520,stroke-width:2px,color:#fff
    style Redis fill:#a85f2f,stroke:#6b3d1f,stroke-width:2px,color:#fff
    style Nginx fill:#5e8240,stroke:#3d5629,stroke-width:2px,color:#fff
```
"""

    output_path = Path("docs/diagrams/deployment.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# Deployment Architecture Diagram\n\n")
        f.write(diagram)

    print(f"Deployment diagram saved to {output_path}")


def generate_data_model_diagram():
    """Generate data model diagram"""
    
    diagram = """
```mermaid
erDiagram
    CITY {
        string name PK
        string dcr_version
        float fsi_base
        float setback_front
        float setback_rear
        string parking_ratio
        float max_height
        json source_documents
        json typical_use_cases
    }
    
    SPEC {
        string spec_id PK
        string user_id
        string project_id
        text prompt
        json spec_json
        int spec_version
        datetime created_at
        datetime updated_at
        string city FK
    }
    
    EVALUATION {
        string eval_id PK
        string spec_id FK
        string user_id
        int score
        text notes
        datetime ts
    }
    
    ITERATION {
        string iter_id PK
        string spec_id FK
        json before_spec
        json after_spec
        text feedback
        datetime ts
    }
    
    USER {
        string id PK
        string username
        string email
        string hashed_password
        boolean is_active
        datetime created_at
    }
    
    CITY ||--o{ SPEC : "applies_to"
    SPEC ||--o{ EVALUATION : "evaluated_by"
    SPEC ||--o{ ITERATION : "iterated_from"
    USER ||--o{ SPEC : "creates"
    USER ||--o{ EVALUATION : "evaluates"
```
"""

    output_path = Path("docs/diagrams/data_model.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# Data Model Diagram\n\n")
        f.write(diagram)

    print(f"Data model diagram saved to {output_path}")


def generate_testing_flow_diagram():
    """Generate testing flow diagram"""
    
    diagram = """
```mermaid
graph TB
    subgraph Test Suites
        DataTests[Data Validation Tests<br/>validate_city_data.py<br/>100% Pass]
        APITests[API Endpoint Tests<br/>validate_api_endpoints.py<br/>Server Required]
        SmokeTests[Smoke Tests<br/>mock_smoke_tests.py<br/>100% Pass]
        IntegrationTests[Integration Tests<br/>integration_tests.py<br/>E2E Workflows]
        LoadTests[Load Tests<br/>load_tests.py<br/>Performance]
    end
    
    subgraph Test Data
        Mumbai[Mumbai Test Data<br/>FSI: 1.33<br/>DCPR 2034]
        Pune[Pune Test Data<br/>FSI: 1.5<br/>DCR 2017]
        Ahmedabad[Ahmedabad Test Data<br/>FSI: 1.8<br/>AUDA DCR 2020]
        Nashik[Nashik Test Data<br/>FSI: 1.2<br/>NMC DCR 2015]
    end
    
    DataTests --> Mumbai
    DataTests --> Pune
    DataTests --> Ahmedabad
    DataTests --> Nashik
    
    subgraph Test Results
        Reports[Test Reports<br/>JSON Format<br/>reports/validation/]
        Summary[Test Summary<br/>Success Rates<br/>Performance Metrics]
    end
    
    DataTests --> Reports
    SmokeTests --> Reports
    IntegrationTests --> Reports
    LoadTests --> Reports
    
    Reports --> Summary
    
    subgraph Test Runner
        RunAll[run_all_tests.py<br/>Orchestrates All Tests<br/>Generates Summary]
    end
    
    RunAll --> DataTests
    RunAll --> SmokeTests
    RunAll --> IntegrationTests
    RunAll --> LoadTests
    
    style DataTests fill:#32b8c6,stroke:#1d7480,stroke-width:2px,color:#fff
    style SmokeTests fill:#5e8240,stroke:#3d5629,stroke-width:2px,color:#fff
    style Reports fill:#a85f2f,stroke:#6b3d1f,stroke-width:2px,color:#fff
    style RunAll fill:#c01f2f,stroke:#801520,stroke-width:3px,color:#fff
```
"""

    output_path = Path("docs/diagrams/testing_flow.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("# Testing Flow Diagram\n\n")
        f.write(diagram)

    print(f"Testing flow diagram saved to {output_path}")


def main():
    """Generate all diagrams"""
    print("Generating architecture diagrams...\n")
    
    generate_system_overview_diagram()
    generate_api_flow_diagram()
    generate_deployment_diagram()
    generate_data_model_diagram()
    generate_testing_flow_diagram()
    
    print(f"\nAll diagrams generated!")
    print(f"Location: docs/diagrams/")


if __name__ == "__main__":
    main()