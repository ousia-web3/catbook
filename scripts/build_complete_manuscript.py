from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_DIR = ROOT / "manuscript"
CORE_PATH = MANUSCRIPT_DIR / "nyangnyang-chur-manuscript-v3-core-expanded.md"
REMAINING_PATH = MANUSCRIPT_DIR / "nyangnyang-chur-manuscript-v3-remaining-expanded.md"
OUT_PATH = MANUSCRIPT_DIR / "nyangnyang-chur-manuscript-v3-complete.md"


PARTS = [
    (
        "Part 1. 웃다가 배우는 고양이 생활",
        [
            "츄르는 왜 갑자기 뛰었을까",
            "웃긴 장면 뒤에 남은 신호",
            "집사의 상처받는 속도",
            "고양이 과시대회의 뒤끝",
            "이름을 바꾸면 운명도 바뀔까",
            "귀여움이 관찰을 가릴 때",
        ],
    ),
    (
        "Part 2. 집 안에 놓는 안심",
        [
            "소파 밑 38센티미터",
            "밥그릇보다 먼저 놓아야 할 것",
            "물그릇 세 개의 정치학",
            "화장실은 집의 중심이다",
            "이동장은 감옥이 아니라 방이어야 한다",
            "출근 전 30초",
        ],
    ),
    (
        "Part 3. 마음의 속도를 맞추는 일",
        [
            "이름을 부르지 않는 인사",
            "하악질의 번역",
            "우다다는 혼난 뒤가 아니라 비운 뒤에 온다",
            "꼬리가 먼저 말한 날",
            "고양이가 나를 좋아한다는 증거",
            "잠깐 싫어할 권리",
        ],
    ),
    (
        "Part 4. 몸이 보내는 작은 알림",
        [
            "똥을 보고 쓰는 일기",
            "발톱깎이는 가위가 아니라 약속",
            "병원에 가져갈 세 줄",
            "물을 많이 마신 날",
            "토한 뒤에 해야 할 일",
            "살이 찐 건 귀여움이 아니다",
        ],
    ),
    (
        "Part 5. 같이 산다는 것의 거리",
        [
            "합사는 사랑보다 동선이다",
            "둘째를 들이기 전 첫째에게 묻는 법",
            "아기와 고양이 사이의 규칙",
            "싸움이 끝난 뒤 사람이 해야 할 일",
            "외로움이라는 사람의 오해",
            "가족이 늘어날 때 고양이가 잃는 것",
        ],
    ),
    (
        "Part 6. 오래 같이 살기 위한 책임",
        [
            "실종을 상상하기 전에 할 일",
            "길고양이를 본 날의 순서",
            "위험한 물건은 귀엽지 않다",
            "노묘의 느린 대답",
            "마지막을 준비한다는 말",
            "모르면 묻는 용기",
        ],
    ),
    (
        "Part 7. 고양이라는 종을 더 정확히 보기",
        [
            "묘종백과를 읽는 법",
            "예쁜 외모 뒤의 유전 이야기",
            "털과 피부가 보내는 힌트",
            "작은 고양이와 작은 오해",
            "품종보다 먼저 보는 생활",
            "오늘도 츄르는 나를 훈련시킨다",
        ],
    ),
]


def extract_sections(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    matches = re.finditer(
        r"(?ms)^##\s+\d+\.\s+(.+?)\n(.*?)(?=^---\n\n##\s+\d+\.|\Z)",
        text,
    )
    sections: dict[str, str] = {}

    for match in matches:
        title = match.group(1).strip()
        body = match.group(2).strip()
        body = re.sub(r"\n---\s*$", "", body).strip()
        body = re.sub(r"(?m)^###\s+", "#### ", body)
        sections[title] = body

    return sections


def main() -> None:
    sections: dict[str, str] = {}
    sections.update(extract_sections(CORE_PATH))
    sections.update(extract_sections(REMAINING_PATH))

    missing = [
        title
        for _, chapters in PARTS
        for title in chapters
        if title not in sections
    ]
    if missing:
        raise SystemExit(f"Missing manuscript sections: {', '.join(missing)}")

    lines: list[str] = [
        "# 냥냥츄르",
        "",
        "> 츄르는 우다다 한 번, 살짝 접힌 귀 한쪽으로 사람을 웃게 한다. 이 책은 그 웃음이 지나간 자리에 남은 작은 신호를 오래 들여다본다.",
        "> 이 책은 특정 영상 대본을 옮긴 글이 아니라, 고양이 돌봄 주제를 바탕으로 새로 쓴 독립 창작 이야기 노트다.",
        "",
        "## 이 노트는 이렇게 펼친다",
        "",
        "- 처음부터 끝까지 따라 읽어도 좋고, 오늘 유난히 눈에 밟히는 신호가 있다면 그 장부터 펼쳐도 좋다.",
        "- 각 장은 짧은 이야기, 30초 체크, 집사 메모, 오늘의 한 문장으로 이어진다.",
        "- 이 책은 진단을 대신하지 않는다. 다만 집사가 본 변화를 차분히 적어 두게 하고, 필요할 때 병원에 가져갈 말로 정리해 준다.",
        "",
        "---",
        "",
    ]

    chapter_number = 1
    for part_title, chapters in PARTS:
        lines.extend([f"## {part_title}", ""])

        for chapter in chapters:
            lines.extend(
                [
                    f"### {chapter_number}. {chapter}",
                    "",
                    sections[chapter],
                    "",
                    "---",
                    "",
                ]
            )
            chapter_number += 1

    OUT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    text = OUT_PATH.read_text(encoding="utf-8")
    print(
        {
            "output": str(OUT_PATH),
            "chapters": chapter_number - 1,
            "characters": len(text),
        }
    )


if __name__ == "__main__":
    main()
