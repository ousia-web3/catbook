# 생성 이미지 보안 표시 및 우클릭 방지 검증 기록

## 요청

- `1~45` 생성 이미지에 `AI 생성` 표기를 추가한다.
- 워터마크는 이미지 파일을 다시 합성하지 않고 HTML/CSS/JS 레이어로 처리한다.
- 우클릭 사용을 금지한다.
- 추가 보안 이슈를 점검한다.

## 적용 내용

- `catbook/web/manuscript.html`
  - `assets/generated/` 경로의 이미지 42개를 자동 감지해 부모 `figure`에 `ai-generated-media` 클래스를 부여한다.
  - CSS `::after` 의사요소로 `AI 생성` 배지를 렌더링한다.
  - 이미지 파일 자체는 수정하지 않았다.
  - 전체 페이지 `contextmenu` 이벤트를 차단하고, 생성 이미지의 `dragstart`와 `draggable` 속성을 차단한다.
- `catbook/web/styles.css`, `catbook/web/script.js`
  - 공용 랜딩 페이지에도 같은 가드를 추가했다.
  - 향후 `assets/generated/` 경로의 배너가 추가되면 자동으로 `AI 생성` 표시가 붙는다.
- `catbook/web/nyangnyang-chur-landing-standalone.html`
  - standalone HTML에도 같은 CSS/JS 가드를 반영했다.
- `catbook/web/production-process-manual.html`
  - 매뉴얼 HTML에도 우클릭 차단과 생성 이미지 자동 표시 가드를 반영했다.
- `catbook/scripts/build_manuscript_html.py`
  - 향후 원고 HTML을 재생성할 때도 같은 CSS/JS 가드가 포함되도록 보강했다.

## 검증

- 정적 검증
  - `node --check catbook/web/script.js`
  - `python -m py_compile catbook/scripts/build_manuscript_html.py`
- HTTP 응답
  - `http://127.0.0.1:8787/catbook/web/manuscript.html?security=20260605` 응답 200
  - `http://127.0.0.1:8787/catbook/web/index.html?security=20260605` 응답 200
  - `http://127.0.0.1:8787/catbook/web/production-process-manual.html?security=20260605` 응답 200
- 브라우저 검증
  - `manuscript.html` 생성 이미지 감지 수: 42
  - `AI 생성` 표시 클래스 적용 수: 42
  - 첫 생성 이미지 CSS `::after` 표시값: `"AI 생성"`
  - 첫 생성 이미지 `draggable` 속성: `false`
  - 본문 우클릭 이벤트 차단: true
  - 이미지 우클릭 이벤트 차단: true
  - 이미지 드래그 시작 차단: true
  - 데스크톱/모바일 가로 오버플로: 0
  - 모바일 390px 폭 콘솔 오류: 없음

## 보안 점검 메모

- CSS/JS 워터마크와 우클릭 차단은 공개 웹에서 원본 다운로드를 완전히 막는 보안 장치가 아니라 얕은 억제 장치다.
- 공개 페이지에 노출된 이미지는 개발자 도구, 네트워크 패널, 브라우저 캐시, 스크린샷으로 여전히 획득될 수 있다.
- 실제 보호 강도가 필요하면 공개 정적 파일 경로 대신 인증된 이미지 라우트, 서명 URL, 만료 URL, CDN 토큰 정책을 검토해야 한다.
- 배포 시 권장 보안 헤더:
  - `Content-Security-Policy`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy`
  - `Permissions-Policy`
  - `frame-ancestors` 또는 `X-Frame-Options`
- 클라이언트 HTML/JS에는 비밀키, 내부 프롬프트, 유료 원본 다운로드 경로, 개인정보를 포함하지 않는 것이 좋다.
- AI 생성 표시는 법적/정책적 고지와 별개로 사용자가 볼 수 있는 공개 문구 또는 약관에도 한 번 더 명시하는 편이 안전하다.
