# AI4SE Automation Scripts Collection

**Purpose**: Production-ready automation scripts for common AI4SE workflows  
**Total Scripts**: 10  
**Languages**: Python, Bash, YAML  
**Version**: 1.0

---

## Script 1: Ontology Validator & Consistency Checker

**File**: `validate_ontology.py`

```python
#!/usr/bin/env python3
"""
Validate AI4SE ontology files for consistency and completeness.
"""
from rdflib import Graph
from owlready2 import get_ontology, sync_reasoner_pellet
import sys
from pathlib import Path

def validate_syntax(ontology_file):
    """Check RDF/Turtle syntax validity."""
    try:
        g = Graph()
        g.parse(ontology_file, format="turtle")
        print(f"✓ Syntax valid: {len(g)} triples")
        return True
    except Exception as e:
        print(f"✗ Syntax error: {e}")
        return False

def check_consistency(ontology_file):
    """Run reasoner to check logical consistency."""
    try:
        onto = get_ontology(f"file://{Path(ontology_file).absolute()}").load()
        sync_reasoner_pellet(infer_property_values=True)
        
        inconsistent = list(onto.inconsistent_classes())
        if inconsistent:
            print(f"✗ Found {len(inconsistent)} inconsistent classes:")
            for cls in inconsistent:
                print(f"   - {cls}")
            return False
        else:
            print("✓ Ontology is logically consistent")
            return True
    except Exception as e:
        print(f"✗ Consistency check failed: {e}")
        return False

def check_completeness(ontology_file):
    """Check for missing labels and definitions."""
    g = Graph()
    g.parse(ontology_file, format="turtle")
    
    # Count classes without labels
    query = """
    SELECT (COUNT(?class) as ?count) WHERE {
        ?class a owl:Class .
        FILTER NOT EXISTS { ?class rdfs:label ?label }
    }
    """
    result = list(g.query(query))
    no_label = int(result[0][0])
    
    # Count classes without definitions
    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT (COUNT(?class) as ?count) WHERE {
        ?class a owl:Class .
        FILTER NOT EXISTS { ?class skos:definition ?def }
    }
    """
    result = list(g.query(query))
    no_def = int(result[0][0])
    
    print(f"Classes without labels: {no_label}")
    print(f"Classes without definitions: {no_def}")
    
    return no_label == 0 and no_def == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_ontology.py <ontology.ttl>")
        sys.exit(1)
    
    ontology_file = sys.argv[1]
    
    print(f"Validating {ontology_file}...")
    print("-" * 50)
    
    results = [
        validate_syntax(ontology_file),
        check_consistency(ontology_file),
        check_completeness(ontology_file)
    ]
    
    if all(results):
        print("\n✓ All checks passed!")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)
```

---

## Script 2: Automated Test Case Generator

**File**: `generate_tests.py`

```python
#!/usr/bin/env python3
"""
Generate test cases from requirements using Claude API.
"""
import os
import json
from anthropic import Anthropic
from pathlib import Path

def load_requirements(file_path):
    """Load requirements from JSON file."""
    with open(file_path) as f:
        return json.load(f)

def generate_tests_for_requirement(client, requirement):
    """Generate test cases for single requirement."""
    prompt = f"""Generate test cases for this requirement:

ID: {requirement['id']}
Description: {requirement['description']}
Type: {requirement.get('type', 'functional')}

Generate 5-8 test cases covering:
1. Happy path
2. Error conditions
3. Edge cases
4. Boundary values

Output as JSON array with: test_name, type, steps, expected_result
"""
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response
    content = response.content[0].text
    # Extract JSON from markdown if present
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    
    return json.loads(content.strip())

def main():
    client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    
    # Load requirements
    requirements = load_requirements("requirements.json")
    
    all_tests = {}
    for req in requirements:
        print(f"Generating tests for {req['id']}...")
        tests = generate_tests_for_requirement(client, req)
        all_tests[req['id']] = tests
    
    # Save to file
    output_file = "generated_tests.json"
    with open(output_file, 'w') as f:
        json.dump(all_tests, f, indent=2)
    
    print(f"\n✓ Generated tests saved to {output_file}")
    print(f"Total: {sum(len(tests) for tests in all_tests.values())} test cases")

if __name__ == "__main__":
    main()
```

---

## Script 3: DORA Metrics Calculator

**File**: `calculate_dora.py`

```python
#!/usr/bin/env python3
"""
Calculate DORA metrics from deployment data.
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict

def calculate_deployment_frequency(deployments: List[Dict]) -> str:
    """Calculate deployments per day."""
    if not deployments:
        return "N/A"
    
    first = datetime.fromisoformat(deployments[0]['timestamp'])
    last = datetime.fromisoformat(deployments[-1]['timestamp'])
    days = (last - first).days or 1
    
    freq = len(deployments) / days
    
    if freq >= 1:
        return f"{freq:.1f} per day (Elite)"
    elif freq >= 0.14:  # ~1 per week
        return f"{freq:.2f} per day (High)"
    elif freq >= 0.03:  # ~1 per month
        return f"{freq:.2f} per day (Medium)"
    else:
        return f"{freq:.2f} per day (Low)"

def calculate_lead_time(commits: List[Dict], deployments: List[Dict]) -> str:
    """Calculate lead time for changes."""
    lead_times = []
    
    for commit in commits:
        # Find deployment containing this commit
        commit_time = datetime.fromisoformat(commit['timestamp'])
        for deploy in deployments:
            if commit['sha'] in deploy.get('commits', []):
                deploy_time = datetime.fromisoformat(deploy['timestamp'])
                lead_time = (deploy_time - commit_time).total_seconds() / 3600
                lead_times.append(lead_time)
                break
    
    if not lead_times:
        return "N/A"
    
    avg_hours = sum(lead_times) / len(lead_times)
    
    if avg_hours < 24:
        return f"{avg_hours:.1f} hours (Elite)"
    elif avg_hours < 168:  # 1 week
        return f"{avg_hours/24:.1f} days (High)"
    elif avg_hours < 720:  # 1 month
        return f"{avg_hours/24:.1f} days (Medium)"
    else:
        return f"{avg_hours/24:.1f} days (Low)"

def calculate_mttr(incidents: List[Dict]) -> str:
    """Calculate mean time to restore."""
    if not incidents:
        return "N/A"
    
    recovery_times = []
    for incident in incidents:
        detected = datetime.fromisoformat(incident['detected_at'])
        resolved = datetime.fromisoformat(incident['resolved_at'])
        recovery_times.append((resolved - detected).total_seconds() / 3600)
    
    avg_hours = sum(recovery_times) / len(recovery_times)
    
    if avg_hours < 1:
        return f"{avg_hours*60:.0f} minutes (Elite)"
    elif avg_hours < 24:
        return f"{avg_hours:.1f} hours (High)"
    elif avg_hours < 168:
        return f"{avg_hours/24:.1f} days (Medium)"
    else:
        return f"{avg_hours/24:.1f} days (Low)"

def calculate_change_failure_rate(deployments: List[Dict]) -> str:
    """Calculate percentage of deployments causing failures."""
    if not deployments:
        return "N/A"
    
    failures = sum(1 for d in deployments if d.get('caused_incident', False))
    rate = (failures / len(deployments)) * 100
    
    if rate <= 15:
        return f"{rate:.1f}% (Elite)"
    elif rate <= 20:
        return f"{rate:.1f}% (High)"
    elif rate <= 30:
        return f"{rate:.1f}% (Medium)"
    else:
        return f"{rate:.1f}% (Low)"

def main():
    # Load data
    with open('deployment_data.json') as f:
        data = json.load(f)
    
    deployments = data['deployments']
    commits = data.get('commits', [])
    incidents = data.get('incidents', [])
    
    print("DORA Metrics Report")
    print("=" * 50)
    print(f"Deployment Frequency: {calculate_deployment_frequency(deployments)}")
    print(f"Lead Time for Changes: {calculate_lead_time(commits, deployments)}")
    print(f"Mean Time to Restore: {calculate_mttr(incidents)}")
    print(f"Change Failure Rate: {calculate_change_failure_rate(deployments)}")
    
    # Overall classification
    # ... implement classification logic

if __name__ == "__main__":
    main()
```

---

## Script 4: CI/CD Pipeline Generator

**File**: `generate_pipeline.sh`

```bash
#!/bin/bash
# Generate CI/CD pipeline configuration for different platforms

set -e

PROJECT_NAME="${1:-my-project}"
LANGUAGE="${2:-python}"
PLATFORM="${3:-github}"  # github, gitlab, jenkins

echo "Generating $PLATFORM pipeline for $LANGUAGE project: $PROJECT_NAME"

generate_github_actions() {
    cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest coverage
      
      - name: Run tests
        run: |
          coverage run -m pytest
          coverage report
      
      - name: Security scan
        run: |
          pip install semgrep
          semgrep --config=auto --json > semgrep-results.json
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploying..."
EOF
    echo "✓ Generated .github/workflows/ci.yml"
}

generate_gitlab_ci() {
    cat > .gitlab-ci.yml << 'EOF'
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pip install pytest coverage
    - coverage run -m pytest
    - coverage report

security:
  stage: test
  image: returntocorp/semgrep
  script:
    - semgrep --config=auto --json > semgrep-results.json
  artifacts:
    reports:
      sast: semgrep-results.json

deploy:
  stage: deploy
  only:
    - main
  script:
    - echo "Deploying to production..."
EOF
    echo "✓ Generated .gitlab-ci.yml"
}

generate_jenkinsfile() {
    cat > Jenkinsfile << 'EOF'
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest --junitxml=test-results.xml'
            }
        }
        
        stage('Security') {
            steps {
                sh 'semgrep --config=auto --json > semgrep-results.json'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh './deploy.sh'
            }
        }
    }
    
    post {
        always {
            junit 'test-results.xml'
        }
    }
}
EOF
    echo "✓ Generated Jenkinsfile"
}

# Generate based on platform
case $PLATFORM in
    github)
        mkdir -p .github/workflows
        generate_github_actions
        ;;
    gitlab)
        generate_gitlab_ci
        ;;
    jenkins)
        generate_jenkinsfile
        ;;
    *)
        echo "Unknown platform: $PLATFORM"
        exit 1
        ;;
esac

echo "✓ Pipeline generated successfully!"
```

---

## Script 5: Knowledge Graph Data Importer

**File**: `import_to_kg.py`

```python
#!/usr/bin/env python3
"""
Import structured data into AI4SE knowledge graph.
"""
import json
from SPARQLWrapper import SPARQLWrapper, POST
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

AI4SE = Namespace("http://ai4se.org/ontology/v4#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

def create_case_study_triples(case_study: dict) -> Graph:
    """Convert case study dict to RDF triples."""
    g = Graph()
    g.bind("ai4se", AI4SE)
    g.bind("skos", SKOS)
    
    # Create URIs
    cs_uri = AI4SE[f"CaseStudy_{case_study['id']}"]
    
    # Add triples
    g.add((cs_uri, RDF.type, AI4SE.CaseStudy))
    g.add((cs_uri, RDFS.label, Literal(case_study['name'], lang="en")))
    g.add((cs_uri, AI4SE.hasIndustry, AI4SE[case_study['industry']]))
    g.add((cs_uri, AI4SE.hasROI, Literal(case_study['roi'], datatype=XSD.decimal)))
    g.add((cs_uri, AI4SE.hasInitialInvestment, 
           Literal(case_study['investment'], datatype=XSD.decimal)))
    
    return g

def upload_to_fuseki(graph: Graph, endpoint: str):
    """Upload RDF graph to Fuseki."""
    sparql = SPARQLWrapper(f"{endpoint}/data")
    sparql.setMethod(POST)
    
    # Convert to Turtle
    data = graph.serialize(format='turtle')
    
    # Upload
    sparql.setQuery(f"""
    INSERT DATA {{
        {data}
    }}
    """)
    sparql.query()

def main():
    # Load case studies
    with open('case_studies.json') as f:
        case_studies = json.load(f)
    
    endpoint = "http://localhost:3030/ai4se"
    
    for cs in case_studies:
        print(f"Importing {cs['name']}...")
        graph = create_case_study_triples(cs)
        upload_to_fuseki(graph, endpoint)
    
    print(f"✓ Imported {len(case_studies)} case studies")

if __name__ == "__main__":
    main()
```

---

## Script 6: ROI Report Generator

**File**: `generate_roi_report.py`

```python
#!/usr/bin/env python3
"""
Generate ROI report with visualizations.
"""
import json
import matplotlib.pyplot as plt
from pathlib import Path

def generate_report(data):
    """Generate ROI analysis report."""
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # ROI comparison chart
    case_studies = data['case_studies']
    names = [cs['name'][:20] for cs in case_studies]
    rois = [cs['roi'] for cs in case_studies]
    
    axes[0, 0].barh(names, rois, color='green')
    axes[0, 0].set_xlabel('ROI (%)')
    axes[0, 0].set_title('ROI Comparison')
    axes[0, 0].axvline(x=100, color='r', linestyle='--', label='Break-even')
    
    # Payback period
    paybacks = [cs['payback_months'] for cs in case_studies]
    axes[0, 1].barh(names, paybacks, color='blue')
    axes[0, 1].set_xlabel('Months')
    axes[0, 1].set_title('Payback Period')
    
    # Investment vs Benefit
    investments = [cs['investment'] for cs in case_studies]
    benefits = [cs['annual_benefit'] for cs in case_studies]
    
    x = range(len(names))
    width = 0.35
    axes[1, 0].bar([i - width/2 for i in x], investments, width, label='Investment')
    axes[1, 0].bar([i + width/2 for i in x], benefits, width, label='Benefit')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(names, rotation=45, ha='right')
    axes[1, 0].set_ylabel('Amount')
    axes[1, 0].set_title('Investment vs Annual Benefit')
    axes[1, 0].legend()
    
    # ROI distribution
    axes[1, 1].hist(rois, bins=10, edgecolor='black')
    axes[1, 1].set_xlabel('ROI (%)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('ROI Distribution')
    axes[1, 1].axvline(x=sum(rois)/len(rois), color='r', 
                        linestyle='--', label='Mean')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig('roi_report.png', dpi=300)
    print("✓ Generated roi_report.png")
    
    # Generate text report
    with open('roi_report.txt', 'w') as f:
        f.write("AI4SE ROI Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Case Studies: {len(case_studies)}\n")
        f.write(f"Average ROI: {sum(rois)/len(rois):.1f}%\n")
        f.write(f"Average Payback: {sum(paybacks)/len(paybacks):.1f} months\n")
        f.write("\nDetailed Results:\n")
        for cs in case_studies:
            f.write(f"\n{cs['name']}:\n")
            f.write(f"  ROI: {cs['roi']}%\n")
            f.write(f"  Payback: {cs['payback_months']} months\n")
            f.write(f"  Investment: ${cs['investment']:,}\n")
    
    print("✓ Generated roi_report.txt")

if __name__ == "__main__":
    with open('roi_data.json') as f:
        data = json.load(f)
    generate_report(data)
```

---

## Scripts 7-10: Quick Utilities

### Script 7: Ontology Statistics

**File**: `ontology_stats.sh`

```bash
#!/bin/bash
# Extract statistics from ontology file

ONTOLOGY=${1:-ontology.ttl}

echo "Ontology Statistics for $ONTOLOGY"
echo "=================================="

# Count classes
CLASSES=$(grep -c "rdf:type owl:Class" $ONTOLOGY)
echo "Classes: $CLASSES"

# Count properties
OBJ_PROPS=$(grep -c "rdf:type owl:ObjectProperty" $ONTOLOGY)
DATA_PROPS=$(grep -c "rdf:type owl:DatatypeProperty" $ONTOLOGY)
echo "Object Properties: $OBJ_PROPS"
echo "Data Properties: $DATA_PROPS"

# Count individuals
INDIVIDUALS=$(grep -c "rdf:type owl:NamedIndividual" $ONTOLOGY)
echo "Individuals: $INDIVIDUALS"

# Count triples (approximate)
TRIPLES=$(grep -c " \." $ONTOLOGY)
echo "Total Triples (approx): $TRIPLES"
```

### Script 8: Batch Test Runner

**File**: `run_all_tests.sh`

```bash
#!/bin/bash
# Run all tests with coverage

set -e

echo "Running AI4SE Test Suite"
echo "========================"

# Unit tests
echo "→ Running unit tests..."
pytest tests/unit --cov=src --cov-report=html

# Integration tests
echo "→ Running integration tests..."
pytest tests/integration

# Mutation tests
echo "→ Running mutation tests..."
mutmut run --paths-to-mutate=src/

# Contract tests
echo "→ Running contract tests..."
npm run test:contract

echo "✓ All tests passed!"
```

### Script 9: Deployment Health Check

**File**: `health_check.sh`

```bash
#!/bin/bash
# Check health of deployed services

SERVICES=("api:8000" "fuseki:3030" "grafana:3000")

echo "Health Check Report"
echo "==================="

for SERVICE in "${SERVICES[@]}"; do
    NAME=$(echo $SERVICE | cut -d: -f1)
    PORT=$(echo $SERVICE | cut -d: -f2)
    
    if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
        echo "✓ $NAME is healthy"
    else
        echo "✗ $NAME is DOWN"
    fi
done
```

### Script 10: Backup & Restore Knowledge Graph

**File**: `backup_kg.sh`

```bash
#!/bin/bash
# Backup Fuseki knowledge graph

ENDPOINT="http://localhost:3030/ai4se"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

mkdir -p $BACKUP_DIR

echo "Backing up knowledge graph..."

# Export all graphs
curl -X GET "$ENDPOINT/data?default" \
    -H "Accept: text/turtle" \
    > "$BACKUP_DIR/default_graph.ttl"

echo "✓ Backup saved to $BACKUP_DIR"

# Create restore script
cat > "$BACKUP_DIR/restore.sh" << EOF
#!/bin/bash
curl -X POST "$ENDPOINT/data?default" \\
    -H "Content-Type: text/turtle" \\
    --data-binary @default_graph.ttl
EOF

chmod +x "$BACKUP_DIR/restore.sh"
```

---

## Usage Guide

### Quick Start

```bash
# 1. Validate ontology
./validate_ontology.py ontology.ttl

# 2. Generate tests from requirements
./generate_tests.py

# 3. Calculate DORA metrics
./calculate_dora.py

# 4. Generate CI/CD pipeline
./generate_pipeline.sh my-project python github

# 5. Import data to knowledge graph
./import_to_kg.py

# 6. Generate ROI report
./generate_roi_report.py

# 7. Get ontology stats
./ontology_stats.sh ontology.ttl

# 8. Run all tests
./run_all_tests.sh

# 9. Check deployment health
./health_check.sh

# 10. Backup knowledge graph
./backup_kg.sh
```

### Integration Example

```bash
# Complete workflow
./validate_ontology.py ontology.ttl && \
./import_to_kg.py && \
./generate_tests.py && \
./run_all_tests.sh && \
./calculate_dora.py && \
./generate_roi_report.py
```

---

**Script Collection Version**: 1.0  
**Total Scripts**: 10  
**Languages**: Python, Bash  
**Last Updated**: November 17, 2025
