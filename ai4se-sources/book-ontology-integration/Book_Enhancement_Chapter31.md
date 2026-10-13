# Chapter 31: ROI Validation and Economic Justification
## Part 2: Ontology-Based ROI Calculation

**Prerequisites**: Basic understanding of SPARQL and knowledge graphs  
**Ontology Module**: Ontology_Module_ROI_Metrics.ttl  
**Estimated Reading Time**: 25 minutes

---

## Introduction

While Part 1 of this chapter covered traditional ROI calculation methodologies, this section demonstrates how to leverage the AI4SE ontology for **automated, semantically-rich ROI analysis**. By formalizing ROI concepts in OWL and storing historical data in a knowledge graph, we enable:

- **Automated ROI calculations** from case study data
- **Benchmarking** against similar organizations
- **Regional economic adjustments** (e.g., Turkey vs. US contexts)
- **What-if scenario analysis** using SPARQL queries
- **Predictive ROI modeling** based on historical patterns

This approach transforms ROI from manual spreadsheet calculations into a **queryable knowledge base** that supports decision-making at scale.

---

## Ontology Structure for ROI

### Core Classes

The ROI ontology module defines formal concepts for economic analysis:

```turtle
# ROI Metrics Ontology (excerpt)
:ROIMetric rdf:type owl:Class ;
    rdfs:label "ROI Metric"@en ;
    skos:definition "Financial metric measuring return on investment"@en .

:CostComponent rdf:type owl:Class ;
    rdfs:label "Cost Component"@en ;
    skos:definition "Individual cost element in investment"@en .

:BenefitComponent rdf:type owl:Class ;
    rdfs:label "Benefit Component"@en ;
    skos:definition "Individual benefit element from investment"@en .

:RegionalEconomicContext rdf:type owl:Class ;
    rdfs:label "Regional Economic Context"@en ;
    skos:definition "Economic factors specific to geographic region"@en .
```

**Key relationships**:
```turtle
:hasInitialInvestment rdf:type owl:DatatypeProperty ;
    rdfs:domain :CaseStudy ;
    rdfs:range xsd:decimal .

:hasAnnualBenefit rdf:type owl:DatatypeProperty ;
    rdfs:domain :CaseStudy ;
    rdfs:range xsd:decimal .

:hasROI rdf:type owl:DatatypeProperty ;
    rdfs:domain :CaseStudy ;
    rdfs:range xsd:decimal .

:hasPaybackPeriod rdf:type owl:DatatypeProperty ;
    rdfs:domain :CaseStudy ;
    rdfs:range xsd:decimal .
```

---

## Querying ROI Data with SPARQL

### Query 1: Find All Case Studies with ROI > 200%

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?caseStudy ?name ?roi ?payback WHERE {
    ?caseStudy rdf:type ai4se:CaseStudy ;
               rdfs:label ?name ;
               ai4se:hasROI ?roi ;
               ai4se:hasPaybackPeriod ?payback .
    
    FILTER(?roi > 200)
}
ORDER BY DESC(?roi)
```

**Result Example**:
```
caseStudy               name                                roi    payback
ai4se:CloudHRCase       "CloudHR Requirements AI"           411    2.2
ai4se:TurkShopCase      "TurkShop Test Automation"         320    4.2
ai4se:AnadoluBankCase   "AnadoluBank DevOps Transform"     279    6.4
ai4se:TurkLogisticsCase "TurkLogistics Microservices Test" 242    5.1
```

### Query 2: Calculate Average ROI by Industry

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?industry (AVG(?roi) as ?avgROI) (COUNT(?case) as ?count) WHERE {
    ?case rdf:type ai4se:CaseStudy ;
          ai4se:hasIndustry ?industry ;
          ai4se:hasROI ?roi .
}
GROUP BY ?industry
ORDER BY DESC(?avgROI)
```

### Query 3: Find Comparable Case Studies for Benchmarking

Given your organization's characteristics, find similar implementations:

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?case ?name ?roi ?investment ?benefit WHERE {
    ?case rdf:type ai4se:CaseStudy ;
          rdfs:label ?name ;
          ai4se:hasIndustry ai4se:ECommerce ;
          ai4se:hasOrganizationSize ai4se:MediumOrganization ;
          ai4se:implementsTechnique ai4se:TestAutomation ;
          ai4se:hasROI ?roi ;
          ai4se:hasInitialInvestment ?investment ;
          ai4se:hasAnnualBenefit ?benefit .
}
```

This query finds e-commerce companies of similar size that implemented test automation—perfect for benchmarking your planned initiative.

---

## Regional Economic Adjustments

### Turkey-Specific Example

The ontology includes regional economic multipliers:

```turtle
:TurkeyEconomicContext rdf:type :RegionalEconomicContext ;
    rdfs:label "Turkey Economic Context"@en ;
    :hasCostMultiplier "0.6"^^xsd:decimal ;
    :hasBenefitMultiplier "0.75"^^xsd:decimal ;
    :hasAverageSeniorDevSalary "900000"^^xsd:decimal ;  # TRY
    :hasCurrency "TRY"@en .

:USEconomicContext rdf:type :RegionalEconomicContext ;
    rdfs:label "United States Economic Context"@en ;
    :hasCostMultiplier "1.0"^^xsd:decimal ;
    :hasBenefitMultiplier "1.0"^^xsd:decimal ;
    :hasAverageSeniorDevSalary "120000"^^xsd:decimal ;  # USD
    :hasCurrency "USD"@en .
```

### Automated Regional ROI Calculation

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

# Calculate adjusted ROI for Turkey context
SELECT ?case ?unadjustedROI 
       (?investment * ?costMult as ?adjInvestment)
       (?benefit * ?benefitMult as ?adjBenefit)
       (((?benefit * ?benefitMult) - (?investment * ?costMult)) / 
        (?investment * ?costMult) * 100 as ?adjustedROI)
WHERE {
    ?case ai4se:hasROI ?unadjustedROI ;
          ai4se:hasInitialInvestment ?investment ;
          ai4se:hasAnnualBenefit ?benefit .
    
    ai4se:TurkeyEconomicContext ai4se:hasCostMultiplier ?costMult ;
                                 ai4se:hasBenefitMultiplier ?benefitMult .
}
```

---

## Python Integration Example

### Complete ROI Calculator Using Ontology

```python
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, List

class OntologyROICalculator:
    """Calculate ROI using AI4SE knowledge graph."""
    
    def __init__(self, sparql_endpoint: str = "http://localhost:3030/ai4se/sparql"):
        self.sparql = SPARQLWrapper(sparql_endpoint)
    
    def calculate_roi(
        self,
        investment: float,
        annual_benefit: float,
        duration_months: int = 12,
        region: str = "Turkey"
    ) -> Dict:
        """
        Calculate ROI with regional adjustments from ontology.
        
        Args:
            investment: Initial investment amount
            annual_benefit: Expected annual benefit
            duration_months: Project duration in months
            region: Geographic region (Turkey, US, etc.)
            
        Returns:
            Dictionary with ROI metrics
        """
        # Get regional multipliers from ontology
        multipliers = self._get_regional_multipliers(region)
        
        # Apply adjustments
        adj_investment = investment * multipliers['cost']
        adj_benefit = annual_benefit * multipliers['benefit']
        
        # Calculate metrics
        actual_benefit = (adj_benefit / 12) * duration_months
        roi = ((actual_benefit - adj_investment) / adj_investment) * 100
        payback = adj_investment / (adj_benefit / 12)
        
        return {
            'roi_percentage': roi,
            'payback_months': payback,
            'adjusted_investment': adj_investment,
            'adjusted_annual_benefit': adj_benefit,
            'total_benefit': actual_benefit,
            'region': region
        }
    
    def _get_regional_multipliers(self, region: str) -> Dict[str, float]:
        """Query ontology for regional economic multipliers."""
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        
        SELECT ?costMult ?benefitMult WHERE {{
            ai4se:{region}EconomicContext 
                ai4se:hasCostMultiplier ?costMult ;
                ai4se:hasBenefitMultiplier ?benefitMult .
        }}
        """
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        
        if results['results']['bindings']:
            binding = results['results']['bindings'][0]
            return {
                'cost': float(binding['costMult']['value']),
                'benefit': float(binding['benefitMult']['value'])
            }
        else:
            # Default to no adjustment
            return {'cost': 1.0, 'benefit': 1.0}
    
    def find_comparables(
        self,
        industry: str,
        org_size: str,
        technique: str
    ) -> List[Dict]:
        """Find comparable case studies for benchmarking."""
        
        query = f"""
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name ?roi ?payback ?investment ?benefit WHERE {{
            ?case rdf:type ai4se:CaseStudy ;
                  rdfs:label ?name ;
                  ai4se:hasIndustry ai4se:{industry} ;
                  ai4se:hasOrganizationSize ai4se:{org_size} ;
                  ai4se:implementsTechnique ai4se:{technique} ;
                  ai4se:hasROI ?roi ;
                  ai4se:hasPaybackPeriod ?payback ;
                  ai4se:hasInitialInvestment ?investment ;
                  ai4se:hasAnnualBenefit ?benefit .
        }}
        ORDER BY DESC(?roi)
        """
        
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        
        comparables = []
        for binding in results['results']['bindings']:
            comparables.append({
                'name': binding['name']['value'],
                'roi': float(binding['roi']['value']),
                'payback': float(binding['payback']['value']),
                'investment': float(binding['investment']['value']),
                'benefit': float(binding['benefit']['value'])
            })
        
        return comparables
    
    def benchmark_results(
        self,
        your_roi: Dict,
        comparables: List[Dict]
    ) -> Dict:
        """Compare your ROI against peer organizations."""
        
        if not comparables:
            return {'status': 'no_comparables'}
        
        peer_rois = [c['roi'] for c in comparables]
        avg_roi = sum(peer_rois) / len(peer_rois)
        
        return {
            'your_roi': your_roi['roi_percentage'],
            'peer_average': avg_roi,
            'peer_count': len(comparables),
            'percentile': self._percentile(your_roi['roi_percentage'], peer_rois),
            'comparison': 'above_average' if your_roi['roi_percentage'] > avg_roi 
                         else 'below_average',
            'top_peer': max(comparables, key=lambda x: x['roi'])
        }
    
    def _percentile(self, value: float, dataset: List[float]) -> int:
        """Calculate percentile rank."""
        sorted_data = sorted(dataset)
        rank = sum(1 for x in sorted_data if x <= value)
        return int((rank / len(sorted_data)) * 100)


# Usage Example
if __name__ == "__main__":
    calculator = OntologyROICalculator()
    
    # Calculate ROI for Turkish e-commerce company
    roi = calculator.calculate_roi(
        investment=1_800_000,  # ₺1.8M
        annual_benefit=5_200_000,  # ₺5.2M/year
        duration_months=18,
        region="Turkey"
    )
    
    print(f"ROI: {roi['roi_percentage']:.1f}%")
    print(f"Payback Period: {roi['payback_months']:.1f} months")
    
    # Find comparable implementations
    comparables = calculator.find_comparables(
        industry="ECommerce",
        org_size="MediumOrganization",
        technique="TestAutomation"
    )
    
    print(f"\nFound {len(comparables)} comparable case studies")
    
    # Benchmark against peers
    benchmark = calculator.benchmark_results(roi, comparables)
    print(f"Your ROI: {benchmark['your_roi']:.1f}%")
    print(f"Peer Average: {benchmark['peer_average']:.1f}%")
    print(f"Percentile: {benchmark['percentile']}th")
    print(f"Status: {benchmark['comparison']}")
```

**Output Example**:
```
ROI: 333.3%
Payback Period: 4.2 months

Found 3 comparable case studies
Your ROI: 333.3%
Peer Average: 289.5%
Percentile: 100th
Status: above_average
```

---

## Advanced Queries

### Sensitivity Analysis

What if costs increase by 20%?

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?case 
       ?baseROI
       ((?benefit - (?investment * 1.2)) / (?investment * 1.2) * 100 as ?newROI)
       (?baseROI - ((?benefit - (?investment * 1.2)) / (?investment * 1.2) * 100) 
        as ?roiChange)
WHERE {
    ?case ai4se:hasROI ?baseROI ;
          ai4se:hasInitialInvestment ?investment ;
          ai4se:hasAnnualBenefit ?benefit .
}
```

### TCO (Total Cost of Ownership) Calculation

```sparql
PREFIX ai4se: <http://ai4se.org/ontology/v4#>

SELECT ?case 
       (?initial + (?annual * 3) as ?tco3year)
       (?benefit * 3 as ?totalBenefit3year)
       (((?benefit * 3) - (?initial + (?annual * 3))) / 
        (?initial + (?annual * 3)) * 100 as ?roi3year)
WHERE {
    ?case ai4se:hasInitialInvestment ?initial ;
          ai4se:hasAnnualOperatingCost ?annual ;
          ai4se:hasAnnualBenefit ?benefit .
}
```

---

## Real-World Application: Business Case Generator

### Automated Business Case from Ontology

```python
def generate_business_case(
    technique: str,
    industry: str,
    org_size: str,
    investment: float,
    region: str = "Turkey"
) -> str:
    """Generate complete business case using ontology data."""
    
    calculator = OntologyROICalculator()
    
    # Find comparable implementations
    comparables = calculator.find_comparables(industry, org_size, technique)
    
    if not comparables:
        return "No comparable case studies found in ontology."
    
    # Use peer average as baseline
    peer_avg_roi = sum(c['roi'] for c in comparables) / len(comparables)
    peer_avg_benefit = sum(c['benefit'] for c in comparables) / len(comparables)
    
    # Scale benefit to investment
    estimated_benefit = (investment / comparables[0]['investment']) * peer_avg_benefit
    
    # Calculate projected ROI
    roi = calculator.calculate_roi(investment, estimated_benefit, region=region)
    
    # Generate report
    report = f"""
# Business Case: {technique} Implementation

## Executive Summary
Based on analysis of {len(comparables)} comparable implementations in the {industry} 
industry, we project the following outcomes:

- **Projected ROI**: {roi['roi_percentage']:.1f}%
- **Payback Period**: {roi['payback_months']:.1f} months
- **Annual Benefit**: {roi['adjusted_annual_benefit']:,.0f} {region} currency

## Peer Benchmarking
- **Peer Average ROI**: {peer_avg_roi:.1f}%
- **Our Projection**: {roi['roi_percentage']:.1f}%
- **Confidence**: {'High' if abs(roi['roi_percentage'] - peer_avg_roi) < 50 else 'Medium'}

## Comparable Implementations
"""
    
    for comp in comparables:
        report += f"\n- {comp['name']}: {comp['roi']:.1f}% ROI, {comp['payback']:.1f} month payback"
    
    report += f"""

## Recommendation
{'APPROVE' if roi['roi_percentage'] > 150 else 'CONDITIONAL APPROVAL' if roi['roi_percentage'] > 100 else 'DEFER'}

This analysis is based on formal ontology data from the AI4SE knowledge graph.
"""
    
    return report


# Usage
business_case = generate_business_case(
    technique="TestAutomation",
    industry="ECommerce",
    org_size="MediumOrganization",
    investment=2_000_000,
    region="Turkey"
)

print(business_case)
```

---

## Benefits of Ontology-Based ROI

### Compared to Traditional Spreadsheets

| Feature | Spreadsheet | Ontology Approach |
|---------|-------------|-------------------|
| **Data Reuse** | Copy-paste between files | Query once, reuse everywhere |
| **Benchmarking** | Manual research | Automated SPARQL queries |
| **Regional Adjustments** | Manual formulas | Formal multipliers in ontology |
| **Sensitivity Analysis** | New columns/sheets | Single SPARQL query |
| **Updates** | Email new versions | Update knowledge graph once |
| **Validation** | Manual checking | OWL reasoning + SHACL |
| **Integration** | Export to CSV | Direct API access |
| **Collaboration** | File sharing | Shared knowledge graph |

### Key Advantages

1. **Semantic Richness**: ROI data linked to techniques, industries, regions
2. **Automated Analysis**: SPARQL queries replace manual calculations
3. **Historical Learning**: Knowledge accumulates in graph
4. **Consistency**: Formal definitions prevent calculation errors
5. **Explainability**: Every metric traceable to source
6. **Scalability**: Handles thousands of case studies efficiently

---

## Integration with Existing Tools

### Excel Add-In (Conceptual)

```vba
' Excel VBA function to query ontology
Function GetPeerAverageROI(industry As String, technique As String) As Double
    ' Call Python script that queries ontology
    Dim result As String
    result = RunPythonScript("query_ontology.py", industry, technique)
    GetPeerAverageROI = CDbl(result)
End Function

' Usage in Excel cell:
' =GetPeerAverageROI("ECommerce", "TestAutomation")
```

### Power BI Integration

```python
# Power BI custom data source
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

def get_roi_data():
    """Fetch ROI data for Power BI dashboard."""
    sparql = SPARQLWrapper("http://localhost:3030/ai4se/sparql")
    
    query = """
    PREFIX ai4se: <http://ai4se.org/ontology/v4#>
    SELECT ?name ?industry ?roi ?payback ?investment WHERE {
        ?case rdf:type ai4se:CaseStudy ;
              rdfs:label ?name ;
              ai4se:hasIndustry ?industry ;
              ai4se:hasROI ?roi ;
              ai4se:hasPaybackPeriod ?payback ;
              ai4se:hasInitialInvestment ?investment .
    }
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # Convert to DataFrame
    data = []
    for result in results['results']['bindings']:
        data.append({
            'Case Study': result['name']['value'],
            'Industry': result['industry']['value'],
            'ROI (%)': float(result['roi']['value']),
            'Payback (months)': float(result['payback']['value']),
            'Investment': float(result['investment']['value'])
        })
    
    return pd.DataFrame(data)
```

---

## Validation & Quality Assurance

### SHACL Constraints for ROI Data

```turtle
# Ensure ROI calculations are consistent
:ROIConsistencyShape a sh:NodeShape ;
    sh:targetClass ai4se:CaseStudy ;
    sh:property [
        sh:path ai4se:hasROI ;
        sh:datatype xsd:decimal ;
        sh:minInclusive -100 ;  # ROI cannot be less than -100%
    ] ;
    sh:property [
        sh:path ai4se:hasPaybackPeriod ;
        sh:datatype xsd:decimal ;
        sh:minInclusive 0 ;
    ] ;
    # Verify ROI formula
    sh:sparql [
        sh:message "ROI calculation doesn't match formula" ;
        sh:select """
        PREFIX ai4se: <http://ai4se.org/ontology/v4#>
        SELECT $this WHERE {
            $this ai4se:hasROI ?roi ;
                  ai4se:hasInitialInvestment ?inv ;
                  ai4se:hasAnnualBenefit ?benefit .
            
            # Calculate expected ROI
            BIND(((?benefit - ?inv) / ?inv * 100) as ?expectedROI)
            
            # Check if recorded ROI matches (within 1% tolerance)
            FILTER(ABS(?roi - ?expectedROI) > 1)
        }
        """
    ] .
```

---

## Summary

Ontology-based ROI calculation transforms financial analysis from isolated spreadsheets into a **connected knowledge system**. By storing ROI metrics in a semantic graph:

✅ **Automated calculations** using SPARQL  
✅ **Benchmarking** against peer organizations  
✅ **Regional adjustments** formalized in ontology  
✅ **Historical learning** from past implementations  
✅ **Integration** with existing tools (Excel, Power BI)  
✅ **Validation** through OWL reasoning and SHACL  

This approach is especially valuable for:
- **Organizations** planning AI4SE initiatives
- **Consultants** building business cases
- **Researchers** analyzing ROI patterns
- **Tool vendors** demonstrating value

---

## Exercises

1. **Query Exercise**: Write SPARQL to find case studies with payback < 6 months
2. **Calculation Exercise**: Use the Python calculator to compute ROI for your organization
3. **Benchmarking Exercise**: Compare your projected ROI against peers in your industry
4. **Integration Exercise**: Create a Power BI dashboard showing ROI trends
5. **Validation Exercise**: Write SHACL constraints for your specific ROI requirements

---

## References

- **Ontology Module**: `Ontology_Module_ROI_Metrics.ttl` (30 classes, V4_NEW_080–V4_NEW_109)
- **Case Studies**: See Chapter 38 for real-world ROI examples
- **SPARQL Tutorial**: Chapter 15 Part 2 for query basics
- **Regional Context**: Chapter 38 for Turkey-specific economic data

**Next**: Chapter 32 explores metrics beyond ROI, including DORA metrics and quality indicators—all formalized in the ontology.
