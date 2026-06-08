import csv
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


BASE = Path(__file__).resolve().parent
CHANNEL_HANDLES_ENV = "CATBOOK_YOUTUBE_CHANNEL_HANDLES"
DEFAULT_CHANNEL_HANDLES = ["@catdoctor"]
TAB_NAMES = ("videos", "shorts")
STAMP = datetime.now().strftime("%Y-%m-%d")

OUT_JSON = BASE / f"youtube_meta_all_tabs_{STAMP}.json"
OUT_CSV = BASE / f"youtube_meta_all_tabs_{STAMP}.csv"
OUT_SHORTS_CSV = BASE / f"youtube_meta_shortform_{STAMP}.csv"
OUT_REPORT = BASE / f"youtube-meta-refresh-report-{STAMP}.md"
PREVIOUS_INVENTORY = BASE / "video_inventory_ko.json"


def parse_channel_handles() -> list[str]:
    raw = os.environ.get(CHANNEL_HANDLES_ENV, "")
    if raw.strip():
        handles = [part.strip() for part in re.split(r"[,;\s]+", raw) if part.strip()]
    else:
        handles = DEFAULT_CHANNEL_HANDLES[:]
    if not handles:
        raise ValueError(f"No YouTube channels configured. Set {CHANNEL_HANDLES_ENV} or DEFAULT_CHANNEL_HANDLES.")
    return handles


def channel_base_url(handle: str) -> str:
    cleaned = handle.strip().rstrip("/")
    if cleaned.startswith(("http://", "https://")):
        return re.sub(r"/(videos|shorts)$", "", cleaned)
    return f"https://www.youtube.com/{cleaned}"


def safe_channel_key(handle: str, index: int) -> str:
    candidate = handle.strip().rstrip("/").split("/")[-1].lstrip("@")
    candidate = re.sub(r"[^A-Za-z0-9_-]+", "-", candidate).strip("-").lower()
    return candidate or f"channel-{index}"


def build_channel_sources() -> list[dict]:
    sources = []
    used_keys = set()
    for index, handle in enumerate(parse_channel_handles(), start=1):
        key = safe_channel_key(handle, index)
        if key in used_keys:
            key = f"{key}-{index}"
        used_keys.add(key)
        base_url = channel_base_url(handle)
        sources.append(
            {
                "key": key,
                "handle": handle,
                "base_url": base_url,
                "urls": {tab_name: f"{base_url}/{tab_name}" for tab_name in TAB_NAMES},
            }
        )
    return sources


CHANNEL_SOURCES = build_channel_sources()
CHANNEL_URLS = (
    CHANNEL_SOURCES[0]["urls"]
    if len(CHANNEL_SOURCES) == 1
    else {source["key"]: source["urls"] for source in CHANNEL_SOURCES}
)


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
        "인사",
        "놀이",
        "싸움",
        "물림",
        "무는",
        "깨무",
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
        "토",
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
        "발톱",
        "아프",
    ],
    "생활/돌봄": [
        "간식",
        "츄르",
        "사료",
        "밥",
        "물그릇",
        "음수",
        "습식",
        "건식",
        "화장실",
        "모래",
        "스크래처",
        "캣타워",
        "이동장",
        "목욕",
        "빗질",
        "출근",
        "외출",
        "장난감",
    ],
    "관계/윤리": [
        "합사",
        "둘째",
        "다묘",
        "보호자",
        "집사",
        "가족",
        "아기",
        "입양",
        "구조",
        "길고양이",
        "실종",
        "유기",
        "위험",
        "안전",
        "학대",
        "책임",
    ],
    "품종/지식": [
        "묘종",
        "품종",
        "백과",
        "랙돌",
        "러시안",
        "페르시안",
        "샴",
        "코숏",
        "브리티시",
        "유전",
        "털",
    ],
    "서사/상담": [
        "사연",
        "상담",
        "고민",
        "이름",
        "일상",
        "브이로그",
        "vlog",
        "q&a",
        "tmi",
        "엄마",
        "아빠",
    ],
}


def run_ytdlp(url: str, prefer_ko: bool = True) -> dict:
    command = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        "--ignore-errors",
        "--no-warnings",
    ]
    if prefer_ko:
        command.extend(["--extractor-args", "youtube:lang=ko"])
    command.append(url)
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return json.loads(completed.stdout)


def compact(text: str) -> str:
    return (text or "").lower().replace(" ", "")


def pick_topics(title: str) -> dict[str, int]:
    normalized = compact(title)
    scores = {}
    for topic, terms in TOPIC_TERMS.items():
        score = 0
        for term in terms:
            if compact(term) in normalized:
                score += 2 if len(term) >= 3 else 1
        if score:
            scores[topic] = score
    if not scores:
        scores["기타/엔터테인먼트"] = 1
    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))


def best_thumbnail(entry: dict) -> str:
    thumbnails = entry.get("thumbnails") or []
    if not thumbnails:
        return ""
    scored = sorted(
        thumbnails,
        key=lambda item: ((item.get("width") or 0) * (item.get("height") or 0), item.get("preference") or 0),
        reverse=True,
    )
    return scored[0].get("url") or ""


def as_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def first_payload_value(tab_payloads: dict[str, dict], *keys: str):
    for tab_name in TAB_NAMES:
        payload = tab_payloads.get(tab_name) or {}
        for key in keys:
            value = payload.get(key)
            if value not in (None, "", []):
                return value
    return None


def build_channel_info(source: dict, tab_payloads: dict[str, dict]) -> dict:
    return {
        "key": source["key"],
        "handle": source["handle"],
        "base_url": source["base_url"],
        "id": first_payload_value(tab_payloads, "channel_id", "id"),
        "title": first_payload_value(tab_payloads, "channel", "uploader", "title"),
        "uploader_id": first_payload_value(tab_payloads, "uploader_id"),
        "description": first_payload_value(tab_payloads, "description"),
        "tags": first_payload_value(tab_payloads, "tags") or [],
    }


def legacy_source_urls() -> dict:
    if len(CHANNEL_SOURCES) == 1:
        return CHANNEL_SOURCES[0]["urls"]
    return {source["key"]: source["urls"] for source in CHANNEL_SOURCES}


def format_collection_targets(channels: list[dict]) -> str:
    return ", ".join(
        f"{channel.get('handle') or channel.get('key')}/videos, {channel.get('handle') or channel.get('key')}/shorts"
        for channel in channels
    )


def normalize_entry(
    entry: dict,
    source_tab: str,
    tab_index: int,
    fallback_entry: dict | None = None,
    source_channel: dict | None = None,
) -> dict:
    fallback_entry = fallback_entry or {}
    source_channel = source_channel or {}
    duration = as_float(entry.get("duration"))
    if duration is None:
        duration = as_float(fallback_entry.get("duration"))
    video_id = entry.get("id") or ""
    source_url = entry.get("url") or ""
    fallback_url = fallback_entry.get("url") or ""
    is_shorts_tab = source_tab == "shorts" or "/shorts/" in source_url
    topic_scores = pick_topics(entry.get("title") or "")
    watch_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else source_url
    canonical_url = source_url or fallback_url or watch_url
    return {
        "id": video_id,
        "title": entry.get("title") or "",
        "default_title": fallback_entry.get("title") or "",
        "url": canonical_url,
        "watch_url": watch_url,
        "source_tabs": [source_tab],
        "primary_tab": source_tab,
        "tab_index": tab_index,
        "source_channels": [source_channel.get("key")] if source_channel.get("key") else [],
        "source_channel_key": source_channel.get("key"),
        "source_channel_handle": source_channel.get("handle"),
        "source_channel_id": source_channel.get("id"),
        "source_channel_title": source_channel.get("title"),
        "media_family": "shorts" if is_shorts_tab else "video",
        "duration": duration,
        "duration_min": round(duration / 60, 2) if duration is not None else None,
        "is_duration_under_60": duration <= 60 if duration is not None else None,
        "view_count": entry.get("view_count") if entry.get("view_count") is not None else fallback_entry.get("view_count"),
        "topic_scores": topic_scores,
        "topics": list(topic_scores.keys()),
        "thumbnail_url": best_thumbnail(entry),
    }


def merge_entries(rows: list[dict]) -> list[dict]:
    by_id = {}
    for row in rows:
        video_id = row["id"]
        if not video_id:
            continue
        existing = by_id.get(video_id)
        if not existing:
            by_id[video_id] = row
            continue
        for source_tab in row["source_tabs"]:
            if source_tab not in existing["source_tabs"]:
                existing["source_tabs"].append(source_tab)
        for source_channel in row.get("source_channels", []):
            if source_channel and source_channel not in existing.setdefault("source_channels", []):
                existing["source_channels"].append(source_channel)
        for field in ("source_channel_key", "source_channel_handle", "source_channel_id", "source_channel_title"):
            if not existing.get(field) and row.get(field):
                existing[field] = row[field]
        if existing["duration"] is None and row["duration"] is not None:
            existing["duration"] = row["duration"]
            existing["duration_min"] = row["duration_min"]
            existing["is_duration_under_60"] = row["is_duration_under_60"]
        if not existing["view_count"] and row["view_count"]:
            existing["view_count"] = row["view_count"]
        if not existing["default_title"] and row["default_title"]:
            existing["default_title"] = row["default_title"]
        if existing["primary_tab"] != "shorts" and row["primary_tab"] == "shorts":
            existing["primary_tab"] = "shorts"
            existing["media_family"] = "shorts"
            existing["url"] = row["url"]
    return sorted(by_id.values(), key=lambda item: (item["primary_tab"] != "videos", item["tab_index"]))


def load_previous_ids() -> set[str]:
    if not PREVIOUS_INVENTORY.exists():
        return set()
    with PREVIOUS_INVENTORY.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    return {row.get("id") for row in rows if row.get("id")}


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "no",
        "id",
        "title",
        "default_title",
        "url",
        "watch_url",
        "source_tabs",
        "primary_tab",
        "media_family",
        "duration",
        "duration_min",
        "is_duration_under_60",
        "view_count",
        "topics",
        "thumbnail_url",
        "source_channels",
        "source_channel_handle",
        "source_channel_title",
        "source_channel_id",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for index, row in enumerate(rows, start=1):
            writer.writerow(
                {
                    "no": index,
                    "id": row["id"],
                    "title": row["title"],
                    "default_title": row["default_title"],
                    "url": row["url"],
                    "watch_url": row["watch_url"],
                    "source_tabs": ";".join(row["source_tabs"]),
                    "primary_tab": row["primary_tab"],
                    "media_family": row["media_family"],
                    "duration": row["duration"] if row["duration"] is not None else "",
                    "duration_min": row["duration_min"] if row["duration_min"] is not None else "",
                    "is_duration_under_60": row["is_duration_under_60"] if row["is_duration_under_60"] is not None else "",
                    "view_count": row["view_count"] if row["view_count"] is not None else "",
                    "topics": ";".join(row["topics"]),
                    "thumbnail_url": row["thumbnail_url"],
                    "source_channels": ";".join(row.get("source_channels") or []),
                    "source_channel_handle": row.get("source_channel_handle") or "",
                    "source_channel_title": row.get("source_channel_title") or "",
                    "source_channel_id": row.get("source_channel_id") or "",
                }
            )


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    divider = ["---"] * len(header)
    all_rows = [header, divider, *rows[1:]]
    return "\n".join("| " + " | ".join(str(cell) for cell in row) + " |" for row in all_rows)


def main() -> None:
    collected_at = datetime.now().astimezone().isoformat(timespec="seconds")
    channel_infos = []
    normalized_rows = []

    for source in CHANNEL_SOURCES:
        tab_payloads = {}
        fallback_by_tab = {}
        for tab_name, url in source["urls"].items():
            payload = run_ytdlp(url, prefer_ko=True)
            fallback_payload = run_ytdlp(url, prefer_ko=False)
            tab_payloads[tab_name] = payload
            fallback_by_tab[tab_name] = {
                entry.get("id"): entry
                for entry in fallback_payload.get("entries") or []
                if entry.get("id")
            }

        channel_info = build_channel_info(source, tab_payloads)
        channel_infos.append(channel_info)
        for tab_name, payload in tab_payloads.items():
            fallback_by_id = fallback_by_tab.get(tab_name, {})
            for tab_index, entry in enumerate(payload.get("entries") or [], start=1):
                normalized_rows.append(
                    normalize_entry(entry, tab_name, tab_index, fallback_by_id.get(entry.get("id")), channel_info)
                )

    rows = merge_entries(normalized_rows)
    previous_ids = load_previous_ids()
    current_ids = {row["id"] for row in rows}
    new_ids = current_ids - previous_ids
    missing_ids = previous_ids - current_ids

    tab_counts = Counter()
    channel_counts = Counter()
    topic_counts = Counter()
    for row in rows:
        for tab in row["source_tabs"]:
            tab_counts[tab] += 1
        for channel_key in row.get("source_channels") or []:
            channel_counts[channel_key] += 1
        for topic in row["topics"]:
            topic_counts[topic] += 1

    known_duration_rows = [row for row in rows if row["duration"] is not None]
    shortform_rows = [
        row
        for row in rows
        if row["media_family"] == "shorts" or row["is_duration_under_60"] is True
    ]
    duration_under_60_rows = [row for row in rows if row["is_duration_under_60"] is True]
    duration_unknown_rows = [row for row in rows if row["duration"] is None]

    primary_channel = channel_infos[0] if channel_infos else {}
    result = {
        "source_urls": legacy_source_urls(),
        "collected_at": collected_at,
        "tool": "yt-dlp --flat-playlist --dump-single-json; Korean translated fields plus default-language fallback metadata",
        "channel": primary_channel,
        "channels": channel_infos,
        "summary": {
            "channel_count": len(channel_infos),
            "combined_unique_count": len(rows),
            "tab_counts": dict(tab_counts),
            "channel_counts": dict(channel_counts),
            "known_duration_count": len(known_duration_rows),
            "duration_unknown_count": len(duration_unknown_rows),
            "duration_under_60_known_count": len(duration_under_60_rows),
            "shortform_or_under_60_count": len(shortform_rows),
            "previous_inventory_count": len(previous_ids),
            "new_vs_previous_count": len(new_ids),
            "missing_from_current_count": len(missing_ids),
            "topic_counts": dict(topic_counts),
        },
        "new_vs_previous_ids": sorted(new_ids),
        "missing_from_current_ids": sorted(missing_ids),
        "items": rows,
    }

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(OUT_CSV, rows)
    write_csv(OUT_SHORTS_CSV, shortform_rows)

    latest_rows = rows[:12]
    latest_table = [["No", "탭", "제목", "분", "주제"]]
    for index, row in enumerate(latest_rows, start=1):
        latest_table.append(
            [
                index,
                ",".join(row["source_tabs"]),
                row["title"].replace("|", "\\|"),
                row["duration_min"] if row["duration_min"] is not None else "미상",
                ", ".join(row["topics"]),
            ]
        )

    topic_table = [["주제", "콘텐츠 수"]]
    for topic, count in topic_counts.most_common():
        topic_table.append([topic, count])

    report = f"""# 유튜브 메타 리서치 업데이트

## 핵심 결론

- 수집일: {STAMP}
- 수집 시각: `{collected_at}`
- 수집 대상: {format_collection_targets(channel_infos)}
- 수집 방식: `yt-dlp` flat playlist, 한국어 번역 필드 우선 + 기본 언어 메타 fallback
- 합산 고유 콘텐츠: {len(rows)}개
- videos 탭 콘텐츠: {tab_counts.get("videos", 0)}개
- shorts 탭 콘텐츠: {tab_counts.get("shorts", 0)}개
- 숏폼 또는 1분 미만 후보: {len(shortform_rows)}개
- duration이 확인된 1분 미만 콘텐츠: {len(duration_under_60_rows)}개
- duration 미상 콘텐츠: {len(duration_unknown_rows)}개
- 기존 `video_inventory_ko.json` 대비 신규 ID: {len(new_ids)}개
- 기존 인벤토리에는 있었지만 이번 탭 합산에서 보이지 않은 ID: {len(missing_ids)}개

이전 리서치의 `Shorts 후보 4개`는 `videos` 탭 안에서 duration이 60초 이하인 항목만 잡은 값이었다. 이번 업데이트는 별도 `shorts` 탭을 수집했기 때문에 숏폼 콘텐츠가 온톨로지/지식그래프에 들어갈 수 있는 메타 범위가 크게 넓어졌다.

## 주제 분포

{markdown_table(topic_table)}

## 최신 탭 순서 샘플

{markdown_table(latest_table)}

## 산출 파일

- `{OUT_JSON.name}`: 합산 JSON 메타와 비교 요약
- `{OUT_CSV.name}`: videos + shorts 합산 CSV
- `{OUT_SHORTS_CSV.name}`: shorts 탭 또는 duration 60초 이하 후보 CSV
- `{OUT_REPORT.name}`: 이 리포트

## 해석

- 현재 `catbook` 온톨로지의 가장 큰 빈틈은 자막 심층 분석보다 먼저 `shorts` 탭 누락이었다.
- 숏폼은 제목과 조회수 중심의 얕은 메타만으로도 `CatSignal`, `생활 장면`, `관계/서사` 노드 후보를 늘리는 데 유용하다.
- 단, flat playlist에서는 shorts duration이 비어 있는 항목이 많다. 정확한 초 단위 길이, 업로드 날짜, 상세 설명까지 필요하면 선택된 후보만 상세 조회하는 2차 저속 수집이 필요하다.

## 리스크

- YouTube는 동적 페이지와 번역 필드를 제공하므로 제목/채널명은 세션 언어에 따라 달라질 수 있다.
- 이번 수집은 원문 자막이나 영상 파일을 저장하지 않고 공개 메타만 저장했다.
- 건강/진료 주제는 온톨로지에서 진단/처방 관계가 아니라 관찰/기록/상담 관계로만 연결해야 한다.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "combined_unique_count": len(rows),
                "videos_tab_count": tab_counts.get("videos", 0),
                "shorts_tab_count": tab_counts.get("shorts", 0),
                "shortform_or_under_60_count": len(shortform_rows),
                "duration_under_60_known_count": len(duration_under_60_rows),
                "duration_unknown_count": len(duration_unknown_rows),
                "new_vs_previous_count": len(new_ids),
                "missing_from_current_count": len(missing_ids),
                "outputs": [str(OUT_JSON), str(OUT_CSV), str(OUT_SHORTS_CSV), str(OUT_REPORT)],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
