# catbook 폴더 이동 및 접속 호환성 검증

## 요청 요약

- 기존 `work-requests/2026-06-02-nyangnyang-chur-cat-book/`에 있던 냥냥츄르 관련 작업 산출물을 Jarvis 루트 아래로 이동한다.
- 새 폴더명은 `catbook/`으로 단순화한다.
- HTML 경로, 로컬 접속, `192.168.82.xxx` 인트라넷 접속에 영향이 없도록 한다.

## 적용 내용

- 실제 산출물 폴더 전체를 `catbook/`으로 이동했다.
  - `assets/`
  - `evidence/`
  - `manuscript/`
  - `research/`
  - `scripts/`
  - `skills/`
  - `web/`
- 기존 경로 `work-requests/2026-06-02-nyangnyang-chur-cat-book/`에는 호환용 최소 파일만 남겼다.
  - `web/index.html`
  - `web/manuscript.html`
  - `web/nyangnyang-chur-landing-standalone.html`
  - `scripts/start-intranet-preview.ps1`
  - `scripts/stop-intranet-preview.ps1`
  - `README.md`
- 기존 `work-requests/.../web/*.html` URL은 브라우저에서 새 `catbook/web/*.html`로 이동한다.
- 기존 `work-requests/.../scripts/start-intranet-preview.ps1` 실행은 새 `catbook/scripts/start-intranet-preview.ps1`로 위임한다.
- `catbook/README.md`의 로컬/인트라넷 URL 안내를 새 경로 기준으로 갱신했다.

## 검증 결과

| 항목 | URL 또는 명령 | 결과 |
| --- | --- | --- |
| 새 로컬 메인 | `http://127.0.0.1:8787/catbook/web/index.html` | 200 |
| 기존 로컬 메인 호환 | `http://127.0.0.1:8787/work-requests/2026-06-02-nyangnyang-chur-cat-book/web/index.html` | 200, `catbook/web/index.html` 안내 포함 |
| 새 로컬 원고 | `http://127.0.0.1:8787/catbook/web/manuscript.html` | 200 |
| 기존 로컬 원고 호환 | `http://127.0.0.1:8787/work-requests/2026-06-02-nyangnyang-chur-cat-book/web/manuscript.html` | 200, `catbook/web/manuscript.html` 안내 포함 |
| 새 standalone | `http://127.0.0.1:8787/catbook/web/nyangnyang-chur-landing-standalone.html` | 200 |
| 기존 standalone 호환 | `http://127.0.0.1:8787/work-requests/2026-06-02-nyangnyang-chur-cat-book/web/nyangnyang-chur-landing-standalone.html` | 200, `catbook/web/nyangnyang-chur-landing-standalone.html` 안내 포함 |
| 새 로컬 자산 | `http://127.0.0.1:8787/catbook/assets/hero-window-cat-1280.jpg` | 200 |
| 인트라넷 메인 | `http://192.168.82.199:8790/web/index.html` | 200 |
| 인트라넷 자산 | `http://192.168.82.199:8790/assets/hero-window-cat-1280.jpg` | 200 |
| 인트라넷 standalone | `http://192.168.82.199:8790/web/nyangnyang-chur-landing-standalone.html` | 200 |
| 기존 인트라넷 시작 스크립트 | `work-requests/.../scripts/start-intranet-preview.ps1` | 새 `catbook` servedRoots 반환 |
| JS 문법 검사 | `node --check catbook/web/script.js` | 통과 |

## 현재 접속 경로

- 로컬 메인: `http://127.0.0.1:8787/catbook/web/index.html`
- 로컬 원고: `http://127.0.0.1:8787/catbook/web/manuscript.html`
- 로컬 standalone: `http://127.0.0.1:8787/catbook/web/nyangnyang-chur-landing-standalone.html`
- 인트라넷 메인: `http://192.168.82.199:8790/web/index.html`
- 인트라넷 원고: `http://192.168.82.199:8790/web/manuscript.html`
- 인트라넷 standalone: `http://192.168.82.199:8790/web/nyangnyang-chur-landing-standalone.html`

## 메모

- 실제 산출물은 `catbook/`에만 있다.
- 기존 작업 요청 경로에는 접속 호환을 위한 작은 래퍼만 남겼다.
