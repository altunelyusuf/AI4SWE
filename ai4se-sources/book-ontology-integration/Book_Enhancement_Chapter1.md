# Chapter 1 Enhancement: Part 1.5

## Domain Engineering Ontology & Semantic Modeling

### Introduction to Formal Domain Engineering

Domain engineering, when enhanced with formal semantic technologies, transforms from an ad-hoc practice into a rigorous, AI-assisted discipline. While Part 1 introduced domain engineering concepts and Part 2-4 covered practical techniques, this section bridges our practical domain discovery methods with the formal ontological foundations that make AI4SE possible.

The integration of formal ontologies with domain engineering enables:
- **Machine-readable domain models** that AI systems can reason over
- **Automated validation** of domain concepts and relationships
- **Semantic consistency** across large, complex domains
- **Intelligent tool support** for domain analysis and evolution
- **Knowledge reuse** across projects and organizations

### What is a Domain Ontology?

A domain ontology is a formal, explicit specification of a shared conceptualization within a specific problem domain. In the AI4SE context, this means:

**Formal**: Uses logic-based languages (OWL, RDF, Turtle) that enable automated reasoning and validation. Unlike informal diagrams or text descriptions, formal ontologies have precise semantics that machines can process.

**Explicit**: All concepts, relationships, constraints, and axioms are clearly defined. Nothing is left implicit or assumed. For example, rather than assuming that "every Order has a Customer," we explicitly state: `Order rdfs:domain :hasCustomer rdfs:range Customer`.

**Shared**: Agreed upon by domain experts, stakeholders, and systems. The ontology serves as a "contract" that ensures all parties understand domain concepts identically.

**Conceptualization**: An abstract model of relevant domain phenomena, focusing on "what exists" and "how things relate" rather than implementation details.

**Ontology Reference**: [:DomainOntology](ai4se:V4_NEW_006)

### Why Semantic Domain Engineering Matters for AI4SE

Traditional domain engineering produces artifacts like UML diagrams, ERDs, or informal documentation. While useful for humans, these artifacts have limitations for AI systems:

1. **Ambiguity**: Natural language descriptions are inherently ambiguous
2. **Inconsistency**: Manual maintenance leads to drift and contradictions
3. **Limited Reasoning**: Tools cannot automatically infer implicit knowledge
4. **Poor Integration**: Different tools use different formats and assumptions
5. **Difficult Validation**: No automated way to verify correctness

Semantic domain engineering addresses these issues by using ontologies as the authoritative source of truth, enabling:

- **LLM-Powered Analysis**: Feed ontologies to LLMs for intelligent querying and explanation
- **Automated Code Generation**: Generate data models, APIs, tests directly from ontology
- **Semantic Search**: Find concepts by meaning, not just keywords
- **Reasoning Services**: Infer implicit relationships and detect inconsistencies
- **Tool Integration**: Universal format understood by AI/SE tools

### The Domain Engineering Ontology Stack

Domain engineering with semantics involves multiple layers:

```
┌─────────────────────────────────────────┐
│     Application Layer                    │
│  (Requirements, Design, Code, Tests)    │
├─────────────────────────────────────────┤
│     Domain Ontology Layer               │
│  (Domain-specific concepts & rules)     │
├─────────────────────────────────────────┤
│     Upper Ontology Layer                │
│  (Generic concepts: Entity, Process)    │
├─────────────────────────────────────────┤
│     Foundation Layer                     │
│  (OWL, RDF, RDFS primitives)           │
└─────────────────────────────────────────┘
```

**Ontology References**: 
- [:DomainEngineeringProcess](ai4se:V4_NEW_001)
- [:DomainConceptualization](ai4se:V4_NEW_008)
- [:DomainModel](ai4se:V4_NEW_005)

### AI-Enhanced Domain Engineering Workflow

Modern domain engineering leverages AI at every stage:

#### Stage 1: Domain Scoping with AI

**Objective**: Define domain boundaries and objectives

**Traditional Approach**: Manual stakeholder interviews, workshops, documentation review

**AI-Enhanced Approach**:
```python
# Using LLM to analyze initial domain documents
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

domain_scoping_prompt = """
Analyze these business documents and identify:
1. Core domain concepts (nouns)
2. Key processes (verbs)  
3. Domain boundaries (what's in/out of scope)
4. Stakeholder roles
5. Success criteria

Documents: {document_text}

Provide structured JSON output.
"""

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    messages=[{
        "role": "user", 
        "content": domain_scoping_prompt.format(document_text=docs)
    }]
)

scope = parse_json_response(response.content[0].text)
```

**Ontology Reference**: [:LLMDomainDiscovery](ai4se:V4_NEW_002)

#### Stage 2: Concept Extraction

**Objective**: Identify key domain concepts and their properties

**AI Techniques**:
- **Named Entity Recognition**: Extract domain entities from text
- **Keyphrase Extraction**: Identify important domain terms
- **Relationship Extraction**: Discover connections between concepts

**Example**:
```python
# Automated concept extraction
extraction_prompt = """
Extract domain concepts from these stakeholder interviews:

Interview 1: {interview_1}
Interview 2: {interview_2}

For each concept, provide:
- Name
- Definition (1 sentence)
- Properties (3-5 key attributes)
- Examples (2-3 concrete instances)

Format as JSON array.
"""

concepts = extract_with_llm(extraction_prompt)

# Output example:
# {
#   "name": "Order",
#   "definition": "A customer request to purchase products",
#   "properties": ["orderNumber", "orderDate", "totalAmount", "status"],
#   "examples": ["Order #12345", "Subscription renewal order"]
# }
```

**Ontology Reference**: [:ConceptExtraction](ai4se:V4_NEW_009)

#### Stage 3: Relationship Mapping

**Objective**: Identify and formalize relationships between concepts

**AI Techniques**:
- **Dependency Parsing**: Analyze sentence structure to find relationships
- **Relation Extraction**: Identify semantic connections
- **Ontology Alignment**: Map to existing ontologies

**Example**:
```python
relationship_prompt = """
Given these concepts: {concepts}

Identify relationships between them:
1. Is-A relationships (taxonomy)
2. Has-A relationships (composition)
3. Associates-With relationships
4. Depends-On relationships

For each relationship:
- Source concept
- Relationship type
- Target concept
- Cardinality (1:1, 1:N, N:M)
- Description

Format as relationship triples.
"""

relationships = extract_relationships(concepts)

# Output: [
#   {"source": "Order", "relation": "hasCustomer", "target": "Customer", "cardinality": "N:1"},
#   {"source": "Order", "relation": "contains", "target": "OrderLine", "cardinality": "1:N"}
# ]
```

**Ontology Reference**: [:RelationshipMapping](ai4se:V4_NEW_010)

#### Stage 4: Ontology Generation

**Objective**: Create formal OWL ontology from extracted knowledge

**Automated Generation**:
```python
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.namespace import SKOS

def generate_ontology(concepts, relationships, domain_name):
    """Generate OWL ontology from extracted concepts and relationships"""
    
    g = Graph()
    
    # Define namespaces
    domain = Namespace(f"http://example.org/{domain_name}#")
    g.bind(domain_name, domain)
    g.bind("skos", SKOS)
    
    # Create ontology header
    ontology_uri = domain[""]
    g.add((ontology_uri, RDF.type, OWL.Ontology))
    g.add((ontology_uri, RDFS.label, Literal(f"{domain_name} Domain Ontology")))
    
    # Generate classes from concepts
    for concept in concepts:
        class_uri = domain[concept['name']]
        g.add((class_uri, RDF.type, OWL.Class))
        g.add((class_uri, RDFS.label, Literal(concept['name'], lang='en')))
        g.add((class_uri, SKOS.definition, Literal(concept['definition'], lang='en')))
        
        # Add examples
        for example in concept.get('examples', []):
            g.add((class_uri, SKOS.example, Literal(example, lang='en')))
    
    # Generate properties from relationships
    for rel in relationships:
        prop_uri = domain[rel['relation']]
        g.add((prop_uri, RDF.type, OWL.ObjectProperty))
        g.add((prop_uri, RDFS.domain, domain[rel['source']]))
        g.add((prop_uri, RDFS.range, domain[rel['target']]))
        g.add((prop_uri, RDFS.label, Literal(rel['relation'], lang='en')))
    
    return g

# Usage
ontology = generate_ontology(concepts, relationships, "ecommerce")
ontology.serialize("ecommerce_ontology.ttl", format="turtle")
```

**Ontology Reference**: [:DomainModel](ai4se:V4_NEW_005)

#### Stage 5: Validation with Stakeholders

**Objective**: Verify ontology accurately represents domain expert knowledge

**AI-Assisted Validation**:
```python
validation_prompt = """
Generate validation questions for this domain ontology:

Ontology summary:
- Classes: {class_list}
- Relationships: {relationship_list}

Create 10 competency questions that should be answerable by querying this ontology.
Format: Natural language question + Expected SPARQL query

Example:
Q: "What products are in order #12345?"
SPARQL: SELECT ?product WHERE {{ :Order12345 :contains ?orderLine . ?orderLine :hasProduct ?product }}
"""

validation_questions = generate_validation_questions(ontology)
```

**Ontology Reference**: [:DomainModelValidation](ai4se:V4_NEW_011)

### Single-Agent vs Multi-Agent Domain Engineering

**Single-Agent Approach** [:SingleAgentDomainEngineering](ai4se:V4_NEW_003)

Uses one comprehensive LLM to handle all domain engineering tasks:

```python
# Single-agent domain engineering
class DomainEngineeringAgent:
    def __init__(self, llm_client):
        self.client = llm_client
        
    def analyze_domain(self, documents, interviews):
        """Complete domain analysis in one pass"""
        prompt = f"""
        You are a domain engineering expert. Perform complete domain analysis:
        
        Documents: {documents}
        Interviews: {interviews}
        
        Output:
        1. Domain scope and boundaries
        2. Core concepts with definitions
        3. Relationships between concepts
        4. Business rules and constraints
        5. Complete domain ontology in Turtle format
        
        Be comprehensive and precise.
        """
        
        return self.client.create_completion(prompt)

agent = DomainEngineeringAgent(claude_client)
result = agent.analyze_domain(docs, interviews)
```

**Benefits**:
- Simple architecture
- Consistent style/terminology
- Fast for small-medium domains
- Lower API costs

**Limitations**:
- May lack specialized expertise for complex domains
- Single point of failure
- Limited parallelization

**When to Use**: Small to medium domains, rapid prototyping, resource constraints

---

**Multi-Agent Approach** [:MultiAgentDomainEngineering](ai4se:V4_NEW_004)

Uses specialized agents working collaboratively:

```python
# Multi-agent domain engineering
class AgentCoordinator:
    def __init__(self):
        self.agents = {
            'scoping': ScopingAgent(),
            'extraction': ConceptExtractionAgent(),
            'mapping': RelationshipMappingAgent(),
            'ontology': OntologyEngineeringAgent(),
            'validation': ValidationAgent()
        }
    
    def run_pipeline(self, inputs):
        """Coordinate multi-agent domain engineering"""
        
        # Stage 1: Scoping
        scope = self.agents['scoping'].define_scope(inputs['documents'])
        
        # Stage 2: Extraction
        concepts = self.agents['extraction'].extract_concepts(
            inputs['documents'], 
            scope
        )
        
        # Stage 3: Mapping
        relationships = self.agents['mapping'].map_relationships(
            concepts,
            inputs['interviews']
        )
        
        # Stage 4: Ontology Generation
        ontology = self.agents['ontology'].generate_ontology(
            concepts,
            relationships,
            scope
        )
        
        # Stage 5: Validation
        validation_results = self.agents['validation'].validate(
            ontology,
            inputs['stakeholder_feedback']
        )
        
        return {
            'ontology': ontology,
            'validation': validation_results,
            'metadata': {'concepts': len(concepts), 'relationships': len(relationships)}
        }

coordinator = AgentCoordinator()
result = coordinator.run_pipeline(domain_inputs)
```

**Benefits**:
- Specialized expertise per task
- Higher quality output
- Parallel execution possible
- Easier to debug and improve individual stages

**Limitations**:
- More complex coordination
- Higher API costs
- Potential consistency issues between agents

**When to Use**: Complex domains, enterprise projects, quality is critical

### Integration with Knowledge Graphs

Domain ontologies serve as schemas for knowledge graphs, which store actual domain data:

```turtle
# Ontology (TBox - Terminological Box)
@prefix ecom: <http://example.org/ecommerce#> .

ecom:Order rdf:type owl:Class ;
    rdfs:label "Order"@en ;
    skos:definition "A customer request to purchase products"@en .

ecom:hasCustomer rdf:type owl:ObjectProperty ;
    rdfs:domain ecom:Order ;
    rdfs:range ecom:Customer .

# Knowledge Graph (ABox - Assertional Box)
ecom:Order12345 rdf:type ecom:Order ;
    ecom:hasCustomer ecom:Customer789 ;
    ecom:orderDate "2025-11-17"^^xsd:date ;
    ecom:totalAmount "299.99"^^xsd:decimal .
```

**Querying with SPARQL**:
```sparql
# Find all orders for a customer
PREFIX ecom: <http://example.org/ecommerce#>

SELECT ?order ?date ?amount
WHERE {
    ?order rdf:type ecom:Order ;
           ecom:hasCustomer ecom:Customer789 ;
           ecom:orderDate ?date ;
           ecom:totalAmount ?amount .
}
ORDER BY DESC(?date)
```

This integration is covered in detail in Chapter 15 (Semantic Technologies).

### Practical Implementation: E-Commerce Domain Ontology

Let's walk through a complete example of creating an e-commerce domain ontology:

**Step 1: Initial Scoping**
```python
# Define scope
scope = {
    'in_scope': [
        'Customer management',
        'Product catalog',
        'Order processing',
        'Payment handling',
        'Inventory tracking'
    ],
    'out_of_scope': [
        'Warehouse logistics',
        'Supplier relationships',
        'Marketing campaigns'
    ]
}
```

**Step 2: Core Concepts**
```python
concepts = [
    {
        'name': 'Customer',
        'definition': 'An individual or organization that purchases products',
        'properties': ['customerId', 'name', 'email', 'address', 'registrationDate']
    },
    {
        'name': 'Product',
        'definition': 'An item available for purchase',
        'properties': ['productId', 'name', 'description', 'price', 'category']
    },
    {
        'name': 'Order',
        'definition': 'A customer request to purchase one or more products',
        'properties': ['orderId', 'orderDate', 'status', 'totalAmount']
    },
    # ... more concepts
]
```

**Step 3: Generate Complete Ontology**
```turtle
@prefix ecom: <http://example.org/ecommerce#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Ontology Header
<http://example.org/ecommerce> rdf:type owl:Ontology ;
    rdfs:label "E-Commerce Domain Ontology"@en ;
    rdfs:comment "Formal model of e-commerce domain concepts and relationships"@en .

# Classes
ecom:Customer rdf:type owl:Class ;
    rdfs:label "Customer"@en ;
    skos:definition "An individual or organization that purchases products"@en ;
    skos:example "John Doe (john@example.com)"@en .

ecom:Product rdf:type owl:Class ;
    rdfs:label "Product"@en ;
    skos:definition "An item available for purchase"@en .

ecom:Order rdf:type owl:Class ;
    rdfs:label "Order"@en ;
    skos:definition "A customer request to purchase products"@en .

ecom:OrderLine rdf:type owl:Class ;
    rdfs:label "Order Line"@en ;
    skos:definition "A single line item within an order"@en .

ecom:Payment rdf:type owl:Class ;
    rdfs:label "Payment"@en ;
    skos:definition "Financial transaction for an order"@en .

# Object Properties
ecom:hasCustomer rdf:type owl:ObjectProperty ;
    rdfs:domain ecom:Order ;
    rdfs:range ecom:Customer ;
    rdfs:label "has customer"@en .

ecom:contains rdf:type owl:ObjectProperty ;
    rdfs:domain ecom:Order ;
    rdfs:range ecom:OrderLine ;
    rdfs:label "contains"@en .

ecom:hasProduct rdf:type owl:ObjectProperty ;
    rdfs:domain ecom:OrderLine ;
    rdfs:range ecom:Product ;
    rdfs:label "has product"@en .

ecom:hasPaid rdf:type owl:ObjectProperty ;
    rdfs:domain ecom:Order ;
    rdfs:range ecom:Payment ;
    rdfs:label "has payment"@en .

# Data Properties
ecom:customerId rdf:type owl:DatatypeProperty ;
    rdfs:domain ecom:Customer ;
    rdfs:range xsd:string .

ecom:orderDate rdf:type owl:DatatypeProperty ;
    rdfs:domain ecom:Order ;
    rdfs:range xsd:dateTime .

ecom:totalAmount rdf:type owl:DatatypeProperty ;
    rdfs:domain ecom:Order ;
    rdfs:range xsd:decimal .

ecom:quantity rdf:type owl:DatatypeProperty ;
    rdfs:domain ecom:OrderLine ;
    rdfs:range xsd:integer .

# Constraints (Axioms)
ecom:Order rdfs:subClassOf [
    rdf:type owl:Restriction ;
    owl:onProperty ecom:hasCustomer ;
    owl:cardinality "1"^^xsd:nonNegativeInteger
] .  # Every order must have exactly one customer

ecom:Order rdfs:subClassOf [
    rdf:type owl:Restriction ;
    owl:onProperty ecom:contains ;
    owl:minCardinality "1"^^xsd:nonNegativeInteger
] .  # Every order must contain at least one order line
```

**Step 4: Validation Queries**
```sparql
# Competency Question 1: Find all orders for a customer
PREFIX ecom: <http://example.org/ecommerce#>

SELECT ?order ?date ?amount
WHERE {
    ?order rdf:type ecom:Order ;
           ecom:hasCustomer ?customer ;
           ecom:orderDate ?date ;
           ecom:totalAmount ?amount .
    ?customer ecom:customerId "CUST123" .
}

# Competency Question 2: Find products in an order
PREFIX ecom: <http://example.org/ecommerce#>

SELECT ?product ?productName ?quantity
WHERE {
    ecom:Order12345 ecom:contains ?orderLine .
    ?orderLine ecom:hasProduct ?product ;
               ecom:quantity ?quantity .
    ?product rdfs:label ?productName .
}
```

### Tools and Technologies

**Ontology Editors** [:OntologyEditor](ai4se:V4_NEW_012):
- **Protégé**: Desktop ontology editor with reasoning and visualization
- **TopBraid Composer**: Enterprise ontology development platform
- **WebVOWL**: Web-based ontology visualization

**Triple Stores**:
- **Apache Jena Fuseki**: SPARQL server with REST API
- **GraphDB**: Enterprise knowledge graph database
- **Blazegraph**: High-performance graph database

**Programming Libraries**:
- **RDFLib** (Python): RDF manipulation and querying
- **OWL API** (Java): OWL ontology processing
- **rdflib.js** (JavaScript): RDF for web applications

### Best Practices

1. **Start Simple**: Begin with core concepts, add complexity iteratively
2. **Use Upper Ontologies**: Leverage standards like FOAF, Dublin Core, Schema.org
3. **Document Everything**: Every class and property needs clear definition and examples
4. **Validate Early**: Test competency questions from day one
5. **Version Control**: Track ontology evolution with Git
6. **Automate**: Use LLMs for initial draft, humans for refinement
7. **Think Reusability**: Design ontologies that can extend to related domains

### Integration with Later Chapters

This foundational understanding of domain ontologies enables:

- **Chapter 15**: Deep dive into semantic technologies and knowledge graphs
- **Chapter 16**: Hybrid systems combining ontologies with LLMs
- **Chapter 2-13**: Domain-specific ontologies for each SE knowledge area
- **Chapter 21-30**: Practical applications in infrastructure, testing, security, etc.

Domain ontologies are not just academic exercises—they're the semantic backbone that makes AI4SE intelligent and maintainable at scale.

---

## Ontology Mapping Table

This section introduced the following ontology concepts:

| Concept | Book Section | Ontology Class | URI |
|---------|--------------|----------------|-----|
| Domain Engineering Process | 1.5 - Workflow | :DomainEngineeringProcess | ai4se:V4_NEW_001 |
| LLM Domain Discovery | 1.5 - Stage 1 | :LLMDomainDiscovery | ai4se:V4_NEW_002 |
| Single-Agent Engineering | 1.5 - Approaches | :SingleAgentDomainEngineering | ai4se:V4_NEW_003 |
| Multi-Agent Engineering | 1.5 - Approaches | :MultiAgentDomainEngineering | ai4se:V4_NEW_004 |
| Domain Model | 1.5 - Stage 4 | :DomainModel | ai4se:V4_NEW_005 |
| Domain Ontology | 1.5 - Core Concept | :DomainOntology | ai4se:V4_NEW_006 |
| Domain Specific Language | 1.5 - Artifacts | :DomainSpecificLanguage | ai4se:V4_NEW_007 |
| Domain Conceptualization | 1.5 - Foundation | :DomainConceptualization | ai4se:V4_NEW_008 |
| Concept Extraction | 1.5 - Stage 2 | :ConceptExtraction | ai4se:V4_NEW_009 |
| Relationship Mapping | 1.5 - Stage 3 | :RelationshipMapping | ai4se:V4_NEW_010 |
| Domain Model Validation | 1.5 - Stage 5 | :DomainModelValidation | ai4se:V4_NEW_011 |
| Ontology Editor | 1.5 - Tools | :OntologyEditor | ai4se:V4_NEW_012 |

**SPARQL Query to Explore Domain Engineering Concepts**:
```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?concept ?label ?definition
WHERE {
  VALUES ?concept { 
    ai4se:V4_NEW_001 ai4se:V4_NEW_002 ai4se:V4_NEW_003 
    ai4se:V4_NEW_004 ai4se:V4_NEW_005 ai4se:V4_NEW_006
  }
  ?concept rdfs:label ?label ;
           skos:definition ?definition .
}
```

---

**Next**: Continue to Part 2 or explore semantic technologies in Chapter 15.

**Cross-References**:
- See Chapter 15 for semantic technology implementation details
- See Chapter 16 for hybrid ontology+LLM architectures
- See Appendix A for complete domain engineering prompt templates
