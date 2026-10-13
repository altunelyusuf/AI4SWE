# Chapter 8: Software Architecture
## Part 3: Formal Architecture Modeling with Ontologies

**Prerequisites**: Understanding of architecture patterns (Parts 1-2)  
**Ontology Module**: Ontology_Module_Architecture_Patterns.ttl  
**Estimated Reading Time**: 30 minutes

---

## Introduction

Traditional architecture documentation suffers from ambiguity, inconsistency, and lack of machine-readability. An architecture described in PowerPoint slides or Word documents cannot be:
- **Queried** programmatically
- **Validated** for consistency
- **Reasoned** over for implicit relationships
- **Integrated** with other systems automatically

This section introduces **formal architecture modeling** using OWL ontologies, where architectural concepts, patterns, and decisions become **first-class semantic entities** that machines can process, validate, and reason about.

### Why Formalize Architecture?

**Benefits**:
1. **Automated Validation**: Check if architecture satisfies constraints
2. **Pattern Selection**: Query which patterns fit your requirements
3. **Impact Analysis**: Trace effects of architectural changes
4. **Tool Integration**: Generate code, configs, documentation automatically
5. **Knowledge Preservation**: Capture rationale in machine-readable form

---

## Architecture Ontology Overview

### Core Concepts

The architecture ontology defines 31 classes across three major categories:

```turtle
# Architectural Styles (8 classes)
:ArchitecturalStyle rdf:type owl:Class .
├── :MicroservicesArchitecture
├── :MonolithicArchitecture
├── :EventDrivenArchitecture
├── :ServerlessArchitecture
├── :LayeredArchitecture
├── :HexagonalArchitecture
└── ... more styles

# Design Patterns (15 classes)
:DesignPattern rdf:type owl:Class .
├── :CreationalPattern
│   ├── :SingletonPattern
│   ├── :FactoryPattern
│   └── :BuilderPattern
├── :StructuralPattern
│   ├── :AdapterPattern
│   └── :DecoratorPattern
└── :BehavioralPattern
    ├── :ObserverPattern
    └── :StrategyPattern

# Cloud-Native Patterns (8 classes)
:CloudNativePattern rdf:type owl:Class .
├── :CircuitBreakerPattern
├── :RetryPattern
├── :BulkheadPattern
├── :SagaPattern
└── :StranglerFigPattern
```

### Key Relationships

```turtle
:requiresTechnique rdf:type owl:ObjectProperty ;
    rdfs:label "requires technique"@en ;
    rdfs:domain :ArchitecturalStyle ;
    rdfs:range :Technique .

:appropriateFor rdf:type owl:DatatypeProperty ;
    rdfs:label "appropriate for"@en ;
    rdfs:domain :ArchitecturalStyle ;
    rdfs:range xsd:string .

:hasBenefit rdf:type owl:DatatypeProperty ;
    rdfs:label "has benefit"@en ;
    rdfs:range xsd:string .

:hasChallenge rdf:type owl:DatatypeProperty ;
    rdfs:label "has challenge"@en ;
    rdfs:range xsd:string .
```

---

## Querying Architectures with SPARQL

### Query 1: Find Appropriate Architecture for Requirements

Given requirements (scalability, microservices), find matching styles:

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?style ?label ?benefit WHERE {
    ?style rdf:type ai4se:ArchitecturalStyle ;
           rdfs:label ?label ;
           ai4se:hasBenefit ?benefit .
    
    # Must support independent deployment
    FILTER(CONTAINS(LCASE(?benefit), "independent deployment") ||
           CONTAINS(LCASE(?benefit), "scalability"))
}
```

**Result**:
```
style                              label                        benefit
ai4se:MicroservicesArchitecture    "Microservices Architecture" "Independent deployment and scaling"
ai4se:EventDrivenArchitecture      "Event-Driven Architecture"  "High scalability"
```

### Query 2: Get Design Patterns for Specific Problem

Need to create objects without specifying exact class?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?pattern ?definition ?example WHERE {
    ?pattern rdfs:subClassOf* ai4se:CreationalPattern ;
             rdfs:label ?label ;
             skos:definition ?definition .
    
    OPTIONAL { ?pattern skos:example ?example }
    
    FILTER(CONTAINS(LCASE(?definition), "without specifying exact class"))
}
```

**Result**: Returns `FactoryPattern` with its definition and examples.

### Query 3: Find Cloud-Native Patterns for Resilience

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?pattern ?label ?benefit WHERE {
    ?pattern rdf:type ai4se:CloudNativePattern ;
             rdfs:label ?label ;
             ai4se:hasBenefit ?benefit .
    
    FILTER(CONTAINS(LCASE(?benefit), "failure") ||
           CONTAINS(LCASE(?benefit), "resilience"))
}
```

**Result**: Returns `CircuitBreakerPattern`, `BulkheadPattern`, `RetryPattern`.

---

## Formalizing Your Architecture

### Step 1: Define System Architecture

```turtle
# Your system's architecture instance
:MyECommerceSystem rdf:type ai4se:System ;
    rdfs:label "E-Commerce Platform"@en ;
    :hasArchitecturalStyle ai4se:MicroservicesArchitecture ;
    :hasPattern ai4se:CircuitBreakerPattern ;
    :hasPattern ai4se:SagaPattern ;
    :hasQualityAttribute ai4se:Scalability ;
    :hasQualityAttribute ai4se:Reliability .
```

### Step 2: Define Components

```turtle
:OrderService rdf:type ai4se:Microservice ;
    rdfs:label "Order Service"@en ;
    :partOf :MyECommerceSystem ;
    :implementsPattern ai4se:CircuitBreakerPattern ;
    :dependsOn :PaymentService ;
    :dependsOn :InventoryService ;
    :exposesAPI :OrderAPI .

:PaymentService rdf:type ai4se:Microservice ;
    rdfs:label "Payment Service"@en ;
    :partOf :MyECommerceSystem ;
    :implementsPattern ai4se:RetryPattern ;
    :exposesAPI :PaymentAPI .
```

### Step 3: Define Dependencies and Constraints

```turtle
# Constraint: Circuit breaker required for external dependencies
:ExternalDependencyRule rdf:type owl:Restriction ;
    owl:onProperty :dependsOn ;
    owl:someValuesFrom :ExternalService ;
    rdfs:subClassOf [
        rdf:type owl:Restriction ;
        owl:onProperty :implementsPattern ;
        owl:hasValue ai4se:CircuitBreakerPattern
    ] .
```

---

## Python Integration: Architecture Validator

### Automated Architecture Validation

```python
from rdflib import Graph, Namespace, RDF, RDFS
from owlready2 import get_ontology, sync_reasoner_pellet

AI4SE = Namespace("http://ai4se.org/ontology/v4#")

class ArchitectureValidator:
    """Validate architecture against ontology constraints."""
    
    def __init__(self, ontology_path: str):
        self.onto = get_ontology(f"file://{ontology_path}").load()
        self.graph = Graph()
        self.graph.parse(ontology_path, format="turtle")
    
    def validate_consistency(self) -> bool:
        """Check logical consistency with reasoner."""
        try:
            sync_reasoner_pellet(infer_property_values=True)
            inconsistent = list(self.onto.inconsistent_classes())
            
            if inconsistent:
                print(f"❌ Found {len(inconsistent)} inconsistencies:")
                for cls in inconsistent:
                    print(f"   - {cls}")
                return False
            else:
                print("✅ Architecture is logically consistent")
                return True
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
    
    def check_pattern_requirements(self, architecture_uri: str) -> list:
        """Check if architecture satisfies pattern requirements."""
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        
        SELECT ?requiredTechnique WHERE {{
            <{architecture_uri}> ai4se:hasArchitecturalStyle ?style .
            ?style ai4se:requiresTechnique ?requiredTechnique .
            
            # Check if technique is implemented
            FILTER NOT EXISTS {{
                <{architecture_uri}> ai4se:implementsTechnique ?requiredTechnique .
            }}
        }}
        """
        
        results = self.graph.query(query)
        missing = [str(row.requiredTechnique) for row in results]
        
        if missing:
            print(f"⚠️  Missing required techniques:")
            for tech in missing:
                print(f"   - {tech}")
        else:
            print("✅ All required techniques implemented")
        
        return missing
    
    def suggest_patterns(self, requirements: dict) -> list:
        """Suggest patterns based on requirements."""
        
        # Build filter conditions
        filters = []
        if requirements.get('scalability'):
            filters.append('CONTAINS(LCASE(?benefit), "scal")')
        if requirements.get('resilience'):
            filters.append('CONTAINS(LCASE(?benefit), "fail")')
        if requirements.get('performance'):
            filters.append('CONTAINS(LCASE(?benefit), "perform")')
        
        filter_str = ' || '.join(filters) if filters else 'true'
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?pattern ?label ?benefit WHERE {{
            ?pattern rdf:type ?patternType ;
                     rdfs:label ?label ;
                     ai4se:hasBenefit ?benefit .
            
            # Pattern types
            ?patternType rdfs:subClassOf* ai4se:DesignPattern .
            
            FILTER({filter_str})
        }}
        ORDER BY ?label
        """
        
        results = self.graph.query(query)
        patterns = [
            {
                'pattern': str(row.pattern),
                'label': str(row.label),
                'benefit': str(row.benefit)
            }
            for row in results
        ]
        
        print(f"✅ Found {len(patterns)} matching patterns:")
        for p in patterns:
            print(f"   - {p['label']}: {p['benefit']}")
        
        return patterns
    
    def generate_architecture_report(self, architecture_uri: str) -> str:
        """Generate comprehensive architecture report."""
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?style ?styleLabel ?pattern ?patternLabel ?quality WHERE {{
            <{architecture_uri}> ai4se:hasArchitecturalStyle ?style ;
                                  ai4se:hasPattern ?pattern ;
                                  ai4se:hasQualityAttribute ?quality .
            ?style rdfs:label ?styleLabel .
            ?pattern rdfs:label ?patternLabel .
        }}
        """
        
        results = self.graph.query(query)
        
        report = f"# Architecture Report\n\n"
        report += f"**System**: {architecture_uri}\n\n"
        
        # Extract unique values
        styles = set()
        patterns = set()
        qualities = set()
        
        for row in results:
            styles.add(str(row.styleLabel))
            patterns.add(str(row.patternLabel))
            qualities.add(str(row.quality))
        
        report += f"## Architectural Style\n"
        for style in styles:
            report += f"- {style}\n"
        
        report += f"\n## Patterns Implemented\n"
        for pattern in patterns:
            report += f"- {pattern}\n"
        
        report += f"\n## Quality Attributes\n"
        for quality in qualities:
            report += f"- {quality}\n"
        
        return report


# Usage Example
if __name__ == "__main__":
    validator = ArchitectureValidator("Ontology_Module_Architecture_Patterns.ttl")
    
    # Validate consistency
    validator.validate_consistency()
    
    # Check microservices requirements
    validator.check_pattern_requirements("http://ai4se.org/MyECommerceSystem")
    
    # Suggest patterns for requirements
    requirements = {
        'scalability': True,
        'resilience': True,
        'performance': True
    }
    validator.suggest_patterns(requirements)
    
    # Generate report
    report = validator.generate_architecture_report(
        "http://ai4se.org/MyECommerceSystem"
    )
    print(report)
```

**Output Example**:
```
✅ Architecture is logically consistent
✅ All required techniques implemented
✅ Found 5 matching patterns:
   - Circuit Breaker Pattern: Prevents cascade failures
   - Retry Pattern: Automatically retries failed operations
   - Bulkhead Pattern: Isolates resources
   - Observer Pattern: Defines one-to-many dependency
   - Strategy Pattern: Defines family of algorithms

# Architecture Report

**System**: http://ai4se.org/MyECommerceSystem

## Architectural Style
- Microservices Architecture

## Patterns Implemented
- Circuit Breaker Pattern
- Saga Pattern

## Quality Attributes
- Scalability
- Reliability
```

---

## Advanced Use Cases

### Use Case 1: Automated Pattern Selection

When designing a new system, query the ontology for appropriate patterns:

```python
def select_architecture(
    system_type: str,
    scale: str,
    team_size: int,
    complexity: str
) -> dict:
    """Select architecture based on system characteristics."""
    
    query = f"""
    PREFIX ai4se: <http://ai4se.org/ontology/v4#>
    
    SELECT ?style ?label ?benefit ?challenge WHERE {{
        ?style rdf:type ai4se:ArchitecturalStyle ;
               rdfs:label ?label ;
               ai4se:appropriateFor ?appropriateFor ;
               ai4se:hasBenefit ?benefit ;
               ai4se:hasChallenge ?challenge .
        
        FILTER(CONTAINS(LCASE(?appropriateFor), LCASE("{system_type}")))
    }}
    """
    
    # Execute query and rank results
    # Return recommended architecture with rationale
```

### Use Case 2: Architecture Migration Planning

Planning to migrate from monolith to microservices? Query the ontology:

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

# Find migration patterns
SELECT ?pattern ?label ?description WHERE {
    ?pattern rdf:type ai4se:CloudNativePattern ;
             rdfs:label ?label ;
             skos:definition ?description .
    
    # Look for migration-related patterns
    FILTER(CONTAINS(LCASE(?label), "strangler") ||
           CONTAINS(LCASE(?description), "legacy") ||
           CONTAINS(LCASE(?description), "migrat"))
}
```

**Result**: Returns `StranglerFigPattern` with guidance on gradual migration.

### Use Case 3: Quality Attribute Analysis

Which architecture best satisfies your quality requirements?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?style (COUNT(?qa) as ?qualityCount) WHERE {
    ?style rdf:type ai4se:ArchitecturalStyle .
    
    # Count quality attributes addressed
    {
        ?style ai4se:hasBenefit ?benefit .
        FILTER(CONTAINS(LCASE(?benefit), "scal")) # Scalability
        BIND("scalability" as ?qa)
    } UNION {
        ?style ai4se:hasBenefit ?benefit .
        FILTER(CONTAINS(LCASE(?benefit), "reliab")) # Reliability
        BIND("reliability" as ?qa)
    } UNION {
        ?style ai4se:hasBenefit ?benefit .
        FILTER(CONTAINS(LCASE(?benefit), "maintain")) # Maintainability
        BIND("maintainability" as ?qa)
    }
}
GROUP BY ?style
ORDER BY DESC(?qualityCount)
```

---

## Integration with Architecture Decision Records (ADRs)

### Linking ADRs to Ontology

```turtle
# Architecture Decision Record as RDF
:ADR_001 rdf:type :ArchitectureDecision ;
    rdfs:label "Use Microservices Architecture"@en ;
    :decidedOn "2024-01-15"^^xsd:date ;
    :decidedBy :ChiefArchitect ;
    :adoptsPattern ai4se:MicroservicesArchitecture ;
    :rationale "Need independent deployment and scaling"@en ;
    :status "Accepted"@en ;
    :consequences [
        :consequenceType "Positive"@en ;
        :description "Enables independent team velocity"@en
    ] ;
    :consequences [
        :consequenceType "Negative"@en ;
        :description "Increased operational complexity"@en
    ] .

# Link to mitigation patterns
:ADR_001 :requiresPattern ai4se:CircuitBreakerPattern ;
         :requiresPattern ai4se:ServiceMesh .
```

Query all decisions for a pattern:
```sparql
SELECT ?adr ?rationale ?status WHERE {
    ?adr :adoptsPattern ai4se:MicroservicesArchitecture ;
         :rationale ?rationale ;
         :status ?status .
}
```

---

## Generating Documentation from Ontology

### Automated Architecture Diagram Generation

```python
def generate_c4_diagram(architecture_uri: str) -> str:
    """Generate PlantUML C4 diagram from ontology."""
    
    query = f"""
    PREFIX ai4se: <http://ai4se.org/ontology/v4#>
    
    SELECT ?component ?componentLabel ?dependency WHERE {{
        ?component ai4se:partOf <{architecture_uri}> ;
                   rdfs:label ?componentLabel .
        OPTIONAL {{ ?component ai4se:dependsOn ?dependency }}
    }}
    """
    
    # Execute query
    results = graph.query(query)
    
    # Generate PlantUML
    uml = "@startuml\n"
    uml += "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n\n"
    
    # Add containers
    for row in results:
        uml += f"Container({row.componentLabel}, \"{row.componentLabel}\", \"Microservice\")\n"
    
    # Add relationships
    for row in results:
        if row.dependency:
            uml += f"Rel({row.componentLabel}, {row.dependency}, \"Uses\")\n"
    
    uml += "@enduml"
    
    return uml
```

---

## Case Study: Netflix Architecture in Ontology

```turtle
:NetflixArchitecture rdf:type ai4se:System ;
    rdfs:label "Netflix Streaming Platform"@en ;
    :hasArchitecturalStyle ai4se:MicroservicesArchitecture ;
    :hasArchitecturalStyle ai4se:EventDrivenArchitecture ;
    :hasPattern ai4se:CircuitBreakerPattern ;
    :hasPattern ai4se:BulkheadPattern ;
    :usesTool ai4se:Hystrix ;
    :hasQualityAttribute ai4se:Scalability ;
    :hasQualityAttribute ai4se:Reliability ;
    :servesUsers "200000000"^^xsd:integer ;
    :hasService :NetflixAPI ;
    :hasService :RecommendationEngine ;
    :hasService :VideoStreamingService .

# Specific microservice
:RecommendationEngine rdf:type ai4se:Microservice ;
    rdfs:label "Recommendation Engine"@en ;
    :partOf :NetflixArchitecture ;
    :implementsPattern ai4se:CircuitBreakerPattern ;
    :uses ai4se:MachineLearning ;
    :processesEventsPerSecond "100000"^^xsd:integer .
```

Query Netflix's patterns:
```sparql
SELECT ?pattern ?label WHERE {
    ai4se:NetflixArchitecture ai4se:hasPattern ?pattern .
    ?pattern rdfs:label ?label .
}
```

---

## Summary

Formal architecture modeling with ontologies transforms architecture from **documentation artifact** to **queryable knowledge**:

✅ **Pattern Selection**: Query which patterns fit your requirements  
✅ **Validation**: Automated consistency checking  
✅ **Impact Analysis**: Trace dependencies and changes  
✅ **Documentation**: Auto-generate diagrams and reports  
✅ **Decision Tracking**: Link ADRs to patterns formally  
✅ **Knowledge Reuse**: Learn from historical architectures  

This approach is invaluable for:
- **Architects** designing complex systems
- **Teams** validating architecture decisions
- **Organizations** maintaining architecture knowledge
- **Tools** generating code from architecture

---

## Exercises

1. **Modeling Exercise**: Formalize your system's architecture in RDF
2. **Query Exercise**: Write SPARQL to find architectures with similar characteristics
3. **Validation Exercise**: Create OWL constraints for your architecture rules
4. **Integration Exercise**: Generate PlantUML diagrams from your ontology
5. **Analysis Exercise**: Query the ontology to compare microservices vs. monolith

---

## References

- **Ontology Module**: `Ontology_Module_Architecture_Patterns.ttl` (31 classes, V4_NEW_160–V4_NEW_190)
- **Design Patterns**: Gang of Four patterns formalized
- **Cloud-Native**: CNCF patterns included
- **Quality Attributes**: ISO 25010 standard aligned

**Next**: Chapter 9 covers architecture evaluation—using the ontology to assess architecture quality systematically.
