#!/usr/bin/env python
"""Local-only Catbook ontology refresh API.

This server intentionally binds to localhost by default. It lets the static
ontology pages trigger the same refresh pipeline an operator would run by hand.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCRIPT = Path(__file__).resolve()
CATBOOK = SCRIPT.parents[1]
REPO = SCRIPT.parents[2]
STATUS_PATH = CATBOOK / "data" / "ontology_refresh_status.json"
REQUEST_ID = "youtube-ontology-refresh-button"
LOCK = threading.Lock()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def tail(text: str, limit: int = 4000) -> str:
    text = text or ""
    return text[-limit:]


def read_status() -> dict[str, Any]:
    if not STATUS_PATH.is_file():
        return {
            "status": "idle",
            "updated_at": now_iso(),
            "detail": "Refresh has not run yet.",
        }
    try:
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "status": "unknown",
            "updated_at": now_iso(),
            "detail": "Status file exists but could not be parsed.",
        }


def write_status(payload: dict[str, Any]) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_command(command: list[str], stage: str, timeout: int = 900) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=REPO,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    elapsed = round(time.monotonic() - started, 2)
    result = {
        "stage": stage,
        "command": command,
        "returncode": completed.returncode,
        "elapsed_seconds": elapsed,
        "stdout_tail": tail(completed.stdout),
        "stderr_tail": tail(completed.stderr),
    }
    if completed.returncode != 0:
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    return result


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_refresh() -> dict[str, Any]:
    stages: list[dict[str, Any]] = []
    write_status(
        {
            "status": "running",
            "updated_at": now_iso(),
            "detail": "Collecting public YouTube metadata and rebuilding Catbook ontology.",
            "stages": stages,
        }
    )

    python = "python"
    pipeline = [
        ([python, "catbook/research/fetch_youtube_meta_all_tabs.py"], "fetch_youtube_meta", 900),
        (
            [
                python,
                "-m",
                "py_compile",
                "catbook/research/build_cat_ontology_graph.py",
                "catbook/research/export_cat_ontology_rdf.py",
                "catbook/research/validate_cat_ontology_rdf.py",
            ],
            "compile_pipeline",
            120,
        ),
        ([python, "catbook/research/build_cat_ontology_graph.py"], "build_ontology_graph", 300),
        ([python, "catbook/research/validate_cat_ontology_rdf.py"], "validate_rdf_owl", 300),
    ]

    try:
        for command, stage, timeout in pipeline:
            write_status(
                {
                    "status": "running",
                    "updated_at": now_iso(),
                    "detail": f"Running {stage}.",
                    "stages": stages,
                }
            )
            stages.append(run_command(command, stage, timeout))

        graph = load_json(CATBOOK / "research" / "cat_ontology_graph.json")
        rdf = load_json(CATBOOK / "data" / "catbook_rdf_status.json")
        latest_meta = sorted(
            (CATBOOK / "research").glob("youtube_meta_all_tabs_*.json"),
            key=lambda path: (path.stat().st_mtime, path.name),
            reverse=True,
        )
        summary = {
            "status": "done",
            "updated_at": now_iso(),
            "detail": "YouTube metadata, ontology graph, RDF/OWL, and SHACL validation refreshed.",
            "latest_meta": latest_meta[0].name if latest_meta else None,
            "graph": {
                "nodes": graph.get("stats", {}).get("node_count"),
                "edges": graph.get("stats", {}).get("edge_count"),
                "content_total": (
                    graph.get("stats", {}).get("content_total")
                    or graph.get("meta", {}).get("content_total")
                    or len(graph.get("content_index", []))
                ),
                "matched_content": graph.get("stats", {}).get("matched_content_count"),
                "generated_from": graph.get("meta", {}).get("generated_from"),
                "source_collected_at": graph.get("meta", {}).get("source_collected_at"),
            },
            "rdf": {
                "status": rdf.get("status"),
                "triples": rdf.get("rdf_triples"),
                "shacl": rdf.get("shacl_conforms"),
                "sparql_queries": rdf.get("sparql_queries"),
                "inferred_triples": rdf.get("inferred_triples"),
            },
            "stages": stages,
        }
        write_status(summary)
        return summary
    except Exception as error:  # noqa: BLE001 - surface operational failure as JSON.
        failure = {
            "status": "failed",
            "updated_at": now_iso(),
            "detail": "Refresh pipeline failed.",
            "error": str(error),
            "stages": stages,
        }
        write_status(failure)
        return failure


class RefreshHandler(BaseHTTPRequestHandler):
    server_version = "CatbookOntologyRefresh/1.0"

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/ontology-refresh/status":
            self.send_json(200, read_status())
            return
        if path == "/api/ontology-refresh":
            self.send_json(200, read_status())
            return
        self.send_json(404, {"status": "not_found", "detail": "Unknown endpoint."})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/ontology-refresh":
            self.send_json(404, {"status": "not_found", "detail": "Unknown endpoint."})
            return

        if not LOCK.acquire(blocking=False):
            status = read_status()
            status["status"] = "running"
            status["detail"] = "A refresh is already running."
            self.send_json(202, status)
            return

        try:
            self.send_json(200, run_refresh())
        finally:
            LOCK.release()

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[{now_iso()}] {self.address_string()} {format % args}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8798)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), RefreshHandler)
    print(f"Catbook ontology refresh API: http://{args.host}:{args.port}/api/ontology-refresh", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
