# AI4SE Ontology - SPARQL Query Examples and Usage Guide

## Introduction

This document provides practical SPARQL queries for the AI4SE Ontology, demonstrating how to extract valuable insights about AI-enhanced software engineering practices, tools, and processes.

---

## 1. Basic Exploration Queries

### 1.1 Find All AI Systems for Software Engineering
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?system ?label ?description
WHERE {
  ?system rdfs:subClassOf* ai4se:AI4SESSystem .
  ?system rdfs:label ?label .
  OPTIONAL { ?system rdfs:comment ?description }
}
ORDER BY ?label
```

### 1.2 List All AI-Enhanced Software Processes
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?process ?label ?automationLevel
WHERE {
  ?process rdfs:subClassOf* ai4se:AIEnhancedProcess .
  ?process rdfs:label ?label .
  OPTIONAL { ?process ai4se:automationLevel ?automationLevel }
}
ORDER BY DESC(?automationLevel)
```

---

## 2. Lifecycle Analysis Queries

### 2.1 AI Support Across SDLC Phases
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?phase ?phaseLabel (COUNT(?aiSystem) as ?aiSystemCount)
WHERE {
  ?phase rdfs:subClassOf o4se:LifecyclePhase .
  ?phase rdfs:label ?phaseLabel .
  ?aiSystem ai4se:supportsPhase ?phase .
}
GROUP BY ?phase ?phaseLabel
ORDER BY DESC(?aiSystemCount)
```

### 2.2 Requirements Engineering AI Capabilities
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX ai: <http://example.org/o4ai#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?capability ?capLabel ?system ?sysLabel
WHERE {
  ?system rdfs:subClassOf* ai4se:RequirementsIntelligence .
  ?system rdfs:label ?sysLabel .
  ?system ai4se:usesAICapability ?capability .
  ?capability rdfs:label ?capLabel .
}
ORDER BY ?capability
```

### 2.3 Testing Phase AI Enhancement Analysis
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?testingTool ?label ?capability ?defectReduction
WHERE {
  ?testingTool rdfs:subClassOf* ai4se:TestingIntelligence .
  ?testingTool rdfs:label ?label .
  ?testingTool ai4se:usesAICapability ?capability .
  OPTIONAL { ?testingTool ai4se:defectReductionRate ?defectReduction }
}
ORDER BY DESC(?defectReduction)
```

---

## 3. Tool and Infrastructure Queries

### 3.1 AI-Powered Development Tools by Category
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?category ?tool ?toolLabel ?example
WHERE {
  ?category rdfs:subClassOf ai4se:AIPoweredTool .
  ?tool rdfs:subClassOf ?category .
  ?tool rdfs:label ?toolLabel .
  OPTIONAL { ?tool skos:example ?example }
  FILTER(?category != ?tool)
}
ORDER BY ?category ?tool
```

### 3.2 Tool Integration Network
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?tool1 ?tool1Label ?tool2 ?tool2Label
WHERE {
  ?tool1 ai4se:integratesWith ?tool2 .
  ?tool1 rdfs:label ?tool1Label .
  ?tool2 rdfs:label ?tool2Label .
}
ORDER BY ?tool1Label
```

### 3.3 Infrastructure Requirements for AI Tools
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?tool ?toolLabel ?infrastructure ?computeCapacity ?storageCapacity
WHERE {
  ?tool rdfs:subClassOf* ai4se:AIPoweredTool .
  ?tool rdfs:label ?toolLabel .
  ?tool ai4se:requiresInfrastructure ?infrastructure .
  OPTIONAL { ?infrastructure ai4se:computeCapacity ?computeCapacity }
  OPTIONAL { ?infrastructure ai4se:storageCapacity ?storageCapacity }
}
ORDER BY DESC(?computeCapacity)
```

---

## 4. Methodology and Practice Queries

### 4.1 AI-Enhanced Agile Practices
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?practice ?practiceLabel ?aiSystem ?effectiveness
WHERE {
  ?practice rdfs:subClassOf* o4se:AgilePractice .
  ?aiSystem ai4se:enhancesPractice ?practice .
  ?practice rdfs:label ?practiceLabel .
  OPTIONAL { ?practice ai4se:practiceEffectiveness ?effectiveness }
}
ORDER BY DESC(?effectiveness)
```

### 4.2 DevOps AI Integration Points
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?devopsTool ?label ?process ?metric ?improvement
WHERE {
  ?devopsTool rdfs:subClassOf* ai4se:IntelligentDevOpsSystem .
  ?devopsTool rdfs:label ?label .
  ?devopsTool ai4se:enhances ?process .
  ?devopsTool ai4se:improvesMetric ?metric .
  OPTIONAL { ?devopsTool ai4se:phaseEfficiencyGain ?improvement }
}
ORDER BY DESC(?improvement)
```

### 4.3 Project Management AI Capabilities
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?pmSystem ?label ?capability ?accuracyScore
WHERE {
  ?pmSystem rdfs:subClassOf* ai4se:ProjectIntelligenceSystem .
  ?pmSystem rdfs:label ?label .
  ?pmSystem ai4se:usesAICapability ?capability .
  OPTIONAL { ?pmSystem ai4se:accuracyScore ?accuracyScore }
  FILTER(?accuracyScore > 0.8)
}
ORDER BY DESC(?accuracyScore)
```

---

## 5. Quality and Metrics Queries

### 5.1 AI System Quality Scores
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX qc: <http://example.org/quality#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?system ?label ?accuracyScore ?confidenceLevel
WHERE {
  ?system rdfs:subClassOf* ai4se:AI4SESSystem .
  ?system rdfs:label ?label .
  OPTIONAL { ?system ai4se:accuracyScore ?accuracyScore }
  OPTIONAL { ?system ai4se:confidenceLevel ?confidenceLevel }
  FILTER(?accuracyScore > 0.9)
}
ORDER BY DESC(?accuracyScore)
```

### 5.2 Code Quality Analysis Tools
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?analyzer ?label ?capability ?metric
WHERE {
  ?analyzer rdfs:subClassOf* ai4se:CodeQualityAnalyzer .
  ?analyzer rdfs:label ?label .
  ?analyzer ai4se:usesAICapability ?capability .
  ?analyzer ai4se:providesMetric ?metric .
}
ORDER BY ?analyzer
```

### 5.3 Technical Debt Detection Systems
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?system ?label ?debtType ?estimationAccuracy
WHERE {
  ?system rdfs:subClassOf* ai4se:TechnicalDebtAnalyzer .
  ?system rdfs:label ?label .
  ?system ai4se:analyzes ?debtType .
  OPTIONAL { ?system ai4se:accuracyScore ?estimationAccuracy }
}
ORDER BY DESC(?estimationAccuracy)
```

---

## 6. Integration Pattern Queries

### 6.1 AI-SE Integration Patterns
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX meta: <http://example.org/ontology-engineering#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?pattern ?patternLabel ?description ?competencyQuestion
WHERE {
  ?pattern rdfs:subClassOf* ai4se:IntegrationPattern .
  ?pattern rdfs:label ?patternLabel .
  OPTIONAL { ?pattern rdfs:comment ?description }
  OPTIONAL { ?pattern meta:hasCompetencyQuestion ?competencyQuestion }
}
ORDER BY ?pattern
```

### 6.2 Automation vs Augmentation Patterns
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?process ?processLabel ?pattern 
       (COALESCE(?automationLevel, 0) as ?automation)
WHERE {
  ?process rdfs:subClassOf* ai4se:AIEnhancedProcess .
  ?process rdfs:label ?processLabel .
  OPTIONAL { ?process ai4se:automationLevel ?automationLevel }
  BIND(
    IF(?automationLevel > 80, "Automation",
      IF(?automationLevel > 50, "Hybrid", "Augmentation")
    ) as ?pattern
  )
}
ORDER BY DESC(?automation)
```

---

## 7. Advanced Analytics Queries

### 7.1 AI Impact on Development Velocity
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?phase ?phaseLabel 
       (AVG(?efficiency) as ?avgEfficiency)
       (MAX(?efficiency) as ?maxEfficiency)
       (COUNT(?aiSystem) as ?toolCount)
WHERE {
  ?phase rdfs:subClassOf* o4se:LifecyclePhase .
  ?phase rdfs:label ?phaseLabel .
  ?aiSystem ai4se:supportsPhase ?phase .
  ?aiSystem ai4se:phaseEfficiencyGain ?efficiency .
}
GROUP BY ?phase ?phaseLabel
HAVING(?avgEfficiency > 20)
ORDER BY DESC(?avgEfficiency)
```

### 7.2 Tool Ecosystem Complexity
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?ecosystem (COUNT(?tool) as ?toolCount) 
       (COUNT(?integration) as ?integrationCount)
WHERE {
  ?ecosystem rdfs:subClassOf* ai4se:ToolEcosystem .
  ?tool ai4se:belongsToEcosystem ?ecosystem .
  OPTIONAL { ?tool ai4se:integratesWith ?otherTool }
  BIND(?tool as ?integration)
}
GROUP BY ?ecosystem
ORDER BY DESC(?toolCount)
```

### 7.3 AI Capability Distribution
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX ai: <http://example.org/o4ai#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?capability ?capLabel (COUNT(?system) as ?usageCount)
WHERE {
  ?capability rdfs:subClassOf* ai4se:SECapability .
  ?capability rdfs:label ?capLabel .
  ?system ai4se:usesAICapability ?capability .
}
GROUP BY ?capability ?capLabel
ORDER BY DESC(?usageCount)
```

---

## 8. Recommendation Queries

### 8.1 Recommend AI Tools for Specific Process
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?tool ?toolLabel ?accuracy ?automation
WHERE {
  # Parameter: Replace with specific process
  BIND(o4se:TestingProcess as ?targetProcess)
  
  ?tool ai4se:enhances ?targetProcess .
  ?tool rdfs:label ?toolLabel .
  OPTIONAL { ?tool ai4se:accuracyScore ?accuracy }
  OPTIONAL { ?tool ai4se:automationLevel ?automation }
}
ORDER BY DESC(?accuracy) DESC(?automation)
LIMIT 5
```

### 8.2 Find Compatible Tool Combinations
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?tool1 ?tool2 ?tool3 ?commonInfra
WHERE {
  ?tool1 ai4se:integratesWith ?tool2 .
  ?tool2 ai4se:integratesWith ?tool3 .
  ?tool1 ai4se:requiresInfrastructure ?commonInfra .
  ?tool2 ai4se:requiresInfrastructure ?commonInfra .
  ?tool3 ai4se:requiresInfrastructure ?commonInfra .
  FILTER(?tool1 != ?tool3)
}
LIMIT 10
```

---

## 9. Validation and Compliance Queries

### 9.1 Check Ontology Completeness
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?phase (COUNT(?aiSystem) as ?coverage)
WHERE {
  ?phase rdfs:subClassOf o4se:LifecyclePhase .
  OPTIONAL { ?aiSystem ai4se:supportsPhase ?phase }
}
GROUP BY ?phase
HAVING(?coverage = 0)
```

### 9.2 Verify Quality Scores
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX qc: <http://example.org/quality#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?dimension ?score ?evidence
WHERE {
  ?assessment rdfs:subClassOf ai4se:QualityAssessment .
  ?assessment qc:measuresCriterion ?dimension .
  ?assessment qc:hasScore ?score .
  ?assessment qc:evidencedBy ?evidence .
  FILTER(?score >= 98)
}
ORDER BY DESC(?score)
```

---

## 10. Federation and Integration Queries

### 10.1 Cross-Ontology Integration Query
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX ai: <http://example.org/o4ai#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?aiConcept ?seConcept ?integration
WHERE {
  ?integration rdfs:subClassOf* ai4se:AI4SESSystem .
  ?integration rdfs:subClassOf* ?aiConcept .
  ?integration rdfs:subClassOf* ?seConcept .
  FILTER(STRSTARTS(STR(?aiConcept), STR(ai:)))
  FILTER(STRSTARTS(STR(?seConcept), STR(o4se:)))
}
LIMIT 20
```

### 10.2 Meta-Ontology Pattern Usage
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX meta: <http://example.org/ontology-engineering#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?pattern ?usage ?implementation
WHERE {
  ?pattern rdfs:subClassOf meta:Pattern .
  ?implementation rdfs:subClassOf* ?pattern .
  ?implementation rdfs:subClassOf* ai4se:IntegrationPattern .
  BIND(COUNT(?implementation) as ?usage)
}
GROUP BY ?pattern
ORDER BY DESC(?usage)
```

---

## Usage Guidelines

### Query Execution Tips
1. **Performance**: Add LIMIT clauses for large result sets
2. **Filtering**: Use FILTER for specific conditions
3. **Optional Data**: Use OPTIONAL for non-mandatory properties
4. **Aggregation**: Use GROUP BY with COUNT, AVG, MAX, MIN
5. **Sorting**: Use ORDER BY for organized results

### Common Prefixes
```sparql
PREFIX ai4se: <http://www.semanticweb.org/ontologies/2025/AI4SE#>
PREFIX o4se: <http://www.semanticweb.org/ontologies/2025/O4SE#>
PREFIX ai: <http://example.org/o4ai#>
PREFIX meta: <http://example.org/ontology-engineering#>
PREFIX qc: <http://example.org/quality#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```

### Query Templates

#### Find Subclasses Template
```sparql
SELECT ?subclass ?label
WHERE {
  ?subclass rdfs:subClassOf* <TARGET_CLASS> .
  ?subclass rdfs:label ?label .
}
```

#### Property Analysis Template
```sparql
SELECT ?subject ?property ?value
WHERE {
  ?subject <TARGET_PROPERTY> ?value .
  ?subject rdf:type ?class .
}
```

#### Integration Analysis Template
```sparql
SELECT ?source ?target ?relation
WHERE {
  ?source <RELATION_PROPERTY> ?target .
  ?source rdf:type ?sourceType .
  ?target rdf:type ?targetType .
}
```

---

## Conclusion

These SPARQL queries demonstrate the rich querying capabilities of the AI4SE ontology, enabling:
- Discovery of AI tools and capabilities
- Analysis of AI impact on SE processes
- Tool integration and compatibility checking
- Quality and performance assessment
- Recommendation generation
- Compliance verification

The queries can be adapted and combined to answer complex questions about AI-enhanced software engineering practices.

---

*End of SPARQL Query Documentation*
