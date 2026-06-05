# 웹페이지 3종 최적화 검증 기록

## 개요

- 일시: 2026-06-04
- 대상:
  - `web/index.html`
  - `web/manuscript.html`
  - `web/nyangnyang-chur-landing-standalone.html`
- 요청: 냥냥츄르 웹페이지 3종 최적화

## 적용 요약

- 첫 화면 hero 이미지를 원본 PNG 직접 로드에서 축소 JPEG 우선 로드로 변경했다.
- `hero-window-cat-1280.jpg`와 `hero-window-cat-768.jpg` 파생 자산을 추가했다.
- `index.html`은 CSS/JS에 버전 쿼리를 붙여 브라우저 캐시로 이전 스크립트가 실행되는 문제를 방지했다.
- `standalone` 페이지는 공통 `index.html`, `styles.css`, `script.js` 기준으로 내장 CSS/JS를 다시 동기화했다.
- 긴 원고 페이지는 `content-visibility: auto`를 장 단위에 적용하고, 모바일에서 파트 목차를 유지했다.
- skip link, reduced motion 대응, focus-visible, tab/tabpanel ARIA, 모달 `aria-hidden` 상태 동기화를 보강했다.

## 정적 검증

- `node --check web/script.js`: 통과
- 새 이미지 자산:
  - `assets/hero-window-cat-1280.jpg`: 96,153 bytes
  - `assets/hero-window-cat-768.jpg`: 41,770 bytes
  - 기존 `assets/hero-window-cat.png`: 1,941,912 bytes, 원본 보존

## 브라우저 검증

로컬 대시보드 서버 `http://127.0.0.1:8787/`에서 Playwright로 확인했다.

| 페이지 | HTTP | 콘솔 오류 | 4xx/실패 요청 | 데스크톱 가로 스크롤 | 모바일 가로 스크롤 | 핵심 확인 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `index.html` | 200 | 0 | 0 | 없음 | 없음 | hero `hero-window-cat-1280.jpg` 로드, tab panel 라벨 정상 |
| `manuscript.html` | 200 | 0 | 0 | 없음 | 없음 | 장 단위 `content-visibility: auto`, 모바일 파트 목차 표시 |
| `nyangnyang-chur-landing-standalone.html` | 200 | 0 | 0 | 없음 | 없음 | standalone 내장 CSS/JS 최신화, hero JPEG 로드 |

## 상호작용 검증

- 카테고리 카드 클릭 시 모달 열림: 통과
- 모달 열림 상태에서 `aria-hidden="false"` 동기화: 통과
- `Escape`로 모달 닫힘 및 포커스 복귀: 통과
- 탭 컨트롤에서 `ArrowRight` 이동 시 선택 파트와 `aria-labelledby` 갱신: 통과

## 스크린샷 증거

- `web-optimization-index-desktop.png`
- `web-optimization-index-mobile.png`
- `web-optimization-manuscript-desktop.png`
- `web-optimization-manuscript-mobile.png`
- `web-optimization-nyangnyang-chur-landing-standalone-desktop.png`
- `web-optimization-nyangnyang-chur-landing-standalone-mobile.png`

## 리스크

- 외부 배포나 공개 릴리스는 수행하지 않았다.
- 원본 이미지는 삭제하지 않고 보존했다.
- `standalone`은 공통 파일에서 재생성했으므로 이후 공통 랜딩을 수정하면 같은 동기화 절차가 필요하다.
