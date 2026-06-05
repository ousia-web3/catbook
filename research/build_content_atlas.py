import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
INVENTORY = BASE / "video_inventory_ko.json"
PARTIAL_TRANSCRIPTS = BASE / "partial_transcript_summary.json"
OUT_JSON = BASE / "content_atlas.json"
OUT_MD = BASE / "content-atlas-report.md"


BOOK_TOPICS = {
    "CAT-SIGNAL 행동 신호": [
        "행동",
        "성격",
        "편안",
        "좋아",
        "싫어",
        "하악",
        "골골",
        "꾹꾹",
        "우다다",
        "꼬리",
        "눈",
        "귀",
        "인사",
        "기억",
        "스트레스",
        "공격",
        "싸움",
        "무는",
        "물어요",
        "울음",
        "야옹",
    ],
    "CARE-ROUTINE 생활 돌봄": [
        "간식",
        "츄르",
        "사료",
        "먹이",
        "밥",
        "물",
        "음수",
        "습식",
        "건식",
        "장난감",
        "놀이",
        "캣타워",
        "스크래처",
        "이동장",
        "방묘",
        "목욕",
        "빗질",
        "옷",
        "출근",
    ],
    "HEALTH-CHECK 건강 관찰": [
        "수의사",
        "진료",
        "병원",
        "건강",
        "아프",
        "통증",
        "구토",
        "토",
        "설사",
        "혈뇨",
        "방광",
        "신장",
        "치아",
        "피부",
        "턱드름",
        "발톱",
        "중성화",
        "비만",
        "다이어트",
        "예방",
        "검사",
    ],
    "LITTER-LOG 배변/화장실": [
        "똥",
        "변",
        "오줌",
        "소변",
        "배변",
        "배뇨",
        "화장실",
        "모래",
        "감자",
        "맛동산",
    ],
    "RELATIONSHIP 관계/합사": [
        "합사",
        "둘째",
        "다묘",
        "보호자",
        "집사",
        "가족",
        "아기",
        "아이",
        "인간관계",
        "질투",
        "분리",
        "외로",
        "손절",
    ],
    "LIFE-STORY 서사/상담": [
        "사연",
        "상담",
        "고민",
        "자랑",
        "과시대회",
        "이름",
        "운명",
        "철학관",
        "레전드",
        "일상",
        "데뷔",
        "TMI",
        "이벤트",
    ],
    "BREED-KNOWLEDGE 묘종/지식": [
        "묘종",
        "품종",
        "백과",
        "랙돌",
        "먼치킨",
        "스코티쉬",
        "폴드",
        "페르시안",
        "러시안",
        "브리티쉬",
        "벵갈",
        "유전",
        "외모",
        "털",
    ],
    "ETHICS-SAFETY 윤리/안전": [
        "입양",
        "구조",
        "길고양이",
        "실종",
        "유기",
        "학대",
        "위험",
        "안전",
        "독성",
        "죽음",
        "장례",
        "노묘",
        "새끼",
    ],
}

SERIES_HINTS = [
    "묘종백과",
    "고양식탁",
    "집사메이커",
    "묘한 진료실",
    "냥천재",
    "미야옹철학관",
    "고양이 과시대회",
    "TMI",
    "궁디팡팡",
]


def norm(text: str) -> str:
    return text.lower().replace(" ", "")


def pick_topics(title: str) -> dict[str, int]:
    compact = norm(title)
    scores = {}
    for topic, terms in BOOK_TOPICS.items():
        score = 0
        for term in terms:
            if norm(term) in compact:
                score += 2 if len(term) >= 3 else 1
        if score:
            scores[topic] = score
    if not scores:
        scores["MIXED-ENTERTAINMENT 기획/엔터테인먼트"] = 1
    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))


def extract_series(title: str) -> str:
    for hint in SERIES_HINTS:
        if hint.lower() in title.lower():
            return hint
    if "[" in title and "]" in title:
        start = title.find("[")
        end = title.find("]", start + 1)
        if end > start:
            return title[start + 1 : end].strip()[:40]
    if "ㅣ" in title:
        tail = title.split("ㅣ", 1)[1].strip()
        if tail:
            return tail[:40]
    return "단발/일반"


def reading_format(topic: str) -> str:
    if topic.startswith("HEALTH") or topic.startswith("LITTER"):
        return "증상 단정 없이 관찰 기록 -> 병원 상담 기준 -> 이야기 장면"
    if topic.startswith("CAT-SIGNAL"):
        return "행동 장면 -> 감정/환경 번역 -> 30초 체크"
    if topic.startswith("CARE"):
        return "집 안 동선/물건 배치 -> 바로 바꾸는 미션 카드"
    if topic.startswith("RELATIONSHIP"):
        return "사람의 욕심과 고양이의 속도 대비 -> 선택권 체크"
    if topic.startswith("ETHICS"):
        return "위험 회피/책임 윤리 -> 작은 행동 선언"
    if topic.startswith("BREED"):
        return "품종 호기심 -> 유전/건강 주의 -> 캐릭터 카드"
    return "웃긴 제목의 긴장을 짧은 생활 서사로 재배치"


def chapter_candidate(topics: list[str]) -> str:
    main = topics[0]
    if main.startswith("CAT-SIGNAL"):
        return "Part 3. 마음의 속도를 맞추는 일"
    if main.startswith("CARE"):
        return "Part 2. 집 안에 놓는 안심"
    if main.startswith("HEALTH") or main.startswith("LITTER"):
        return "Part 4. 몸이 보내는 작은 알림"
    if main.startswith("RELATIONSHIP"):
        return "Part 5. 같이 산다는 것의 거리"
    if main.startswith("ETHICS"):
        return "Part 6. 오래 같이 살기 위한 책임"
    if main.startswith("BREED"):
        return "Part 7. 고양이라는 종을 더 정확히 보기"
    return "Part 1. 웃다가 배우는 고양이 생활"


def duration_band(minutes: float) -> str:
    if minutes < 5:
        return "short-form 일반영상"
    if minutes < 12:
        return "standard"
    if minutes < 25:
        return "deep-dive"
    return "long-talk"


def tokenize_title(title: str) -> list[str]:
    return re.findall("[가-힣A-Za-z0-9]{2,}", title.lower())


def main() -> None:
    rows = json.loads(INVENTORY.read_text(encoding="utf-8"))
    non = [r for r in rows if not r.get("is_short_duration_le_60")]
    transcript_summary = {}
    if PARTIAL_TRANSCRIPTS.exists():
        transcript_summary = json.loads(PARTIAL_TRANSCRIPTS.read_text(encoding="utf-8"))

    videos = []
    topic_counts = Counter()
    topic_minutes = Counter()
    series_counts = Counter()
    band_counts = Counter()
    term_counts = Counter()
    examples = defaultdict(list)

    for row in non:
        topics_score = pick_topics(row["title"])
        topics = list(topics_score.keys())
        main_topic = topics[0]
        minutes = float(row.get("duration_min") or 0)
        series = extract_series(row["title"])
        band = duration_band(minutes)
        topic_counts.update(topics)
        topic_minutes.update({main_topic: minutes})
        series_counts[series] += 1
        band_counts[band] += 1
        term_counts.update(tokenize_title(row["title"]))
        if len(examples[main_topic]) < 18:
            examples[main_topic].append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "duration_min": row["duration_min"],
                    "url": row["url"],
                    "series": series,
                }
            )
        videos.append(
            {
                "index": row["index"],
                "id": row["id"],
                "title": row["title"],
                "url": row["url"],
                "duration_min": row["duration_min"],
                "duration_band": band,
                "series": series,
                "topic_scores": topics_score,
                "dominant_topics": topics[:4],
                "book_part_candidate": chapter_candidate(topics),
                "book_conversion": reading_format(main_topic),
            }
        )

    atlas = {
        "source": "video_inventory_ko.json",
        "method": "Full metadata/title census for 644 non-Shorts plus partial non-verbatim transcript signals where available.",
        "limits": [
            "Full transcript collection was blocked by YouTube 429/IP limits after partial success.",
            "No transcript text is stored; this atlas is safe for original manuscript planning but not a substitute for licensed source material.",
        ],
        "total_non_shorts": len(non),
        "duration_hours": round(sum(float(r.get("duration") or 0) for r in non) / 3600, 2),
        "topic_counts_multi_label": dict(topic_counts.most_common()),
        "topic_minutes_by_primary": {k: round(v, 2) for k, v in topic_minutes.most_common()},
        "series_counts": dict(series_counts.most_common(40)),
        "duration_band_counts": dict(band_counts.most_common()),
        "top_title_terms": term_counts.most_common(120),
        "topic_examples": dict(examples),
        "partial_transcript_summary": transcript_summary,
        "videos": videos,
    }
    OUT_JSON.write_text(json.dumps(atlas, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# 콘텐츠 아틀라스 전수 분석")
    lines.append("")
    lines.append("## 핵심 결론")
    lines.append("")
    lines.append(f"- Shorts 제외 전체 후보: {len(non)}개")
    lines.append(f"- 전체 분량: 약 {atlas['duration_hours']}시간")
    lines.append("- 이번 보강은 제목/길이/시리즈 신호를 644개 전수 분석하고, 확보된 자막 분석 신호를 보조로 결합했다.")
    lines.append("- 자막 원문은 저장하지 않았다. 원고는 원본 콘텐츠의 문장·구성·진행자 말투를 복제하지 않는 독립 창작으로 유지한다.")
    lines.append("")
    lines.append("## 주제별 전수 분포")
    lines.append("")
    lines.append("| 주제 | 영상 수 | 1차 원고 전환 방식 |")
    lines.append("| --- | ---: | --- |")
    for topic, count in topic_counts.most_common():
        lines.append(f"| {topic} | {count} | {reading_format(topic)} |")
    lines.append("")
    lines.append("## 주요 시리즈/포맷 신호")
    lines.append("")
    lines.append("| 시리즈/형식 | 영상 수 |")
    lines.append("| --- | ---: |")
    for series, count in series_counts.most_common(30):
        lines.append(f"| {series} | {count} |")
    lines.append("")
    lines.append("## 길이 구조")
    lines.append("")
    lines.append("| 길이 밴드 | 영상 수 |")
    lines.append("| --- | ---: |")
    for band, count in band_counts.most_common():
        lines.append(f"| {band} | {count} |")
    lines.append("")
    lines.append("## 책 구조로의 재설계")
    lines.append("")
    lines.append("채널의 방대한 콘텐츠는 그대로 요약본으로 옮기면 산만해진다. 책은 다음 7개 파트로 압축하는 편이 좋다.")
    lines.append("")
    for part in [
        "Part 1. 웃다가 배우는 고양이 생활",
        "Part 2. 집 안에 놓는 안심",
        "Part 3. 마음의 속도를 맞추는 일",
        "Part 4. 몸이 보내는 작은 알림",
        "Part 5. 같이 산다는 것의 거리",
        "Part 6. 오래 같이 살기 위한 책임",
        "Part 7. 고양이라는 종을 더 정확히 보기",
    ]:
        lines.append(f"- {part}")
    lines.append("")
    lines.append("## 주제별 대표 영상 예시")
    lines.append("")
    for topic, items in examples.items():
        lines.append(f"### {topic}")
        lines.append("")
        for item in items[:10]:
            lines.append(f"- {item['title']} ({item['duration_min']}분) — {item['url']}")
        lines.append("")
    lines.append("## 전수 파일")
    lines.append("")
    lines.append("- `content_atlas.json`: 644개 비-Shorts 영상별 주제, 시리즈, 책 파트 후보, 전환 방식")
    lines.append("- `video_inventory_ko.csv`: 원본 메타데이터 표")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({k: atlas[k] for k in ["total_non_shorts", "duration_hours", "duration_band_counts", "topic_counts_multi_label"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
