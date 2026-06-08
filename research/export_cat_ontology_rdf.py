from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, XSD


BASE = Path(__file__).resolve().parent
CATBOOK = BASE.parent
DATA = CATBOOK / "data"
GRAPH_JSON = BASE / "cat_ontology_graph.json"
TTL_OUT = DATA / "catbook_ontology.ttl"
OWL_OUT = DATA / "catbook_ontology.owl"
SHAPES_OUT = DATA / "catbook_shapes.ttl"

CAT = Namespace("https://jarvis.local/catbook/ontology#")
RES = Namespace("https://jarvis.local/catbook/resource/")

RELATION_PROPERTIES = {
    "STARTS_WITH": "startsWith",
    "SHOWS_SIGNAL": "showsSignal",
    "HAS_TOPIC": "hasTopic",
    "MAPS_TO_PART": "mapsToPart",
    "COVERS": "covers",
    "MAY_INDICATE": "mayIndicate",
    "OBSERVE_WITH": "observeWith",
    "SUGGESTS": "suggests",
    "SUPPORTS": "supports",
    "REQUIRES_RECORD": "requiresRecord",
    "CONSULT_WHEN": "consultWhen",
    "PREVENTS": "prevents",
    "HAS_EVIDENCE": "hasEvidence",
}

SAFETY_RELATIONS = {"REQUIRES_RECORD", "CONSULT_WHEN", "PREVENTS"}
GUIDANCE_RELATIONS = {
    "MAY_INDICATE",
    "OBSERVE_WITH",
    "SUGGESTS",
    "SUPPORTS",
    "REQUIRES_RECORD",
    "CONSULT_WHEN",
    "PREVENTS",
}


def load_graph_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resource_uri(identifier: str) -> URIRef:
    return URIRef(str(RES) + quote(identifier, safe=""))


def class_uri(class_id: str) -> URIRef:
    return CAT[class_id]


def prop_uri(relation_id: str) -> URIRef:
    return CAT[RELATION_PROPERTIES.get(relation_id, relation_id[:1].lower() + relation_id[1:])]


def literal_or_none(value, datatype=None):
    if value is None:
        return None
    return Literal(value, datatype=datatype)


def add_literal(graph: Graph, subject: URIRef, predicate: URIRef, value, datatype=None) -> None:
    literal = literal_or_none(value, datatype=datatype)
    if literal is not None:
        graph.add((subject, predicate, literal))


def bind_namespaces(graph: Graph) -> None:
    graph.bind("cat", CAT)
    graph.bind("res", RES)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("owl", OWL)
    graph.bind("xsd", XSD)
    graph.bind("dcterms", DCTERMS)
    graph.bind("sh", SH)


def add_schema(graph: Graph, payload: dict) -> None:
    ontology = CAT.CatbookOntology
    graph.add((ontology, RDF.type, OWL.Ontology))
    graph.add((ontology, DCTERMS.title, Literal(payload["meta"].get("title", "냥톨로지"))))
    graph.add((ontology, DCTERMS.description, Literal(payload["meta"].get("description", ""))))
    graph.add((ontology, OWL.versionInfo, Literal(payload["meta"].get("schema_version", "unknown"))))
    graph.add((ontology, DCTERMS.created, Literal(datetime.now(timezone.utc).isoformat(), datatype=XSD.dateTime)))
    graph.add((ontology, DCTERMS.source, Literal("catbook/research/cat_ontology_graph.json")))

    for helper_class, label in [
        (CAT.CatbookConcept, "냥톨로지 개념"),
        (CAT.SafetySensitiveConcept, "안전 민감 개념"),
        (CAT.RelationAssertion, "관계 단언"),
    ]:
        graph.add((helper_class, RDF.type, OWL.Class))
        graph.add((helper_class, RDFS.label, Literal(label)))

    graph.add((CAT.SafetySensitiveConcept, RDFS.subClassOf, CAT.CatbookConcept))

    for class_id, info in payload["classes"].items():
        uri = class_uri(class_id)
        graph.add((uri, RDF.type, OWL.Class))
        graph.add((uri, RDFS.label, Literal(info.get("label", class_id))))
        add_literal(graph, uri, RDFS.comment, info.get("description"))
        add_literal(graph, uri, CAT.color, info.get("color"))
        if class_id in {"HealthObservation", "SafetyRisk"}:
            graph.add((uri, RDFS.subClassOf, CAT.SafetySensitiveConcept))
        else:
            graph.add((uri, RDFS.subClassOf, CAT.CatbookConcept))

    for prop, label in [
        (CAT.nodeId, "원본 노드 ID"),
        (CAT.sourceId, "원본 콘텐츠 ID"),
        (CAT.classId, "원본 클래스 ID"),
        (CAT.color, "시각화 색상"),
        (CAT.summary, "요약"),
        (CAT.beginnerGuide, "초보자 안내"),
        (CAT.observePoint, "관찰 포인트"),
        (CAT.keyword, "키워드"),
        (CAT.firstCheck, "첫 확인 질문"),
        (CAT.question, "상황 질문"),
        (CAT.mediaFamily, "콘텐츠 유형"),
        (CAT.watchUrl, "시청 URL"),
        (CAT.thumbnailUrl, "썸네일 URL"),
        (CAT.durationMinutes, "길이(분)"),
        (CAT.viewCount, "조회 수"),
        (CAT.evidenceCount, "근거 콘텐츠 수"),
        (CAT.confidence, "관계 신뢰 수준"),
        (CAT.safety, "안전 주석"),
        (CAT.score, "매칭 점수"),
        (CAT.matchHit, "매칭 히트"),
        (CAT.isMedicalSensitive, "의료 민감 여부"),
        (CAT.nonDiagnosticOnly, "진단/처방 금지"),
    ]:
        graph.add((prop, RDF.type, OWL.DatatypeProperty))
        graph.add((prop, RDFS.label, Literal(label)))

    graph.add((CAT.url, RDF.type, OWL.AnnotationProperty))
    graph.add((CAT.url, RDFS.label, Literal("대표 URL")))

    for helper_prop, label in [
        (CAT.semanticLink, "의미 관계"),
        (CAT.guidanceRelation, "돌봄 안내 관계"),
        (CAT.safetyGuidance, "안전 안내 관계"),
    ]:
        graph.add((helper_prop, RDF.type, OWL.ObjectProperty))
        graph.add((helper_prop, RDFS.label, Literal(label)))

    for relation_id, label in payload["relations"].items():
        uri = prop_uri(relation_id)
        graph.add((uri, RDF.type, OWL.ObjectProperty))
        graph.add((uri, RDFS.label, Literal(label)))
        graph.add((uri, RDFS.subPropertyOf, CAT.semanticLink))
        if relation_id in GUIDANCE_RELATIONS:
            graph.add((uri, RDFS.subPropertyOf, CAT.guidanceRelation))
        if relation_id in SAFETY_RELATIONS:
            graph.add((uri, RDFS.subPropertyOf, CAT.safetyGuidance))

    graph.add((CAT.hasEvidence, RDFS.domain, CAT.CatbookConcept))
    graph.add((CAT.hasEvidence, RDFS.range, CAT.Source))
    graph.add((CAT.hasTopic, RDFS.domain, CAT.Source))
    graph.add((CAT.hasTopic, RDFS.range, CAT.Topic))
    graph.add((CAT.requiresRecord, RDFS.domain, CAT.HealthObservation))
    graph.add((CAT.requiresRecord, RDFS.range, CAT.CareAction))

    restriction = BNode()
    graph.add((restriction, RDF.type, OWL.Restriction))
    graph.add((restriction, OWL.onProperty, CAT.requiresRecord))
    graph.add((restriction, OWL.someValuesFrom, CAT.CareAction))
    graph.add((CAT.HealthObservation, RDFS.subClassOf, restriction))


def add_node(graph: Graph, node: dict) -> URIRef:
    uri = resource_uri(node["id"])
    cls = class_uri(node["class"])
    graph.add((uri, RDF.type, cls))
    graph.add((uri, RDF.type, CAT.CatbookConcept))
    if node["class"] in {"HealthObservation", "SafetyRisk"}:
        graph.add((uri, RDF.type, CAT.SafetySensitiveConcept))
    graph.add((uri, RDFS.label, Literal(node.get("label", node["id"]))))
    graph.add((uri, CAT.nodeId, Literal(node["id"])))
    graph.add((uri, CAT.classId, Literal(node["class"])))
    add_literal(graph, uri, RDFS.comment, node.get("summary"))
    add_literal(graph, uri, CAT.summary, node.get("summary"))
    add_literal(graph, uri, CAT.beginnerGuide, node.get("beginner"))
    add_literal(graph, uri, CAT.color, node.get("color"))
    add_literal(graph, uri, CAT.url, node.get("url"), datatype=XSD.anyURI)
    add_literal(graph, uri, CAT.watchUrl, node.get("watch_url"), datatype=XSD.anyURI)
    add_literal(graph, uri, CAT.thumbnailUrl, node.get("thumbnail_url"), datatype=XSD.anyURI)
    add_literal(graph, uri, CAT.mediaFamily, node.get("media_family"))
    add_literal(graph, uri, CAT.durationMinutes, node.get("duration_min"), datatype=XSD.decimal)
    add_literal(graph, uri, CAT.viewCount, node.get("view_count"), datatype=XSD.integer)
    add_literal(graph, uri, CAT.evidenceCount, node.get("evidence_count"), datatype=XSD.integer)

    for point in node.get("observe", []):
        graph.add((uri, CAT.observePoint, Literal(point)))
    for keyword in node.get("keywords", []):
        graph.add((uri, CAT.keyword, Literal(keyword)))
    for check in node.get("checks", []):
        graph.add((uri, CAT.firstCheck, Literal(check)))

    if node.get("medical") or node["class"] in {"HealthObservation", "SafetyRisk"}:
        graph.add((uri, CAT.isMedicalSensitive, Literal(bool(node.get("medical")), datatype=XSD.boolean)))
        graph.add((uri, CAT.nonDiagnosticOnly, Literal(True, datatype=XSD.boolean)))

    return uri


def add_content_item(graph: Graph, item: dict) -> URIRef | None:
    content_id = item.get("id")
    if not content_id:
        return None
    uri = resource_uri(f"source:{content_id}")
    graph.add((uri, RDF.type, CAT.Source))
    graph.add((uri, RDF.type, CAT.CatbookConcept))
    graph.add((uri, RDFS.label, Literal(item.get("title") or item.get("default_title") or content_id)))
    graph.add((uri, CAT.sourceId, Literal(content_id)))
    graph.add((uri, CAT.nodeId, Literal(f"source:{content_id}")))
    graph.add((uri, CAT.classId, Literal("Source")))
    graph.add((uri, RDFS.comment, Literal("영상/숏폼 공개 메타 근거")))
    add_literal(graph, uri, CAT.url, item.get("url"), datatype=XSD.anyURI)
    add_literal(graph, uri, CAT.watchUrl, item.get("watch_url"), datatype=XSD.anyURI)
    add_literal(graph, uri, CAT.thumbnailUrl, item.get("thumbnail_url"), datatype=XSD.anyURI)
    add_literal(graph, uri, CAT.mediaFamily, item.get("media_family"))
    add_literal(graph, uri, CAT.durationMinutes, item.get("duration_min"), datatype=XSD.decimal)
    add_literal(graph, uri, CAT.viewCount, item.get("view_count"), datatype=XSD.integer)

    for topic in item.get("topics", []):
        topic_uri = resource_uri(f"topic:{topic}")
        graph.add((topic_uri, RDF.type, CAT.Topic))
        graph.add((topic_uri, RDFS.label, Literal(topic)))
        graph.add((topic_uri, CAT.nodeId, Literal(f"topic:{topic}")))
        graph.add((topic_uri, CAT.classId, Literal("Topic")))
        graph.add((uri, CAT.hasTopic, topic_uri))

    return uri


def add_edge(graph: Graph, edge: dict) -> None:
    source = resource_uri(edge["source"])
    target = resource_uri(edge["target"])
    predicate = prop_uri(edge["relation"])
    graph.add((source, predicate, target))

    assertion = resource_uri(edge["id"])
    graph.add((assertion, RDF.type, CAT.RelationAssertion))
    graph.add((assertion, RDF.subject, source))
    graph.add((assertion, RDF.predicate, predicate))
    graph.add((assertion, RDF.object, target))
    graph.add((assertion, RDFS.label, Literal(edge.get("label", edge["relation"]))))
    graph.add((assertion, CAT.nodeId, Literal(edge["id"])))
    graph.add((assertion, CAT.confidence, Literal(edge.get("confidence", "unspecified"))))
    add_literal(graph, assertion, CAT.safety, edge.get("safety"))
    add_literal(graph, assertion, CAT.score, edge.get("score"), datatype=XSD.decimal)
    for hit in edge.get("hits", []):
        graph.add((assertion, CAT.matchHit, Literal(hit)))


def add_content_matches(graph: Graph, payload: dict) -> None:
    for item in payload.get("content_index", []):
        source = add_content_item(graph, item)
        if source is None:
            continue
        for index, match in enumerate(item.get("matched_concepts", [])):
            concept_id = match.get("id")
            if not concept_id:
                continue
            concept = resource_uri(concept_id)
            graph.add((concept, CAT.hasEvidence, source))

            assertion_id = f"match:{item.get('id')}:{index}:{concept_id}"
            assertion = resource_uri(assertion_id)
            graph.add((assertion, RDF.type, CAT.RelationAssertion))
            graph.add((assertion, RDF.subject, concept))
            graph.add((assertion, RDF.predicate, CAT.hasEvidence))
            graph.add((assertion, RDF.object, source))
            graph.add((assertion, RDFS.label, Literal("개념과 전체 콘텐츠 인덱스 근거 연결")))
            graph.add((assertion, CAT.nodeId, Literal(assertion_id)))
            graph.add((assertion, CAT.confidence, Literal("metadata_title")))
            add_literal(graph, assertion, CAT.score, match.get("score"), datatype=XSD.decimal)
            for hit in match.get("hits", []):
                graph.add((assertion, CAT.matchHit, Literal(hit)))


def enrich_scenarios(graph: Graph, payload: dict) -> None:
    for scenario in payload.get("scenarios", []):
        uri = resource_uri(scenario["id"])
        graph.add((uri, RDF.type, CAT.Scenario))
        graph.add((uri, CAT.question, Literal(scenario.get("question", ""))))
        for check in scenario.get("first_checks", []):
            graph.add((uri, CAT.firstCheck, Literal(check)))


def build_data_graph(payload: dict) -> Graph:
    graph = Graph()
    bind_namespaces(graph)
    add_schema(graph, payload)
    for node in payload["nodes"]:
        add_node(graph, node)
    add_content_matches(graph, payload)
    enrich_scenarios(graph, payload)
    for edge in payload["edges"]:
        add_edge(graph, edge)
    return graph


def property_shape(
    graph: Graph,
    node_shape: URIRef,
    path: URIRef,
    *,
    min_count: int | None = None,
    max_count: int | None = None,
    datatype: URIRef | None = None,
    class_: URIRef | None = None,
    has_value: Literal | None = None,
    message: str | None = None,
) -> None:
    shape = BNode()
    graph.add((node_shape, SH.property, shape))
    graph.add((shape, SH.path, path))
    if min_count is not None:
        graph.add((shape, SH.minCount, Literal(min_count, datatype=XSD.integer)))
    if max_count is not None:
        graph.add((shape, SH.maxCount, Literal(max_count, datatype=XSD.integer)))
    if datatype is not None:
        graph.add((shape, SH.datatype, datatype))
    if class_ is not None:
        graph.add((shape, SH["class"], class_))
    if has_value is not None:
        graph.add((shape, SH.hasValue, has_value))
    if message is not None:
        graph.add((shape, SH.message, Literal(message)))


def build_shapes_graph() -> Graph:
    shapes = Graph()
    bind_namespaces(shapes)

    concept_shape = CAT.CatbookConceptShape
    shapes.add((concept_shape, RDF.type, SH.NodeShape))
    shapes.add((concept_shape, SH.targetClass, CAT.CatbookConcept))
    property_shape(shapes, concept_shape, RDFS.label, min_count=1, datatype=XSD.string)
    property_shape(shapes, concept_shape, CAT.nodeId, min_count=1, datatype=XSD.string)
    property_shape(shapes, concept_shape, CAT.classId, min_count=1, datatype=XSD.string)

    source_shape = CAT.SourceShape
    shapes.add((source_shape, RDF.type, SH.NodeShape))
    shapes.add((source_shape, SH.targetClass, CAT.Source))
    property_shape(shapes, source_shape, RDFS.label, min_count=1, datatype=XSD.string)
    property_shape(shapes, source_shape, CAT.sourceId, min_count=1, datatype=XSD.string)
    property_shape(shapes, source_shape, CAT.url, min_count=1, datatype=XSD.anyURI)
    property_shape(shapes, source_shape, CAT.mediaFamily, min_count=1, datatype=XSD.string)

    scenario_shape = CAT.ScenarioShape
    shapes.add((scenario_shape, RDF.type, SH.NodeShape))
    shapes.add((scenario_shape, SH.targetClass, CAT.Scenario))
    property_shape(shapes, scenario_shape, RDFS.label, min_count=1, datatype=XSD.string)
    property_shape(shapes, scenario_shape, RDFS.comment, min_count=1, datatype=XSD.string)
    property_shape(shapes, scenario_shape, CAT.startsWith, min_count=1)

    topic_shape = CAT.TopicShape
    shapes.add((topic_shape, RDF.type, SH.NodeShape))
    shapes.add((topic_shape, SH.targetClass, CAT.Topic))
    property_shape(shapes, topic_shape, RDFS.label, min_count=1, datatype=XSD.string)
    property_shape(shapes, topic_shape, CAT.nodeId, min_count=1, datatype=XSD.string)
    property_shape(shapes, topic_shape, CAT.classId, min_count=1, datatype=XSD.string)

    health_shape = CAT.HealthObservationShape
    shapes.add((health_shape, RDF.type, SH.NodeShape))
    shapes.add((health_shape, SH.targetClass, CAT.HealthObservation))
    property_shape(shapes, health_shape, CAT.requiresRecord, min_count=1, class_=CAT.CareAction)
    property_shape(
        shapes,
        health_shape,
        CAT.isMedicalSensitive,
        min_count=1,
        has_value=Literal(True, datatype=XSD.boolean),
        message="건강 관찰 노드는 의료 민감 표시를 가져야 한다.",
    )
    property_shape(
        shapes,
        health_shape,
        CAT.nonDiagnosticOnly,
        min_count=1,
        has_value=Literal(True, datatype=XSD.boolean),
        message="건강 관찰 노드는 진단/처방 금지 플래그를 가져야 한다.",
    )

    sensitive_shape = CAT.SafetySensitiveConceptShape
    shapes.add((sensitive_shape, RDF.type, SH.NodeShape))
    shapes.add((sensitive_shape, SH.targetClass, CAT.SafetySensitiveConcept))
    property_shape(
        shapes,
        sensitive_shape,
        CAT.nonDiagnosticOnly,
        min_count=1,
        has_value=Literal(True, datatype=XSD.boolean),
    )
    property_shape(shapes, sensitive_shape, CAT.diagnosis, max_count=0)
    property_shape(shapes, sensitive_shape, CAT.prescribes, max_count=0)

    assertion_shape = CAT.RelationAssertionShape
    shapes.add((assertion_shape, RDF.type, SH.NodeShape))
    shapes.add((assertion_shape, SH.targetClass, CAT.RelationAssertion))
    property_shape(shapes, assertion_shape, CAT.nodeId, min_count=1, datatype=XSD.string)
    property_shape(shapes, assertion_shape, RDF.subject, min_count=1)
    property_shape(shapes, assertion_shape, RDF.predicate, min_count=1)
    property_shape(shapes, assertion_shape, RDF.object, min_count=1)
    property_shape(shapes, assertion_shape, CAT.confidence, min_count=1, datatype=XSD.string)

    return shapes


def export(payload_path: Path, ttl_out: Path, owl_out: Path, shapes_out: Path) -> dict:
    payload = load_graph_payload(payload_path)
    ttl_out.parent.mkdir(parents=True, exist_ok=True)
    shapes_out.parent.mkdir(parents=True, exist_ok=True)

    data_graph = build_data_graph(payload)
    shapes_graph = build_shapes_graph()

    data_graph.serialize(destination=str(ttl_out), format="turtle")
    data_graph.serialize(destination=str(owl_out), format="xml")
    shapes_graph.serialize(destination=str(shapes_out), format="turtle")

    return {
        "status": "ok",
        "source": str(payload_path.relative_to(CATBOOK)),
        "ttl": str(ttl_out.relative_to(CATBOOK)),
        "owl": str(owl_out.relative_to(CATBOOK)),
        "shapes": str(shapes_out.relative_to(CATBOOK)),
        "triples": len(data_graph),
        "shape_triples": len(shapes_graph),
        "classes": len(payload.get("classes", {})),
        "relations": len(payload.get("relations", {})),
        "nodes": len(payload.get("nodes", [])),
        "content_items": len(payload.get("content_index", [])),
        "edges": len(payload.get("edges", [])),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export catbook JSON ontology to RDF/OWL/SHACL artifacts.")
    parser.add_argument("--graph", type=Path, default=GRAPH_JSON)
    parser.add_argument("--ttl", type=Path, default=TTL_OUT)
    parser.add_argument("--owl", type=Path, default=OWL_OUT)
    parser.add_argument("--shapes", type=Path, default=SHAPES_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = export(args.graph, args.ttl, args.owl, args.shapes)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
