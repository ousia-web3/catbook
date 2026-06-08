# 냥냥츄르 고양이 이야기 책 + 소개 웹페이지 작업

## 작업 개요

- 요청자 원문: 미야옹철의 냥냥펀치 유튜브 채널의 Shorts 제외 전체 콘텐츠를 분석해, `냥냥츄르`라는 고양이 이야기를 담은 책을 출판하고 관련 소개 웹페이지까지 구현한다.
- 채널: 미야옹철의 냥냥펀치
- 채널 URL: https://www.youtube.com/@catdoctor/videos
- requestId: `nyangnyang-chur-cat-book`
- 작업 시작일: 2026-06-02
- 최신 업데이트: 2026-06-08
- 현재 폴더: `catbook/`
- 이전 `work-requests/`의 catbook 관련 작업 기록은 `catbook/project-records/work-requests/`에 보관한다.

## 산출물 구조

- `human-brief.md`: 사용자 요청 기반 Human Brief 초안
- `jarvis-strategy-brief.md`: Jarvis 전략 판단과 성공 기준
- `friday-task-breakdown.md`: 에이전트별 작업 분해
- `decision-log.md`: 주요 결정과 보류 리스크
- `research/`: 채널 메타데이터, 자막 기반 비원문 분석, 리서치 리포트
- `data/`: 냥톨로지 SQLite SSOT와 구조화 저장소
- `skills/`: 원고 작성에 사용할 프로젝트 전용 문체 스킬
- `manuscript/`: 책 기획서, 목차, 원고
- `web/`: 소개 웹페이지 구현물
- `assets/`: 생성 이미지와 웹 자산
- `evidence/`: 실행/검증 증거
- `scripts/build_complete_manuscript.py`: v3 핵심/나머지 확장본을 7파트 42유닛 순서로 조립하는 스크립트
- `scripts/build_standalone_html.py`: 소개 페이지를 CSS/JS 인라인 단일 HTML로 조립하는 스크립트
- `scripts/build_manuscript_html.py`: v3 전체 원고 Markdown을 집사용 이야기 노트 HTML로 변환하는 스크립트
- `diagrams/`: 프로젝트 구성 유형별 PlantUML 다이어그램

## 저작권/안전 원칙

- 유튜브 자막 원문 전체를 저장하거나 재배포하지 않는다.
- 분석 산출물은 비문장형 신호, 키워드, 주제 히트, 비원문 요약으로 제한한다.
- 책 원고는 영상 대본의 요약본이나 변형물이 아니라 독립 창작물로 작성한다.
- “AI 탐지 회피” 목적의 글쓰기 스킬은 만들지 않는다. 대신 자연스러운 문학적 목소리, 구체적 관찰, 장면 중심 퇴고를 위한 안전한 편집 스킬을 사용한다.

## 로컬 확인

작업 대시보드:

```powershell
http://127.0.0.1:8787/dashboards/agent-assignment-dashboard.html
```

소개 웹페이지:

```text
http://127.0.0.1:8787/catbook/web/index.html
```

단일 HTML 소개 페이지:

```text
http://127.0.0.1:8787/catbook/web/nyangnyang-chur-landing-standalone.html
```

집사용 이야기 노트 HTML:

```text
http://127.0.0.1:8787/catbook/web/manuscript.html
```

냥톨로지 2D 지식그래프:

```text
http://127.0.0.1:8787/catbook/web/ontology.html
```

냥톨로지 3D 살쾡이자리:

```text
http://127.0.0.1:8787/catbook/web/ontology-3d.html
```

제작 프로세스 매뉴얼:

```text
http://127.0.0.1:8787/catbook/web/production-process-manual.html
```

catbook 관련 작업 기록은 `work-requests/`가 아니라 `catbook/project-records/work-requests/`에서 확인한다.

인트라넷 미리보기:

```powershell
powershell -ExecutionPolicy Bypass -File catbook/scripts/start-intranet-preview.ps1 -Port 8790 -MaxPort 8800 -Restart
```

반환되는 `http://192.168.82.xxx:8790/web/index.html` 형식의 URL은 그대로 사용한다.

서버가 꺼져 있으면 프로젝트 루트에서 실행한다.

```powershell
python -m http.server 8787 --bind 127.0.0.1
```

## 핵심 산출물

- 전수 콘텐츠 아틀라스: `research/content_atlas.json`
- 아틀라스 리포트: `research/content-atlas-report.md`
- 채널 분석 리포트: `research/channel-analysis-report.md`
- 숏폼 포함 최신 유튜브 메타: `research/youtube_meta_all_tabs_2026-06-05.json`
- 숏폼/1분 미만 후보 목록: `research/youtube_meta_shortform_2026-06-05.csv`
- 숏폼 포함 메타 보강 리포트: `research/youtube-meta-refresh-report-2026-06-05.md`
- 냥톨로지 그래프 빌더: `research/build_cat_ontology_graph.py`
- 냥톨로지 SQLite DB: `data/catbook_ontology.sqlite`
- 냥톨로지 JSON export: `research/cat_ontology_graph.json`
- 냥톨로지 RDF Turtle: `data/catbook_ontology.ttl`
- 냥톨로지 OWL/RDFXML: `data/catbook_ontology.owl`
- 냥톨로지 SHACL shapes: `data/catbook_shapes.ttl`
- 냥톨로지 RDF/OWL 웹 상태 JSON: `data/catbook_rdf_status.json`
- RDF/OWL export 스크립트: `research/export_cat_ontology_rdf.py`
- RDF/OWL 검증 스크립트: `research/validate_cat_ontology_rdf.py`
- RDF/OWL 로컬 검증 게이트: `scripts/validate-rdf-owl.ps1`
- SPARQL competency queries: `research/queries/*.rq`
- 냥톨로지 생성 리포트: `research/cat-ontology-graph-report.md`
- 책 기획서: `manuscript/book-proposal.md`
- v2 빠른 독서판 보관본: `manuscript/nyangnyang-chur-manuscript-v2.md`
- v3 핵심 확장 원고: `manuscript/nyangnyang-chur-manuscript-v3-core-expanded.md`
- v3 나머지 30유닛 확장 원고: `manuscript/nyangnyang-chur-manuscript-v3-remaining-expanded.md`
- v3 전체 통합 원고: `manuscript/nyangnyang-chur-manuscript-v3-complete.md`
- 출판 패키지: `manuscript/publishing-package.md`
- 독자 체크 카드: `manuscript/reader-check-cards.md`
- 표지 배경 시안: `assets/cover-window-notebook-cat.png`
- 소개 웹페이지: `web/index.html`
- 냥톨로지 2D 지식그래프 웹페이지: `web/ontology.html`
- 냥톨로지 3D 살쾡이자리 웹페이지: `web/ontology-3d.html`
- 단일 HTML 소개 페이지: `web/nyangnyang-chur-landing-standalone.html`
- 집사용 이야기 노트 HTML: `web/manuscript.html`
- 제작 프로세스 매뉴얼: `web/production-process-manual.html`
- 검증 리포트: `evidence/verification-report.md`
- 구성 다이어그램 인덱스: `diagrams/README.md`

## 냥톨로지 적용 요약

- 적용 목적: 흩어진 유튜브 공개 메타, 콘텐츠 아틀라스, 책 목차, 고양이 행동 신호를 초보자 질문에서 출발하는 탐색형 지식그래프로 연결한다.
- 데이터 흐름: `research/build_cat_ontology_graph.py`가 `research/youtube_meta_all_tabs_2026-06-05.json`과 `research/content_atlas.json`을 읽어 `data/catbook_ontology.sqlite`를 만들고, 정적 웹용 `research/cat_ontology_graph.json`으로 export한다.
- RDF/OWL 흐름: 같은 빌더가 JSON export 이후 `research/export_cat_ontology_rdf.py`를 호출해 `data/catbook_ontology.ttl`, `data/catbook_ontology.owl`, `data/catbook_shapes.ttl`을 함께 갱신한다.
- SSOT: 운영 질의 원본은 `data/catbook_ontology.sqlite`, 의미론적 표준 산출물은 `data/catbook_ontology.ttl`과 `data/catbook_ontology.owl`, 웹 표시용 산출물은 `research/cat_ontology_graph.json`과 `data/catbook_rdf_status.json`이다. SQLite에는 `nodes`, `edges`, `content_items`, `content_matches`, `content_topics`, `scenarios`, `relations`, `classes`, `safety_rules`, `metadata` 테이블과 `v_node_counts_by_class`, `v_edge_counts_by_relation`, `v_top_evidence_concepts` 뷰가 있다.
- 그래프 규모: 스키마 `2026-06-05.2` 기준 노드 396개, 엣지 2,039개, 콘텐츠 인덱스 1,277개, 개념 매칭 콘텐츠 815개, 그래프 표시용 근거 콘텐츠 노드 260개, RDF triple 82,471개를 포함한다.
- 콘텐츠 범위: 최신 메타는 영상 649개와 Shorts 628개를 합친 1,277개 고유 콘텐츠를 기준으로 하며, Shorts 또는 1분 미만 후보 632개를 온톨로지 후보 풀에 반영했다.
- 주요 클래스: `Scenario`, `Topic`, `BookPart`, `Chapter`, `CatSignal`, `HealthObservation`, `EnvironmentElement`, `Need`, `CareAction`, `SafetyRisk`, `Source`를 사용한다.
- 주요 관계: `STARTS_WITH`, `HAS_TOPIC`, `COVERS`, `MAY_INDICATE`, `OBSERVE_WITH`, `SUGGESTS`, `SUPPORTS`, `REQUIRES_RECORD`, `CONSULT_WHEN`, `PREVENTS`, `HAS_EVIDENCE` 등 13개 관계를 사용한다.
- 초보자 입구: `갑자기 뛰어요`, `숨어요`, `하악질해요`, `토했어요`, `화장실이 달라졌어요`, `밥을 안 먹어요`, `배고파 보여요`, `습식·건식이 고민돼요`, `그루밍·빗질이 고민돼요`, `둘째를 고민해요`, `위험할까 걱정돼요`의 11개 상황 질문을 제공한다.
- 2D 화면: `web/ontology.html`은 `초보 길잡이`, `온톨로지`, `콘텐츠 근거` 모드와 검색, 상황 입구, 상세 패널을 통해 JSON export를 탐색한다.
- 3D 화면: `web/ontology-3d.html`은 `3d-force-graph@1.80.0` 기반 WebGL 화면이며, `살쾡이자리 관측선` 은유로 상황 노드를 잇고 `초보`, `구조`, `근거` 모드를 제공한다.
- 제작 매뉴얼 반영: `web/production-process-manual.html`에는 냥톨로지 적용 섹션이 추가되어 콘텐츠 인덱스, 노드, 엣지, RDF triple 수치와 `공개 메타 수집 -> SQLite SSOT -> JSON/RDF/OWL export -> 2D/3D 탐색 -> 원고/웹 반영` 흐름을 한 화면에서 볼 수 있다.
- 적용 샘플: 매뉴얼은 `하악질해요`, `토했어요`, `둘째를 고민해요`를 샘플로 들어 각각 `Scenario -> CatSignal/HealthObservation/Need -> CareAction/SafetyRisk`로 이어지는 실제 노드 경로와 체크 질문을 보여준다.
- 명칭 통일: 사용자-facing 명칭은 2D/3D 페이지 title, brand, H1, JSON meta, SQLite metadata, 루트 노드 label 모두 `냥톨로지`로 통일했다.
- 안전 원칙: 건강/진료 관계는 진단이나 처방이 아니라 관찰, 기록, 상담 준비로만 표현한다. 유튜브 자막 원문과 영상 파일은 저장하거나 재배포하지 않는다.

## RDF/OWL 검증

최초 1회 또는 새 환경에서는 RDF 의존성을 설치한다.

```powershell
python -m pip install -r catbook\requirements-rdf.txt
```

전체 온톨로지 산출물을 다시 생성한다.

```powershell
python catbook\research\build_cat_ontology_graph.py
```

RDF/OWL 적용 여부를 검증한다.

```powershell
python catbook\research\validate_cat_ontology_rdf.py
```

로컬에서 전체 재생성, Python 문법 검사, RDF/OWL/SHACL/SPARQL/추론 검증을 한 번에 실행하려면 검증 게이트를 사용한다.

```powershell
powershell -ExecutionPolicy Bypass -File catbook\scripts\validate-rdf-owl.ps1 -SkipInstall
```

검증은 Turtle/OWL 파싱, SHACL 적합성, 8개 SPARQL 질의, RDFS/OWL-RL 추론 triple 증가를 확인한다. 같은 기준은 `.github/workflows/catbook-rdf-owl.yml`에서도 사용한다. 검증 스크립트는 `data/catbook_rdf_status.json`을 함께 생성하고, 2D/3D 냥톨로지 웹페이지는 이 파일을 읽어 `RDF/OWL 상태`, triple 수, SHACL/SPARQL/추론 지표와 TTL/OWL/SHACL 링크를 표시한다. 최신 검증 증거는 `project-records/work-requests/2026-06-08-catbook-ontology-rdf-owl-audit/evidence/rdf-owl-validation-2026-06-08.md`에 있다.

## 최신 UI/UX 업데이트

- 2026-06-05 리서치 보강에서 `@catdoctor/videos`와 `@catdoctor/shorts`를 함께 수집해 합산 고유 콘텐츠 1,277개, 숏폼 또는 1분 미만 후보 632개를 별도 메타 산출물로 추가했다.
- 소개 페이지에 `고양이 신호` 카테고리 섹션을 추가해 생활, 집 안 동선, 마음 거리, 건강 메모, 함께 살기, 오래 함께를 바로 선택할 수 있게 했다.
- 제작자 중심의 기술 표기를 `츄르의 관찰일지`, `집사용 이야기 노트`, `냥냥노트 목차`처럼 독자 친화적인 표현으로 교체했다.
- 원고 도입부의 내부 제작 메모를 제거하고, 독자가 바로 이해할 수 있는 `이 노트는 이렇게 펼친다` 안내로 바꿨다.
- 최신 검증 캡처: `evidence/web-integrated-cat-landing-desktop.png`, `evidence/web-integrated-cat-landing-mobile.png`, `evidence/web-integrated-cat-popup-desktop.png`, `evidence/web-integrated-cat-popup-mobile.png`, `evidence/web-integrated-manuscript-mobile-top-v2.png`
- 냥톨로지 3D 화면을 `살쾡이자리` 시각화로 업그레이드해 WebGL 별자리 관측선, Lynx 리서치 은유, 데스크톱/모바일 검증 캡처를 추가했다.
- 냥톨로지 백엔드를 `data/catbook_ontology.sqlite` SSOT로 승격하고, 웹 대시보드는 SQLite에서 export된 `research/cat_ontology_graph.json`을 읽도록 유지했다. 2D/3D 화면 상단에는 `SQLite DB` 출처와 `RDF Pass` 상태가 표시된다.
- 사용자-facing 콘텐츠 타이틀은 2D/3D 페이지, JSON meta, SQLite metadata, 루트 노드 모두 `냥톨로지`로 통일했다.
- 제작 프로세스 매뉴얼에 `냥톨로지` 내비게이션, 적용 흐름 시각화, RDF/OWL 상태, SSOT 파일 링크, 샘플 노드 경로, RDF/OWL 검증 명령을 추가했다.
- 매뉴얼의 프로세스 단계와 산출물 검색 목록에 `냥톨로지 SSOT와 RDF/OWL 적용` 단계를 추가해 `ontology`, `RDF`, `하악질`, `토했어요`, `둘째` 같은 검색어로 관련 파일과 작업 단계를 찾을 수 있게 했다.
