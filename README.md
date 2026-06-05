# 냥냥츄르 고양이 이야기 책 + 소개 웹페이지 작업

## 작업 개요

- 요청자 원문: 미야옹철의 냥냥펀치 유튜브 채널의 Shorts 제외 전체 콘텐츠를 분석해, `냥냥츄르`라는 고양이 이야기를 담은 책을 출판하고 관련 소개 웹페이지까지 구현한다.
- 채널: 미야옹철의 냥냥펀치
- 채널 URL: https://www.youtube.com/@catdoctor/videos
- requestId: `nyangnyang-chur-cat-book`
- 작업 시작일: 2026-06-02
- 현재 폴더: `catbook/`
- 이전 작업 폴더 경로 `work-requests/2026-06-02-nyangnyang-chur-cat-book/`에는 브라우저 호환용 리다이렉트만 남겨 둔다.

## 산출물 구조

- `human-brief.md`: 사용자 요청 기반 Human Brief 초안
- `jarvis-strategy-brief.md`: Jarvis 전략 판단과 성공 기준
- `friday-task-breakdown.md`: 에이전트별 작업 분해
- `decision-log.md`: 주요 결정과 보류 리스크
- `research/`: 채널 메타데이터, 자막 기반 비원문 분석, 리서치 리포트
- `skills/`: 원고 작성에 사용할 프로젝트 전용 문체 스킬
- `manuscript/`: 책 기획서, 목차, 원고
- `web/`: 소개 웹페이지 구현물
- `assets/`: 생성 이미지와 웹 자산
- `evidence/`: 실행/검증 증거
- `scripts/build_complete_manuscript.py`: v3 핵심/나머지 확장본을 7파트 42유닛 순서로 조립하는 스크립트
- `scripts/build_standalone_html.py`: 소개 페이지를 CSS/JS 인라인 단일 HTML로 조립하는 스크립트
- `scripts/build_manuscript_html.py`: v3 전체 원고 Markdown을 집사용 이야기 노트 HTML로 변환하는 스크립트

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

기존 `work-requests/2026-06-02-nyangnyang-chur-cat-book/web/*.html` URL은 위 `catbook` URL로 자동 이동한다.

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
- 책 기획서: `manuscript/book-proposal.md`
- v2 빠른 독서판 보관본: `manuscript/nyangnyang-chur-manuscript-v2.md`
- v3 핵심 확장 원고: `manuscript/nyangnyang-chur-manuscript-v3-core-expanded.md`
- v3 나머지 30유닛 확장 원고: `manuscript/nyangnyang-chur-manuscript-v3-remaining-expanded.md`
- v3 전체 통합 원고: `manuscript/nyangnyang-chur-manuscript-v3-complete.md`
- 출판 패키지: `manuscript/publishing-package.md`
- 독자 체크 카드: `manuscript/reader-check-cards.md`
- 표지 배경 시안: `assets/cover-window-notebook-cat.png`
- 소개 웹페이지: `web/index.html`
- 단일 HTML 소개 페이지: `web/nyangnyang-chur-landing-standalone.html`
- 집사용 이야기 노트 HTML: `web/manuscript.html`
- 검증 리포트: `evidence/verification-report.md`

## 최신 UI/UX 업데이트

- 소개 페이지에 `고양이 신호` 카테고리 섹션을 추가해 생활, 집 안 동선, 마음 거리, 건강 메모, 함께 살기, 오래 함께를 바로 선택할 수 있게 했다.
- 제작자 중심의 기술 표기를 `츄르의 관찰일지`, `집사용 이야기 노트`, `냥냥노트 목차`처럼 독자 친화적인 표현으로 교체했다.
- 원고 도입부의 내부 제작 메모를 제거하고, 독자가 바로 이해할 수 있는 `이 노트는 이렇게 펼친다` 안내로 바꿨다.
- 최신 검증 캡처: `evidence/web-integrated-cat-landing-desktop.png`, `evidence/web-integrated-cat-landing-mobile.png`, `evidence/web-integrated-cat-popup-desktop.png`, `evidence/web-integrated-cat-popup-mobile.png`, `evidence/web-integrated-manuscript-mobile-top-v2.png`
