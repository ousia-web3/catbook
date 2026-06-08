# Decision Log

```text
{D-01, 리서치 범위, Shorts 제외 전체 업로드를 duration > 60초 기준으로 분류,
"YouTube Shorts URL만으로는 누락 가능성이 있어 duration 기준을 병행",
"648개 중 644개를 비-Shorts 후보로 분석",
"대안: URL /shorts/만 제외",
"보류: YouTube 표시상 Shorts지만 60초 초과인 예외"}
```

```text
{D-02, 자막 저장 정책, 전체 자막 원문 미저장,
"저작권 리스크를 낮추고 분석 목적에 맞는 비원문 신호만 보존",
"원고 독립성과 공개 가능성이 높아짐",
"대안: 전체 transcript raw 저장",
"보류: 특정 영상 세부 검증이 필요할 때만 제한적 재조회"}
```

```text
{D-03, 글쓰기 스킬 방향, AI 탐지 회피 대신 자연 문학 편집 스킬로 전환,
"탐지 회피 목적의 지침은 부적절하므로 창작 품질과 목소리 개선에 집중",
"책 원고의 윤리성과 출판 안정성이 높아짐",
"대안: 탐지 회피 프롬프트 작성",
"보류: 최종 출판 시 AI 사용 표기 정책 검토"}
```

```text
{D-04, 책 형식, 3분 에피소드 + 30초 체크 + 1문장 다짐 구조,
"일반 사용자가 빠르게 읽는 새로운 형태라는 요구에 직접 부합",
"반복 리듬이 생겨 웹 소개 페이지와도 잘 연결됨",
"대안: 일반 에세이/정보서 형식",
"보류: 최종 분량과 인쇄 판형"}
```

```text
{D-05, 숏폼 포함 메타 보강, videos 탭과 shorts 탭을 분리 수집해 합산 인벤토리를 별도 산출물로 보존,
"기존 리서치는 duration > 60초 비-Shorts 중심이라 지식그래프의 생활/밈/짧은 행동 신호가 누락될 수 있음",
"합산 고유 콘텐츠 1,277개와 숏폼 또는 1분 미만 후보 632개를 온톨로지 후보 풀로 확보",
"대안: 기존 644개 비-Shorts 아틀라스만 유지",
"보류: shorts 상세 duration/업로드일/설명은 후보 선별 후 저속 상세 수집"}
```

```text
{D-06, 온톨로지 SQLite SSOT 승격, catbook/data/catbook_ontology.sqlite를 운영 원본으로 만들고 JSON은 SQLite export 산출물로 유지,
"JSON만으로는 노드/엣지/콘텐츠 매칭을 질의하거나 검증하기 어렵고, 추후 챕터/콘텐츠/관계 확장 시 구조화 저장소가 필요함",
"정적 웹 대시보드는 그대로 JSON을 읽어 배포 단순성을 유지하면서 DB 테이블과 view로 온톨로지 지식화를 검증할 수 있음",
"대안: JSON 단일 산출물 유지 또는 웹에서 SQLite를 직접 로드",
"보류: 웹 런타임의 직접 SQLite/WASM 로딩, 추가 콘텐츠 상세 수집 후 증분 업데이트"}
```

```text
{D-07, 콘텐츠 타이틀 통일, 사용자-facing 지식그래프 콘텐츠명을 냥톨로지로 적용,
"냥 + 온톨로지의 결합어로 고양이 지식화 콘셉트를 직관적으로 전달하고 2D/3D/DB 메타 명칭 혼선을 줄임",
"2D/3D 페이지 title, brand, H1, JSON meta, SQLite metadata, 루트 노드 label이 같은 이름을 사용함",
"대안: 냥냥츄르 Cat Ontology 또는 살쾡이자리 지식그래프를 페이지별 제목으로 유지",
"보류: 책 본체 브랜드 냥냥츄르와 냥톨로지 서브브랜드의 최종 출판/마케팅 표기 체계"}
```

```text
{D-08, RDF/OWL 1차 전환, SQLite/JSON 지식그래프에 RDF Turtle, OWL/RDFXML, SHACL, SPARQL, RDFS/OWL-RL 검증 계층을 추가,
"RDF/OWL 적용이 필수 요구사항이므로 표준 온톨로지 산출물과 재현 가능한 검증 파이프라인이 필요함",
"catbook/data/catbook_ontology.ttl, catbook_ontology.owl, catbook_shapes.ttl과 8개 SPARQL competency query, SHACL 직접 타입 검증, 로컬/CI 검증 게이트를 확보함",
"대안: open-ontologies MCP를 즉시 핵심 의존성으로 채택",
"보류: open-ontologies/Oxigraph는 2차 운영 보조 엔진으로 검토"}
```
