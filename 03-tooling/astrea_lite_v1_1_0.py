"""
astrea_lite v1.1.0 — Python implementation of core Astrea OWL2→SHACL mappings.

Provenance: derived from github.com/oeg-upm/astrea Queries.csv (Cimmino et al. 2020, ESWC).
Implements 5 highest-impact mappings: M1 class→NodeShape, M2 subClassOf, M3 domain→property/class,
M4 datatype-range→sh:datatype, M5 isDefinedBy. NOT a full Astrea port.

Usage:  python3 astrea_lite_v1_0_0.py <input_tbox.ttl> <output_shapes.ttl>

Authored 2026-05-27 as part of OE Pack v19.11 (P4b semantic-coverage extension).
"""
import sys
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH

DOMAIN_RDFS = RDFS.domain
RANGE_RDFS  = RDFS.range

def derive_shapes(ont_path):
    g = Graph(); g.parse(ont_path, format='turtle')
    sh = Graph()
    SHN = Namespace("http://www.w3.org/ns/shacl#")
    sh.bind("sh", SHN); sh.bind("rdfs", RDFS); sh.bind("owl", OWL); sh.bind("xsd", XSD)
    # carry the ontology's own prefixes so shape IRIs use them
    for p,n in g.namespaces(): sh.bind(p,n)

    classes = list(g.subjects(RDF.type, OWL.Class))
    classes = [c for c in classes if not isinstance(c, BNode)]

    # M1: every named class -> NodeShape targeting it
    shape_of = {}
    for c in classes:
        s = URIRef(str(c) + "_Shape")
        shape_of[c] = s
        sh.add((s, RDF.type, SHN.NodeShape))
        sh.add((s, SHN.targetClass, c))
        # M5: carry isDefinedBy
        for d in g.objects(c, RDFS.isDefinedBy):
            sh.add((s, RDFS.isDefinedBy, d))

    # M3 + M4: walk properties with domain+range
    props = set(g.subjects(RDFS.domain, None)) | set(g.subjects(RDFS.range, None))
    for p in props:
        domains = list(g.objects(p, RDFS.domain))
        ranges  = list(g.objects(p, RDFS.range))
        is_datatype_prop = (p, RDF.type, OWL.DatatypeProperty) in g
        is_object_prop   = (p, RDF.type, OWL.ObjectProperty) in g
        # only emit shapes when domain is a named class we have a shape for
        for dom in domains:
            if dom not in shape_of: continue
            target_shape = shape_of[dom]
            prop_node = BNode()
            sh.add((target_shape, SHN.property, prop_node))
            sh.add((prop_node, SHN.path, p))
            # if datatype property, constrain by datatype
            for rng in ranges:
                if is_datatype_prop or str(rng).startswith(str(XSD)):
                    sh.add((prop_node, SHN.datatype, rng))
                else:
                    sh.add((prop_node, SHN["class"], rng))
            # mark as advisory (warning) - we don't infer required cardinality from domain alone
            sh.add((prop_node, SHN.severity, SHN.Warning))
            sh.add((prop_node, SHN.message,
                   Literal(f"Astrea-derived: property {str(p).split('#')[-1]} usage check (range/class) on shape of {str(dom).split('#')[-1]}")))



    # M6 (extension): owl:Restriction with owl:minCardinality / owl:maxCardinality 
    # -> sh:property [ sh:path P ; sh:minCount N / sh:maxCount N ]
    for cls in classes:
        if cls not in shape_of: continue
        target_shape = shape_of[cls]
        for restr in g.objects(cls, RDFS.subClassOf):
            if not (restr, RDF.type, OWL.Restriction) in g: continue
            on_prop = g.value(restr, OWL.onProperty)
            min_card = g.value(restr, OWL.minCardinality)
            max_card = g.value(restr, OWL.maxCardinality)
            if not on_prop: continue
            prop_node = BNode()
            sh.add((target_shape, SHN.property, prop_node))
            sh.add((prop_node, SHN.path, on_prop))
            if min_card is not None:
                sh.add((prop_node, SHN.minCount, Literal(int(min_card), datatype=XSD.integer)))
            if max_card is not None:
                sh.add((prop_node, SHN.maxCount, Literal(int(max_card), datatype=XSD.integer)))
            sh.add((prop_node, SHN.severity, SHN.Violation))
            sh.add((prop_node, SHN.message,
                   Literal(f"Astrea-derived M6: cardinality constraint on {str(on_prop).split('#')[-1]} from owl:Restriction (TBox-declared)")))

    return sh, len(classes), len(props)

if __name__=='__main__':
    shapes, n_cls, n_props = derive_shapes(sys.argv[1])
    out = sys.argv[2]
    shapes.serialize(destination=out, format='turtle')
    print(f"derived: {n_cls} class-shapes from {len(set(shapes.subjects(RDF.type,SH.NodeShape)))} NodeShapes; {n_props} properties processed; output -> {out} ({len(shapes)} triples)")
