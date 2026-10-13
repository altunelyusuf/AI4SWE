# Getting started

One sitting, one small ontology, from nothing to a green gate. No prior knowledge of the method
is assumed. Roughly an hour.

If you only ever do this once, you will still have seen the thing that matters: **the gates decide,
not you.**

---

## Before you start

```bash
python3 -m pip install rdflib pyshacl
```

Then verify the package you just downloaded, because the method's first rule is that you check
rather than trust:

```bash
MF=$(ls MANIFEST_SHA256_v*.txt | sort -V | tail -1)
grep -v '^#' "$MF" | grep . | sed -E 's/[[:space:]]+\([0-9]+b\)[[:space:]]*$//' | sha256sum -c
```

Every line must say `OK`. If one does not, stop — you have a corrupted copy, and nothing below
would mean anything.

## 1. Make a package, not a file

A single `.ttl` on your desktop is not a package. A package is a directory that can prove things
about itself:

```
library/
  VERSION.txt
  01-ontologies/
    library_tbox_v1_0_0.ttl
  02-shacl/
    library_shacl_v1_0_1.ttl
  03-tooling/
```

```bash
mkdir -p library/01-ontologies library/02-shacl library/03-tooling
echo "1.0.0" > library/VERSION.txt
```

Two things are already doing work. `VERSION.txt` means the package has an identity that can be
compared. The `_v1_0_0` in the filename means a later edit cannot silently replace this one — you
will get a *second* file, and the difference will be visible.

## 2. Write the vocabulary

`library/01-ontologies/library_tbox_v1_0_0.ttl`:

```turtle
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix lib:  <http://example.org/library#> .

<http://example.org/library>
    a owl:Ontology ;
    owl:versionInfo "1.0.0" ;
    owl:versionIRI <http://example.org/library/1.0.0> .

lib:Book a owl:Class ;
    rdfs:label "Book"@en ;
    skos:definition "A published work held by the library."@en .

lib:hasISBN a owl:DatatypeProperty ;
    rdfs:domain lib:Book ;
    rdfs:range xsd:string .
```

`owl:versionInfo` must equal `VERSION.txt` and the version token in the filename. Three places,
one number. That redundancy is deliberate: it is what lets a gate catch a half-finished edit.

## 3. Write a constraint that can fail

`library/02-shacl/library_shacl_v1_0_1.ttl`:

```turtle
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix lib:  <http://example.org/library#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/library-shapes> a owl:Ontology ;
    owl:versionInfo "1.0.1" ;
    owl:versionIRI <http://example.org/library-shapes/1.0.1> ;
    rdfs:comment "Every class needs a definition."@en .

lib:ClassDefinitionShape
    a sh:NodeShape ;
    sh:targetClass owl:Class ;
    sh:property [ sh:path skos:definition ; sh:minCount 1 ;
                  sh:message "Every class needs a definition." ] .
```

## 4. Prove the constraint discriminates

This is the step people skip, and it is the one that matters. A constraint that has only ever seen
data it accepts tells you nothing.

Make a deliberately broken copy:

```bash
cp -r library /tmp/library-bad
cat >> /tmp/library-bad/01-ontologies/library_tbox_v1_0_0.ttl <<'EOF'

lib:Shelf a owl:Class ;
    rdfs:label "Shelf"@en .
EOF
```

`lib:Shelf` has no `skos:definition`. Now run both:

```bash
python3 - <<'PY'
import glob, rdflib, pyshacl, sys
for root in ('library', '/tmp/library-bad'):
    d = rdflib.Graph()
    for f in glob.glob(f'{root}/01-ontologies/*.ttl'): d.parse(f)
    s = rdflib.Graph()
    for f in glob.glob(f'{root}/02-shacl/*.ttl'): s.parse(f)
    ok, _, txt = pyshacl.validate(data_graph=d, shacl_graph=s, inference='rdfs')
    print(f'{root}: conforms={ok} violations={txt.count("Severity: sh:Violation")}')
PY
```

You must see:

```
library:           conforms=True  violations=0
/tmp/library-bad:  conforms=False violations=1
```

**If the bad copy also passes, your constraint is decorative.** Fix it before going further. Every
gate in this method carries a negative fixture for this reason, and the practice has caught real
defects in the method's own tooling — including a check whose pattern silently matched nothing.

## 5. Build the manifest

```bash
cd library && python3 - <<'PY'
import hashlib, os
files = sorted(os.path.relpath(os.path.join(r,f),'.')
               for r,d,fs in os.walk('.') for f in fs
               if not f.startswith('MANIFEST_SHA256') and '__pycache__' not in r)
lines = ['# library v1.0.0 — SHA-256 Manifest','']
for rel in files:
    b = open(rel,'rb').read()
    lines.append(f'{hashlib.sha256(b).hexdigest()}  {rel}  ({len(b)}b)')
open('MANIFEST_SHA256_v1_0_0.txt','w').write('\n'.join(lines)+'\n')
print('manifest:', len(files), 'files')
PY
```

Verify it, the same way you verified this package:

```bash
grep -v '^#' MANIFEST_SHA256_v1_0_0.txt | grep . \
  | sed -E 's/[[:space:]]+\([0-9]+b\)[[:space:]]*$//' | sha256sum -c
```

The manifest is now the package's own answer to "is this the thing I built?" — a question you will
want answered in six months, by someone who is not you.

## 6. Change something, and watch the rule bite

Add a class to the TBox. Now:

- `VERSION.txt` must become `1.1.0` — new content, new version
- the file must become `library_tbox_v1_1_0.ttl` — the old one is deleted
- `owl:versionInfo` must become `"1.1.0"`
- the manifest must be **regenerated**, never edited

This feels like ceremony the first time. It is the entire difference between a package you can
trust in six months and one you cannot, and the failure it prevents — a file changed under a fixed
version token — is the single most common defect this method catches, including in its own history.

## What you now have

A package that verifies its own integrity, a constraint proven able to fail, and a version scheme
where a change cannot hide. That is the method. Everything else is this, applied consistently and
at larger scale.

## Where to go next

- `HANDBOOK.md` — why each rule exists and which failure it prevents
- `USE_CASES.md` — whether it is worth it for your situation
- `01-vocabularies/knowledge_base_abox_v*.ttl` — 175 accumulated rules, each with its evidence
