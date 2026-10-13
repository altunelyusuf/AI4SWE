# Chapter 26: Data Engineering
## Part 3: Data Pipeline Ontology

**Prerequisites**: Data engineering basics (Parts 1-2)  
**Ontology Module**: Ontology_Module_Data_Engineering.ttl  
**Estimated Reading Time**: 25 minutes

---

## Introduction

Data pipelines grow complex: ETL/ELT, streaming, batch, ML pipelines, data quality checks, lineage tracking. Traditional pipeline definitions (Airflow DAGs, SQL scripts) lack:
- **Semantic understanding** of data flow
- **Automated lineage** tracking
- **Quality validation** against schemas
- **Impact analysis** for changes

**Data Pipeline Ontology** formalizes data concepts, enabling semantic data engineering where machines understand data relationships, not just move bytes.

---

## Data Ontology Structure (23 Classes)

```turtle
# Pipeline Types
:DataPipeline rdf:type owl:Class .
├── :ETLPipeline       # Extract, Transform, Load
├── :ELTPipeline       # Extract, Load, Transform
├── :StreamingPipeline # Real-time processing
└── :MLPipeline        # ML model training

# Data Storage
:DataStorage rdf:type owl:Class .
├── :DataWarehouse     # OLAP, analytics
├── :DataLake          # Raw, schema-on-read
└── :DataLakehouse     # Hybrid approach

# Data Quality
:DataQuality rdf:type owl:Class .
├── :DataValidation    # Check correctness
└── :DataProfiling     # Statistical analysis

# ML Engineering
:MLPipeline rdf:type owl:Class .
├── :FeatureStore      # Reusable features
└── :ModelRegistry     # Model versioning
```

---

## Querying Data Pipelines

### Query 1: Find Pipelines Processing Specific Data

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?pipeline ?source ?target WHERE {
    ?pipeline rdf:type ai4se:DataPipeline ;
              ai4se:readsFrom ?source ;
              ai4se:writesTo ?target .
    
    FILTER(CONTAINS(STR(?source), "orders"))
}
```

### Query 2: Data Lineage Tracking

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

# Find all transformations of customer data
SELECT ?pipeline ?transformation ?output WHERE {
    :CustomerRawData ai4se:transformedBy+ ?pipeline .
    ?pipeline ai4se:appliesTransformation ?transformation ;
              ai4se:produces ?output .
}
```

### Query 3: Data Quality Dimensions

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?dimension ?definition WHERE {
    ai4se:DataQuality ai4se:hasDimension ?dimension .
    ?dimension skos:definition ?definition .
}
```

**Result**:
```
Accuracy, Completeness, Consistency, Timeliness
```

---

## Intelligent Pipeline Generation

### Ontology-Driven Airflow DAG Generator

```python
from rdflib import Graph, Namespace
from typing import Dict, List
from datetime import datetime

AI4SE = Namespace("http://ai4se.org/ontology/v4#")

class SemanticDataPipelineGenerator:
    """Generate data pipelines from ontology."""
    
    def __init__(self, ontology_path: str):
        self.graph = Graph()
        self.graph.parse(ontology_path, format="turtle")
    
    def generate_airflow_dag(
        self,
        pipeline_name: str,
        schedule: str = "@daily"
    ) -> str:
        """Generate Airflow DAG from ontology pipeline definition."""
        
        # Query pipeline stages
        stages_query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        
        SELECT ?stage ?stageLabel ?order WHERE {{
            :{pipeline_name} ai4se:hasStage ?stage .
            ?stage rdfs:label ?stageLabel ;
                   ai4se:executionOrder ?order .
        }}
        ORDER BY ?order
        """
        
        stages = list(self.graph.query(stages_query))
        
        # Generate Python DAG code
        dag_code = f"""from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Generated from ontology: {pipeline_name}
default_args = {{
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}}

dag = DAG(
    '{pipeline_name}',
    default_args=default_args,
    description='Ontology-generated data pipeline',
    schedule_interval='{schedule}',
    catchup=False,
)

"""
        
        # Generate task functions
        for stage in stages:
            stage_name = str(stage.stageLabel).lower().replace(' ', '_')
            dag_code += f"""
def {stage_name}_task(**context):
    # TODO: Implement {stage.stageLabel}
    print(f"Executing {stage.stageLabel}")
    return "success"

{stage_name} = PythonOperator(
    task_id='{stage_name}',
    python_callable={stage_name}_task,
    dag=dag,
)

"""
        
        # Generate dependencies
        if len(stages) > 1:
            for i in range(len(stages) - 1):
                current = str(stages[i].stageLabel).lower().replace(' ', '_')
                next_stage = str(stages[i+1].stageLabel).lower().replace(' ', '_')
                dag_code += f"{current} >> {next_stage}\n"
        
        return dag_code
    
    def generate_dbt_model(
        self,
        transformation_name: str
    ) -> str:
        """Generate dbt model from ontology transformation."""
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        
        SELECT ?source ?target ?logic WHERE {{
            :{transformation_name} rdf:type ai4se:DataTransformation ;
                                    ai4se:readsFrom ?source ;
                                    ai4se:writesTo ?target ;
                                    ai4se:transformationLogic ?logic .
        }}
        """
        
        results = list(self.graph.query(query))
        
        if not results:
            return ""
        
        result = results[0]
        
        dbt_model = f"""-- Ontology-generated dbt model
-- Transformation: {transformation_name}

{{{{ config(materialized='table') }}}}

WITH source_data AS (
    SELECT * FROM {{{{ source('{result.source}') }}}}
),

transformed AS (
    {result.logic}
)

SELECT * FROM transformed
"""
        
        return dbt_model
    
    def validate_data_quality(
        self,
        dataset_uri: str
    ) -> List[Dict]:
        """Validate dataset against quality dimensions."""
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        
        SELECT ?dimension ?threshold ?actual WHERE {{
            <{dataset_uri}> ai4se:hasQualityMetric ?metric .
            ?metric ai4se:dimension ?dimension ;
                    ai4se:threshold ?threshold ;
                    ai4se:actualValue ?actual .
        }}
        """
        
        results = self.graph.query(query)
        
        issues = []
        for row in results:
            if float(row.actual) < float(row.threshold):
                issues.append({
                    'dimension': str(row.dimension),
                    'threshold': float(row.threshold),
                    'actual': float(row.actual),
                    'status': 'FAILED'
                })
        
        return issues
    
    def trace_data_lineage(
        self,
        dataset_uri: str,
        direction: str = "upstream"
    ) -> List[str]:
        """Trace data lineage upstream or downstream."""
        
        if direction == "upstream":
            query = f"""
            PREFIX ai4se: <http://ai4se.org/ontology/v4#>
            
            SELECT ?source WHERE {{
                <{dataset_uri}> ai4se:derivedFrom+ ?source .
            }}
            """
        else:  # downstream
            query = f"""
            PREFIX ai4se: <http://ai4se.org/ontology/v4#>
            
            SELECT ?target WHERE {{
                ?target ai4se:derivedFrom+ <{dataset_uri}> .
            }}
            """
        
        results = self.graph.query(query)
        return [str(row[0]) for row in results]


# Usage Example
if __name__ == "__main__":
    generator = SemanticDataPipelineGenerator(
        "Ontology_Module_Data_Engineering.ttl"
    )
    
    # Generate Airflow DAG
    dag_code = generator.generate_airflow_dag(
        pipeline_name="customer_360_pipeline",
        schedule="@daily"
    )
    
    with open('dags/customer_360_pipeline.py', 'w') as f:
        f.write(dag_code)
    
    print("✅ Generated Airflow DAG")
    
    # Generate dbt model
    dbt_model = generator.generate_dbt_model(
        transformation_name="aggregate_customer_metrics"
    )
    
    with open('models/customer_metrics.sql', 'w') as f:
        f.write(dbt_model)
    
    print("✅ Generated dbt model")
    
    # Validate data quality
    issues = generator.validate_data_quality(
        "http://ai4se.org/datasets/customer_data"
    )
    
    if issues:
        print("⚠️  Data quality issues:")
        for issue in issues:
            print(f"  - {issue['dimension']}: {issue['actual']}% " +
                  f"(threshold: {issue['threshold']}%)")
    else:
        print("✅ Data quality validated")
    
    # Trace lineage
    upstream = generator.trace_data_lineage(
        "http://ai4se.org/datasets/customer_360",
        direction="upstream"
    )
    
    print(f"Upstream dependencies: {len(upstream)}")
    for source in upstream:
        print(f"  ← {source}")
```

---

## Formalizing Data Pipelines

### Example: Customer 360 Pipeline

```turtle
# Pipeline definition
:Customer360Pipeline rdf:type ai4se:ETLPipeline ;
    rdfs:label "Customer 360 Pipeline"@en ;
    ai4se:hasStage :ExtractStage ;
    ai4se:hasStage :TransformStage ;
    ai4se:hasStage :LoadStage ;
    ai4se:schedule "@daily" ;
    ai4se:owner :DataTeam .

# Extract stage
:ExtractStage rdf:type ai4se:PipelineStage ;
    rdfs:label "Extract Customer Data"@en ;
    ai4se:executionOrder "1"^^xsd:integer ;
    ai4se:readsFrom :CRMDatabase ;
    ai4se:readsFrom :TransactionDatabase ;
    ai4se:readsFrom :WebAnalytics .

# Transform stage
:TransformStage rdf:type ai4se:PipelineStage ;
    rdfs:label "Transform and Aggregate"@en ;
    ai4se:executionOrder "2"^^xsd:integer ;
    ai4se:appliesTransformation :JoinCustomerData ;
    ai4se:appliesTransformation :CalculateMetrics ;
    ai4se:appliesValidation :DataQualityCheck .

# Load stage
:LoadStage rdf:type ai4se:PipelineStage ;
    rdfs:label "Load to Data Warehouse"@en ;
    ai4se:executionOrder "3"^^xsd:integer ;
    ai4se:writesTo :DataWarehouse ;
    ai4se:updateStrategy "upsert" .

# Data lineage
:Customer360Dataset rdf:type ai4se:Dataset ;
    rdfs:label "Customer 360 View"@en ;
    ai4se:producedBy :Customer360Pipeline ;
    ai4se:derivedFrom :CRMDatabase ;
    ai4se:derivedFrom :TransactionDatabase ;
    ai4se:derivedFrom :WebAnalytics ;
    ai4se:hasQualityScore "95"^^xsd:decimal .
```

Query lineage:
```sparql
SELECT ?pipeline ?stage ?source WHERE {
    :Customer360Dataset ai4se:producedBy ?pipeline .
    ?pipeline ai4se:hasStage ?stage .
    ?stage ai4se:readsFrom ?source .
}
```

---

## ML Pipeline Formalization

### Feature Store Ontology

```turtle
:CustomerFeatureStore rdf:type ai4se:FeatureStore ;
    rdfs:label "Customer Feature Store"@en ;
    ai4se:hasFeature :CustomerLifetimeValue ;
    ai4se:hasFeature :PurchaseFrequency ;
    ai4se:hasFeature :AverageOrderValue ;
    ai4se:servingLatency "10"^^xsd:integer ;  # milliseconds
    ai4se:freshnessWindow "1h"^^xsd:duration .

:CustomerLifetimeValue rdf:type ai4se:Feature ;
    rdfs:label "Customer Lifetime Value"@en ;
    ai4se:dataType "float" ;
    ai4se:computedBy :LTVPipeline ;
    ai4se:updateFrequency "daily" .
```

### ML Training Pipeline

```turtle
:ChurnPredictionPipeline rdf:type ai4se:MLPipeline ;
    rdfs:label "Churn Prediction Training"@en ;
    ai4se:hasStage :FeatureEngineering ;
    ai4se:hasStage :ModelTraining ;
    ai4se:hasStage :ModelEvaluation ;
    ai4se:hasStage :ModelDeployment ;
    ai4se:usesFeatureStore :CustomerFeatureStore ;
    ai4se:producesModel :ChurnPredictionModel .

:ChurnPredictionModel rdf:type ai4se:MLModel ;
    rdfs:label "Churn Prediction Model v2.1"@en ;
    ai4se:modelType "XGBoost" ;
    ai4se:accuracy "0.87"^^xsd:decimal ;
    ai4se:registeredIn :ModelRegistry ;
    ai4se:deployedTo :ProductionServing .
```

---

## Data Quality Automation

### Quality Checks as Ontology Constraints

```turtle
# Data quality rule
:CustomerDataQualityRule rdf:type ai4se:DataQualityRule ;
    rdfs:label "Customer Email Completeness"@en ;
    ai4se:appliesTo :CustomerTable ;
    ai4se:dimension ai4se:Completeness ;
    ai4se:condition "email IS NOT NULL" ;
    ai4se:threshold "99.5"^^xsd:decimal .  # 99.5% required
```

Query failed quality checks:
```sparql
SELECT ?dataset ?rule ?actual ?threshold WHERE {
    ?dataset ai4se:failsQualityRule ?rule .
    ?rule ai4se:actualScore ?actual ;
          ai4se:threshold ?threshold .
    
    FILTER(?actual < ?threshold)
}
```

---

## Benefits Summary

| Feature | Traditional Pipelines | Ontology-Based |
|---------|----------------------|----------------|
| **Lineage** | Manual docs | Automated tracing |
| **Validation** | Custom code | Ontology constraints |
| **Reusability** | Copy-paste | Query patterns |
| **Impact Analysis** | Grep code | SPARQL reasoning |
| **Documentation** | Separate | Self-documenting |
| **ML Integration** | Custom | Formal feature/model |

---

## Summary

Data pipeline ontology transforms data engineering from **scripts** into **queryable knowledge**:

✅ **Automated Lineage**: Trace data flow automatically  
✅ **Quality Validation**: Formal quality dimensions  
✅ **Intelligent Generation**: Pipelines from specs  
✅ **Impact Analysis**: Reason about changes  
✅ **ML Integration**: Formal feature/model management  
✅ **Cross-Tool**: Abstract Airflow, dbt, Spark  

---

## Exercises

1. **Modeling**: Formalize your data pipeline in RDF
2. **Lineage**: Trace upstream/downstream dependencies
3. **Generation**: Build Airflow DAG from ontology
4. **Quality**: Create quality constraints with SHACL
5. **ML**: Formalize your feature store and models

---

## References

- **Ontology Module**: `Ontology_Module_Data_Engineering.ttl` (23 classes, V4_NEW_270–V4_NEW_292)
- **Tools**: Airflow, dbt, Spark, Kafka formalized
- **Patterns**: ETL, ELT, streaming, ML pipelines

**Next**: Chapter 27 explores data governance—extending semantic data management to compliance and privacy.
