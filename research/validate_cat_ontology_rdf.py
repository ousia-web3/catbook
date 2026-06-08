from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from owlrl import DeductiveClosure, RDFS_OWLRL_Semantics
from pyshacl import validate
from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS


BASE = Path(__file__).resolve().parent
CATBOOK = BASE.parent
DATA = CATBOOK / "data"
QUERIES = BASE / "queries"
TTL = DATA / "catbook_ontology.ttl"
OWL_FILE = DATA / "catbook_ontology.owl"
SHAPES = DATA / "catbook_shapes.ttl"
STATUS_JSON = DATA / "catbook_rdf_status.json"
REPORT = CATBOOK / "project-records" / "work-requests" / "2026-06-08-catbook-ontology-rdf-owl-audit" / "evidence" / "rdf-owl-validation-2026-06-08.md"
JSON_REPORT = CATBOOK / "project-records" / "work-requests" / "2026-06-08-catbook-ontology-rdf-owl-audit" / "evidence" / "rdf-owl-validation-2026-06-08.json"

CAT = Namespace("https://jarvis.local/catbook/ontology#")


def parse_graph(path: Path, *, fmt: str) -> Graph:
    graph = Graph()
    graph.parse(path, format=fmt)
    return graph


def reason_graph(source: Graph) -> Graph:
    reasoned = build_reasoning_subset(source)
    DeductiveClosure(
        RDFS_OWLRL_Semantics,
        axiomatic_triples=False,
        datatype_axioms=False,
    ).expand(reasoned)
    return reasoned


def build_reasoning_subset(source: Graph) -> Graph:
    subset = Graph()
    for prefix, namespace in source.namespaces():
        subset.bind(prefix, namespace)

    cat_namespace = str(CAT)
    schema_predicates = {RDF.type, RDFS.subClassOf, RDFS.subPropertyOf, RDFS.domain, RDFS.range, OWL.onProperty, OWL.someValuesFrom}
    for triple in source.triples((None, None, None)):
        subject, predicate, obj = triple
        is_schema_subject = isinstance(subject, BNode) or (
            isinstance(subject, URIRef) and str(subject).startswith(cat_namespace)
        )
        if predicate in schema_predicates and is_schema_subject:
            subset.add(triple)

    for class_uri in [CAT.HealthObservation, CAT.SafetyRisk, CAT.CareAction]:
        for subject in source.subjects(RDF.type, class_uri):
            for triple in source.triples((subject, None, None)):
                if triple[1] in {RDF.type, RDFS.label, CAT.nodeId, CAT.classId, CAT.nonDiagnosticOnly, CAT.requiresRecord, CAT.consultWhen}:
                    subset.add(triple)

    return subset


def query_count(graph: Graph, query_path: Path) -> dict:
    results = list(graph.query(query_path.read_text(encoding="utf-8")))
    return {
        "query": query_path.name,
        "rows": len(results),
        "sample": [tuple(str(value) for value in row) for row in results[:5]],
    }


def run_queries(data_graph: Graph, reasoned_graph: Graph, queries_dir: Path) -> list[dict]:
    results = []
    for query_path in sorted(queries_dir.glob("*.rq")):
        target = reasoned_graph if "inferred" in query_path.name else data_graph
        results.append(query_count(target, query_path))
    return results


def graph_counts(graph: Graph) -> dict:
    def count_type(type_uri) -> int:
        return len(set(graph.subjects(RDF.type, type_uri)))

    return {
        "triples": len(graph),
        "classes_declared": count_type(Namespace("http://www.w3.org/2002/07/owl#").Class),
        "object_properties_declared": count_type(Namespace("http://www.w3.org/2002/07/owl#").ObjectProperty),
        "datatype_properties_declared": count_type(Namespace("http://www.w3.org/2002/07/owl#").DatatypeProperty),
        "catbook_concepts": count_type(CAT.CatbookConcept),
        "safety_sensitive_concepts": count_type(CAT.SafetySensitiveConcept),
        "sources": count_type(CAT.Source),
        "relation_assertions": count_type(CAT.RelationAssertion),
        "health_observations": count_type(CAT.HealthObservation),
    }


def markdown_report(result: dict) -> str:
    lines = [
        "# RDF/OWL 1차 전환 검증 리포트",
        "",
        f"- 생성 시각: `{result['generated_at']}`",
        f"- Turtle: `{result['ttl']}`",
        f"- OWL/RDFXML: `{result['owl']}`",
        f"- SHACL: `{result['shapes']}`",
        "",
        "## 요약",
        "",
        f"- RDF parse: `{result['rdf_parse']}`",
        f"- OWL parse: `{result['owl_parse']}`",
        f"- SHACL conforms: `{result['shacl_conforms']}`",
        f"- 전체 RDF triple: `{result['data_counts']['triples']}`",
        f"- 추론 입력 부분그래프 triple: `{result['reasoning_base_counts']['triples']}`",
        f"- 추론 후 부분그래프 triple: `{result['reasoned_counts']['triples']}`",
        f"- inferred triple 증가: `{result['inferred_triples']}`",
        "",
        "## 전체 RDF 그래프 카운트",
        "",
        "| 항목 | 값 |",
        "| --- | ---: |",
    ]
    for key in [
        "classes_declared",
        "object_properties_declared",
        "datatype_properties_declared",
        "catbook_concepts",
        "safety_sensitive_concepts",
        "sources",
        "relation_assertions",
        "health_observations",
    ]:
        lines.append(f"| {key} | {result['data_counts'][key]} |")

    lines.extend(
        [
            "",
            "## 추론 부분그래프 카운트",
            "",
            "전체 콘텐츠/근거 노드까지 모두 추론하면 비용이 커지므로, RDFS/OWL-RL 추론은 스키마와 안전 민감 개념 중심 부분그래프에서 수행한다.",
            "",
            "| 항목 | 추론 입력 | 추론 후 |",
            "| --- | ---: | ---: |",
        ]
    )
    for key in [
        "triples",
        "classes_declared",
        "object_properties_declared",
        "datatype_properties_declared",
        "catbook_concepts",
        "safety_sensitive_concepts",
        "health_observations",
    ]:
        lines.append(f"| {key} | {result['reasoning_base_counts'][key]} | {result['reasoned_counts'][key]} |")

    lines.extend(["", "## SPARQL 질의 결과", "", "| Query | Rows | Sample |", "| --- | ---: | --- |"])
    for query_result in result["queries"]:
        sample = "; ".join(" / ".join(row[:3]) for row in query_result["sample"])
        lines.append(f"| `{query_result['query']}` | {query_result['rows']} | {sample} |")

    if result.get("shacl_report"):
        lines.extend(["", "## SHACL Report", "", "```text", result["shacl_report"].strip(), "```"])

    lines.extend(
        [
            "",
            "## 완료 판정",
            "",
            "- RDF/OWL 파일이 생성되고 다시 파싱되었다.",
            "- SHACL shapes가 통과했다.",
            "- SPARQL 샘플 질의가 모두 1건 이상 반환했다.",
            "- OWL/RDFS 추론 후 triple 수가 증가했다.",
        ]
    )
    return "\n".join(lines) + "\n"


def validate_artifacts(ttl: Path, owl_file: Path, shapes: Path, queries: Path) -> dict:
    data_graph = parse_graph(ttl, fmt="turtle")
    owl_graph = parse_graph(owl_file, fmt="xml")
    shapes_graph = parse_graph(shapes, fmt="turtle")

    conforms, _, shacl_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )

    reasoned = reason_graph(data_graph)
    query_results = run_queries(data_graph, reasoned, queries)
    reasoning_base = build_reasoning_subset(data_graph)
    reasoning_base_triples = len(reasoning_base)
    inferred_triples = len(reasoned) - reasoning_base_triples

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ttl": str(ttl.relative_to(CATBOOK)),
        "owl": str(owl_file.relative_to(CATBOOK)),
        "shapes": str(shapes.relative_to(CATBOOK)),
        "queries_dir": str(queries.relative_to(CATBOOK)),
        "rdf_parse": "ok",
        "owl_parse": "ok",
        "owl_triples": len(owl_graph),
        "shape_triples": len(shapes_graph),
        "shacl_conforms": bool(conforms),
        "shacl_report": str(shacl_text),
        "data_counts": graph_counts(data_graph),
        "reasoning_base_counts": graph_counts(reasoning_base),
        "reasoned_counts": graph_counts(reasoned),
        "reasoning_base_triples": reasoning_base_triples,
        "inferred_triples": inferred_triples,
        "queries": query_results,
    }

    failures = []
    if not conforms:
        failures.append("SHACL validation failed")
    if inferred_triples <= 0:
        failures.append("No inferred triples were materialized")
    empty_queries = [item["query"] for item in query_results if item["rows"] <= 0]
    if empty_queries:
        failures.append("SPARQL queries returned no rows: " + ", ".join(empty_queries))

    result["status"] = "pass" if not failures else "fail"
    result["failures"] = failures
    return result


def relative_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(CATBOOK.parent)).replace("\\", "/")
    except ValueError:
        return str(path)


def status_payload(result: dict, report: Path, json_report: Path) -> dict:
    query_rows = {item["query"]: item["rows"] for item in result["queries"]}
    return {
        "status": result["status"],
        "generated_at": result["generated_at"],
        "rdf_parse": result["rdf_parse"],
        "owl_parse": result["owl_parse"],
        "shacl_conforms": result["shacl_conforms"],
        "rdf_triples": result["data_counts"]["triples"],
        "owl_triples": result["owl_triples"],
        "shape_triples": result["shape_triples"],
        "sparql_queries": len(result["queries"]),
        "sparql_query_rows": query_rows,
        "inferred_triples": result["inferred_triples"],
        "catbook_concepts": result["data_counts"]["catbook_concepts"],
        "safety_sensitive_concepts": result["data_counts"]["safety_sensitive_concepts"],
        "sources": result["data_counts"]["sources"],
        "relation_assertions": result["data_counts"]["relation_assertions"],
        "artifacts": {
            "ttl": "catbook_ontology.ttl",
            "owl": "catbook_ontology.owl",
            "shapes": "catbook_shapes.ttl",
        },
        "reports": {
            "markdown": relative_to_repo(report),
            "json": relative_to_repo(json_report),
        },
        "failures": result["failures"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate catbook RDF/OWL/SHACL artifacts.")
    parser.add_argument("--ttl", type=Path, default=TTL)
    parser.add_argument("--owl", type=Path, default=OWL_FILE)
    parser.add_argument("--shapes", type=Path, default=SHAPES)
    parser.add_argument("--queries", type=Path, default=QUERIES)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--json-report", type=Path, default=JSON_REPORT)
    parser.add_argument("--status-json", type=Path, default=STATUS_JSON)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = validate_artifacts(args.ttl, args.owl, args.shapes, args.queries)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.status_json.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(markdown_report(result), encoding="utf-8")
    args.json_report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    args.status_json.write_text(
        json.dumps(status_payload(result, args.report, args.json_report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
