import concurrent.futures
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi


BASE = Path(__file__).resolve().parent
INVENTORY = BASE / "video_inventory_ko.json"
OUT_JSONL = BASE / "transcript_insights.jsonl"
SUMMARY = BASE / "transcript_summary.json"
PROGRESS = BASE / "transcript_progress.json"

MAX_WORKERS = 4

TOPIC_TERMS = {
    "행동/감정": [
        "행동",
        "성격",
        "편안",
        "긴장",
        "스트레스",
        "불안",
        "공격",
        "하악",
        "울음",
        "골골",
        "꾹꾹",
        "우다다",
        "꼬리",
        "귀",
        "눈",
        "동공",
        "사냥",
        "놀이",
        "합사",
        "사회화",
        "영역",
        "기억",
        "인사",
    ],
    "건강/진료": [
        "수의사",
        "병원",
        "진료",
        "검사",
        "치료",
        "예방",
        "통증",
        "구토",
        "설사",
        "변비",
        "혈뇨",
        "방광",
        "신장",
        "치아",
        "비만",
        "다이어트",
        "중성화",
        "피부",
        "턱드름",
        "알레르기",
        "수술",
        "백신",
        "발톱",
        "똥",
    ],
    "생활/돌봄": [
        "사료",
        "간식",
        "츄르",
        "물",
        "음수",
        "습식",
        "건식",
        "영양",
        "칼로리",
        "화장실",
        "모래",
        "스크래처",
        "캣타워",
        "이동장",
        "방묘",
        "장난감",
        "출근",
        "외출",
        "보호자",
        "집사",
    ],
    "품종/지식": [
        "품종",
        "묘종",
        "랙돌",
        "먼치킨",
        "스코티쉬",
        "페르시안",
        "러시안",
        "브리티쉬",
        "벵갈",
        "유전",
        "외모",
        "털",
    ],
    "관계/윤리": [
        "입양",
        "구조",
        "길고양이",
        "노묘",
        "새끼",
        "가족",
        "아이",
        "학대",
        "유기",
        "책임",
        "안전",
        "위험",
        "독성",
        "법",
    ],
    "서사/상담": [
        "사연",
        "고민",
        "상담",
        "이름",
        "운명",
        "자랑",
        "이벤트",
        "레전드",
        "일상",
        "가족",
        "기억",
    ],
}

STOPWORDS = {
    "그리고",
    "그러면",
    "그런데",
    "그래서",
    "하지만",
    "이렇게",
    "저렇게",
    "오늘",
    "진짜",
    "약간",
    "너무",
    "정말",
    "지금",
    "계속",
    "우리",
    "고양이",
    "고양이가",
    "고양이는",
    "보호자",
    "집사",
    "여러분",
    "제가",
    "저는",
    "이거",
    "그거",
    "저거",
    "이런",
    "그런",
    "저런",
    "때문",
    "경우",
    "생각",
    "합니다",
    "있습니다",
    "없습니다",
}


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) <= 20]


def topic_hits(text: str, title: str) -> dict[str, int]:
    combined = f"{title}\n{text}"
    hits = {}
    for topic, terms in TOPIC_TERMS.items():
        count = sum(combined.count(term) for term in terms)
        if count:
            hits[topic] = count
    return dict(sorted(hits.items(), key=lambda item: item[1], reverse=True))


def fetch_one(row: dict) -> dict:
    video_id = row["id"]
    result = {
        "index": row["index"],
        "id": video_id,
        "title": row["title"],
        "url": row["url"],
        "duration_min": row["duration_min"],
        "metadata_categories": row.get("categories", ""),
        "transcript_status": "pending",
    }
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        transcript = None
        try:
            transcript = transcript_list.find_transcript(["ko"])
        except Exception:
            transcript = transcript_list.find_generated_transcript(["ko"])
        fetched = transcript.fetch()
        lines = [snippet.text.strip() for snippet in fetched if snippet.text and snippet.text.strip()]
        text = " ".join(lines)
        terms = Counter(tokenize(text))
        hits = topic_hits(text, row["title"])
        result.update(
            {
                "transcript_status": "ok",
                "language_code": transcript.language_code,
                "language": transcript.language,
                "is_generated": transcript.is_generated,
                "line_count": len(lines),
                "char_count": len(text),
                "top_terms": terms.most_common(18),
                "topic_hits": hits,
                "dominant_topics": list(hits.keys())[:3],
                "non_verbatim_digest": build_digest(row["title"], hits, terms),
            }
        )
    except Exception as exc:
        result.update(
            {
                "transcript_status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc)[:500],
            }
        )
    return result


def build_digest(title: str, hits: dict[str, int], terms: Counter) -> list[str]:
    dominant = list(hits.keys())[:3] if hits else ["기타/엔터테인먼트"]
    top_terms = [term for term, _ in terms.most_common(8)]
    digest = [f"영상 주제 후보: {', '.join(dominant)}"]
    if top_terms:
        digest.append(f"반복 출현 신호: {', '.join(top_terms)}")
    if "건강/진료" in dominant:
        digest.append("창작 전환 포인트: 증상 단정 대신 관찰-기록-병원 상담의 안전한 흐름으로 변환")
    if "행동/감정" in dominant:
        digest.append("창작 전환 포인트: 행동을 꾸짖기보다 감정과 환경을 읽는 장면으로 변환")
    if "생활/돌봄" in dominant:
        digest.append("창작 전환 포인트: 집사의 일상 선택이 고양이의 안심감으로 이어지는 구조")
    if len(digest) == 1:
        digest.append(f"제목 기반 맥락: {title[:80]}")
    return digest


def write_progress(done: int, total: int, ok: int, errors: int, started: float) -> None:
    payload = {
        "done": done,
        "total": total,
        "ok": ok,
        "errors": errors,
        "elapsed_sec": round(time.time() - started, 1),
        "updated_at_epoch": time.time(),
    }
    PROGRESS.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    rows = json.loads(INVENTORY.read_text(encoding="utf-8"))
    targets = [row for row in rows if not row.get("is_short_duration_le_60")]
    total = len(targets)
    started = time.time()
    done = ok = errors = 0
    aggregate_terms = Counter()
    aggregate_topics = Counter()
    status_counts = Counter()
    results = []

    OUT_JSONL.write_text("", encoding="utf-8")
    write_progress(done, total, ok, errors, started)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(fetch_one, row) for row in targets]
        with OUT_JSONL.open("a", encoding="utf-8") as out:
            for future in concurrent.futures.as_completed(futures):
                item = future.result()
                results.append(item)
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
                out.flush()
                done += 1
                status_counts[item["transcript_status"]] += 1
                if item["transcript_status"] == "ok":
                    ok += 1
                    aggregate_terms.update(dict(item.get("top_terms", [])))
                    aggregate_topics.update(item.get("topic_hits", {}))
                else:
                    errors += 1
                if done % 10 == 0 or done == total:
                    write_progress(done, total, ok, errors, started)

    by_topic_examples = defaultdict(list)
    for item in sorted(results, key=lambda r: r.get("index", 99999)):
        for topic in item.get("dominant_topics", [])[:2]:
            if len(by_topic_examples[topic]) < 12:
                by_topic_examples[topic].append(
                    {
                        "id": item["id"],
                        "title": item["title"],
                        "duration_min": item.get("duration_min"),
                        "url": item["url"],
                    }
                )

    summary = {
        "source_inventory": str(INVENTORY.name),
        "targets_non_shorts": total,
        "transcript_ok": ok,
        "transcript_errors": errors,
        "status_counts": dict(status_counts),
        "aggregate_topics": dict(aggregate_topics.most_common()),
        "aggregate_terms": aggregate_terms.most_common(80),
        "topic_examples": dict(by_topic_examples),
        "elapsed_sec": round(time.time() - started, 1),
        "copyright_note": "Full transcripts were not saved; only non-verbatim analysis signals, counts, and keywords are stored.",
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_progress(done, total, ok, errors, started)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
