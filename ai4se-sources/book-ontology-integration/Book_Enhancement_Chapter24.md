# Chapter 24: Containers and Kubernetes
## Part 2: Cloud Infrastructure Ontology

**Prerequisites**: Container basics (Part 1)  
**Ontology Module**: Ontology_Module_Cloud_Containerization.ttl  
**Estimated Reading Time**: 26 minutes

---

## Introduction

Cloud infrastructure has exploded in complexity: containers, orchestrators, service meshes, serverless, multiple cloud providers. Traditional infrastructure documentation (Confluence pages, diagrams) cannot:
- **Validate** infrastructure configurations
- **Query** "which services run in Kubernetes?"
- **Reason** about dependencies and impacts
- **Automate** infrastructure generation

**Cloud Infrastructure Ontology** formalizes cloud concepts, enabling semantic infrastructure-as-code where machines understand cloud architecture, not just execute commands.

---

## Cloud Ontology Structure (28 Classes)

```turtle
# Cloud Service Models
:CloudServiceModel rdf:type owl:Class .
├── :IaaS  # Virtual machines, storage, networks
├── :PaaS  # Platform for applications
├── :SaaS  # Complete applications
└── :FaaS  # Serverless functions

# Container Technology
:ContainerTechnology rdf:type owl:Class .
├── :Docker
│   ├── :DockerImage
│   ├── :DockerContainer
│   └── :Dockerfile
└── :ContainerOrchestration
    ├── :Kubernetes
    │   ├── :Pod
    │   ├── :Service
    │   └── :Deployment
    └── :DockerSwarm

# Cloud Providers
:CloudProvider rdf:type owl:Class .
├── :AWS
├── :Azure
└── :GoogleCloud

# Service Mesh
:ServiceMesh rdf:type owl:Class .
├── :Istio
└── :Linkerd
```

---

## Querying Cloud Infrastructure

### Query 1: Find Services Running in Kubernetes

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?service ?pod ?image WHERE {
    ?service ai4se:runsIn ai4se:Kubernetes ;
             ai4se:hasP

od ?pod ;
             ai4se:usesImage ?image .
}
```

### Query 2: Container Orchestrators by Scale

Need to handle 100+ services?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?orchestrator ?label ?benefit WHERE {
    ?orchestrator rdfs:subClassOf ai4se:ContainerOrchestration ;
                  rdfs:label ?label ;
                  ai4se:hasBenefit ?benefit .
    
    FILTER(CONTAINS(LCASE(?benefit), "scal"))
}
```

**Result**: Returns `Kubernetes` with "Automatic scaling" benefit.

### Query 3: Find Cloud Providers with Regional Presence

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?provider ?region WHERE {
    ?provider rdf:type ai4se:CloudProvider ;
              ai4se:hasRegion ?region .
    
    FILTER(CONTAINS(?region, "eu-central") || 
           CONTAINS(?region, "Turkey"))
}
```

---

## Intelligent Infrastructure Generation

### Ontology-Driven Terraform Generator

```python
from rdflib import Graph, Namespace
import hcl2
from typing import Dict

AI4SE = Namespace("http://ai4se.org/ontology/v4#")

class SemanticInfraGenerator:
    """Generate infrastructure code from ontology."""
    
    def __init__(self, ontology_path: str):
        self.graph = Graph()
        self.graph.parse(ontology_path, format="turtle")
    
    def generate_kubernetes_manifest(
        self,
        service_name: str,
        replicas: int = 3,
        image: str = None
    ) -> str:
        """Generate K8s YAML from service definition."""
        
        # Query ontology for service details
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        
        SELECT ?port ?protocol WHERE {{
            :{service_name} ai4se:exposesPort ?port ;
                            ai4se:usesProtocol ?protocol .
        }}
        """
        
        results = list(self.graph.query(query))
        
        # Generate Kubernetes Deployment
        manifest = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
    spec:
      containers:
      - name: {service_name}
        image: {image or f'{service_name}:latest'}
        ports:
"""
        
        for row in results:
            port = str(row.port)
            manifest += f"        - containerPort: {port}\n"
        
        # Generate Service
        manifest += f"""---
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
spec:
  selector:
    app: {service_name}
  ports:
"""
        
        for row in results:
            port = str(row.port)
            protocol = str(row.protocol)
            manifest += f"""  - port: {port}
    targetPort: {port}
    protocol: {protocol}
"""
        
        return manifest
    
    def generate_terraform_aws(
        self,
        infrastructure_name: str,
        region: str = "eu-central-1"
    ) -> str:
        """Generate Terraform for AWS infrastructure."""
        
        tf_config = f"""terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{region}"
}}

# VPC
resource "aws_vpc" "{infrastructure_name}_vpc" {{
  cidr_block = "10.0.0.0/16"
  
  tags = {{
    Name = "{infrastructure_name}-vpc"
    Generated = "Semantic Infrastructure Generator"
  }}
}}

# Subnet
resource "aws_subnet" "{infrastructure_name}_subnet" {{
  vpc_id     = aws_vpc.{infrastructure_name}_vpc.id
  cidr_block = "10.0.1.0/24"
  
  tags = {{
    Name = "{infrastructure_name}-subnet"
  }}
}}

# EKS Cluster
resource "aws_eks_cluster" "{infrastructure_name}_cluster" {{
  name     = "{infrastructure_name}"
  role_arn = aws_iam_role.cluster_role.arn
  
  vpc_config {{
    subnet_ids = [aws_subnet.{infrastructure_name}_subnet.id]
  }}
}}
"""
        
        return tf_config
    
    def validate_infrastructure(self, infrastructure_uri: str) -> list:
        """Validate infrastructure against ontology constraints."""
        
        issues = []
        
        # Check: Kubernetes clusters should have monitoring
        query = f"""
        ASK {{
            <{infrastructure_uri}> ai4se:uses ai4se:Kubernetes .
            FILTER NOT EXISTS {{
                <{infrastructure_uri}> ai4se:hasMonitoring ?monitor .
            }}
        }}
        """
        
        if self.graph.query(query):
            issues.append("Kubernetes cluster lacks monitoring")
        
        # Check: Production should use service mesh
        query = f"""
        ASK {{
            <{infrastructure_uri}> ai4se:environment "production" .
            FILTER NOT EXISTS {{
                <{infrastructure_uri}> ai4se:usesServiceMesh ?mesh .
            }}
        }}
        """
        
        if self.graph.query(query):
            issues.append("Production should use service mesh")
        
        return issues


# Usage
if __name__ == "__main__":
    generator = SemanticInfraGenerator(
        "Ontology_Module_Cloud_Containerization.ttl"
    )
    
    # Generate Kubernetes manifests
    k8s_yaml = generator.generate_kubernetes_manifest(
        service_name="order-service",
        replicas=3,
        image="myapp/order-service:v1.2"
    )
    
    with open('k8s/order-service.yaml', 'w') as f:
        f.write(k8s_yaml)
    
    print("✅ Generated Kubernetes manifests")
    
    # Generate Terraform
    terraform = generator.generate_terraform_aws(
        infrastructure_name="myapp",
        region="eu-central-1"
    )
    
    with open('terraform/main.tf', 'w') as f:
        f.write(terraform)
    
    print("✅ Generated Terraform configuration")
    
    # Validate
    issues = generator.validate_infrastructure("http://ai4se.org/MyInfrastructure")
    if issues:
        print("⚠️  Validation issues:")
        for issue in issues:
            print(f"  - {issue}")
```

---

## Formalizing Your Cloud Infrastructure

### Example: E-Commerce Platform in AWS

```turtle
# System definition
:ECommercePlatform rdf:type ai4se:System ;
    rdfs:label "E-Commerce Platform"@en ;
    ai4se:deployedOn ai4se:AWS ;
    ai4se:usesRegion "eu-central-1" ;
    ai4se:uses ai4se:Kubernetes ;
    ai4se:usesServiceMesh ai4se:Istio ;
    ai4se:hasMonitoring ai4se:Prometheus .

# Kubernetes cluster
:ECommerceK8sCluster rdf:type ai4se:Kubernetes ;
    rdfs:label "E-Commerce K8s Cluster"@en ;
    ai4se:partOf :ECommercePlatform ;
    ai4se:nodeCount "10"^^xsd:integer ;
    ai4se:hasNamespace :ProductionNamespace ;
    ai4se:hasNamespace :StagingNamespace .

# Microservices
:OrderService rdf:type ai4se:Microservice ;
    rdfs:label "Order Service"@en ;
    ai4se:runsIn :ECommerceK8sCluster ;
    ai4se:hasPod :OrderServicePod ;
    ai4se:usesImage "myregistry/order-service:v2.1" ;
    ai4se:exposesPort "8080"^^xsd:integer ;
    ai4se:hasReplicas "3"^^xsd:integer .

:OrderServicePod rdf:type ai4se:Pod ;
    ai4se:hasContainer :OrderServiceContainer .

# Service mesh configuration
:OrderServiceMeshConfig rdf:type ai4se:IstioConfig ;
    ai4se:appliesTo :OrderService ;
    ai4se:hasCircuitBreaker [
        ai4se:maxConnections "1000"^^xsd:integer ;
        ai4se:http1MaxPendingRequests "100"^^xsd:integer
    ] ;
    ai4se:hasRetryPolicy [
        ai4se:attempts "3"^^xsd:integer ;
        ai4se:perTryTimeout "2s"^^xsd:string
    ] .
```

Query deployment details:
```sparql
SELECT ?service ?image ?replicas ?port WHERE {
    ?service ai4se:runsIn :ECommerceK8sCluster ;
             ai4se:usesImage ?image ;
             ai4se:hasReplicas ?replicas ;
             ai4se:exposesPort ?port .
}
```

---

## Advanced Cloud Patterns

### Multi-Cloud Strategy in Ontology

```turtle
:MultiCloudStrategy rdf:type ai4se:DeploymentStrategy ;
    rdfs:label "Multi-Cloud Strategy"@en ;
    ai4se:usesProvider ai4se:AWS ;
    ai4se:usesProvider ai4se:Azure ;
    ai4se:primaryRegion "AWS eu-central-1" ;
    ai4se:failoverRegion "Azure West Europe" ;
    ai4se:dataReplication "active-active" .
```

### Serverless Functions

```turtle
:OrderProcessingFunction rdf:type ai4se:ServerlessFunction ;
    rdfs:label "Order Processing Lambda"@en ;
    ai4se:runtime "python3.10" ;
    ai4se:memorySize "512"^^xsd:integer ;  # MB
    ai4se:timeout "30"^^xsd:integer ;      # seconds
    ai4se:triggeredBy :OrderCreatedEvent ;
    ai4se:deployedOn ai4se:AWSLambda .
```

---

## Cost Optimization Through Ontology

### Query Infrastructure Costs

```python
def calculate_infrastructure_cost(infrastructure_uri: str) -> float:
    """Calculate monthly infrastructure cost from ontology."""
    
    query = f"""
    PREFIX ai4se: <http://ai4se.org/ontology/v4#>
    
    SELECT (SUM(?cost) as ?totalCost) WHERE {{
        <{infrastructure_uri}> ai4se:hasResource ?resource .
        ?resource ai4se:monthlyCost ?cost .
    }}
    """
    
    results = graph.query(query)
    for row in results:
        return float(row.totalCost)
    return 0.0

# Find cost optimization opportunities
def find_over_provisioned_resources():
    """Find resources with low utilization."""
    
    query = """
    PREFIX ai4se: <http://ai4se.org/ontology/v4#>
    
    SELECT ?resource ?utilization ?cost WHERE {
        ?resource ai4se:cpuUtilization ?utilization ;
                  ai4se:monthlyCost ?cost .
        
        FILTER(?utilization < 30)  # Less than 30% utilized
    }
    ORDER BY DESC(?cost)
    """
    
    # Returns expensive under-utilized resources
```

---

## Integration with Helm

### Ontology-Driven Helm Chart Generation

```python
def generate_helm_chart(service_name: str) -> Dict:
    """Generate Helm chart from ontology definition."""
    
    # Query ontology for service config
    query = f"""
    SELECT ?image ?port ?replicas ?env WHERE {{
        :{service_name} ai4se:usesImage ?image ;
                        ai4se:exposesPort ?port ;
                        ai4se:hasReplicas ?replicas .
        OPTIONAL {{ :{service_name} ai4se:requiresEnv ?env }}
    }}
    """
    
    results = list(graph.query(query))
    
    # Generate values.yaml
    values = {
        'replicaCount': results[0].replicas,
        'image': {
            'repository': results[0].image.split(':')[0],
            'tag': results[0].image.split(':')[1]
        },
        'service': {
            'port': results[0].port
        }
    }
    
    return values
```

---

## Benefits Summary

| Feature | Traditional IaC | Ontology-Based |
|---------|----------------|----------------|
| **Validation** | Syntax only | Semantic constraints |
| **Querying** | Grep/search | SPARQL |
| **Reusability** | Terraform modules | Ontology patterns |
| **Documentation** | Separate docs | Self-documenting |
| **Impact Analysis** | Manual | Automated reasoning |
| **Multi-Tool** | Tool-specific | Tool-agnostic |

---

## Summary

Cloud infrastructure ontology transforms infrastructure from **code files** into **queryable knowledge**:

✅ **Semantic Validation**: Check constraints, not just syntax  
✅ **Intelligent Generation**: Infrastructure from high-level specs  
✅ **Impact Analysis**: Reason about changes automatically  
✅ **Cost Optimization**: Query and optimize spending  
✅ **Multi-Cloud**: Abstract provider differences  
✅ **Tool Integration**: Generate for any tool (Terraform, K8s, Helm)  

---

## Exercises

1. **Modeling**: Formalize your infrastructure in RDF
2. **Query**: Find all services in Kubernetes
3. **Generation**: Build Terraform generator from ontology
4. **Validation**: Create constraints for production infrastructure
5. **Cost**: Query and optimize infrastructure costs

---

## References

- **Ontology Module**: `Ontology_Module_Cloud_Containerization.ttl` (28 classes, V4_NEW_240–V4_NEW_267)
- **Tools**: Docker, Kubernetes, Istio, Terraform formalized
- **Patterns**: Multi-cloud, serverless, service mesh included

**Next**: Chapter 25 explores Kubernetes patterns in depth—building on this ontological foundation.
