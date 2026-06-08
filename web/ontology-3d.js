const GRAPH_URL = "../research/cat_ontology_graph.json";
const RDF_STATUS_URL = "../data/catbook_rdf_status.json";
const REFRESH_API_PATH = "/api/ontology-refresh";
const FALLBACK_REFRESH_API = "http://127.0.0.1:8798/api/ontology-refresh";
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

const SOURCE_LIMIT = 150;
const STARTER_SOURCE_LIMIT = 28;
const LYNX_RELATION = "LYNX_SIGHTLINE";
const LYNX_SIGHTLINE_IDS = [
  "scenario:sudden_run",
  "signal:zoomies",
  "need:energy_release",
  "action:context_record",
  "health:litter_change",
  "chapter:19",
  "action:vet_notes",
  "risk:self_diagnosis",
];
const LYNX_SIGHTLINE_SET = new Set(LYNX_SIGHTLINE_IDS);
const LYNX_COORDINATES = {
  "scenario:sudden_run": { x: -92, y: 24, z: 0 },
  "signal:zoomies": { x: -58, y: 47, z: -10 },
  "need:energy_release": { x: -16, y: 18, z: 8 },
  "action:context_record": { x: 26, y: 39, z: -6 },
  "health:litter_change": { x: 62, y: 4, z: 14 },
  "chapter:19": { x: 98, y: -24, z: -11 },
  "action:vet_notes": { x: 134, y: 2, z: 7 },
  "risk:self_diagnosis": { x: 170, y: -30, z: 0 },
};
const RELATION_COLORS = {
  [LYNX_RELATION]: "#F6C56B",
  STARTS_WITH: "#38BDF8",
  COVERS: "#B6C2C0",
  MAY_INDICATE: "#2DD4BF",
  OBSERVE_WITH: "#7DD3FC",
  SUGGESTS: "#FB806A",
  SUPPORTS: "#34D399",
  REQUIRES_RECORD: "#FB7185",
  CONSULT_WHEN: "#F43F5E",
  PREVENTS: "#F59E0B",
  HAS_TOPIC: "#8B9CFF",
  HAS_EVIDENCE: "#94A3B8",
};

const state = {
  raw: null,
  graph3d: null,
  nodeById: new Map(),
  contentById: new Map(),
  neighbors: new Map(),
  selectedId: "scenario:sudden_run",
  scenarioId: "scenario:sudden_run",
  mode: "starter",
  query: "",
  visibleClasses: new Set(DEFAULT_CLASSES),
  visibleNodeIds: new Set(),
  visibleLinks: [],
  highlightNodes: new Set(),
  highlightLinks: new Set(),
  autoRotate: true,
  paused: false,
  refreshing: false,
  fitTimer: null,
  graphSize: null,
  rdfStatus: null,
};

const els = {
  graph: document.querySelector("#graph-3d"),
  loading: document.querySelector("#loading-panel"),
  loadingDetail: document.querySelector("#loading-detail"),
  statNodes: document.querySelector("#stat-nodes"),
  statLinks: document.querySelector("#stat-links"),
  statMatched: document.querySelector("#stat-matched"),
  statBackend: document.querySelector("#stat-backend"),
  statRdf: document.querySelector("#stat-rdf"),
  rdfBadge: document.querySelector("#rdf-status-badge"),
  rdfTriples: document.querySelector("#rdf-triples"),
  rdfShapes: document.querySelector("#rdf-shapes"),
  rdfQueries: document.querySelector("#rdf-queries"),
  rdfInference: document.querySelector("#rdf-inference"),
  rdfGenerated: document.querySelector("#rdf-generated"),
  visibleSummary: document.querySelector("#visible-summary"),
  selectionSummary: document.querySelector("#selection-summary"),
  scenarioList: document.querySelector("#scenario-list"),
  classGrid: document.querySelector("#class-grid"),
  modeButtons: Array.from(document.querySelectorAll(".mode-button")),
  search: document.querySelector("#graph-search"),
  fitGraph: document.querySelector("#fit-graph"),
  autoRotate: document.querySelector("#auto-rotate"),
  pauseGraph: document.querySelector("#pause-graph"),
  resetFilter: document.querySelector("#reset-filter"),
  refreshOntology: document.querySelector("#refresh-ontology"),
  refreshStatus: document.querySelector("#refresh-status"),
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
    if (typeof ForceGraph3D !== "function") {
      throw new Error("3d-force-graph 라이브러리를 불러오지 못했습니다.");
    }
    const response = await fetch(cacheBustedUrl(GRAPH_URL), { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`그래프 JSON 로드 실패: ${response.status}`);
    }
    state.raw = await response.json();
    state.rdfStatus = await loadRdfStatus();
    buildIndexes();
    initGraph();
    bindEvents();
    renderStaticControls();
    selectNode(state.selectedId, { moveCamera: false });
    renderGraph();
    setTimeout(() => fitVisibleGraph(900), 800);
    els.loading.hidden = true;
  } catch (error) {
    els.loadingDetail.textContent = error.message || "알 수 없는 오류가 발생했습니다.";
    console.error(error);
  }
}

async function loadRdfStatus() {
  try {
    const response = await fetch(cacheBustedUrl(RDF_STATUS_URL), { cache: "no-store" });
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

  state.raw.nodes.forEach((node) => {
    state.nodeById.set(node.id, node);
    state.neighbors.set(node.id, []);
  });

  state.raw.content_index.forEach((item) => {
    state.contentById.set(item.id, item);
  });

  state.raw.edges.forEach((edge) => {
    const source = state.nodeById.get(edge.source);
    const target = state.nodeById.get(edge.target);
    if (!source || !target) return;
    state.neighbors.get(edge.source).push({ edge, node: target, direction: "out" });
    state.neighbors.get(edge.target).push({ edge, node: source, direction: "in" });
  });
}

function initGraph() {
  const viewport = getGraphViewport();
  state.graphSize = viewport;
  state.graph3d = createForceGraph(els.graph)
    .backgroundColor("rgba(0,0,0,0)")
    .showNavInfo(false)
    .nodeId("id")
    .nodeLabel(nodeTooltip)
    .nodeColor(nodeColor)
    .nodeVal(nodeValue)
    .nodeRelSize(4.15)
    .nodeOpacity(0.98)
    .nodeResolution(12)
    .nodePositionUpdate((object, coords, node) => {
      object.position.set(coords.x, coords.y, coords.z);
      object.scale.setScalar(nodeScale(node));
      return true;
    })
    .linkSource("source")
    .linkTarget("target")
    .linkLabel(linkTooltip)
    .linkColor(linkColor)
    .linkOpacity(0.74)
    .linkWidth(linkWidth)
    .linkDirectionalParticles(linkParticles)
    .linkDirectionalParticleSpeed(0.004)
    .linkDirectionalParticleWidth((link) => {
      if (link.relation === LYNX_RELATION) return state.highlightLinks.has(link.id) ? 4.2 : 2.7;
      return state.highlightLinks.has(link.id) ? 3.6 : 1.75;
    })
    .linkDirectionalParticleColor((link) => linkColor(link))
    .enablePointerInteraction(true)
    .enableNodeDrag(true)
    .onNodeHover((node) => {
      els.graph.style.cursor = node ? "pointer" : "grab";
    })
    .onNodeClick((node) => {
      selectNode(node.id, { moveCamera: true });
    })
    .onBackgroundClick(() => {
      setHighlight(state.selectedId);
    })
    .cooldownTicks(120)
    .cooldownTime(9000)
    .d3VelocityDecay(0.36)
    .width(viewport.width)
    .height(viewport.height);

  const controls = state.graph3d.controls();
  if (controls) {
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.65;
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
  }

  window.addEventListener("resize", resizeGraph);
}

function createForceGraph(container) {
  const options = {
    controlType: "orbit",
    rendererConfig: {
      antialias: true,
      alpha: true,
      preserveDrawingBuffer: true,
      powerPreference: "high-performance",
    },
  };

  try {
    return ForceGraph3D(options)(container);
  } catch (error) {
    return new ForceGraph3D(container, options);
  }
}

function bindEvents() {
  els.modeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      els.modeButtons.forEach((item) => item.classList.toggle("active", item === button));
      renderGraph();
      setTimeout(() => fitVisibleGraph(700), 260);
    });
  });

  els.search.addEventListener("input", () => {
    clearScheduledFit();
    state.query = els.search.value.trim().toLocaleLowerCase("ko-KR");
    renderGraph();
    if (state.query) {
      const first = Array.from(state.visibleNodeIds).find((id) => id !== state.selectedId);
      if (first) selectNode(first, { moveCamera: false, rerender: false });
      scheduleFitVisibleGraph(700, 280);
    }
  });

  els.fitGraph.addEventListener("click", () => fitVisibleGraph(700));

  els.autoRotate.addEventListener("click", () => {
    state.autoRotate = !state.autoRotate;
    els.autoRotate.classList.toggle("active", state.autoRotate);
    const controls = state.graph3d.controls();
    if (controls) controls.autoRotate = state.autoRotate;
  });

  els.pauseGraph.addEventListener("click", () => {
    state.paused = !state.paused;
    els.pauseGraph.classList.toggle("active", state.paused);
    els.pauseGraph.textContent = state.paused ? "재생" : "정지";
    if (state.paused) {
      state.graph3d.pauseAnimation();
    } else {
      state.graph3d.resumeAnimation();
    }
  });

  els.resetFilter.addEventListener("click", () => {
    state.query = "";
    state.mode = "starter";
    state.scenarioId = "scenario:sudden_run";
    state.selectedId = "scenario:sudden_run";
    state.visibleClasses = new Set(DEFAULT_CLASSES);
    els.search.value = "";
    els.modeButtons.forEach((button) => button.classList.toggle("active", button.dataset.mode === state.mode));
    renderStaticControls();
    selectNode(state.selectedId, { moveCamera: false, rerender: false });
    renderGraph();
    setTimeout(() => fitVisibleGraph(800), 260);
  });

  if (els.refreshOntology) {
    els.refreshOntology.addEventListener("click", requestOntologyRefresh);
  }
}

async function requestOntologyRefresh() {
  if (state.refreshing) return;
  state.refreshing = true;
  setRefreshUi("running", "YouTube 공개 메타 수집과 냥톨로지 재생성을 시작했습니다. 완료까지 시간이 걸릴 수 있습니다.");

  let lastError = null;
  for (const apiUrl of refreshApiUrls()) {
    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: "ontology-3d" }),
        cache: "no-store",
      });
      const result = await readRefreshJson(response);
      if (response.status === 409 || result.status === "running") {
        const finalStatus = await pollRefreshStatus(apiUrl);
        if (finalStatus.status === "done") {
          finishRefresh(finalStatus);
          return;
        }
        if (finalStatus.status === "failed") {
          lastError = new Error(finalStatus.error || finalStatus.detail || "갱신 파이프라인 실패");
          continue;
        }
        lastError = new Error("기존 갱신 작업이 아직 끝나지 않았습니다.");
        continue;
      }
      if (!response.ok) {
        lastError = new Error(`${apiUrl} 응답 실패: ${response.status}`);
        continue;
      }
      if (result.status === "failed") {
        lastError = new Error(result.error || result.detail || "갱신 파이프라인 실패");
        continue;
      }
      finishRefresh(result);
      return;
    } catch (error) {
      lastError = error;
    }
  }

  state.refreshing = false;
  setRefreshUi(
    "failed",
    `로컬 갱신 서버에 연결하지 못했습니다. catbook/scripts/start-ontology-refresh-server.ps1 실행 후 다시 눌러주세요. ${lastError?.message || ""}`
  );
}

async function readRefreshJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return { status: "unknown", detail: error.message };
  }
}

async function pollRefreshStatus(apiUrl) {
  const statusUrl = `${apiUrl.replace(/\/$/, "")}/status`;
  for (let attempt = 0; attempt < 180; attempt += 1) {
    const response = await fetch(cacheBustedUrl(statusUrl), { cache: "no-store" });
    const status = await readRefreshJson(response);
    if (status.status === "done" || status.status === "failed") return status;
    const stage = status.stages?.at?.(-1)?.stage || status.detail || "갱신 작업";
    setRefreshUi("running", `이미 갱신 작업이 실행 중입니다. ${stage} 상태를 확인하는 중입니다.`);
    await sleep(2000);
  }
  return { status: "running", detail: "갱신 작업이 오래 실행 중입니다. 잠시 뒤 상태를 다시 확인해주세요." };
}

function finishRefresh(result) {
  const graph = result.graph || {};
  const contentTotal = graph.content_total ?? state.raw?.meta?.content_total ?? state.raw?.content_index?.length ?? 0;
  setRefreshUi(
    "done",
    `반영 완료: ${formatNumber(contentTotal)}개 콘텐츠, ${formatNumber(graph.nodes)}개 노드, ${formatNumber(graph.edges)}개 연결. 화면을 다시 불러옵니다.`
  );
  setTimeout(() => window.location.reload(), 1200);
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function refreshApiUrls() {
  const urls = [];
  if (window.location.protocol === "http:" || window.location.protocol === "https:") {
    urls.push(new URL(REFRESH_API_PATH, window.location.origin).href);
  }
  if (!urls.includes(FALLBACK_REFRESH_API)) {
    urls.push(FALLBACK_REFRESH_API);
  }
  return urls;
}

function setRefreshUi(status, message) {
  if (els.refreshStatus) {
    els.refreshStatus.dataset.state = status;
    els.refreshStatus.textContent = message;
  }
  if (els.refreshOntology) {
    els.refreshOntology.disabled = status === "running";
    els.refreshOntology.textContent = status === "running" ? "업데이트 중" : "YouTube 최신 반영";
  }
}

function renderStaticControls() {
  const stats = state.raw.stats;
  els.statNodes.textContent = formatNumber(stats.node_count);
  els.statLinks.textContent = formatNumber(stats.edge_count);
  els.statMatched.textContent = formatNumber(stats.matched_content_count);
  els.statBackend.textContent = backendLabel(state.raw.meta);
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
  const buttons = state.raw.scenarios.map((scenario) => {
    const isActive = scenario.id === state.scenarioId;
    const isInactive = Boolean(state.scenarioId) && !isActive;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "scenario-button";
    button.classList.toggle("active", isActive);
    button.classList.toggle("inactive", isInactive);
    button.setAttribute("aria-pressed", isActive ? "true" : "false");
    button.setAttribute("title", isActive ? "관측 입구 선택 해제" : "관측 입구 선택");
    button.innerHTML = `<span><strong>${escapeHtml(scenario.label)}</strong><span>${escapeHtml(scenario.question)}</span></span>`;
    button.addEventListener("click", () => {
      if (state.scenarioId === scenario.id) {
        state.scenarioId = "";
        state.selectedId = "ontology:catbook";
        renderScenarios();
        selectNode(state.selectedId, { moveCamera: false, rerender: false });
        renderGraph();
        setTimeout(() => fitVisibleGraph(650), 120);
        return;
      }
      state.scenarioId = scenario.id;
      state.selectedId = scenario.id;
      renderScenarios();
      selectNode(scenario.id, { moveCamera: true, rerender: false });
      renderGraph();
    });
    return button;
  });
  els.scenarioList.replaceChildren(...buttons);
}

function renderClassFilters() {
  const counts = state.raw.stats.class_counts;
  const buttons = DEFAULT_CLASSES.map((className) => {
    const meta = state.raw.classes[className] || {};
    const button = document.createElement("button");
    button.type = "button";
    button.className = "class-button";
    button.setAttribute("aria-pressed", state.visibleClasses.has(className) ? "true" : "false");
    button.innerHTML = `
      <span><span class="class-dot" style="background:${meta.color || "#64748b"}"></span>${escapeHtml(meta.label || className)}</span>
      <span>${formatNumber(counts[className] || 0)}</span>
    `;
    button.addEventListener("click", () => {
      if (state.visibleClasses.has(className)) {
        state.visibleClasses.delete(className);
      } else {
        state.visibleClasses.add(className);
      }
      renderClassFilters();
      renderGraph();
    });
    return button;
  });
  els.classGrid.replaceChildren(...buttons);
}

function renderGraph() {
  const visible = computeVisibleGraph();
  state.visibleNodeIds = visible.nodeIds;
  state.visibleLinks = visible.links;

  const graphData = {
    nodes: visible.nodes.map(toGraphNode),
    links: visible.links.map(toGraphLink),
  };

  state.graph3d.graphData(graphData);
  tuneForces();
  setHighlight(state.selectedId);
  renderDetail();
  renderGraphMeta(graphData);

  window.__catbook3d = {
    getState: () => ({
      nodes: document.querySelectorAll("#graph-3d canvas").length ? graphData.nodes.length : 0,
      links: graphData.links.length,
      selectedId: state.selectedId,
      mode: state.mode,
      query: state.query,
      title: state.raw.meta?.title || "",
      lynxLinks: graphData.links.filter((link) => link.relation === LYNX_RELATION).length,
      canvas: Boolean(document.querySelector("#graph-3d canvas")),
      backend: state.raw.meta?.backend || "",
      sqlitePath: state.raw.meta?.sqlite_path || "",
      schemaVersion: state.raw.meta?.schema_version || "",
    }),
    sampleCanvas: sampleCanvasPixels,
  };
}

function computeVisibleGraph() {
  const nodeIds = new Set();
  const queryMatches = getQueryMatches();

  if (state.query) {
    queryMatches.forEach((id) => {
      addNodeAndNeighbors(nodeIds, id, state.mode === "evidence" ? 2 : 1, { excludeSources: state.mode !== "evidence" });
    });
  } else if (state.mode === "starter") {
    nodeIds.add("ontology:catbook");
    state.raw.scenarios.forEach((scenario) => nodeIds.add(scenario.id));
    LYNX_SIGHTLINE_IDS.forEach((id) => nodeIds.add(id));
    const scenario = state.scenarioId
      ? state.raw.scenarios.find((item) => item.id === state.scenarioId)
      : null;
    if (scenario) {
      nodeIds.add(scenario.id);
      scenario.start.forEach((id) => addNodeAndNeighbors(nodeIds, id, 1, { excludeSources: true }));
      collectEvidenceIds(scenario.start, STARTER_SOURCE_LIMIT).forEach((id) => nodeIds.add(`source:${id}`));
    }
    addNodeAndNeighbors(nodeIds, state.selectedId, 1, { excludeSources: true });
  } else if (state.mode === "ontology") {
    state.raw.nodes.forEach((node) => {
      if (node.class !== "Source") nodeIds.add(node.id);
    });
  } else {
    state.raw.nodes.forEach((node) => {
      if (node.class !== "Source") nodeIds.add(node.id);
    });
    topSourceNodes(SOURCE_LIMIT).forEach((node) => nodeIds.add(node.id));
    addNodeAndNeighbors(nodeIds, state.selectedId, 1);
  }

  const filteredIds = new Set(Array.from(nodeIds).filter((id) => {
    const node = state.nodeById.get(id);
    return node && state.visibleClasses.has(node.class);
  }));

  const links = [
    ...state.raw.edges.filter((edge) => filteredIds.has(edge.source) && filteredIds.has(edge.target)),
    ...buildLynxSightlineLinks(filteredIds),
  ];
  const nodes = Array.from(filteredIds)
    .map((id) => state.nodeById.get(id))
    .filter(Boolean)
    .sort(sortNodes);

  return { nodeIds: filteredIds, nodes, links };
}

function buildLynxSightlineLinks(visibleIds) {
  const links = [];
  for (let index = 0; index < LYNX_SIGHTLINE_IDS.length - 1; index += 1) {
    const source = LYNX_SIGHTLINE_IDS[index];
    const target = LYNX_SIGHTLINE_IDS[index + 1];
    if (visibleIds.has(source) && visibleIds.has(target)) {
      links.push(makeLynxEdge(source, target, index));
    }
  }
  return links;
}

function makeLynxEdge(source, target, index) {
  return {
    id: `lynx-sightline:${index}:${source}->${target}`,
    source,
    target,
    relation: LYNX_RELATION,
    synthetic: true,
  };
}

function toGraphNode(node) {
  const fixed = state.mode === "starter" && !state.query ? LYNX_COORDINATES[node.id] : null;
  const position = fixed || initialPosition(node);
  return {
    ...node,
    name: node.label,
    group: node.class,
    val: nodeValue(node),
    x: position.x,
    y: position.y,
    z: position.z,
  };
}

function toGraphLink(edge) {
  return {
    ...edge,
    source: edge.source,
    target: edge.target,
    sourceId: edge.source,
    targetId: edge.target,
    name: `${relationLabel(edge.relation)} · ${nodeLabel(edge.source)} → ${nodeLabel(edge.target)}`,
    color: RELATION_COLORS[edge.relation] || "#B6C2C0",
  };
}

function tuneForces() {
  const charge = state.graph3d.d3Force("charge");
  if (charge) charge.strength(state.mode === "evidence" ? -90 : -58);
  const link = state.graph3d.d3Force("link");
  if (link) {
    link.distance((edge) => {
      if (edge.relation === LYNX_RELATION) return 46;
      if (edge.relation === "HAS_EVIDENCE") return 58;
      if (edge.relation === "STARTS_WITH") return 78;
      if (edge.relation === "COVERS") return 64;
      return 72;
    });
  }
}

function getQueryMatches() {
  if (!state.query) return new Set();
  const matches = new Set();
  state.raw.nodes.forEach((node) => {
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

  state.raw.content_index.forEach((item) => {
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
  return state.raw.nodes
    .filter((node) => node.class === "Source")
    .sort((a, b) => (b.view_count || 0) - (a.view_count || 0) || a.label.localeCompare(b.label, "ko"))
    .slice(0, limit);
}

function selectNode(id, options = {}) {
  if (!state.nodeById.has(id)) return;
  state.selectedId = id;
  const scenario = state.raw.scenarios.find((item) => item.id === id);
  if (scenario) {
    state.scenarioId = scenario.id;
    renderScenarios();
  }
  setHighlight(id);
  renderDetail();
  if (options.moveCamera) focusCameraOnNode(id);
  if (options.rerender) renderGraph();
}

function setHighlight(id) {
  state.highlightNodes.clear();
  state.highlightLinks.clear();
  if (id && state.nodeById.has(id)) {
    state.highlightNodes.add(id);
    (state.neighbors.get(id) || []).forEach(({ edge, node }) => {
      if (state.visibleNodeIds.has(node.id)) {
        state.highlightNodes.add(node.id);
        state.highlightLinks.add(edge.id);
      }
    });
    if (LYNX_SIGHTLINE_SET.has(id)) {
      LYNX_SIGHTLINE_IDS.forEach((nodeId) => {
        if (state.visibleNodeIds.has(nodeId)) state.highlightNodes.add(nodeId);
      });
      buildLynxSightlineLinks(state.visibleNodeIds).forEach((edge) => {
        state.highlightLinks.add(edge.id);
      });
    }
  }
  if (state.graph3d) {
    state.graph3d
      .nodeColor(nodeColor)
      .linkColor(linkColor)
      .linkWidth(linkWidth)
      .linkDirectionalParticles(linkParticles);
  }
}

function focusCameraOnNode(id) {
  const graphData = state.graph3d.graphData();
  const node = graphData.nodes.find((item) => item.id === id);
  if (!node || typeof node.x !== "number") {
    setTimeout(() => focusCameraOnNode(id), 240);
    return;
  }
  moveCameraTo(
    { x: node.x + 42, y: node.y + 34, z: node.z + (node.class === "Source" ? 150 : 125) },
    { x: node.x, y: node.y, z: node.z },
  );
}

function fitVisibleGraph(ms = 600) {
  if (!state.graph3d) return;
  const bbox = state.graph3d.getGraphBbox((node) => state.visibleNodeIds.has(node.id));
  if (!bbox) return;
  const visualBounds = getVisibleGraphVisualBounds(bbox);
  const center = visualBounds.center;
  const spanX = Math.max(80, visualBounds.spanX);
  const spanY = Math.max(80, visualBounds.spanY);
  const spanZ = Math.max(80, visualBounds.spanZ);
  const viewport = getGraphViewport();
  const camera = state.graph3d.camera();
  const verticalFov = ((camera?.fov || 45) * Math.PI) / 180;
  const horizontalFov = 2 * Math.atan(Math.tan(verticalFov / 2) * viewport.aspect);
  const distanceForX = (spanX * 0.54) / Math.tan(horizontalFov / 2);
  const distanceForY = (spanY * 0.56) / Math.tan(verticalFov / 2);
  const distanceForZ = spanZ * 1.36;
  const widthScale = viewport.width < 520 ? 1.34 : viewport.width < 760 ? 1.24 : 1.18;
  const distance = Math.max(210, distanceForX, distanceForY, distanceForZ) * widthScale;
  moveCameraTo({ x: center.x + distance * 0.12, y: center.y + distance * 0.1, z: center.z + distance }, center, ms);
}

function getVisibleGraphVisualBounds(bbox) {
  const graphData = state.graph3d.graphData();
  const visibleNodes = graphData.nodes.filter((node) => (
    state.visibleNodeIds.has(node.id)
    && Number.isFinite(node.x)
    && Number.isFinite(node.y)
    && Number.isFinite(node.z)
  ));

  if (!visibleNodes.length) {
    return {
      center: {
        x: (bbox.x[0] + bbox.x[1]) / 2,
        y: (bbox.y[0] + bbox.y[1]) / 2,
        z: (bbox.z[0] + bbox.z[1]) / 2,
      },
      spanX: bbox.x[1] - bbox.x[0],
      spanY: bbox.y[1] - bbox.y[0],
      spanZ: bbox.z[1] - bbox.z[0],
    };
  }

  const bounds = visibleNodes.reduce((acc, node) => {
    const radius = graphNodeVisualRadius(node);
    acc.minX = Math.min(acc.minX, node.x - radius);
    acc.maxX = Math.max(acc.maxX, node.x + radius);
    acc.minY = Math.min(acc.minY, node.y - radius);
    acc.maxY = Math.max(acc.maxY, node.y + radius);
    acc.minZ = Math.min(acc.minZ, node.z - radius);
    acc.maxZ = Math.max(acc.maxZ, node.z + radius);
    return acc;
  }, {
    minX: bbox.x[0],
    maxX: bbox.x[1],
    minY: bbox.y[0],
    maxY: bbox.y[1],
    minZ: bbox.z[0],
    maxZ: bbox.z[1],
  });

  return {
    center: {
      x: (bounds.minX + bounds.maxX) / 2,
      y: (bounds.minY + bounds.maxY) / 2,
      z: (bounds.minZ + bounds.maxZ) / 2,
    },
    spanX: bounds.maxX - bounds.minX,
    spanY: bounds.maxY - bounds.minY,
    spanZ: bounds.maxZ - bounds.minZ,
  };
}

function graphNodeVisualRadius(node) {
  const val = Math.max(1, Number(node.val || nodeValue(node)));
  return Math.sqrt(val) * nodeScale(node) * 7.5;
}

function getGraphViewport() {
  const width = Math.max(1, els.graph.clientWidth || window.innerWidth || 1);
  const height = Math.max(1, els.graph.clientHeight || window.innerHeight || 1);
  return { width, height, aspect: Math.max(0.18, width / height) };
}

function scheduleFitVisibleGraph(ms = 600, delay = 220) {
  clearScheduledFit();
  state.fitTimer = window.setTimeout(() => {
    state.fitTimer = null;
    fitVisibleGraph(ms);
  }, delay);
}

function clearScheduledFit() {
  if (!state.fitTimer) return;
  window.clearTimeout(state.fitTimer);
  state.fitTimer = null;
}

function renderGraphMeta(graphData) {
  const lynxLinks = graphData.links.filter((link) => link.relation === LYNX_RELATION).length;
  els.visibleSummary.textContent = `표시 ${formatNumber(graphData.nodes.length)}개 별 · ${formatNumber(graphData.links.length)}개 연결 · ${backendLabel(state.raw.meta)} export`;
  const selected = state.nodeById.get(state.selectedId);
  els.selectionSummary.textContent = selected
    ? `${selected.label}${lynxLinks ? " · Lynx" : ""}`
    : "선택 없음";
}

function renderDetail() {
  const node = state.nodeById.get(state.selectedId) || state.nodeById.get("ontology:catbook");
  if (!node) return;

  els.detailImage.src = imageForNode(node);
  els.detailImage.alt = node.class === "Source" ? `${node.label} 썸네일` : `${node.label} 관련 이미지`;
  els.detailClass.textContent = classLabel(node.class);
  els.detailClass.style.color = LYNX_SIGHTLINE_SET.has(node.id)
    ? RELATION_COLORS[LYNX_RELATION]
    : node.color || state.raw.classes[node.class]?.color || "#2dd4bf";
  els.detailTitle.textContent = node.label;
  els.detailSummary.textContent = node.beginner || node.summary || "연결된 노드를 통해 맥락을 확인할 수 있다.";

  const chips = buildChips(node).map((chip) => {
    const span = document.createElement("span");
    span.className = `chip ${chip.medical ? "medical" : ""}`;
    span.textContent = chip.text;
    return span;
  });
  els.detailChips.replaceChildren(...chips);

  renderObserve(node);
  renderRelations(node);
  renderEvidence(node);
}

function renderObserve(node) {
  const scenario = state.raw.scenarios.find((item) => item.id === node.id);
  const observeItems = scenario?.first_checks || node.observe || [];
  els.observeBox.hidden = observeItems.length === 0;
  els.observeList.replaceChildren(...observeItems.map((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    return li;
  }));
}

function renderRelations(node) {
  const related = [
    ...lynxNeighbors(node.id),
    ...(state.neighbors.get(node.id) || []),
  ]
    .filter(({ node: relatedNode }) => relatedNode.class !== "Source")
    .slice(0, 12);

  if (!related.length) {
    const empty = document.createElement("div");
    empty.className = "evidence-empty";
    empty.textContent = "가까운 개념 연결이 없습니다.";
    els.relationList.replaceChildren(empty);
    return;
  }

  const buttons = related.map(({ edge, node: relatedNode }) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "relation-pill";
    button.textContent = `${relatedNode.label} · ${relationLabel(edge.relation)}`;
    button.addEventListener("click", () => {
      selectNode(relatedNode.id, { moveCamera: true });
    });
    return button;
  });
  els.relationList.replaceChildren(...buttons);
}

function lynxNeighbors(id) {
  const index = LYNX_SIGHTLINE_IDS.indexOf(id);
  if (index === -1) return [];
  const neighbors = [];
  if (index > 0) {
    const source = LYNX_SIGHTLINE_IDS[index - 1];
    const target = LYNX_SIGHTLINE_IDS[index];
    const node = state.nodeById.get(source);
    if (node) neighbors.push({ edge: makeLynxEdge(source, target, index - 1), node, direction: "in" });
  }
  if (index < LYNX_SIGHTLINE_IDS.length - 1) {
    const source = LYNX_SIGHTLINE_IDS[index];
    const target = LYNX_SIGHTLINE_IDS[index + 1];
    const node = state.nodeById.get(target);
    if (node) neighbors.push({ edge: makeLynxEdge(source, target, index), node, direction: "out" });
  }
  return neighbors;
}

function renderEvidence(node) {
  const evidence = evidenceForNode(node).slice(0, 10);
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
          <span>${decorated.duration_min ? `${Number(decorated.duration_min).toFixed(1)}분` : "길이 미상"}</span>
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

  if (node.top_evidence?.length) return node.top_evidence;

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
  if (LYNX_SIGHTLINE_SET.has(node.id)) chips.push({ text: "살쾡이자리 관측선" });
  if (node.evidence_count) chips.push({ text: `근거 ${formatNumber(node.evidence_count)}건` });
  if (node.media_family) chips.push({ text: node.media_family === "shorts" ? "Shorts" : "Video" });
  if (node.duration_min) chips.push({ text: `${Number(node.duration_min).toFixed(1)}분` });
  if (node.view_count) chips.push({ text: `${formatNumber(node.view_count)}회` });
  if (node.medical || node.class === "HealthObservation") {
    chips.push({ text: "진단 아님 · 관찰/기록", medical: true });
  }
  return chips;
}

function imageForNode(node) {
  if (node.class === "Chapter" && node.image) return node.image;
  if (node.class === "Source" && node.thumbnail_url) return node.thumbnail_url;
  const thumbnail = evidenceForNode(node).map(decorateEvidence).find((item) => item.thumbnail_url)?.thumbnail_url;
  return thumbnail || HERO_IMAGE;
}

function nodeColor(node) {
  if (node.id === state.selectedId) return "#F8E7A7";
  if (LYNX_SIGHTLINE_SET.has(node.id) && state.highlightNodes.has(node.id)) return "#F6C56B";
  if (state.highlightNodes.size && state.highlightNodes.has(node.id)) return brightenColor(node.color || state.raw.classes[node.class]?.color || "#D8E5E0", 22);
  if (state.highlightNodes.size && !state.highlightNodes.has(node.id)) return fadeColor(brightenColor(node.color || state.raw.classes[node.class]?.color || "#D8E5E0", 18), 0.46);
  if (LYNX_SIGHTLINE_SET.has(node.id)) return "#F6C56B";
  return brightenColor(node.color || state.raw.classes[node.class]?.color || "#D8E5E0", 18);
}

function linkColor(link) {
  if (state.highlightLinks.has(link.id)) return link.relation === LYNX_RELATION ? "#F8E7A7" : "#F6FBF4";
  const base = link.color || RELATION_COLORS[link.relation] || "#B6C2C0";
  if (state.highlightNodes.size) {
    const sourceId = getLinkEndpointId(link.source);
    const targetId = getLinkEndpointId(link.target);
    return state.highlightNodes.has(sourceId) && state.highlightNodes.has(targetId)
      ? brightenColor(base, 20)
      : "rgba(210, 228, 224, 0.34)";
  }
  return brightenColor(base, 16);
}

function linkWidth(link) {
  if (link.relation === LYNX_RELATION && state.highlightLinks.has(link.id)) return 3.8;
  if (link.relation === LYNX_RELATION) return 2.6;
  if (state.highlightLinks.has(link.id)) return 2.7;
  if (link.relation === "HAS_EVIDENCE") return state.mode === "evidence" ? 0.72 : 0.42;
  if (link.relation === "STARTS_WITH") return 1.75;
  return 1.05;
}

function linkParticles(link) {
  if (link.relation === LYNX_RELATION) return state.highlightLinks.has(link.id) ? 4 : 2;
  if (state.highlightLinks.has(link.id)) return 3;
  if (["STARTS_WITH", "MAY_INDICATE", "SUGGESTS", "REQUIRES_RECORD"].includes(link.relation)) return 1;
  return 0;
}

function nodeValue(node) {
  const base = {
    Scenario: 7.2,
    CatSignal: 6.2,
    Need: 5.6,
    EnvironmentElement: 5,
    HealthObservation: 6.5,
    CareAction: 5.3,
    SafetyRisk: 5.8,
    Topic: 4.6,
    BookPart: 5.2,
    Chapter: 4.3,
    Source: 1.35,
  }[node.class] || 3;
  const evidenceBoost = node.evidence_count ? Math.min(3.2, Math.log10(node.evidence_count + 1) * 1.15) : 0;
  const lynxBoost = LYNX_SIGHTLINE_SET.has(node.id) ? 1.8 : 0;
  return base + evidenceBoost + lynxBoost;
}

function nodeScale(node) {
  const lynxBoost = LYNX_SIGHTLINE_SET.has(node.id) ? 0.18 : 0;
  if (node.id === state.selectedId) return (node.class === "Source" ? 1.05 : 1.55) + lynxBoost;
  if (state.highlightNodes.has(node.id)) return (node.class === "Source" ? 0.92 : 1.25) + lynxBoost;
  if (node.class === "Source") return 0.56;
  if (node.class === "Scenario") return 1.05 + lynxBoost;
  if (node.class === "HealthObservation") return 1.02 + lynxBoost;
  if (node.class === "CatSignal") return 0.96 + lynxBoost;
  if (node.class === "Chapter") return 0.76;
  return 0.88 + lynxBoost;
}

function initialPosition(node) {
  const classIndex = Math.max(0, DEFAULT_CLASSES.indexOf(node.class));
  const hash = hashNumber(node.id);
  const shell = {
    Scenario: 34,
    Topic: 82,
    BookPart: 106,
    Chapter: 138,
    CatSignal: 72,
    HealthObservation: 92,
    EnvironmentElement: 112,
    Need: 92,
    CareAction: 118,
    SafetyRisk: 132,
    Source: 172,
  }[node.class] || 100;
  const angle = ((hash % 360) / 180) * Math.PI;
  const lift = (((hash >> 3) % 120) - 60) * (node.class === "Source" ? 0.9 : 0.62);
  const band = (classIndex % 5) * 0.18 + 0.78;
  return {
    x: Math.cos(angle) * shell * band,
    y: Math.sin(angle) * shell * band,
    z: lift,
  };
}

function moveCameraTo(position, target, ms = 650) {
  const camera = state.graph3d.camera();
  const controls = state.graph3d.controls();
  const start = { x: camera.position.x, y: camera.position.y, z: camera.position.z };
  const startTarget = controls?.target ? { x: controls.target.x, y: controls.target.y, z: controls.target.z } : { x: 0, y: 0, z: 0 };
  const duration = Math.max(0, ms);
  const started = performance.now();

  function step(now) {
    const raw = duration ? Math.min(1, (now - started) / duration) : 1;
    const t = 1 - Math.pow(1 - raw, 3);
    camera.position.set(
      lerp(start.x, position.x, t),
      lerp(start.y, position.y, t),
      lerp(start.z, position.z, t),
    );
    if (controls?.target) {
      controls.target.set(
        lerp(startTarget.x, target.x, t),
        lerp(startTarget.y, target.y, t),
        lerp(startTarget.z, target.z, t),
      );
      controls.update();
    } else {
      camera.lookAt(target.x, target.y, target.z);
    }
    if (raw < 1) requestAnimationFrame(step);
  }

  requestAnimationFrame(step);
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function nodeTooltip(node) {
  const lynx = LYNX_SIGHTLINE_SET.has(node.id) ? " · 살쾡이자리 관측선" : "";
  return `
    <div class="node-tip">
      <strong>${escapeHtml(node.label)}</strong>
      <span>${escapeHtml(classLabel(node.class))}${lynx}${node.evidence_count ? ` · 근거 ${formatNumber(node.evidence_count)}건` : ""}</span>
    </div>
  `;
}

function linkTooltip(link) {
  return `
    <div class="node-tip">
      <strong>${escapeHtml(relationLabel(link.relation))}</strong>
      <span>${escapeHtml(nodeLabel(getLinkEndpointId(link.source)))} → ${escapeHtml(nodeLabel(getLinkEndpointId(link.target)))}</span>
    </div>
  `;
}

function resizeGraph() {
  if (!state.graph3d || !els.graph.clientWidth || !els.graph.clientHeight) return;
  const size = getGraphViewport();
  const previous = state.graphSize;
  state.graphSize = size;
  state.graph3d.width(size.width).height(size.height);
  if (previous && (Math.abs(previous.width - size.width) > 4 || Math.abs(previous.height - size.height) > 4)) {
    scheduleFitVisibleGraph(420, 140);
  }
}

function sampleCanvasPixels() {
  const canvas = document.querySelector("#graph-3d canvas");
  if (!canvas) return { canvas: false, coloredSamples: 0, samples: 0 };
  const gl = canvas.getContext("webgl2", { preserveDrawingBuffer: true }) || canvas.getContext("webgl", { preserveDrawingBuffer: true });
  if (!gl) return { canvas: true, webgl: false, coloredSamples: 0, samples: 0 };
  let coloredSamples = 0;
  let alphaSamples = 0;
  let samples = 0;
  const pixel = new Uint8Array(4);
  const stepX = Math.max(8, Math.floor(canvas.width / 88));
  const stepY = Math.max(8, Math.floor(canvas.height / 54));
  for (let x = 16; x < canvas.width - 16; x += stepX) {
    for (let y = 16; y < canvas.height - 16; y += stepY) {
      gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixel);
      samples += 1;
      if (pixel[3] > 0) alphaSamples += 1;
      if (pixel[3] > 0 && (pixel[0] + pixel[1] + pixel[2] > 18)) coloredSamples += 1;
    }
  }
  return { canvas: true, webgl: true, coloredSamples, alphaSamples, samples, width: canvas.width, height: canvas.height };
}

function classLabel(className) {
  return state.raw?.classes?.[className]?.label || className;
}

function relationLabel(relation) {
  if (relation === LYNX_RELATION) return "살쾡이자리 관측선";
  return state.raw?.relations?.[relation] || relation;
}

function nodeLabel(id) {
  return state.nodeById.get(id)?.label || id;
}

function getLinkEndpointId(endpoint) {
  return typeof endpoint === "object" && endpoint !== null ? endpoint.id : endpoint;
}

function sortNodes(a, b) {
  const classDelta = DEFAULT_CLASSES.indexOf(a.class) - DEFAULT_CLASSES.indexOf(b.class);
  if (classDelta !== 0) return classDelta;
  return a.label.localeCompare(b.label, "ko");
}

function fadeColor(color, opacity) {
  const hex = String(color || "#B6C2C0").replace("#", "");
  if (hex.length !== 6) return `rgba(182, 194, 192, ${opacity})`;
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

function brightenColor(color, amount = 18) {
  const hex = String(color || "#D8E5E0").replace("#", "");
  if (hex.length !== 6) return color || "#D8E5E0";
  const r = Math.min(255, parseInt(hex.slice(0, 2), 16) + amount);
  const g = Math.min(255, parseInt(hex.slice(2, 4), 16) + amount);
  const b = Math.min(255, parseInt(hex.slice(4, 6), 16) + amount);
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function toHex(value) {
  return value.toString(16).padStart(2, "0");
}

function hashNumber(input) {
  let hash = 0;
  String(input).split("").forEach((char) => {
    hash = ((hash << 5) - hash) + char.charCodeAt(0);
    hash |= 0;
  });
  return Math.abs(hash);
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

function cacheBustedUrl(url) {
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}ts=${Date.now()}`;
}

function backendLabel(meta = {}) {
  return String(meta.backend || "").toLowerCase().includes("sqlite") ? "SQLite" : "JSON";
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
