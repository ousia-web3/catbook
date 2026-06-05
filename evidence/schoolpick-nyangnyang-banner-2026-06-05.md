# SchoolPick 모바일 배너 이미지 생성 검증

## 요청 요약

- 대상 URL: `https://schoolpick.vercel.app/`
- 목적: SchoolPick 모바일 웹페이지에 넣을 `냥냥츄르 이야기` 분위기의 배너 이미지를 만든다.

## 화면 기준

- 모바일 홈은 흰 배경, 파란 포인트, 카드형 UI, 검색 중심 구조다.
- 배너는 텍스트를 이미지에 직접 넣지 않고, 앱에서 HTML 텍스트를 올릴 수 있도록 왼쪽 여백을 남겼다.
- 기존 `catbook/assets/hero-window-cat-1280.jpg`를 기반으로 웹용 배너를 합성했다.

## 산출물

| 용도 | 파일 | 크기 |
| --- | --- | ---: |
| 원본급 PNG | `catbook/assets/generated/banners/schoolpick-nyangnyang-banner-mobile-1170x450.png` | 350,789 bytes |
| 권장 WebP 3x | `catbook/assets/generated/banners/schoolpick-nyangnyang-banner-mobile-1170x450.webp` | 31,336 bytes |
| 권장 WebP 2x | `catbook/assets/generated/banners/schoolpick-nyangnyang-banner-mobile-780x300.webp` | 16,866 bytes |
| 권장 WebP 1x | `catbook/assets/generated/banners/schoolpick-nyangnyang-banner-mobile-390x150.webp` | 6,076 bytes |

## 검증

- 이미지 열람 확인 완료.
- 모바일 배너 비율: 390 x 150 기준 대응.
- 웹 적용 시 원본 PNG보다 WebP `srcset` 사용 권장.
- 이미지 생성 도구가 요청 제한에 걸려, 기존 프로젝트 자산 기반 로컬 합성 방식으로 생성했다.

## 권장 적용 예시

```html
<picture>
  <source
    type="image/webp"
    srcset="
      /assets/schoolpick-nyangnyang-banner-mobile-390x150.webp 390w,
      /assets/schoolpick-nyangnyang-banner-mobile-780x300.webp 780w,
      /assets/schoolpick-nyangnyang-banner-mobile-1170x450.webp 1170w
    "
    sizes="calc(100vw - 48px)"
  />
  <img
    src="/assets/schoolpick-nyangnyang-banner-mobile-1170x450.png"
    alt="창가의 고양이와 관찰 노트가 있는 냥냥츄르 이야기 배너"
    width="1170"
    height="450"
    loading="lazy"
    decoding="async"
  />
</picture>
```
