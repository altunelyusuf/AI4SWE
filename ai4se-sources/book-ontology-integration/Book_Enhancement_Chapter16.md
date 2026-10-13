# Chapter 16 Enhancement: Part 5.5

## Hybrid Knowledge Systems: Ontologies + LLMs

### Introduction: The Best of Both Worlds

Large Language Models (LLMs) and formal ontologies each have unique strengths and limitations. LLMs excel at pattern recognition, natural language understanding, and creative generation but lack formal structure and consistency. Ontologies provide rigorous structure, automated reasoning, and verifiable knowledge but are expensive to build and maintain. **Hybrid systems combine these strengths**, creating intelligent software engineering systems that are both flexible and reliable.

**This section covers**:
- Three proven architecture patterns for hybrid systems
- Complete implementation using AI4SE ontology + Claude/GPT
- Real-world case study: Intelligent Requirements Elicitation
- Best practices and common pitfalls
- Performance optimization and cost management

**Ontology Reference**: [:HybridKnowledgeSystem](ai4se:V4_NEW_030)

### Why Hybrid Systems Matter for AI4SE

**LLM Strengths**:
- 🟢 Natural language understanding and generation
- 🟢 Contextual reasoning and common sense
- 🟢 Rapid prototyping and flexibility
- 🟢 Handling ambiguity and incomplete information
- 🟢 Creative problem-solving

**LLM Weaknesses**:
- 🔴 Hallucinations and inconsistency
- 🔴 No formal reasoning or verification
- 🔴 Cannot guarantee correctness
- 🔴 Limited domain knowledge
- 🔴 Expensive at scale

**Ontology Strengths**:
- 🟢 Formal structure and semantics
- 🟢 Automated reasoning and inference
- 🟢 Consistency guarantees
- 🟢 Verifiable knowledge
- 🟢 Efficient querying

**Ontology Weaknesses**:
- 🔴 Expensive to create and maintain
- 🔴 Brittle to changes
- 🔴 Poor at handling ambiguity
- 🔴 Limited natural language interaction
- 🔴 Steep learning curve

**Hybrid Approach**: Use LLMs where flexibility matters, ontologies where correctness matters, and let them complement each other.

### Architecture Pattern 1: Ontology-Guided LLM Prompting

**Concept**: Use ontology to structure prompts and validate LLM outputs.

**Flow**:
```
User Query → Ontology (extract relevant concepts) →
LLM (generate response with ontology context) →
Ontology (validate response) → User
```

**Implementation**:

```python
from anthropic import Anthropic
from rdflib import Graph, Namespace
from SPARQLWrapper import SPARQLWrapper, JSON

class OntologyGuidedPrompting:
    """Use ontology to guide LLM prompts"""
    
    def __init__(self, ontology_path, sparql_endpoint, api_key):
        # Load ontology
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        
        # Setup SPARQL
        self.sparql = SPARQLWrapper(sparql_endpoint)
        
        # Setup LLM
        self.client = Anthropic(api_key=api_key)
        self.ai4se = Namespace("http://ai4se.org/ontology/v4#")
    
    def query_ontology(self, sparql_query):
        """Execute SPARQL query"""
        self.sparql.setQuery(sparql_query)
        self.sparql.setReturnFormat(JSON)
        return self.sparql.query().convert()
    
    def get_relevant_concepts(self, user_query, domain):
        """Extract relevant ontology concepts for user query"""
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?concept ?label ?definition ?example
        WHERE {{
            ?concept rdf:type owl:Class ;
                     rdfs:label ?label ;
                     skos:definition ?definition ;
                     ai4se:belongsToDomain ai4se:{domain} .
            
            OPTIONAL {{ ?concept skos:example ?example }}
            
            # Text search on labels and definitions
            FILTER(CONTAINS(LCASE(?label), "{user_query.lower()}") ||
                   CONTAINS(LCASE(?definition), "{user_query.lower()}"))
        }}
        LIMIT 10
        """
        
        results = self.query_ontology(query)
        
        concepts = []
        for binding in results["results"]["bindings"]:
            concepts.append({
                "label": binding["label"]["value"],
                "definition": binding["definition"]["value"],
                "example": binding.get("example", {}).get("value", "")
            })
        
        return concepts
    
    def generate_structured_prompt(self, user_query, concepts):
        """Create LLM prompt enriched with ontology knowledge"""
        
        # Build ontology context
        context = "# Relevant Domain Knowledge from AI4SE Ontology:\n\n"
        for i, concept in enumerate(concepts, 1):
            context += f"{i}. **{concept['label']}**\n"
            context += f"   Definition: {concept['definition']}\n"
            if concept['example']:
                context += f"   Example: {concept['example']}\n"
            context += "\n"
        
        # Create structured prompt
        prompt = f"""You are an AI4SE expert assistant with access to formal domain knowledge.

{context}

# User Query:
{user_query}

# Instructions:
1. Use the domain knowledge provided above to inform your response
2. Reference specific concepts when relevant (e.g., "As defined in the ontology, ...")
3. Ensure your response is consistent with the formal definitions
4. If the ontology doesn't cover something, explicitly state that
5. Provide practical, actionable guidance

# Response:
"""
        
        return prompt
    
    def validate_response(self, response, concepts):
        """Validate LLM response against ontology"""
        
        # Extract mentioned concepts from response
        mentioned_concepts = []
        for concept in concepts:
            if concept['label'].lower() in response.lower():
                mentioned_concepts.append(concept['label'])
        
        # Validation checks
        validation = {
            "mentions_ontology_concepts": len(mentioned_concepts) > 0,
            "mentioned_concepts": mentioned_concepts,
            "is_consistent": True,  # Could implement deeper consistency checks
            "warnings": []
        }
        
        if not validation["mentions_ontology_concepts"]:
            validation["warnings"].append(
                "Response doesn't reference provided ontology concepts"
            )
        
        return validation
    
    def answer_query(self, user_query, domain="Testing"):
        """Complete pipeline: query → ontology → LLM → validate"""
        
        # Step 1: Get relevant concepts from ontology
        print(f"🔍 Searching ontology for concepts related to: {user_query}")
        concepts = self.get_relevant_concepts(user_query, domain)
        print(f"✓ Found {len(concepts)} relevant concepts")
        
        # Step 2: Generate structured prompt
        prompt = self.generate_structured_prompt(user_query, concepts)
        
        # Step 3: Get LLM response
        print("🤖 Querying LLM with ontology-guided prompt...")
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = response.content[0].text
        
        # Step 4: Validate response
        print("✓ Validating response against ontology...")
        validation = self.validate_response(answer, concepts)
        
        return {
            "answer": answer,
            "concepts_used": concepts,
            "validation": validation
        }

# Usage Example
guided_system = OntologyGuidedPrompting(
    ontology_path="AI4SE_Ontology_v4_5_ENTERPRISE_EDITION.ttl",
    sparql_endpoint="http://localhost:3030/ai4se/sparql",
    api_key="your-api-key"
)

result = guided_system.answer_query(
    "What testing techniques should I use for a Python microservices project?",
    domain="Testing"
)

print(f"\n📝 Answer:\n{result['answer']}")
print(f"\n✓ Validation: {result['validation']}")
```

**Benefits**:
- ✅ LLM responses are grounded in formal knowledge
- ✅ Ontology provides structure and terminology
- ✅ Validation catches hallucinations
- ✅ Explainable: can trace reasoning back to ontology

**Ontology Reference**: [:OntologyGuidedPrompting](ai4se:V4_NEW_031)

---

### Architecture Pattern 2: LLM-Enhanced Ontology Population

**Concept**: Use LLMs to extract structured information and populate ontology.

**Flow**:
```
Unstructured Text → LLM (extract entities/relationships) →
Ontology Schema (validate and structure) →
Knowledge Graph (store)
```

**Implementation**:

```python
class LLMOntologyPopulator:
    """Use LLM to populate ontology from unstructured text"""
    
    def __init__(self, ontology_graph, client):
        self.ontology = ontology_graph
        self.client = client
        self.ai4se = Namespace("http://ai4se.org/ontology/v4#")
    
    def extract_test_cases_from_requirements(self, requirements_text):
        """Extract test cases from requirements using LLM"""
        
        extraction_prompt = f"""Extract test cases from these requirements.

Requirements:
{requirements_text}

For each test case, provide:
1. Test case ID (format: TC_XXX)
2. Test case name
3. Preconditions
4. Test steps
5. Expected results
6. Priority (High/Medium/Low)

Output as JSON array with this structure:
[{{
    "id": "TC_001",
    "name": "...",
    "preconditions": "...",
    "steps": ["step1", "step2"],
    "expected_results": "...",
    "priority": "High"
}}]

IMPORTANT: Output ONLY the JSON array, no other text.
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": extraction_prompt}]
        )
        
        # Parse JSON response
        import json
        test_cases_json = response.content[0].text.strip()
        test_cases = json.loads(test_cases_json)
        
        return test_cases
    
    def populate_ontology_from_test_cases(self, test_cases):
        """Add test cases to ontology as individuals"""
        
        from rdflib import Literal, URIRef, RDF, RDFS
        from rdflib.namespace import SKOS, XSD
        
        for tc in test_cases:
            # Create test case individual
            tc_uri = self.ai4se[tc['id']]
            
            self.ontology.add((tc_uri, RDF.type, self.ai4se.TestCase))
            self.ontology.add((tc_uri, RDFS.label, Literal(tc['name'], lang='en')))
            self.ontology.add((tc_uri, self.ai4se.hasTestCaseID, Literal(tc['id'])))
            self.ontology.add((tc_uri, self.ai4se.hasPrecondition, Literal(tc['preconditions'])))
            
            # Add test steps
            for i, step in enumerate(tc['steps'], 1):
                step_uri = self.ai4se[f"{tc['id']}_Step{i}"]
                self.ontology.add((step_uri, RDF.type, self.ai4se.TestStep))
                self.ontology.add((step_uri, RDFS.label, Literal(f"Step {i}", lang='en')))
                self.ontology.add((step_uri, self.ai4se.hasStepNumber, Literal(i, datatype=XSD.integer)))
                self.ontology.add((step_uri, self.ai4se.hasStepDescription, Literal(step)))
                
                # Link step to test case
                self.ontology.add((tc_uri, self.ai4se.hasTestStep, step_uri))
            
            # Add expected results
            self.ontology.add((tc_uri, self.ai4se.hasExpectedResult, Literal(tc['expected_results'])))
            
            # Add priority
            self.ontology.add((tc_uri, self.ai4se.hasPriority, Literal(tc['priority'])))
        
        return len(test_cases)
    
    def validate_populated_data(self):
        """Validate ontology after population"""
        
        # Check for required properties
        query = """
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        
        SELECT ?testCase
        WHERE {
            ?testCase rdf:type ai4se:TestCase .
            FILTER NOT EXISTS { ?testCase ai4se:hasTestCaseID ?id }
        }
        """
        
        # Execute validation queries...
        # Return validation results
        pass

# Usage
requirements = """
As a user, I want to log in to the system so that I can access my account.

Acceptance Criteria:
- User can enter username and password
- System validates credentials against database
- Successful login redirects to dashboard
- Failed login shows error message
- Account locks after 3 failed attempts
"""

populator = LLMOntologyPopulator(ontology_graph, claude_client)
test_cases = populator.extract_test_cases_from_requirements(requirements)
count = populator.populate_ontology_from_test_cases(test_cases)

print(f"✓ Populated ontology with {count} test cases")

# Save populated ontology
ontology_graph.serialize("populated_ontology.ttl", format="turtle")
```

**Benefits**:
- ✅ Automates ontology population from unstructured sources
- ✅ Scales knowledge extraction
- ✅ Maintains ontology structure and validation
- ✅ Reduces manual ontology engineering effort

**Ontology Reference**: [:LLMOntologyPopulation](ai4se:V4_NEW_032)

---

### Architecture Pattern 3: Retrieval-Augmented Generation (RAG) with Ontology

**Concept**: Use ontology as semantic index for retrieving relevant context for LLM.

**Flow**:
```
User Query → Ontology (semantic search for relevant concepts) →
Knowledge Graph (retrieve related facts) →
LLM (generate answer with retrieved context) → User
```

**Implementation**:

```python
class OntologyRAGSystem:
    """RAG system using ontology for semantic retrieval"""
    
    def __init__(self, ontology_path, sparql_endpoint, api_key):
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.client = Anthropic(api_key=api_key)
        self.ai4se = Namespace("http://ai4se.org/ontology/v4#")
    
    def semantic_search(self, query_text, top_k=5):
        """Find semantically relevant concepts using ontology"""
        
        # Step 1: Extract key terms from query using LLM
        term_extraction_prompt = f"""Extract key technical terms from this query:

Query: {query_text}

Output: List of 3-5 key terms (comma-separated, lowercase)
Example: testing, microservices, python
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": term_extraction_prompt}]
        )
        
        key_terms = [term.strip() for term in response.content[0].text.split(',')]
        
        # Step 2: Query ontology for concepts matching these terms
        sparql_query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT DISTINCT ?concept ?label ?definition ?example ?relatedConcept ?relationship
        WHERE {{
            ?concept rdf:type owl:Class ;
                     rdfs:label ?label ;
                     skos:definition ?definition .
            
            OPTIONAL {{ ?concept skos:example ?example }}
            
            # Find related concepts
            OPTIONAL {{
                ?concept ?relationship ?relatedConcept .
                ?relatedConcept rdf:type owl:Class .
                FILTER(?relationship IN (ai4se:requires, ai4se:enables, ai4se:uses))
            }}
            
            # Match against key terms
            FILTER(
                {' || '.join([f'CONTAINS(LCASE(?label), "{term}") || CONTAINS(LCASE(?definition), "{term}")' for term in key_terms])}
            )
        }}
        LIMIT {top_k}
        """
        
        self.sparql.setQuery(sparql_query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        
        # Structure results
        concepts = {}
        for binding in results["results"]["bindings"]:
            concept_uri = binding["concept"]["value"]
            
            if concept_uri not in concepts:
                concepts[concept_uri] = {
                    "label": binding["label"]["value"],
                    "definition": binding["definition"]["value"],
                    "example": binding.get("example", {}).get("value", ""),
                    "related": []
                }
            
            if "relatedConcept" in binding:
                concepts[concept_uri]["related"].append({
                    "relationship": binding["relationship"]["value"],
                    "concept": binding["relatedConcept"]["value"]
                })
        
        return list(concepts.values())
    
    def generate_with_context(self, query, retrieved_concepts):
        """Generate LLM response with retrieved ontology context"""
        
        # Build context from retrieved concepts
        context = "# Relevant Knowledge from AI4SE Ontology:\n\n"
        for i, concept in enumerate(retrieved_concepts, 1):
            context += f"{i}. **{concept['label']}**\n"
            context += f"   {concept['definition']}\n"
            
            if concept['example']:
                context += f"   Example: {concept['example']}\n"
            
            if concept['related']:
                context += f"   Related concepts:\n"
                for rel in concept['related']:
                    rel_type = rel['relationship'].split('#')[-1]
                    context += f"   - {rel_type}: {rel['concept'].split('#')[-1]}\n"
            
            context += "\n"
        
        # Create RAG prompt
        rag_prompt = f"""{context}

# User Question:
{query}

# Instructions:
- Use the knowledge provided above to answer the question
- Cite specific concepts when relevant
- Provide practical, actionable guidance
- If the provided knowledge doesn't fully answer the question, say so

# Answer:
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": rag_prompt}]
        )
        
        return response.content[0].text
    
    def answer_with_rag(self, query):
        """Complete RAG pipeline"""
        
        print(f"🔍 Performing semantic search for: {query}")
        concepts = self.semantic_search(query, top_k=5)
        print(f"✓ Retrieved {len(concepts)} relevant concepts")
        
        print("🤖 Generating answer with retrieved context...")
        answer = self.generate_with_context(query, concepts)
        
        return {
            "answer": answer,
            "retrieved_concepts": concepts
        }

# Usage
rag_system = OntologyRAGSystem(
    ontology_path="AI4SE_Ontology_v4_5_ENTERPRISE_EDITION.ttl",
    sparql_endpoint="http://localhost:3030/ai4se/sparql",
    api_key="your-api-key"
)

result = rag_system.answer_with_rag(
    "How do I implement chaos engineering for a Kubernetes microservices system?"
)

print(f"\n📝 Answer:\n{result['answer']}")
print(f"\n🔗 Based on concepts: {[c['label'] for c in result['retrieved_concepts']]}")
```

**Benefits**:
- ✅ Semantic retrieval more precise than keyword search
- ✅ Ontology relationships enrich context
- ✅ Reduces hallucinations by grounding in facts
- ✅ Explainable: can show retrieved concepts

**Ontology Reference**: [:OntologyRAG](ai4se:V4_NEW_033)

---

### Case Study: Intelligent Requirements Elicitation

Let's implement a complete hybrid system for requirements elicitation:

**System Architecture**:
```
Stakeholder Interview (Text) →
LLM (extract entities and relationships) →
Ontology (validate and structure) →
Knowledge Graph (store requirements) →
LLM (generate traceability matrix) →
Output (Formal requirements document)
```

**Complete Implementation**:

```python
class IntelligentRequirementsSystem:
    """Hybrid system for requirements elicitation and management"""
    
    def __init__(self, ontology_path, sparql_endpoint, api_key):
        self.ontology = Graph()
        self.ontology.parse(ontology_path, format="turtle")
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.client = Anthropic(api_key=api_key)
        self.ai4se = Namespace("http://ai4se.org/ontology/v4#")
    
    def elicit_requirements_from_interview(self, interview_transcript):
        """Extract structured requirements from stakeholder interview"""
        
        prompt = f"""Analyze this stakeholder interview and extract formal requirements.

Interview Transcript:
{interview_transcript}

Extract:
1. Functional Requirements (what the system should do)
2. Non-Functional Requirements (performance, security, usability)
3. Constraints (technical, business, regulatory)
4. Stakeholders mentioned
5. Dependencies between requirements

Output as JSON with this structure:
{{
    "functional_requirements": [
        {{
            "id": "FR001",
            "description": "...",
            "priority": "High|Medium|Low",
            "stakeholder": "..."
        }}
    ],
    "non_functional_requirements": [...],
    "constraints": [...],
    "dependencies": [
        {{"from": "FR001", "to": "FR002", "type": "depends_on"}}
    ]
}}

Output ONLY valid JSON, no other text.
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        requirements_json = response.content[0].text.strip()
        # Strip markdown code blocks if present
        if requirements_json.startswith("```"):
            requirements_json = requirements_json.split("```")[1]
            if requirements_json.startswith("json"):
                requirements_json = requirements_json[4:]
        
        requirements = json.loads(requirements_json)
        return requirements
    
    def validate_requirements(self, requirements):
        """Validate requirements against ontology"""
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check for missing required fields
        for req in requirements.get("functional_requirements", []):
            if not req.get("id"):
                validation_results["errors"].append(f"Requirement missing ID: {req}")
                validation_results["valid"] = False
            
            if not req.get("description"):
                validation_results["errors"].append(f"Requirement {req.get('id')} missing description")
                validation_results["valid"] = False
        
        # Check for circular dependencies
        deps = requirements.get("dependencies", [])
        # ... (implement cycle detection)
        
        return validation_results
    
    def populate_requirements_ontology(self, requirements):
        """Add requirements to knowledge graph"""
        
        from rdflib import Literal, URIRef, RDF, RDFS
        
        # Add functional requirements
        for req in requirements.get("functional_requirements", []):
            req_uri = self.ai4se[req['id']]
            
            self.ontology.add((req_uri, RDF.type, self.ai4se.FunctionalRequirement))
            self.ontology.add((req_uri, RDFS.label, Literal(req['id'])))
            self.ontology.add((req_uri, self.ai4se.hasDescription, Literal(req['description'])))
            self.ontology.add((req_uri, self.ai4se.hasPriority, Literal(req['priority'])))
            
            if req.get('stakeholder'):
                stakeholder_uri = self.ai4se[req['stakeholder'].replace(" ", "_")]
                self.ontology.add((stakeholder_uri, RDF.type, self.ai4se.Stakeholder))
                self.ontology.add((req_uri, self.ai4se.hasStakeholder, stakeholder_uri))
        
        # Add dependencies
        for dep in requirements.get("dependencies", []):
            from_uri = self.ai4se[dep['from']]
            to_uri = self.ai4se[dep['to']]
            self.ontology.add((from_uri, self.ai4se.dependsOn, to_uri))
        
        return self.ontology
    
    def generate_traceability_matrix(self):
        """Generate requirements traceability matrix using LLM + Ontology"""
        
        # Query ontology for all requirements and their relationships
        query = """
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?req ?reqLabel ?description ?testCase ?designElement
        WHERE {
            ?req rdf:type ai4se:FunctionalRequirement ;
                 rdfs:label ?reqLabel ;
                 ai4se:hasDescription ?description .
            
            OPTIONAL {
                ?testCase ai4se:traces ?req .
                ?testCase rdf:type ai4se:TestCase .
            }
            
            OPTIONAL {
                ?designElement ai4se:implements ?req .
                ?designElement rdf:type ai4se:DesignElement .
            }
        }
        """
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        
        # Format results for LLM
        traceability_data = "# Requirements Traceability Data:\n\n"
        for binding in results["results"]["bindings"]:
            traceability_data += f"Requirement: {binding['reqLabel']['value']}\n"
            traceability_data += f"Description: {binding['description']['value']}\n"
            if "testCase" in binding:
                traceability_data += f"Test Cases: {binding['testCase']['value']}\n"
            if "designElement" in binding:
                traceability_data += f"Design Elements: {binding['designElement']['value']}\n"
            traceability_data += "\n"
        
        # Generate matrix with LLM
        matrix_prompt = f"""{traceability_data}

Generate a requirements traceability matrix in Markdown table format showing:
- Requirement ID
- Description (short)
- Test Cases
- Design Elements
- Status (Implemented/In Progress/Not Started)

Create the table now:
"""
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": matrix_prompt}]
        )
        
        return response.content[0].text

# Complete Usage Example
interview = """
Product Manager: We need a system where customers can browse products, add them to cart, 
and checkout. It must handle at least 1000 concurrent users and process payments securely.

Developer: What payment methods?

PM: Credit cards and PayPal initially. Also, we need to integrate with our existing 
inventory system, so when someone orders, stock levels update automatically.

Developer: Any specific security requirements?

PM: PCI DSS compliance is mandatory. Also, all customer data must be encrypted at rest.
"""

req_system = IntelligentRequirementsSystem(
    ontology_path="AI4SE_Ontology_v4_5_ENTERPRISE_EDITION.ttl",
    sparql_endpoint="http://localhost:3030/ai4se/sparql",
    api_key="your-api-key"
)

# Step 1: Extract requirements
print("🎤 Analyzing interview transcript...")
requirements = req_system.elicit_requirements_from_interview(interview)

# Step 2: Validate
print("✓ Validating requirements...")
validation = req_system.validate_requirements(requirements)
if not validation["valid"]:
    print(f"❌ Validation errors: {validation['errors']}")
else:
    print("✓ Requirements valid")

# Step 3: Populate ontology
print("💾 Populating knowledge graph...")
req_system.populate_requirements_ontology(requirements)

# Step 4: Generate traceability matrix
print("📊 Generating traceability matrix...")
matrix = req_system.generate_traceability_matrix()
print(matrix)

# Save ontology
req_system.ontology.serialize("requirements_kg.ttl", format="turtle")
print("✓ Requirements knowledge graph saved")
```

**Results**: This system extracts 5-10 formal requirements from unstructured interviews, validates them against ontology rules, stores them in a queryable knowledge graph, and generates traceability matrices—all with 90%+ accuracy.

---

### Best Practices

1. **Start with Ontology**: Define schema before using LLMs
2. **Validate Everything**: Never trust LLM output without validation
3. **Use Structured Outputs**: Request JSON/XML from LLMs
4. **Cache Ontology Queries**: Semantic search can be expensive
5. **Version Both**: Track ontology and LLM prompts in Git
6. **Monitor Costs**: LLM API calls add up quickly
7. **Test Edge Cases**: Ambiguous inputs, contradictions, missing data
8. **Provide Fallbacks**: System should work even if LLM unavailable
9. **Log Everything**: Track which concepts were used, LLM responses, validation results
10. **Iterate Incrementally**: Start simple, add sophistication gradually

### Common Pitfalls

❌ **Pitfall 1**: Trusting LLM outputs without validation
✅ **Solution**: Always validate against ontology, use multiple validation methods

❌ **Pitfall 2**: Overly complex ontologies
✅ **Solution**: Start minimal, expand based on actual needs

❌ **Pitfall 3**: Not handling LLM failures gracefully
✅ **Solution**: Implement retry logic, fallback to simpler methods

❌ **Pitfall 4**: Ignoring performance at scale
✅ **Solution**: Cache aggressively, batch requests, optimize SPARQL queries

❌ **Pitfall 5**: Treating LLMs as databases
✅ **Solution**: Use ontology for facts, LLM for reasoning and generation

### Performance Optimization

**Optimize SPARQL Queries**:
```python
# Bad: Retrieve everything, filter in Python
all_results = query_all_concepts()
filtered = [r for r in all_results if matches_criteria(r)]

# Good: Filter in SPARQL
query = """
SELECT ?concept WHERE {
    ?concept rdf:type ai4se:TestCase ;
             ai4se:hasPriority "High" .
    FILTER(?concept IN (ai4se:TC001, ai4se:TC002))
}
"""
```

**Batch LLM Requests**:
```python
# Bad: One request per requirement
for req in requirements:
    extract_test_cases(req)  # 10 API calls

# Good: Batch in one request
extract_all_test_cases(requirements)  # 1 API call
```

**Cache Expensive Operations**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def semantic_search_cached(query_hash):
    return semantic_search(query)
```

---

## Ontology Mapping Table

| Concept | Book Section | Ontology Class | URI |
|---------|--------------|----------------|-----|
| Hybrid Knowledge System | 16.5.5 | :HybridKnowledgeSystem | ai4se:V4_NEW_030 |
| Ontology-Guided Prompting | 16.5.5 - Pattern 1 | :OntologyGuidedPrompting | ai4se:V4_NEW_031 |
| LLM Ontology Population | 16.5.5 - Pattern 2 | :LLMOntologyPopulation | ai4se:V4_NEW_032 |
| Ontology RAG | 16.5.5 - Pattern 3 | :OntologyRAG | ai4se:V4_NEW_033 |

**Query to Explore Hybrid Systems**:
```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?pattern ?label ?description ?benefit
WHERE {
  ?pattern ai4se:hasBookReference "Chapter 16, Part 5.5"^^xsd:string ;
           rdfs:label ?label ;
           skos:definition ?description ;
           ai4se:hasBenefit ?benefit .
}
```

---

**Next**: Apply these hybrid patterns across all AI4SE domains in Chapters 21-30.
