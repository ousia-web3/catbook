import argparse
import json
import random
import re
import time
from collections import Counter
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi


BASE = Path(__file__).resolve().parent
INVENTORY = BASE / "video_inventory_ko.json"
EXISTING = BASE / "transcript_insights.jsonl"
OUT_JSONL = BASE / "transcript_backfill_insights.jsonl"
STATE = BASE / "transcript_backfill_state.json"

TOPIC_TERMS = {
    "행동/감정": ["행동", "성격", "편안", "스트레스", "하악", "우다다", "꼬리", "귀", "눈", "인사", "기억", "싸움", "합사"],
    "건강/진료": ["수의사", "병원", "진료", "검사", "치료", "통증", "구토", "설사", "혈뇨", "방광", "신장", "치아", "피부", "발톱", "똥"],
    "생활/돌봄": ["사료", "간식", "츄르", "물", "습식", "건식", "화장실", "모래", "이동장", "장난감", "놀이", "출근"],
    "관계/윤리": ["입양", "구조", "길고양이", "실종", "가족", "아기", "책임", "안전", "위험", "노묘"],
    "품종/지식": ["묘종", "품종", "백과", "랙돌", "먼치킨", "스코티쉬", "페르시안", "유전", "외모", "털"],
    "서사/상담": ["사연", "고민", "상담", "이름", "운명", "자랑", "이벤트", "레전드", "일상"],
}

STOPWORDS = {
    "그리고", "그런데", "그래서", "하지만", "이렇게", "저렇게", "오늘", "진짜", "약간", "너무", "정말",
    "지금", "우리", "고양이", "고양이가", "고양이는", "보호자", "집사", "여러분", "제가", "저는",
    "이거", "그거", "저거", "이런", "그런", "저런", "합니다", "있습니다", "없습니다", "근데", "웃음",
    "음악", "이제", "있는", "하는", "하고", "그냥", "내가", "같아요", "때문에", "되게", "가지고",
}


def load_done_ids() -> set[str]:
    done = set()
    for path in (EXISTING, OUT_JSONL):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("transcript_status") == "ok":
                done.add(item["id"])
    return done


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", text.lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) <= 20]


def topic_hits(text: str, title: str) -> dict[str, int]:
    combined = f"{title}\n{text}"
    hits = {}
    for topic, terms in TOPIC_TERMS.items():
        count = sum(combined.count(term) for term in terms)
        if count:
            hits[topic] = count
    return dict(sorted(hits.items(), key=lambda item: item[1], reverse=True))


def digest(title: str, hits: dict[str, int], terms: Counter) -> list[str]:
    dominant = list(hits.keys())[:3] if hits else ["기타/엔터테인먼트"]
    result = [f"영상 주제 후보: {', '.join(dominant)}"]
    if terms:
        result.append("반복 출현 신호: " + ", ".join(term for term, _ in terms.most_common(8)))
    if "건강/진료" in dominant:
        result.append("책 전환: 증상 단정 대신 관찰-기록-상담 구조")
    if "행동/감정" in dominant:
        result.append("책 전환: 행동을 문제로 단정하지 않고 환경/감정 신호로 번역")
    if "생활/돌봄" in dominant:
        result.append("책 전환: 물건 배치와 루틴을 30초 체크로 전환")
    if len(result) == 1:
        result.append(f"제목 기반 보조 맥락: {title[:80]}")
    return result


def fetch(video: dict) -> dict:
    video_id = video["id"]
    result = {
        "index": video["index"],
        "id": video_id,
        "title": video["title"],
        "url": video["url"],
        "duration_min": video.get("duration_min"),
        "transcript_status": "pending",
    }
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    try:
        transcript = transcript_list.find_transcript(["ko"])
    except Exception:
        transcript = transcript_list.find_generated_transcript(["ko"])
    fetched = transcript.fetch()
    lines = [snippet.text.strip() for snippet in fetched if snippet.text and snippet.text.strip()]
    text = " ".join(lines)
    terms = Counter(tokenize(text))
    hits = topic_hits(text, video["title"])
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
            "non_verbatim_digest": digest(video["title"], hits, terms),
        }
    )
    return result


def save_state(payload: dict) -> None:
    STATE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-videos", type=int, default=5)
    parser.add_argument("--sleep-min", type=float, default=20.0)
    parser.add_argument("--sleep-max", type=float, default=45.0)
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--stop-on-block", action="store_true")
    args = parser.parse_args()

    rows = json.loads(INVENTORY.read_text(encoding="utf-8"))
    done_ids = load_done_ids()
    targets = [
        row
        for row in rows
        if not row.get("is_short_duration_le_60")
        and row["id"] not in done_ids
        and row["index"] >= args.start_index
    ]

    attempted = ok = errors = 0
    started = time.time()
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)

    with OUT_JSONL.open("a", encoding="utf-8") as out:
        for video in targets[: args.max_videos]:
            attempted += 1
            try:
                item = fetch(video)
                ok += 1
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
                out.flush()
            except Exception as exc:
                errors += 1
                item = {
                    "index": video["index"],
                    "id": video["id"],
                    "title": video["title"],
                    "url": video["url"],
                    "duration_min": video.get("duration_min"),
                    "transcript_status": "error",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:700],
                }
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
                out.flush()
                lowered = item["error"].lower()
                if args.stop_on_block and ("blocked" in lowered or "too many requests" in lowered or "ip" in lowered):
                    save_state(
                        {
                            "status": "blocked",
                            "reason": item,
                            "attempted": attempted,
                            "ok": ok,
                            "errors": errors,
                            "elapsed_sec": round(time.time() - started, 1),
                        }
                    )
                    break
            save_state(
                {
                    "status": "running" if attempted < args.max_videos else "finished",
                    "attempted": attempted,
                    "ok": ok,
                    "errors": errors,
                    "last_video": {"id": video["id"], "index": video["index"], "title": video["title"]},
                    "elapsed_sec": round(time.time() - started, 1),
                }
            )
            if attempted < args.max_videos:
                time.sleep(random.uniform(args.sleep_min, args.sleep_max))

    final = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    final.update({"attempted": attempted, "ok": ok, "errors": errors, "elapsed_sec": round(time.time() - started, 1)})
    if final.get("status") == "running":
        final["status"] = "finished"
    save_state(final)
    print(json.dumps(final, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
