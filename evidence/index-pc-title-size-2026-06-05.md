# index.html PC 섹션 타이틀 폰트 조정 검증

## 요청 요약

- `web/index.html`은 모바일에서는 괜찮지만 PC에서 주요 섹션 타이틀이 너무 커 보여 최적화되지 않은 인상을 준다.
- 대상 섹션: `Reading rhythm`, `Cat signals`, `Chur note`, `42 units`, `For cat guardians`.

## 수정 내용

- `web/styles.css`의 공통 섹션 제목 토큰을 PC 기준으로 축소했다.
  - 기존: `clamp(2.2rem, 3.6vw, 3.4rem)`
  - 변경: `clamp(1.85rem, 2.35vw, 2.5rem)`
- `.section-copy h2`, `.final-cta h2`에 `max-width: 720px`를 적용해 PC에서 제목 행 길이를 안정화했다.
- 제목 행간을 `1.18`로 조정해 줄바꿈 후 밀도가 답답하지 않게 했다.
- `web/index.html`의 CSS 캐시 버전을 `20260605-pctitles`로 갱신했다.

## 검증 결과

- 로컬 URL: `http://127.0.0.1:8787/work-requests/2026-06-02-nyangnyang-chur-cat-book/web/index.html`
- HTTP 응답: `200`
- `node --check web/script.js`: 통과
- PC 1440px 기준 계산 폰트 크기: `33.84px`
- 모바일 390px 기준 계산 폰트 크기: `24.8px`
- PC/모바일 모두 가로 오버플로 없음

## 계산 스타일 샘플

| 뷰포트 | 대상 | font-size | line-height | 추정 줄 수 |
| --- | --- | ---: | ---: | ---: |
| PC 1440px | Reading rhythm | 33.84px | 39.93px | 2 |
| PC 1440px | Cat signals | 33.84px | 39.93px | 2 |
| PC 1440px | Chur note | 33.84px | 39.93px | 2 |
| PC 1440px | 42 units | 33.84px | 39.93px | 3 |
| PC 1440px | For cat guardians | 33.84px | 39.93px | 2 |
| Mobile 390px | 공통 섹션 제목 | 24.8px | 30.26px | 2-3 |

## 캡처 증거

- `evidence/index-pc-title-size-format-desktop-2026-06-05.png`
- `evidence/index-pc-title-size-signals-desktop-2026-06-05.png`
- `evidence/index-pc-title-size-chapters-desktop-2026-06-05.png`
- `evidence/index-pc-title-size-cta-desktop-2026-06-05.png`
- `evidence/index-pc-title-size-desktop-2026-06-05.png`
- `evidence/index-pc-title-size-mobile-2026-06-05.png`

## 남은 메모

- `nyangnyang-chur-landing-standalone.html`은 이번 요청 대상이 아니어서 재빌드하지 않았다.
