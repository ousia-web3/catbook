const GRAPH_URL = "../research/cat_ontology_graph.json";
const RDF_STATUS_URL = "../data/catbook_rdf_status.json";
const HERO_IMAGE = "../assets/hero-window-cat-768.jpg";
const DEFAULT_CLASSES = [
  "Scenario",
  "CatSignal",
  "Need",
  "EnvironmentElement",
  "HealthObservation",
  "CareAction",
  "SafetyRisk",
  "Topic",
  "BookPart",
  "Chapter",
  "Source",
];

const SOURCE_LIMIT = 170;
const BEGINNER_SOURCE_LIMIT = 34;
const svgNS = "http://www.w3.org/2000/svg";

const state = {
  graph: null,
  nodeById: new Map(),
  contentById: new Map(),
  neighbors: new Map(),
  selectedId: "scenario:sudden_run",
  scenarioId: "scenario:sudden_run",
  mode: "beginner",
  query: "",
  visibleClasses: new Set(DEFAULT_CLASSES),
  transform: { x: 0, y: 0, scale: 1 },
  visibleNodeIds: new Set(),
  visibleEdges: [],
  rdfStatus: null,
};

const els = {
  statNodes: document.querySelector("#stat-nodes"),
  statEdges: document.querySelector("#stat-edges"),
  statMatched: document.querySelector("#stat-matched"),
  statBackend: document.querySelector("#stat-backend"),
  statRdf: document.querySelector("#stat-rdf"),
  rdfBadge: document.querySelector("#rdf-status-badge"),
  rdfTriples: document.querySelector("#rdf-triples"),
  rdfShapes: document.querySelector("#rdf-shapes"),
  rdfQueries: document.querySelector("#rdf-queries"),
  rdfInference: document.querySelector("#rdf-inference"),
  rdfGenerated: document.querySelector("#rdf-generated"),
  scenarioList: document.querySelector("#scenario-list"),
  clearScenario: document.querySelector("#clear-scenario"),
  classGrid: document.querySelector("#class-grid"),
  resetClasses: document.querySelector("#reset-classes"),
  modeButtons: Array.from(document.querySelectorAll(".mode-button")),
  search: document.querySelector("#graph-search"),
  zoomIn: document.querySelector("#zoom-in"),
  zoomOut: document.querySelector("#zoom-out"),
  zoomReset: document.querySelector("#zoom-reset"),
  visibleSummary: document.querySelector("#visible-summary"),
  selectionSummary: document.querySelector("#selection-summary"),
  svg: document.querySelector("#graph-svg"),
  graphLayer: document.querySelector("#graph-layer"),
  edgeLayer: document.querySelector("#edge-layer"),
  nodeLayer: document.querySelector("#node-layer"),
  loading: document.querySelector("#loading-state"),
  detailImage: document.querySelector("#detail-image"),
  detailClass: document.querySelector("#detail-class"),
  detailTitle: document.querySelector("#detail-title"),
  detailSummary: document.querySelector("#detail-summary"),
  detailChips: document.querySelector("#detail-chips"),
  observeBox: document.querySelector("#observe-box"),
  observeList: document.querySelector("#observe-list"),
  relationList: document.querySelector("#relation-list"),
  evidenceCount: document.querySelector("#evidence-count"),
  evidenceList: document.querySelector("#evidence-list"),
};

async function init() {
  try {
    const response = await fetch(GRAPH_URL);
    if (!response.ok) {
      throw new Error(`Graph fetch failed: ${response.status}`);
    }
    state.graph = await response.json();
    state.rdfStatus = await loadRdfStatus();
    buildIndexes();
    bindEvents();
    renderStaticControls();
    selectNode(state.selectedId);
    render();
    els.loading.hidden = true;
  } catch (error) {
    els.loading.textContent = "그래프 데이터를 불러오지 못했습니다";
    console.error(error);
  }
}

async function loadRdfStatus() {
  try {
    const response = await fetch(RDF_STATUS_URL);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.warn("RDF/OWL status unavailable", error);
    return null;
  }
}

function buildIndexes() {
  state.nodeById.clear();
  state.contentById.clear();
  state.neighbors.clear();

  state.graph.nodes.forEach((node) => {
    state.nodeById.set(node.id, node);
    state.neighbors.set(node.id, []);
  });

  state.graph.content_index.forEach((item) => {
    state.contentById.set(item.id, item);
  });

  state.graph.edges.forEach((edge) => {
    const source = state.nodeById.get(edge.source);
    const target = state.nodeById.get(edge.target);
    if (!source || !target) return;
    state.neighbors.get(edge.source).push({ edge, node: target, direction: "out" });
    state.neighbors.get(edge.target).push({ edge, node: source, direction: "in" });
  });
}

function bindEvents() {
  els.modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      els.modeButtons.forEach((item) => item.classList.toggle("active", item === button));
      render();
    });
  });

  els.search.addEventListener("input", () => {
    state.query = els.search.value.trim().toLocaleLowerCase("ko-KR");
    render();
  });

  els.clearScenario.addEventListener("click", () => {
    state.scenarioId = "";
    renderScenarios();
    render();
  });

  els.resetClasses.addEventListener("click", () => {
    state.visibleClasses = new Set(DEFAULT_CLASSES);
    renderClassFilters();
    render();
  });

  els.zoomIn.addEventListener("click", () => setZoom(state.transform.scale * 1.18));
  els.zoomOut.addEventListener("click", () => setZoom(state.transform.scale / 1.18));
  els.zoomReset.addEventListener("click", () => {
    state.transform = { x: 0, y: 0, scale: 1 };
    applyTransform();
  });

  els.svg.addEventListener("wheel", (event) => {
    event.preventDefault();
    const nextScale = state.transform.scale * (event.deltaY < 0 ? 1.08 : 0.92);
    setZoom(nextScale);
  }, { passive: false });

  let drag = null;
  els.svg.addEventListener("pointerdown", (event) => {
    const nodeElement = event.target.closest?.(".graph-node");
    if (nodeElement) return;
    drag = { x: event.clientX, y: event.clientY, ox: state.transform.x, oy: state.transform.y };
    els.svg.setPointerCapture(event.pointerId);
  });

  els.svg.addEventListener("pointermove", (event) => {
    if (!drag) return;
    state.transform.x = drag.ox + (event.clientX - drag.x);
    state.transform.y = drag.oy + (event.clientY - drag.y);
    applyTransform();
  });

  els.svg.addEventListener("pointerup", () => {
    drag = null;
  });
}

function renderStaticControls() {
  const stats = state.graph.stats;
  els.statNodes.textContent = formatNumber(stats.node_count);
  els.statEdges.textContent = formatNumber(stats.edge_count);
  els.statMatched.textContent = formatNumber(stats.matched_content_count);
  els.statBackend.textContent = backendLabel(state.graph.meta);
  renderRdfStatus();
  renderScenarios();
  renderClassFilters();
}

function renderRdfStatus() {
  const status = state.rdfStatus;
  const passed = status?.status === "pass";
  const label = status ? status.status : "미확인";

  els.statRdf.textContent = passed ? "Pass" : "-";
  els.rdfBadge.textContent = label;
  els.rdfBadge.classList.toggle("fail", status && !passed);
  els.rdfTriples.textContent = status ? formatNumber(status.rdf_triples) : "-";
  els.rdfShapes.textContent = status ? formatNumber(status.shape_triples) : "-";
  els.rdfQueries.textContent = status ? formatNumber(status.sparql_queries) : "-";
  els.rdfInference.textContent = status ? formatNumber(status.inferred_triples) : "-";
  els.rdfGenerated.textContent = status
    ? `${formatDateTime(status.generated_at)} 검증 · ${formatNumber(status.sources)}개 Source · ${formatNumber(status.relation_assertions)}개 assertion`
    : "검증 상태 파일을 찾지 못했습니다";
}

function renderScenarios() {
  els.scenarioList.replaceChildren(...state.graph.scenarios.map((scenario) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "scenario-button";
    button.classList.toggle("active", state.scenarioId === scenario.id);
    button.innerHTML = `<span><strong>${escapeHtml(scenario.label)}</strong><span>${escapeHtml(scenario.question)}</span></span>`;
    button.addEventListener("click", () => {
      state.scenarioId = scenario.id;
      state.selectedId = scenario.id;
      renderScenarios();
      selectNode(scenario.id);
      render();
    });
    return button;
  }));
}

function renderClassFilters() {
  const counts = state.graph.stats.class_counts;
  const buttons = DEFAULT_CLASSES.map((className) => {
    const meta = state.graph.classes[className] || {};
    const button = document.createElement("button");
    button.type = "button";
    button.className = "class-button";
    button.setAttribute("aria-pressed", state.visibleClasses.has(className) ? "true" : "false");
    button.innerHTML = `
      <span><span class="class-dot" style="background:${meta.color || "#64748b"}"></span>${escapeHtml(meta.label || className)}</span>
      <span class="class-count">${formatNumber(counts[className] || 0)}</span>
    `;
    button.addEventListener("click", () => {
      if (state.visibleClasses.has(className)) {
        state.visibleClasses.delete(className);
      } else {
        state.visibleClasses.add(className);
      }
      renderClassFilters();
      render();
    });
    return button;
  });
  els.classGrid.replaceChildren(...buttons);
}

function render() {
  const visible = computeVisibleGraph();
  state.visibleNodeIds = visible.nodeIds;
  state.visibleEdges = visible.edges;
  const positions = computePositions(visible.nodes);
  renderEdges(visible.edges, positions);
  renderNodes(visible.nodes, positions);
  renderGraphMeta(visible);
  renderDetail();
  applyTransform();

  window.__catbookOntology = {
    getState: () => ({
      nodes: visible.nodes.length,
      links: visible.edges.length,
      selectedId: state.selectedId,
      mode: state.mode,
      query: state.query,
      title: state.graph.meta?.title || "",
      backend: state.graph.meta?.backend || "",
      sqlitePath: state.graph.meta?.sqlite_path || "",
      schemaVersion: state.graph.meta?.schema_version || "",
    }),
  };
}

function computeVisibleGraph() {
  const nodeIds = new Set();
  const queryMatches = getQueryMatches();

  if (state.query) {
    queryMatches.forEach((id) => {
      addNodeAndNeighbors(nodeIds, id, state.mode === "content" ? 2 : 1);
    });
  } else if (state.mode === "beginner") {
    nodeIds.add("ontology:catbook");
    state.graph.scenarios.forEach((scenario) => nodeIds.add(scenario.id));
    const scenario = state.graph.scenarios.find((item) => item.id === state.scenarioId) || state.graph.scenarios[0];
    if (scenario) {
      nodeIds.add(scenario.id);
      scenario.start.forEach((id) => addNodeAndNeighbors(nodeIds, id, 1, { excludeSources: true }));
      const evidenceIds = collectEvidenceIds(scenario.start, BEGINNER_SOURCE_LIMIT);
      evidenceIds.forEach((id) => nodeIds.add(`source:${id}`));
    }
    addNodeAndNeighbors(nodeIds, state.selectedId, 1, { excludeSources: true });
  } else if (state.mode === "ontology") {
    state.graph.nodes.forEach((node) => {
      if (node.class !== "Source") nodeIds.add(node.id);
    });
  } else {
    const sourceIds = topSourceNodes(SOURCE_LIMIT).map((node) => node.id);
    state.graph.nodes.forEach((node) => {
      if (node.class !== "Source") nodeIds.add(node.id);
    });
    sourceIds.forEach((id) => nodeIds.add(id));
    addNodeAndNeighbors(nodeIds, state.selectedId, 1);
  }

  const classFiltered = Array.from(nodeIds).filter((id) => {
    const node = state.nodeById.get(id);
    return node && state.visibleClasses.has(node.class);
  });

  const finalIds = new Set(classFiltered);
  const edges = state.graph.edges.filter((edge) => finalIds.has(edge.source) && finalIds.has(edge.target));
  const nodes = Array.from(finalIds)
    .map((id) => state.nodeById.get(id))
    .filter(Boolean)
    .sort(sortNodes);

  return { nodeIds: finalIds, nodes, edges, queryMatches };
}

function getQueryMatches() {
  if (!state.query) return new Set();
  const matches = new Set();
  state.graph.nodes.forEach((node) => {
    if (!state.visibleClasses.has(node.class)) return;
    const text = [
      node.label,
      node.summary,
      node.beginner,
      ...(node.observe || []),
      ...(node.keywords || []),
    ].join(" ").toLocaleLowerCase("ko-KR");
    if (text.includes(state.query)) matches.add(node.id);
  });
  state.graph.content_index.forEach((item) => {
    const text = [item.title, item.default_title, ...(item.topics || [])].join(" ").toLocaleLowerCase("ko-KR");
    if (text.includes(state.query)) {
      matches.add(`source:${item.id}`);
      (item.matched_concepts || []).slice(0, 6).forEach((concept) => matches.add(concept.id));
    }
  });
  return matches;
}

function addNodeAndNeighbors(targetSet, id, depth, options = {}) {
  if (!state.nodeById.has(id) || depth < 0) return;
  targetSet.add(id);
  if (depth === 0) return;
  (state.neighbors.get(id) || []).forEach(({ node }) => {
    if (options.excludeSources && node.class === "Source") return;
    targetSet.add(node.id);
    if (node.class !== "Source") {
      addNodeAndNeighbors(targetSet, node.id, depth - 1, options);
    }
  });
}

function collectEvidenceIds(conceptIds, limit) {
  const seen = new Set();
  conceptIds.forEach((id) => {
    const node = state.nodeById.get(id);
    (node?.top_evidence || []).forEach((item) => seen.add(item.id));
  });
  return Array.from(seen).slice(0, limit);
}

function topSourceNodes(limit) {
  return state.graph.nodes
    .filter((node) => node.class === "Source")
    .sort((a, b) => (b.view_count || 0) - (a.view_count || 0) || a.label.localeCompare(b.label, "ko"))
    .slice(0, limit);
}

function computePositions(nodes) {
  const groups = new Map();
  nodes.forEach((node) => {
    if (!groups.has(node.class)) groups.set(node.class, []);
    groups.get(node.class).push(node);
  });

  const visibleClasses = DEFAULT_CLASSES.filter((className) => groups.has(className));
  const positions = new Map();
  const maxRadius = state.mode === "content" ? 650 : 560;
  const step = visibleClasses.length > 1 ? maxRadius / (visibleClasses.length - 1) : 0;

  visibleClasses.forEach((className, classIndex) => {
    const group = groups.get(className).sort(sortNodes);
    const radius = className === "Scenario" ? 70 : 105 + step * classIndex;
    const angleOffset = hashNumber(className) % 360;
    group.forEach((node, index) => {
      if (node.id === "ontology:catbook") {
        positions.set(node.id, { x: 0, y: 0 });
        return;
      }
      const count = group.length;
      const angle = ((index / Math.max(count, 1)) * Math.PI * 2) + degrees(angleOffset);
      const jitter = (hashNumber(node.id) % 32) - 16;
      positions.set(node.id, {
        x: Math.cos(angle) * (radius + jitter),
        y: Math.sin(angle) * (radius + jitter),
      });
    });
  });

  return positions;
}

function renderEdges(edges, positions) {
  const selectedLinks = new Set((state.neighbors.get(state.selectedId) || []).map(({ node }) => node.id));
  const edgeElements = edges.map((edge) => {
    const source = positions.get(edge.source);
    const target = positions.get(edge.target);
    if (!source || !target) return null;
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("class", `graph-edge ${selectedLinks.has(edge.source) || selectedLinks.has(edge.target) ? "focused" : ""}`);
    line.setAttribute("x1", source.x);
    line.setAttribute("y1", source.y);
    line.setAttribute("x2", target.x);
    line.setAttribute("y2", target.y);
    line.setAttribute("stroke-width", edge.relation === "HAS_EVIDENCE" ? "1.1" : "1.7");
    line.dataset.relation = edge.relation;
    return line;
  }).filter(Boolean);
  els.edgeLayer.replaceChildren(...edgeElements);
}

function renderNodes(nodes, positions) {
  const selectedLinks = new Set((state.neighbors.get(state.selectedId) || []).map(({ node }) => node.id));
  const nodeElements = nodes.map((node) => {
    const position = positions.get(node.id);
    if (!position) return null;
    const group = document.createElementNS(svgNS, "g");
    const isSelected = node.id === state.selectedId;
    const isNeighbor = selectedLinks.has(node.id);
    const shouldDim = state.selectedId && !isSelected && !isNeighbor && state.visibleNodeIds.has(state.selectedId);
    group.setAttribute("class", `graph-node ${node.class.toLowerCase()} ${isSelected ? "selected" : ""} ${isNeighbor ? "neighbor" : ""} ${shouldDim ? "dim" : ""}`);
    group.setAttribute("transform", `translate(${position.x.toFixed(2)} ${position.y.toFixed(2)})`);
    group.dataset.id = node.id;
    group.addEventListener("click", () => {
      selectNode(node.id);
      render();
    });

    const radius = nodeRadius(node);
    const circle = document.createElementNS(svgNS, "circle");
    circle.setAttribute("r", radius);
    circle.setAttribute("fill", node.color || state.graph.classes[node.class]?.color || "#64748b");
    circle.setAttribute("opacity", node.class === "Source" ? "0.86" : "0.96");

    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("text-anchor", "middle");
    label.setAttribute("y", radius + 15);
    label.textContent = shortLabel(node.label, node.class === "Chapter" ? 14 : 12);

    const title = document.createElementNS(svgNS, "title");
    title.textContent = `${node.label} · ${classLabel(node.class)}`;

    group.replaceChildren(circle, label, title);
    return group;
  }).filter(Boolean);
  els.nodeLayer.replaceChildren(...nodeElements);
}

function renderGraphMeta(visible) {
  els.visibleSummary.textContent = `표시 ${formatNumber(visible.nodes.length)}개 노드 · ${formatNumber(visible.edges.length)}개 연결 · ${backendLabel(state.graph.meta)} export`;
  const selected = state.nodeById.get(state.selectedId);
  els.selectionSummary.textContent = selected ? `${selected.label} 선택` : "선택 없음";
}

function selectNode(id) {
  if (!state.nodeById.has(id)) return;
  state.selectedId = id;
  const scenario = state.graph.scenarios.find((item) => item.id === id);
  if (scenario) {
    state.scenarioId = scenario.id;
    renderScenarios();
  }
  renderDetail();
}

function renderDetail() {
  const node = state.nodeById.get(state.selectedId) || state.nodeById.get("ontology:catbook");
  if (!node) return;

  els.detailImage.src = imageForNode(node);
  els.detailImage.alt = node.class === "Source" ? `${node.label} 썸네일` : `${node.label} 관련 이미지`;
  els.detailClass.textContent = classLabel(node.class);
  els.detailClass.style.color = node.color || state.graph.classes[node.class]?.color || "#0f766e";
  els.detailTitle.textContent = node.label;
  els.detailSummary.textContent = node.beginner || node.summary || "연결된 노드를 통해 맥락을 확인할 수 있다.";

  const chips = buildChips(node);
  els.detailChips.replaceChildren(...chips.map((chip) => {
    const span = document.createElement("span");
    span.className = `chip ${chip.medical ? "medical" : ""}`;
    span.textContent = chip.text;
    return span;
  }));

  renderObserve(node);
  renderRelations(node);
  renderEvidence(node);
}

function renderObserve(node) {
  const scenario = state.graph.scenarios.find((item) => item.id === node.id);
  const observeItems = scenario?.first_checks || node.observe || [];
  els.observeBox.hidden = observeItems.length === 0;
  els.observeList.replaceChildren(...observeItems.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

function renderRelations(node) {
  const related = (state.neighbors.get(node.id) || [])
    .filter(({ node: relatedNode }) => relatedNode.class !== "Source")
    .slice(0, 14);

  if (!related.length) {
    const empty = document.createElement("span");
    empty.className = "chip";
    empty.textContent = "연결된 개념 없음";
    els.relationList.replaceChildren(empty);
    return;
  }

  const buttons = related.map(({ edge, node: relatedNode }) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "relation-pill";
    button.textContent = `${relatedNode.label} · ${relationLabel(edge.relation)}`;
    button.addEventListener("click", () => {
      selectNode(relatedNode.id);
      render();
    });
    return button;
  });
  els.relationList.replaceChildren(...buttons);
}

function renderEvidence(node) {
  const evidence = evidenceForNode(node).slice(0, 12);
  els.evidenceCount.textContent = evidence.length;

  if (!evidence.length) {
    const empty = document.createElement("div");
    empty.className = "evidence-empty";
    empty.textContent = "이 노드는 책 구조나 개념 관계 중심이라 직접 표시할 근거 콘텐츠가 없다.";
    els.evidenceList.replaceChildren(empty);
    return;
  }

  const items = evidence.map((item) => {
    const decorated = decorateEvidence(item);
    const article = document.createElement("article");
    article.className = "evidence-item";
    article.innerHTML = `
      <a class="evidence-thumb" href="${escapeAttribute(decorated.url)}" target="_blank" rel="noopener noreferrer">
        <img src="${escapeAttribute(decorated.thumbnail_url || HERO_IMAGE)}" alt="" loading="lazy" />
      </a>
      <div>
        <a class="evidence-title" href="${escapeAttribute(decorated.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(decorated.title)}</a>
        <div class="evidence-meta">
          <span>${decorated.media_family === "shorts" ? "Shorts" : "Video"}</span>
          <span>${decorated.duration_min ? `${decorated.duration_min.toFixed(1)}분` : "길이 미상"}</span>
          <span>${decorated.view_count ? `${formatNumber(decorated.view_count)}회` : "조회수 미상"}</span>
        </div>
      </div>
    `;
    return article;
  });
  els.evidenceList.replaceChildren(...items);
}

function evidenceForNode(node) {
  if (node.class === "Source") {
    return [{
      id: node.id.replace("source:", ""),
      title: node.label,
      url: node.url,
      media_family: node.media_family,
      view_count: node.view_count,
      duration_min: node.duration_min,
      thumbnail_url: node.thumbnail_url,
    }];
  }

  const direct = node.top_evidence || [];
  if (direct.length) return direct;

  const byId = new Map();
  (state.neighbors.get(node.id) || []).forEach(({ node: relatedNode }) => {
    (relatedNode.top_evidence || []).forEach((item) => {
      if (!byId.has(item.id)) byId.set(item.id, item);
    });
  });
  return Array.from(byId.values());
}

function decorateEvidence(item) {
  const indexed = state.contentById.get(item.id) || {};
  return {
    ...indexed,
    ...item,
    title: item.title || indexed.title || "제목 없음",
    url: item.url || indexed.url || indexed.watch_url || "#",
    media_family: item.media_family || indexed.media_family || "video",
    thumbnail_url: item.thumbnail_url || indexed.thumbnail_url || "",
  };
}

function buildChips(node) {
  const chips = [
    { text: node.id },
    { text: classLabel(node.class) },
  ];
  if (node.evidence_count) chips.push({ text: `근거 ${formatNumber(node.evidence_count)}건` });
  if (node.media_family) chips.push({ text: node.media_family === "shorts" ? "Shorts" : "Video" });
  if (node.duration_min) chips.push({ text: `${node.duration_min.toFixed(1)}분` });
  if (node.view_count) chips.push({ text: `${formatNumber(node.view_count)}회` });
  if (node.medical || node.class === "HealthObservation") {
    chips.push({ text: "진단 아님 · 관찰/기록", medical: true });
  }
  return chips;
}

function imageForNode(node) {
  if (node.class === "Chapter" && node.image) return node.image;
  if (node.class === "Source" && node.thumbnail_url) return node.thumbnail_url;
  const evidence = evidenceForNode(node);
  const thumbnail = evidence.map(decorateEvidence).find((item) => item.thumbnail_url)?.thumbnail_url;
  return thumbnail || HERO_IMAGE;
}

function setZoom(nextScale) {
  state.transform.scale = Math.min(2.4, Math.max(0.38, nextScale));
  applyTransform();
}

function applyTransform() {
  els.graphLayer.setAttribute(
    "transform",
    `translate(${state.transform.x.toFixed(2)} ${state.transform.y.toFixed(2)}) scale(${state.transform.scale.toFixed(3)})`,
  );
}

function nodeRadius(node) {
  if (node.id === "ontology:catbook") return 24;
  if (node.class === "Source") return 7;
  if (node.class === "Scenario") return 19;
  if (node.class === "Chapter") return 15;
  if (node.class === "BookPart") return 17;
  return 13;
}

function sortNodes(a, b) {
  const classDelta = DEFAULT_CLASSES.indexOf(a.class) - DEFAULT_CLASSES.indexOf(b.class);
  if (classDelta !== 0) return classDelta;
  return a.label.localeCompare(b.label, "ko");
}

function classLabel(className) {
  return state.graph?.classes?.[className]?.label || className;
}

function relationLabel(relation) {
  return state.graph?.relations?.[relation] || relation;
}

function shortLabel(text, limit) {
  const plain = String(text || "");
  return plain.length > limit ? `${plain.slice(0, limit - 1)}…` : plain;
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("ko-KR");
}

function formatDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function backendLabel(meta = {}) {
  return String(meta.backend || "").toLowerCase().includes("sqlite") ? "SQLite" : "JSON";
}

function degrees(value) {
  return (value / 180) * Math.PI;
}

function hashNumber(input) {
  let hash = 0;
  String(input).split("").forEach((char) => {
    hash = ((hash << 5) - hash) + char.charCodeAt(0);
    hash |= 0;
  });
  return Math.abs(hash);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

init();
