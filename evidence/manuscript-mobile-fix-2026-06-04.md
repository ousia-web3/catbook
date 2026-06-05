# 원고 상세페이지 모바일 긴급 수정 검증

- 일시: 2026-06-04
- 대상: `web/manuscript.html`
- 문제: 400px 모바일 뷰포트에서 목차 칩과 원고 영역이 오른쪽으로 밀려 가로 스크롤 및 본문 클리핑 발생
- 수정: 모바일 본문 래퍼 폭을 뷰포트 안으로 고정하고, 560px 이하 목차를 가로 스크롤 칩에서 2열 그리드로 변경했으며, 본문/인용문/메모 카드에 줄바꿈 보호를 추가함

## 검증

- HTTP 확인: `http://127.0.0.1:8787/work-requests/2026-06-02-nyangnyang-chur-cat-book/web/manuscript.html` → 200
- Playwright 400px 근처 검증: `docScrollWidth`가 `docClientWidth`를 넘지 않음, 오버플로 요소 0개
- Playwright 320px 근처 검증: `docScrollWidth`가 `docClientWidth`를 넘지 않음, 오버플로 요소 0개

## 참고

- C 드라이브 여유 공간이 0바이트라 신규 스크린샷 증거는 추가하지 않았음
