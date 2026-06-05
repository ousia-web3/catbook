# index.html 메인 제목 줄바꿈 조정 검증

## 요청 요약

- 메인 안내 제목 `하악질은 미움보다 먼저, 거리의 요청일 수 있다`를 2줄로 처리한다.
- 메인 목차 안내 제목 `초보 집사부터 숙련 집사까지, 단계별 생애주기`를 3줄로 처리한다.

## 수정 내용

- `sample-title`을 2개 `span`으로 분리했다.
  - `하악질은 미움보다 먼저,`
  - `거리의 요청일 수 있다`
- `chapters-title`을 3개 `span`으로 분리했다.
  - `초보 집사부터`
  - `숙련 집사까지,`
  - `단계별 생애주기`
- `.title-lines span`에 `display: block`을 적용했다.
- 해당 제목 전용 글자 크기를 조정해 데스크톱/모바일에서 span 내부가 다시 줄바꿈되지 않게 했다.

## 보존 확인

- 탭 버튼 수: 7개
- 렌더링된 전체 챕터 타이틀 수: 42개
- 첫 타이틀: `츄르는 왜 갑자기 뛰었을까`
- 마지막 타이틀: `오늘도 츄르는 나를 훈련시킨다`

## 검증 결과

- 데스크톱 `sample-title`: 2개 span, 각 span 1줄
- 데스크톱 `chapters-title`: 3개 span, 각 span 1줄
- 모바일 `sample-title`: 2개 span, 각 span 1줄
- 모바일 `chapters-title`: 3개 span, 각 span 1줄
- 가로 오버플로: 없음
- 로컬 페이지 HTTP 응답: 200

## 검증 캡처

- `index-title-lines-fixed-desktop-2026-06-04.png`
- `index-title-lines-fixed-mobile-2026-06-04.png`
