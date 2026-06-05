# 사내망 접속 안내

## 접속 URL

사내 임직원이 같은 네트워크에 있을 때 아래 URL로 접속할 수 있다.

```text
http://192.168.82.199:8790/web/index.html
```

추가 페이지:

```text
http://192.168.82.199:8790/web/manuscript.html
http://192.168.82.199:8790/web/nyangnyang-chur-landing-standalone.html
```

## 서버 상태

- 실행 PID: `27824`
- 바인딩: `0.0.0.0:8790`
- 노출 범위:
  - `/web/` -> `work-requests/2026-06-02-nyangnyang-chur-cat-book/web`
  - `/assets/` -> `work-requests/2026-06-02-nyangnyang-chur-cat-book/assets`
- 차단 확인:
  - `/evidence/...` 경로는 `404 File not found`

## 운영 명령

서버 시작 또는 재시작:

```powershell
powershell -ExecutionPolicy Bypass -File work-requests/2026-06-02-nyangnyang-chur-cat-book/scripts/start-intranet-preview.ps1 -Port 8790 -MaxPort 8800 -Restart
```

서버 중지:

```powershell
powershell -ExecutionPolicy Bypass -File work-requests/2026-06-02-nyangnyang-chur-cat-book/scripts/stop-intranet-preview.ps1
```

## 검증 결과

2026-06-04 기준 HTTP HEAD 검증:

| URL | 결과 |
| --- | --- |
| `/web/index.html` | `200 OK` |
| `/web/manuscript.html` | `200 OK` |
| `/web/nyangnyang-chur-landing-standalone.html` | `200 OK` |
| `/assets/hero-window-cat-1280.jpg` | `200 OK` |
| `/evidence/web-optimization-verification-2026-06-04.md` | `404 File not found` |

## 리스크와 안내

- 이 방식은 외부 공개 배포가 아니라 현재 PC에서 사내망으로 여는 임시 미리보기다.
- 접속하려는 임직원은 같은 사내 네트워크 또는 VPN 안에 있어야 한다.
- Windows 방화벽이 Python 서버를 차단하면 이 PC에서 개인/사내 네트워크 접근 허용이 필요할 수 있다.
- PC가 절전, 재부팅, 네트워크 변경 상태가 되면 URL이 바뀌거나 서버가 중단될 수 있다.
- 고정 운영이 필요하면 사내 정적 웹 서버, NAS, IIS, 또는 내부 배포 환경으로 옮기는 것이 적합하다.
