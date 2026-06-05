# 검증 리포트

## 1. 리서치 검증

- 전체 업로드 메타데이터 수집: 648개
- Shorts 제외 기준: duration > 60초
- 비-Shorts 후보: 644개
- 비-Shorts 총 분량: 약 100.56시간
- 콘텐츠 아틀라스 생성: `research/content_atlas.json`
- 전수 아틀라스 리포트: `research/content-atlas-report.md`

## 2. 자막 수집 검증

- 자막 API 처리 시도: 94개
- 성공: 34개
- 실패: 60개
- 주요 실패 원인: YouTube IP block / HTTP 429
- yt-dlp 단건 자막 재시도도 HTTP 429로 실패
- 원문 자막 저장 정책: 전체 자막 원문 저장 안 함

판단:

- 전체 영상 목록과 제목/길이/시리즈 기반 전수 분석은 완료.
- 전체 자막 심층 분석은 플랫폼 제한으로 1차 완료 범위에서 제외.
- 이 제한은 원고의 독립성에는 유리하지만, “모든 영상 발화 내용의 문장 단위 분석”으로 주장하면 안 된다.

## 3. 원고 검증

- 12장 초안: `manuscript/nyangnyang-chur-manuscript.md`
- 확장 구조 v2: `manuscript/book-structure-v2.md`
- 42유닛 빠른 독서판 원고: `manuscript/nyangnyang-chur-manuscript-v2.md`
- v2 원고 규모: 523라인, 3,111단어, 21,891자 기준

검토 기준:

- 원본 영상 대본 문장 복제 없음
- 채널 말투/진행자 캐릭터 모방 없음
- 건강 표현은 진단/처방 대신 관찰/기록/상담 기준으로 작성
- AI 탐지 회피 목적 지침은 만들지 않고 자연 문체 편집 스킬로 전환

## 4. 이미지 자산 검증

- `assets/hero-window-cat.png`
- `assets/carrier-cat.png`
- `assets/litter-log-cat.png`

검토:

- 웹페이지에 필요한 3개 이미지 모두 작업 폴더로 복사 완료.
- 원본 생성 파일은 `.codex/generated_images/`에 그대로 보존.
- 이미지에는 텍스트, 로고, 워터마크 없음.

## 5. 웹페이지 검증

로컬 URL:

```text
http://127.0.0.1:8787/work-requests/2026-06-02-nyangnyang-chur-cat-book/web/index.html
```

검증 내용:

- HTTP 200 응답 확인
- HTML/CSS/JS 파일 존재 확인
- 이미지와 원고 링크 참조 파일 존재 확인
- Playwright CLI 데스크톱 스크린샷 생성: `evidence/web-desktop.png`
- Playwright CLI 모바일 스크린샷 생성: `evidence/web-mobile.png`

제한:

- 로컬 Node 프로젝트에 `playwright` 모듈이 설치되어 있지 않아 콘솔 이벤트 수집 스크립트는 실패.
- `npx playwright install chromium` 중 디스크 여유 공간 부족 경고가 발생했지만, 이후 데스크톱/모바일 스크린샷 생성은 성공.
- C 드라이브 잔여 공간이 약 267MB 수준이므로 추가 대용량 생성/설치는 피해야 한다.

## 6. 남은 리스크

- 전체 자막 심층 분석은 YouTube 429 제한 해소 후 저속 배치로 재개할 수 있다.
- 출판 전에는 수의학 표현을 전문가가 감수해야 한다.
- 실제 출판/판매/배포는 Human Conductor 승인 필요.
- 생성 이미지를 상업 출판 표지에 쓰려면 별도 아트 디렉션과 라이선스 정책 확인이 필요하다.

## 7. 최종 보강 검증

2026-06-02 후속 작업에서 다음 산출물을 추가로 완료했다.

- 나머지 30개 유닛 확장 원고: `manuscript/nyangnyang-chur-manuscript-v3-remaining-expanded.md`
- 42유닛 전체 통합 원고: `manuscript/nyangnyang-chur-manuscript-v3-complete.md`
- 통합 원고 조립 스크립트: `scripts/build_complete_manuscript.py`
- 표지 배경 시안 이미지: `assets/cover-window-notebook-cat.png`
- 웹 표지 섹션과 최종 원고 CTA 반영: `web/index.html`

구조 검사 결과:

- 파트 수: 7
- 장 수: 42
- `30초 체크`: 42개
- `집사 메모`: 42개
- `오늘의 한 문장`: 42개
