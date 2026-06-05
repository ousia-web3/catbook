# 30초 체크 취소선 제거 검증

## 요청 요약

- `30초 체크` 항목을 체크해도 항목 문장에 취소선이 적용되지 않게 수정한다.

## 수정 내용

- `web/manuscript.html`의 체크 완료 텍스트 스타일에서 `text-decoration: line-through` 관련 선언을 제거했다.
- `scripts/build_manuscript_html.py`의 재생성용 체크리스트 CSS에서도 같은 선언을 제거했다.
- 체크 완료 상태는 체크박스, 배경색, 진행률로만 표현한다.

## 검증 결과

- `line-through`, `text-decoration-thickness`, `text-underline-offset` 검색 결과: 없음
- `build_manuscript_html.py` 문법 검사: 통과
- 로컬 페이지 HTTP 응답: 200
- 체크 후 진행률: `1/4 완료`
- 체크된 항목 계산 스타일: `textDecorationLine = none`

## 검증 캡처

- `manuscript-checklist-no-strikethrough-2026-06-04.png`
