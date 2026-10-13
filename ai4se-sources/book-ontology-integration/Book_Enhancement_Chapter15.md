# Chapter 15 Enhancement: Part 2.5

## Practical Semantic Technology Implementation for AI4SE

### Introduction: From Theory to Practice

While Parts 1-2 of this chapter covered semantic web fundamentals and knowledge graph theory, this section provides hands-on guidance for implementing semantic technologies in real AI4SE projects. You'll learn to set up a complete semantic stack, write practical SPARQL queries, integrate with development workflows, and optimize performance for production use.

**Key Learning Objectives**:
- Set up a production-ready semantic technology stack
- Write SPARQL queries that solve real software engineering problems
- Integrate semantic technologies into CI/CD pipelines
- Optimize query performance for large knowledge graphs
- Build semantic APIs for tool integration

### Setting Up Your Semantic Stack

A production semantic stack typically consists of four layers:

```
┌─────────────────────────────────────────┐
│  Application Layer (Tools, IDEs, Apps) │
├─────────────────────────────────────────┤
│  Query Layer (SPARQL Endpoint + API)   │
├─────────────────────────────────────────┤
│  Storage Layer (Triple Store)          │
├─────────────────────────────────────────┤
│  Data Layer (Ontologies + KG Data)     │
└─────────────────────────────────────────┘
```

#### Layer 1: Ontology Development Environment

**Install Protégé** (Desktop Ontology Editor):

```bash
# Download from https://protege.stanford.edu/
# Or use Homebrew on macOS
brew install --cask protege

# Launch Protégé
open -a Protégé
```

**Alternative: Visual Studio Code with RDF Extensions**:

```bash
# Install VS Code extensions
code --install-extension stardog-union.vscode-langserver-sparql
code --install-extension stardog-union.vscode-rdf-languages

# Create sample ontology file
cat > ai4se_sample.ttl << 'EOF'
@prefix ai4se: <http://ai4se.org/ontology/v4#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ai4se:TestCase rdf:type owl:Class ;
    rdfs:label "Test Case"@en ;
    skos:definition "A specification of test inputs, execution conditions, and expected results"@en .
EOF
```

#### Layer 2: Triple Store Setup (Apache Jena Fuseki)

**Installation**:

```bash
# Download Fuseki
wget https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.9.0.tar.gz
tar xzf apache-jena-fuseki-4.9.0.tar.gz
cd apache-jena-fuseki-4.9.0

# Start Fuseki server
./fuseki-server --mem /ai4se
```

**Docker Alternative** (Recommended for Development):

```bash
# Pull Fuseki Docker image
docker pull stain/jena-fuseki

# Run Fuseki container
docker run -d \
  --name fuseki \
  -p 3030:3030 \
  -e ADMIN_PASSWORD=admin123 \
  -v $(pwd)/data:/fuseki \
  stain/jena-fuseki

# Access Fuseki UI at http://localhost:3030
```

**Create Dataset**:

```bash
# Via Fuseki UI: http://localhost:3030
# Or via REST API:
curl -X POST \
  'http://localhost:3030/$/datasets' \
  --data 'dbName=ai4se&dbType=mem'
```

#### Layer 3: Load Ontology and Data

**Using Python**:

```python
from rdflib import Graph
import requests

# Load ontology
g = Graph()
g.parse("AI4SE_Ontology_v4_5_ENTERPRISE_EDITION.ttl", format="turtle")

# Upload to Fuseki
fuseki_url = "http://localhost:3030/ai4se/data"
headers = {"Content-Type": "application/x-turtle"}

response = requests.post(
    fuseki_url,
    data=g.serialize(format="turtle"),
    headers=headers,
    auth=("admin", "admin123")
)

print(f"Upload status: {response.status_code}")
```

**Using curl**:

```bash
# Upload ontology to Fuseki
curl -X POST \
  -H "Content-Type: application/x-turtle" \
  --data-binary @AI4SE_Ontology_v4_5_ENTERPRISE_EDITION.ttl \
  http://admin:admin123@localhost:3030/ai4se/data
```

#### Layer 4: Python Client Library

**Install Dependencies**:

```bash
pip install rdflib SPARQLWrapper requests
```

**Basic Python Client**:

```python
from SPARQLWrapper import SPARQLWrapper, JSON

class AI4SEKnowledgeGraph:
    """Client for querying AI4SE knowledge graph"""
    
    def __init__(self, endpoint="http://localhost:3030/ai4se/sparql"):
        self.endpoint = endpoint
        self.sparql = SPARQLWrapper(endpoint)
    
    def query(self, sparql_query):
        """Execute SPARQL query and return results"""
        self.sparql.setQuery(sparql_query)
        self.sparql.setReturnFormat(JSON)
        
        try:
            results = self.sparql.query().convert()
            return results
        except Exception as e:
            print(f"Query error: {e}")
            return None
    
    def get_all_classes(self):
        """Get all OWL classes in the ontology"""
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?class ?label
        WHERE {
            ?class rdf:type owl:Class .
            OPTIONAL { ?class rdfs:label ?label }
        }
        ORDER BY ?label
        """
        return self.query(query)

# Usage
kg = AI4SEKnowledgeGraph()
classes = kg.get_all_classes()
print(f"Found {len(classes['results']['bindings'])} classes")
```

### SPARQL Queries for Software Engineering

Let's explore 10 practical SPARQL queries that solve real SE problems:

#### Query 1: Find All Testing Techniques for a Given Technology

**Use Case**: You're working on a Python project and want to know which testing techniques are applicable.

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?technique ?label ?description ?applicableTool
WHERE {
    ?technique rdf:type ai4se:TestingTechnique ;
               rdfs:label ?label ;
               skos:definition ?description ;
               ai4se:applicableToTechnology "Python" .
    
    OPTIONAL {
        ?technique ai4se:implementedIn ?tool .
        ?tool rdfs:label ?applicableTool .
    }
}
ORDER BY ?label
```

**Python Wrapper**:

```python
def find_testing_techniques(kg, technology):
    """Find testing techniques applicable to a technology"""
    query = f"""
    PREFIX ai4se: <http://ai4se.org/ontology/v4#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?technique ?label ?description
    WHERE {{
        ?technique rdf:type ai4se:TestingTechnique ;
                   rdfs:label ?label ;
                   skos:definition ?description ;
                   ai4se:applicableToTechnology "{technology}" .
    }}
    ORDER BY ?label
    """
    return kg.query(query)

# Usage
techniques = find_testing_techniques(kg, "Python")
for result in techniques['results']['bindings']:
    print(f"- {result['label']['value']}: {result['description']['value']}")
```

#### Query 2: Find Prerequisites for a Technique

**Use Case**: Before implementing DevSecOps, what prerequisites must be in place?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prerequisite ?label ?description ?priority
WHERE {
    ai4se:DevSecOps ai4se:requires ?prerequisite .
    ?prerequisite rdfs:label ?label ;
                  skos:definition ?description .
    
    OPTIONAL { ?prerequisite ai4se:hasPriority ?priority }
}
ORDER BY DESC(?priority)
```

#### Query 3: Find Tools Implementing a Technique

**Use Case**: Which tools can I use for mutation testing?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?tool ?label ?url ?language
WHERE {
    ?tool ai4se:implements ai4se:MutationTesting ;
          rdfs:label ?label .
    
    OPTIONAL { ?tool ai4se:hasToolURL ?url }
    OPTIONAL { ?tool ai4se:supportsLanguage ?language }
}
ORDER BY ?label
```

#### Query 4: Calculate Maturity Level for an Organization

**Use Case**: Assess organization's testing maturity based on practices.

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?dimension ?currentLevel ?score ?nextLevel
WHERE {
    # Organization's current practices
    VALUES ?adoptedPractice {
        ai4se:UnitTesting
        ai4se:ContinuousIntegration
        ai4se:CodeReview
    }
    
    # Find maturity dimension
    ?dimension rdf:type ai4se:MaturityDimension ;
               ai4se:includesPractice ?adoptedPractice .
    
    # Calculate score
    ?dimension ai4se:hasMaturityLevel ?currentLevel .
    ?currentLevel ai4se:hasScore ?score ;
                  ai4se:nextLevel ?nextLevel .
}
GROUP BY ?dimension
ORDER BY ?score
```

#### Query 5: Find Learning Path for a Topic

**Use Case**: I want to learn about microservices. What's the recommended sequence?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?sequence ?topic ?label ?bookChapter
WHERE {
    ai4se:MicroservicesLearningPath ai4se:hasSequence ?sequence ;
                                     ai4se:includesTopic ?topic .
    
    ?topic rdfs:label ?label ;
           ai4se:hasBookReference ?bookChapter .
}
ORDER BY ?sequence
```

#### Query 6: Find Alternatives to a Tool

**Use Case**: Looking for alternatives to Jenkins.

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?alternative ?label ?pros ?cons
WHERE {
    ai4se:Jenkins ai4se:isAlternativeTo ?alternative .
    ?alternative rdfs:label ?label .
    
    OPTIONAL { ?alternative ai4se:hasBenefit ?pros }
    OPTIONAL { ?alternative ai4se:hasLimitation ?cons }
}
```

#### Query 7: Calculate ROI for a Technique

**Use Case**: What's the expected ROI for implementing test automation?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?technique ?initialCost ?annualBenefit ?paybackMonths ?roi
WHERE {
    ?technique rdfs:label "Test Automation"@en ;
               ai4se:hasInitialInvestment ?initialCost ;
               ai4se:hasAnnualBenefit ?annualBenefit ;
               ai4se:hasPaybackPeriod ?paybackMonths ;
               ai4se:hasExpectedROI ?roi .
}
```

#### Query 8: Find Security Vulnerabilities for a Stack

**Use Case**: What security issues should I watch for with Node.js + React?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?vulnerability ?label ?severity ?mitigation
WHERE {
    VALUES ?technology { ai4se:NodeJS ai4se:React }
    
    ?vulnerability ai4se:affectsTechnology ?technology ;
                   rdfs:label ?label ;
                   ai4se:hasSeverity ?severity ;
                   ai4se:hasMitigation ?mitigation .
}
ORDER BY DESC(?severity)
```

#### Query 9: Find Case Studies Similar to My Context

**Use Case**: Find case studies from similar organizations (size, industry, region).

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?caseStudy ?company ?industry ?outcome ?roi
WHERE {
    ?caseStudy rdf:type ai4se:CaseStudy ;
               ai4se:hasOrganizationSize "Medium"@en ;
               ai4se:hasIndustry ?industry ;
               ai4se:hasRegion "Turkey"@en ;
               ai4se:hasCompany ?company ;
               ai4se:hasOutcome ?outcome ;
               ai4se:hasROI ?roi .
}
ORDER BY DESC(?roi)
```

#### Query 10: Discover Integration Patterns

**Use Case**: How can I integrate semantic technologies with my CI/CD pipeline?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?pattern ?label ?description ?example
WHERE {
    ?pattern rdf:type ai4se:IntegrationPattern ;
             ai4se:appliesTo ai4se:SemanticTechnologies ;
             ai4se:integratsWith ai4se:CICD ;
             rdfs:label ?label ;
             skos:definition ?description ;
             ai4se:hasCodeExample ?example .
}
```

### Integrating with Development Workflows

#### CI/CD Integration Pattern

**Jenkins Pipeline Example**:

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Validate Ontology') {
            steps {
                script {
                    // Validate ontology syntax
                    sh '''
                        python3 - << EOF
from rdflib import Graph

try:
    g = Graph()
    g.parse("src/ontology/domain.ttl", format="turtle")
    print(f"✓ Ontology valid: {len(g)} triples")
except Exception as e:
    print(f"✗ Ontology invalid: {e}")
    exit(1)
EOF
                    '''
                }
            }
        }
        
        stage('Reason Over Ontology') {
            steps {
                script {
                    // Check for inconsistencies
                    sh '''
                        python3 - << EOF
from owlready2 import get_ontology

onto = get_ontology("src/ontology/domain.ttl").load()

with onto:
    # Run reasoner
    sync_reasoner_pellet(infer_property_values=True)

# Check for inconsistencies
inconsistent_classes = list(onto.inconsistent_classes())
if inconsistent_classes:
    print(f"✗ Inconsistent classes found: {inconsistent_classes}")
    exit(1)
else:
    print("✓ No inconsistencies found")
EOF
                    '''
                }
            }
        }
        
        stage('Generate Documentation') {
            steps {
                script {
                    // Auto-generate API docs from ontology
                    sh 'python scripts/generate_docs_from_ontology.py'
                }
            }
        }
        
        stage('Deploy to Knowledge Graph') {
            steps {
                script {
                    // Upload to production triple store
                    sh '''
                        curl -X POST \
                          -H "Content-Type: application/x-turtle" \
                          --data-binary @src/ontology/domain.ttl \
                          ${FUSEKI_URL}/data
                    '''
                }
            }
        }
    }
}
```

#### IDE Integration (VS Code Extension)

**package.json**:

```json
{
  "name": "ai4se-semantic-assistant",
  "displayName": "AI4SE Semantic Assistant",
  "description": "Query AI4SE knowledge graph from VS Code",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.60.0"
  },
  "activationEvents": [
    "onCommand:ai4se.findTestingTechniques",
    "onCommand:ai4se.findAlternativeTools"
  ],
  "main": "./extension.js",
  "contributes": {
    "commands": [
      {
        "command": "ai4se.findTestingTechniques",
        "title": "AI4SE: Find Testing Techniques for Current File"
      }
    ]
  }
}
```

**extension.js**:

```javascript
const vscode = require('vscode');
const axios = require('axios');

function activate(context) {
    let disposable = vscode.commands.registerCommand(
        'ai4se.findTestingTechniques',
        async function () {
            // Get current file language
            const editor = vscode.window.activeTextEditor;
            const language = editor.document.languageId;
            
            // Query knowledge graph
            const query = `
                PREFIX ai4se: <http://ai4se.org/ontology/v4#>
                SELECT ?technique ?label WHERE {
                    ?technique rdf:type ai4se:TestingTechnique ;
                               rdfs:label ?label ;
                               ai4se:applicableToTechnology "${language}" .
                }
            `;
            
            const response = await axios.post(
                'http://localhost:3030/ai4se/sparql',
                { query },
                { headers: { 'Accept': 'application/json' } }
            );
            
            const techniques = response.data.results.bindings.map(
                b => b.label.value
            );
            
            // Show results
            vscode.window.showQuickPick(techniques, {
                placeHolder: `Testing techniques for ${language}`
            });
        }
    );
    
    context.subscriptions.push(disposable);
}

module.exports = { activate };
```

### Performance Optimization

#### Strategy 1: Query Optimization

**Bad Query** (Slow):

```sparql
# Retrieves everything, then filters
SELECT ?s ?p ?o
WHERE {
    ?s ?p ?o .
    FILTER(CONTAINS(STR(?o), "Testing"))
}
```

**Good Query** (Fast):

```sparql
# Uses indexed properties and specific patterns
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
SELECT ?technique ?label
WHERE {
    ?technique rdf:type ai4se:TestingTechnique ;
               rdfs:label ?label .
    FILTER(REGEX(?label, "Testing", "i"))
}
```

#### Strategy 2: Indexing

Configure Fuseki for better performance:

```bash
# fuseki-config.ttl
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix tdb2: <http://jena.apache.org/2016/tdb#> .

<#service> rdf:type fuseki:Service ;
    fuseki:name "ai4se" ;
    fuseki:endpoint [ fuseki:operation fuseki:query ] ;
    fuseki:dataset <#dataset> .

<#dataset> rdf:type tdb2:DatasetTDB2 ;
    tdb2:location "data/ai4se" ;
    tdb2:unionDefaultGraph true ;
    # Enable full-text indexing
    text:textIndex <#indexLucene> .

<#indexLucene> a text:TextIndexLucene ;
    text:directory <file:data/lucene> ;
    text:entityMap <#entMap> .
```

#### Strategy 3: Caching

**Python Caching Layer**:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedKnowledgeGraph:
    def __init__(self, endpoint):
        self.kg = AI4SEKnowledgeGraph(endpoint)
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    @lru_cache(maxsize=128)
    def query_with_cache(self, query_hash, query):
        """Execute query with caching"""
        now = datetime.now()
        
        # Check cache
        if query_hash in self.cache:
            cached_result, timestamp = self.cache[query_hash]
            if now - timestamp < self.cache_ttl:
                return cached_result
        
        # Execute query
        result = self.kg.query(query)
        
        # Update cache
        self.cache[query_hash] = (result, now)
        
        return result

# Usage
cached_kg = CachedKnowledgeGraph("http://localhost:3030/ai4se/sparql")
```

#### Strategy 4: Query Rewriting

Automatically optimize queries:

```python
def optimize_sparql_query(query):
    """Rewrite SPARQL query for better performance"""
    
    optimizations = [
        # Push FILTERs down
        (r'}\s*FILTER', ' FILTER ... }'),
        
        # Use specific predicates instead of ?p
        (r'\?s \?p \?o', '?s rdf:type ?type'),
        
        # Limit results early
        (r'WHERE \{', 'WHERE {\n    # Add LIMIT early')
    ]
    
    optimized = query
    for pattern, replacement in optimizations:
        optimized = re.sub(pattern, replacement, optimized)
    
    return optimized
```

### Real-World Implementation Example

**Complete Project Structure**:

```
ai4se-semantic-platform/
├── ontologies/
│   ├── ai4se_core.ttl          # Core AI4SE ontology
│   ├── domain_specific.ttl     # Project domain ontology
│   └── instances.ttl            # Knowledge graph data
├── queries/
│   ├── testing.sparql          # Testing-related queries
│   ├── architecture.sparql     # Architecture queries
│   └── roi.sparql              # ROI calculation queries
├── src/
│   ├── kg_client.py            # Knowledge graph client
│   ├── query_optimizer.py     # Query optimization
│   └── api.py                  # REST API wrapper
├── scripts/
│   ├── validate_ontology.py   # CI/CD validation
│   ├── load_data.py            # Data loader
│   └── generate_docs.py       # Auto-documentation
├── tests/
│   ├── test_queries.py         # Query unit tests
│   └── test_reasoning.py       # Reasoning tests
├── docker-compose.yml          # Fuseki + API
└── README.md
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  fuseki:
    image: stain/jena-fuseki
    ports:
      - "3030:3030"
    environment:
      - ADMIN_PASSWORD=admin123
    volumes:
      - ./data:/fuseki
      - ./ontologies:/ontologies
    command: /jena-fuseki/fuseki-server --mem /ai4se

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - fuseki
    environment:
      - FUSEKI_URL=http://fuseki:3030/ai4se/sparql
    command: uvicorn api:app --host 0.0.0.0 --port 8000

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

**REST API Wrapper** (FastAPI):

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kg_client import AI4SEKnowledgeGraph

app = FastAPI(title="AI4SE Semantic API")
kg = AI4SEKnowledgeGraph()

class QueryRequest(BaseModel):
    technology: str
    
@app.post("/api/testing-techniques")
async def get_testing_techniques(request: QueryRequest):
    """Find testing techniques for a technology"""
    try:
        results = find_testing_techniques(kg, request.technology)
        return {"techniques": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/maturity/{organization_id}")
async def get_maturity_level(organization_id: str):
    """Calculate maturity level for an organization"""
    # Implementation...
    pass

@app.get("/api/roi/{technique}")
async def calculate_roi(technique: str, org_size: str = "medium"):
    """Calculate ROI for implementing a technique"""
    # Implementation...
    pass
```

### Best Practices Summary

1. **Start with Clean Ontologies**: Validate before loading
2. **Index Strategically**: Focus on frequently queried properties
3. **Cache Intelligently**: Cache queries, not data
4. **Monitor Performance**: Log slow queries, optimize iteratively
5. **Version Everything**: Git for ontologies, timestamped KG snapshots
6. **Document Queries**: Every SPARQL query should have comments
7. **Test Reasoning**: Automated tests for inference correctness
8. **Secure Access**: Authentication on SPARQL endpoints
9. **Backup Regularly**: Triple stores are stateful
10. **Plan for Scale**: Design for 10x growth from day one

### Integration with Chapter 16

This practical foundation enables the hybrid ontology+LLM systems covered in Chapter 16, where we combine:
- Ontology's formal structure (this chapter)
- LLM's natural language understanding (Chapter 16)
- Together: Intelligent, explainable AI4SE systems

---

## Ontology Mapping Table

| Concept | Book Section | Ontology Class | URI |
|---------|--------------|----------------|-----|
| Semantic Technology Stack | 15.2.5 | :SemanticTechnologyStack | ai4se:V4_NEW_020 |
| Triple Store | 15.2.5 | :TripleStore | ai4se:V4_NEW_021 |
| SPARQL Endpoint | 15.2.5 | :SPARQLEndpoint | ai4se:V4_NEW_022 |
| Query Optimization | 15.2.5 | :QueryOptimization | ai4se:V4_NEW_023 |
| CI/CD Integration | 15.2.5 | :CICDIntegration | ai4se:V4_NEW_024 |

**Query to Explore Semantic Tech Concepts**:
```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?concept ?label ?definition ?example
WHERE {
  ?concept ai4se:hasBookReference "Chapter 15, Part 2.5"^^xsd:string ;
           rdfs:label ?label ;
           skos:definition ?definition ;
           skos:example ?example .
}
```

---

**Next**: Explore hybrid ontology+LLM systems in Chapter 16, Part 5.5.
