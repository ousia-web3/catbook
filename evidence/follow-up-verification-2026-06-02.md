# 후속 작업 검증 리포트

## 1. 요청 재오픈

- requestId: `nyangnyang-chur-cat-book`
- 재오픈 사유: 사용자가 “이어서 진행” 요청
- 재오픈 결과: `start-jarvis-request.ps1`로 기존 Done 상태에서 In Progress 이벤트 기록

## 2. 환경 상태

- C 드라이브 여유 공간: 약 118MB
- 판단: 이미지 추가 생성, 브라우저 추가 설치, 대용량 자막 저장 작업은 위험
- 대응: 텍스트 중심 산출물 작성, 원문 자막 미저장 유지

## 3. 자막 백필 파이프라인

생성 파일:

- `research/slow_transcript_backfill.py`

기능:

- 이미 성공한 자막 영상은 건너뜀
- 비-Shorts 목록에서 미처리 영상만 시도
- 자막 원문 전체 저장 금지
- 주제 히트, 키워드, 비원문 digest만 저장
- IP block/429 감지 시 즉시 상태 저장 후 중지 가능

소규모 테스트:

- 실행: `--max-videos 3 --sleep-min 12 --sleep-max 18 --stop-on-block`
- 결과: 첫 번째 미처리 영상에서 `IpBlocked`
- 성공 추가: 0개
- 결론: 현재 네트워크 경로로는 YouTube 자막 재수집 불가

상태 파일:

- `research/transcript_backfill_state.json`

## 4. 출판 패키지 보강

생성 파일:

- `manuscript/publishing-package.md`
- `manuscript/editorial-expansion-map.md`

포함 내용:

- 제목/부제 후보
- 책 소개문
- 뒷표지 문구
- 서문 초안
- 표지 아트 디렉션
- 6만~10만 자 확장 계획
- 수의학 감수 체크리스트
- 저작권/원천 콘텐츠 처리 원칙
- 웹/마케팅 카피

## 5. 원고 v3 핵심 확장

생성 파일:

- `manuscript/nyangnyang-chur-manuscript-v3-core-expanded.md`

확장 유닛:

1. 똥을 보고 쓰는 일기
2. 병원에 가져갈 세 줄
3. 하악질의 번역
4. 합사는 사랑보다 동선이다
5. 토한 뒤에 해야 할 일
6. 물을 많이 마신 날
7. 우다다는 혼난 뒤가 아니라 비운 뒤에 온다
8. 꼬리가 먼저 말한 날
9. 소파 밑 38센티미터
10. 화장실은 집의 중심이다
11. 싸움이 끝난 뒤 사람이 해야 할 일
12. 노묘의 느린 대답

규모:

- 189라인
- 1,912단어
- 14,204자 기준

판단:

- v2의 짧은 유닛을 출판 초고 스타일로 확장하는 방향을 12개 핵심 유닛에 적용했다.
- 전체 42유닛 중 건강/행동/환경/관계 핵심 축을 먼저 보강했다.

## 6. 추가 출판 산출물

생성 파일:

- `manuscript/medical-review-notes.md`
- `manuscript/reader-check-cards.md`
- `manuscript/cover-concepts.md`

포함 내용:

- 수의학 감수 우선순위와 표시 체계
- 독자용 30초 체크 카드 12종
- 표지 콘셉트 3종
- 표지 문구와 아트 디렉션

## 7. 후속 완료 작업

- v3 원고를 나머지 30개 유닛까지 확장했다.
- `nyangnyang-chur-manuscript-v3-complete.md`로 42유닛 전체 원고를 7파트 순서에 맞춰 조립했다.
- `build_complete_manuscript.py`로 통합 원고 재생성 경로를 남겼다.
- 표지 배경 시안 `assets/cover-window-notebook-cat.png`를 생성해 웹에 반영했다.
- 웹 CTA를 v3 전체 원고로 연결했다.

## 8. 남은 리스크와 다음 액션

- 자막 재수집은 현재 차단 상태라 반복 실행해도 성과 없이 차단만 길어질 수 있다.
- 출판 원고 확장은 가능하지만, 건강 파트는 전문가 감수 전까지 “최종 의학 조언”으로 쓰면 안 된다.
- 실제 출판/판매/외부 배포는 Human Conductor 승인 후 진행해야 한다.
- 상업 표지 사용 전에는 생성 이미지 사용 정책과 별도 디자인 감수를 확인해야 한다.
