# catbook 구성 다이어그램

이 폴더는 `catbook/` 프로젝트의 구조를 유형별 PlantUML 파일로 정리한 문서 묶음이다. 외부 C4 include 없이 순수 PlantUML 문법만 사용해 로컬 PlantUML, VS Code PlantUML 확장, Kroki 같은 렌더러에서 바로 열 수 있게 했다.

## 다이어그램 목록

| 파일 | 유형 | 목적 |
| --- | --- | --- |
| `00-project-context.puml` | 컨텍스트 다이어그램 | 사용자, Jarvis 운영 모델, `catbook/`, 유튜브 공개 메타, 로컬 웹 미리보기의 관계를 본다. |
| `01-directory-map.puml` | 마인드맵 | 폴더와 핵심 산출물을 운영, 리서치, 데이터, 원고, 웹, 자산, 검증으로 묶어 본다. |
| `02-research-content-flow.puml` | 데이터 흐름 다이어그램 | 유튜브 메타와 자막 신호가 비원문 리서치 산출물로 변환되는 과정을 본다. |
| `03-ontology-rdf-pipeline.puml` | 파이프라인 다이어그램 | SQLite SSOT, JSON export, RDF/OWL/SHACL, SPARQL 검증 흐름을 본다. |
| `04-web-runtime.puml` | 웹 런타임 컴포넌트 | 소개 페이지, 원고 페이지, 2D/3D 냥톨로지 화면과 정적 자산 의존성을 본다. |
| `05-manuscript-assets-flow.puml` | 원고/자산 제작 흐름 | 원고 조립, 원고 HTML 생성, 이미지 자산 반영 과정을 본다. |
| `06-agent-operations-sequence.puml` | 시퀀스 다이어그램 | Human Conductor, Jarvis, Friday, 전문 에이전트의 작업 운영 순서를 본다. |
| `07-validation-risk-shield.puml` | 검증/리스크 게이트 | 저작권, 의료 표현, RDF/OWL, 웹, 증거 기록의 확인 지점을 본다. |

## 렌더링 예시

```powershell
plantuml catbook\diagrams\*.puml
```

PlantUML CLI가 없으면 VS Code의 PlantUML 확장이나 Kroki 호환 프리뷰에서 개별 파일을 열어 확인한다.
