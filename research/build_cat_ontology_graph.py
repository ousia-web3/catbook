import json
import math
import os
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent
CATBOOK = BASE.parent
DATA = CATBOOK / "data"
WEB = CATBOOK / "web"

ATLAS = BASE / "content_atlas.json"
DB = DATA / "catbook_ontology.sqlite"
OUT = BASE / "cat_ontology_graph.json"
OUT_REPORT = BASE / "cat-ontology-graph-report.md"
SCHEMA_VERSION = "2026-06-05.2"


def resolve_latest_youtube_meta() -> Path:
    override = os.environ.get("CATBOOK_YOUTUBE_META_JSON")
    if override:
        path = Path(override)
        if not path.is_absolute():
            path = (BASE / path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"CATBOOK_YOUTUBE_META_JSON not found: {path}")
        return path

    candidates = sorted(
        BASE.glob("youtube_meta_all_tabs_*.json"),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError("No youtube_meta_all_tabs_*.json file found in catbook/research.")
    return candidates[0]


CLASSES = {
    "Scenario": {
        "label": "초보자 상황",
        "description": "고양이를 잘 모르는 사람이 자연어로 시작하는 입구",
        "color": "#2563EB",
    },
    "CatSignal": {
        "label": "고양이 신호",
        "description": "보호자가 눈으로 보는 행동, 자세, 소리, 반복 패턴",
        "color": "#0F766E",
    },
    "Need": {
        "label": "욕구/상태",
        "description": "신호 뒤에 있을 수 있는 안심, 거리, 에너지, 통증 관찰 같은 필요",
        "color": "#7C3AED",
    },
    "EnvironmentElement": {
        "label": "환경 요소",
        "description": "물그릇, 화장실, 숨을 곳, 이동장처럼 집 안에 놓는 지식",
        "color": "#0891B2",
    },
    "HealthObservation": {
        "label": "건강 관찰",
        "description": "진단이 아니라 병원 상담 전 기록해야 할 변화",
        "color": "#DC2626",
    },
    "CareAction": {
        "label": "집사 행동",
        "description": "관찰, 기록, 멈춤, 위치 조정, 상담 준비처럼 바로 할 수 있는 행동",
        "color": "#EA580C",
    },
    "SafetyRisk": {
        "label": "안전/윤리 리스크",
        "description": "실종, 위험물, 구조 판단, 자가진단처럼 주의해야 하는 영역",
        "color": "#B45309",
    },
    "Topic": {
        "label": "콘텐츠 주제",
        "description": "영상/숏폼 메타에서 뽑은 주제 축",
        "color": "#4F46E5",
    },
    "BookPart": {
        "label": "책 파트",
        "description": "냥냥츄르 7개 독서 길",
        "color": "#059669",
    },
    "Chapter": {
        "label": "책 챕터",
        "description": "42개 짧은 이야기와 체크리스트",
        "color": "#BE123C",
    },
    "Source": {
        "label": "근거 콘텐츠",
        "description": "영상/숏폼 공개 메타 기반 근거",
        "color": "#64748B",
    },
}


RELATIONS = {
    "STARTS_WITH": "초보자 질문에서 출발",
    "SHOWS_SIGNAL": "콘텐츠가 신호를 보여줌",
    "HAS_TOPIC": "콘텐츠가 주제에 속함",
    "MAPS_TO_PART": "콘텐츠가 책 파트 후보와 연결됨",
    "COVERS": "파트/챕터가 개념을 다룸",
    "MAY_INDICATE": "신호가 어떤 필요를 암시할 수 있음",
    "OBSERVE_WITH": "신호를 함께 관찰해야 함",
    "SUGGESTS": "필요가 행동을 제안함",
    "SUPPORTS": "환경/행동이 필요를 지원함",
    "REQUIRES_RECORD": "건강 관찰에 기록이 필요함",
    "CONSULT_WHEN": "상담 기준을 제시함",
    "PREVENTS": "행동이 리스크를 낮춤",
    "HAS_EVIDENCE": "개념과 근거 콘텐츠 연결",
}


TOPICS = [
    "행동/감정",
    "건강/진료",
    "생활/돌봄",
    "관계/윤리",
    "품종/지식",
    "서사/상담",
    "기타/엔터테인먼트",
    "CAT-SIGNAL 행동 신호",
    "HEALTH-CHECK 건강 관찰",
    "CARE-ROUTINE 생활 돌봄",
    "RELATIONSHIP 관계/합사",
    "LITTER-LOG 배변/화장실",
    "ETHICS-SAFETY 윤리/안전",
    "BREED-KNOWLEDGE 묘종/지식",
    "LIFE-STORY 서사/상담",
    "MIXED-ENTERTAINMENT 기획/엔터테인먼트",
]


CHAPTER_IMAGE_FILES = {
    1: "chapter_01_sudden_run_context_monoline.png",
    2: "chapter_02_funny_signal_box_monoline.png",
    3: "chapter_03_new_cushion_time_monoline.png",
    4: "chapter_04_quiet_trust_distance_monoline.png",
    5: "chapter_05_name_safe_signal_monoline.png",
    6: "chapter_06_cute_signal_water_bowl_monoline.png",
    7: "chapter_07_safe_hide_sofa_monoline.png",
    8: "chapter_08_quiet_food_place_monoline.png",
    9: "chapter_09_safe_water_bowls_monoline.png",
    10: "chapter_10_litter_box_access_monoline.png",
    11: "chapter_11_carrier_safe_room_monoline.png",
    12: "chapter_12_before_work_check_monoline.png",
    13: "chapter_13_quiet_greeting_monoline.png",
    14: "chapter_14_hiss_translation_monoline.png",
    15: "chapter_15_zoomies_after_release_monoline.png",
    16: "chapter_16_tail_signal_pause_monoline.png",
    17: "chapter_17_quiet_trust_same_room_monoline.png",
    18: "chapter_18_right_to_dislike_brush_monoline.png",
    19: "chapter_19_litter_diary_observation_monoline.png",
    20: "chapter_20_claw_clip_promise_monoline.png",
    21: "chapter_21_vet_three_lines_notes_monoline.png",
    22: "chapter_22_water_intake_tracking_monoline.png",
    23: "chapter_23_after_vomit_observe_monoline.png",
    24: "chapter_24_weight_is_care_monoline.png",
    25: "chapter_25_cat_introduction_routes_monoline.png",
    26: "chapter_26_before_second_cat_space_monoline.png",
    27: "chapter_27_baby_and_cat_rules_monoline.png",
    28: "chapter_28_after_cat_fight_space_monoline.png",
    29: "chapter_29_misreading_loneliness_monoline.png",
    30: "chapter_30_family_change_lost_places_monoline.png",
    31: "chapter_31_door_escape_prevention_monoline.png",
    32: "chapter_32_stray_cat_help_order_monoline.png",
    33: "chapter_33_dangerous_small_objects_monoline.png",
    34: "chapter_34_senior_cat_slow_answer_monoline.png",
    35: "chapter_35_good_days_record_monoline.png",
    36: "chapter_36_courage_to_ask_monoline.png",
    37: "chapter_37_breed_book_observation_monoline.png",
    38: "chapter_38_genetic_beauty_responsibility_monoline.png",
    39: "chapter_39_fur_skin_hints_monoline.png",
    40: "chapter_40_kitten_small_risks_monoline.png",
    41: "chapter_41_life_before_breed_monoline.png",
    42: "chapter_42_cat_trains_observer_monoline.png",
}


BOOK_PARTS = [
    {
        "id": "part:01",
        "label": "Part 1. 웃다가 배우는 고양이 생활",
        "short": "생활",
        "chapters": [
            ("chapter:01", "츄르는 왜 갑자기 뛰었을까", ["signal:zoomies", "need:energy_release", "action:context_record"]),
            ("chapter:02", "웃긴 장면 뒤에 남은 신호", ["signal:tail_ear_tension", "need:safety", "action:context_record"]),
            ("chapter:03", "집사의 상처받는 속도", ["need:scent_familiarity", "action:slow_introduction"]),
            ("chapter:04", "고양이 과시대회의 뒤끝", ["need:choice", "signal:relaxed_presence"]),
            ("chapter:05", "이름을 바꾸면 운명도 바뀔까", ["need:predictable_routine", "action:context_record"]),
            ("chapter:06", "귀여움이 관찰을 가릴 때", ["action:context_record", "signal:box_seeking"]),
        ],
    },
    {
        "id": "part:02",
        "label": "Part 2. 집 안에 놓는 안심",
        "short": "안심",
        "chapters": [
            ("chapter:07", "소파 밑 38센티미터", ["signal:hiding", "environment:hideout", "need:safety"]),
            (
                "chapter:08",
                "밥그릇보다 먼저 놓아야 할 것",
                ["environment:food_place", "need:predictable_routine", "need:hunger_satiety", "environment:dry_food"],
            ),
            ("chapter:09", "물그릇 세 개의 정치학", ["environment:water_station", "health:water_change", "environment:wet_food"]),
            ("chapter:10", "화장실은 집의 중심이다", ["environment:litter_box", "health:litter_change"]),
            ("chapter:11", "이동장은 감옥이 아니라 방이어야 한다", ["environment:carrier_room", "need:safety"]),
            ("chapter:12", "출근 전 30초", ["action:daily_check", "risk:escape", "environment:door_window"]),
        ],
    },
    {
        "id": "part:03",
        "label": "Part 3. 마음의 속도를 맞추는 일",
        "short": "마음",
        "chapters": [
            ("chapter:13", "이름을 부르지 않는 인사", ["signal:slow_blink", "need:distance", "action:pause_contact"]),
            ("chapter:14", "하악질의 번역", ["signal:hissing", "need:distance", "action:pause_contact"]),
            ("chapter:15", "우다다는 혼난 뒤가 아니라 비운 뒤에 온다", ["signal:zoomies", "need:energy_release", "action:play_enrichment"]),
            ("chapter:16", "꼬리가 먼저 말한 날", ["signal:tail_ear_tension", "action:pause_contact"]),
            ("chapter:17", "고양이가 나를 좋아한다는 증거", ["signal:relaxed_presence", "signal:slow_blink"]),
            ("chapter:18", "잠깐 싫어할 권리", ["signal:biting", "need:choice", "action:pause_contact", "action:grooming_care"]),
        ],
    },
    {
        "id": "part:04",
        "label": "Part 4. 몸이 보내는 작은 알림",
        "short": "몸",
        "chapters": [
            ("chapter:19", "똥을 보고 쓰는 일기", ["health:litter_change", "environment:litter_box", "action:vet_notes"]),
            ("chapter:20", "발톱깎이는 가위가 아니라 약속", ["health:claw_skin_fur", "action:pause_contact"]),
            ("chapter:21", "병원에 가져갈 세 줄", ["action:vet_notes", "risk:self_diagnosis"]),
            ("chapter:22", "물을 많이 마신 날", ["health:water_change", "environment:water_station", "action:vet_notes"]),
            ("chapter:23", "토한 뒤에 해야 할 일", ["health:vomiting", "action:vet_notes"]),
            ("chapter:24", "살이 찐 건 귀여움이 아니다", ["health:weight_change", "action:vet_notes"]),
        ],
    },
    {
        "id": "part:05",
        "label": "Part 5. 같이 산다는 것의 거리",
        "short": "관계",
        "chapters": [
            ("chapter:25", "합사는 사랑보다 동선이다", ["context:introduction", "environment:route", "action:slow_introduction"]),
            ("chapter:26", "둘째를 들이기 전 첫째에게 묻는 법", ["context:second_cat", "need:choice"]),
            ("chapter:27", "아기와 고양이 사이의 규칙", ["context:baby_family", "risk:unsafe_touch"]),
            ("chapter:28", "싸움이 끝난 뒤 사람이 해야 할 일", ["signal:fight_or_play", "action:separate_and_reset"]),
            ("chapter:29", "외로움이라는 사람의 오해", ["context:guardian_absence", "need:predictable_routine"]),
            ("chapter:30", "가족이 늘어날 때 고양이가 잃는 것", ["context:family_change", "need:scent_familiarity"]),
        ],
    },
    {
        "id": "part:06",
        "label": "Part 6. 오래 같이 살기 위한 책임",
        "short": "책임",
        "chapters": [
            ("chapter:31", "실종을 상상하기 전에 할 일", ["risk:escape", "environment:door_window", "action:remove_hazards"]),
            ("chapter:32", "길고양이를 본 날의 순서", ["risk:unsafe_rescue", "action:consult_expert"]),
            ("chapter:33", "위험한 물건은 귀엽지 않다", ["risk:hazard_object", "action:remove_hazards"]),
            ("chapter:34", "노묘의 느린 대답", ["health:senior_change", "need:rest_recovery"]),
            ("chapter:35", "마지막을 준비한다는 말", ["health:senior_change", "action:vet_notes"]),
            ("chapter:36", "모르면 묻는 용기", ["action:consult_expert", "risk:self_diagnosis"]),
        ],
    },
    {
        "id": "part:07",
        "label": "Part 7. 고양이라는 종을 더 정확히 보기",
        "short": "지식",
        "chapters": [
            ("chapter:37", "묘종백과를 읽는 법", ["knowledge:breed_context", "risk:self_diagnosis"]),
            ("chapter:38", "예쁜 외모 뒤의 유전 이야기", ["knowledge:genetics", "health:claw_skin_fur"]),
            ("chapter:39", "털과 피부가 보내는 힌트", ["health:claw_skin_fur", "health:grooming_change", "action:grooming_care", "action:vet_notes"]),
            ("chapter:40", "작은 고양이와 작은 오해", ["context:kitten", "risk:unsafe_touch"]),
            ("chapter:41", "품종보다 먼저 보는 생활", ["knowledge:breed_context", "need:predictable_routine"]),
            ("chapter:42", "오늘도 츄르는 나를 훈련시킨다", ["action:daily_check", "need:choice"]),
        ],
    },
]


CONCEPTS = [
    {
        "id": "signal:zoomies",
        "class": "CatSignal",
        "label": "우다다 / 갑자기 뛰기",
        "summary": "갑작스러운 질주나 점프는 배변 후 리듬, 에너지 배출, 자극 반응, 몸의 불편함까지 전후 맥락으로 읽는다.",
        "keywords": ["우다다", "갑자기", "뛰", "질주", "똥싸", "똥", "달리", "흥분"],
        "topics": ["행동/감정", "CAT-SIGNAL 행동 신호", "LITTER-LOG 배변/화장실"],
        "parts": ["part:01", "part:03"],
        "observe": ["직전 화장실 사용 여부", "식욕과 활력 변화", "반복 빈도와 시간대"],
        "beginner": "뛰는 행동만 보지 말고, 직전/직후에 화장실·소리·놀이·식욕 변화가 있었는지 먼저 본다.",
    },
    {
        "id": "signal:hissing",
        "class": "CatSignal",
        "label": "하악질",
        "summary": "하악질은 나쁜 성격 판정이 아니라 거리와 시간을 요청하는 강한 멈춤 신호다.",
        "keywords": ["하악", "위협", "성격", "싫", "무서", "긴장"],
        "topics": ["행동/감정", "관계/윤리", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:03", "part:05"],
        "observe": ["접근 거리", "새 고양이/사람/물건 등장", "도망갈 길 유무"],
        "beginner": "하악질이 나오면 친해지려 하기보다 손과 몸을 멈추고 고양이의 퇴로를 열어 둔다.",
    },
    {
        "id": "signal:slow_blink",
        "class": "CatSignal",
        "label": "눈인사 / 느린 눈",
        "summary": "느리게 감는 눈, 같은 방에 머무는 선택, 등을 보이는 태도는 부담 없는 신뢰의 단서가 될 수 있다.",
        "keywords": ["눈인사", "눈", "인사", "좋아", "편안", "신뢰", "느린"],
        "topics": ["행동/감정", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:03"],
        "observe": ["눈을 오래 응시하지 않는지", "몸 방향", "같은 공간에 남는지"],
        "beginner": "친밀함은 만지는 시간보다 고양이가 스스로 남아 있는 거리에서 먼저 보인다.",
    },
    {
        "id": "signal:tail_ear_tension",
        "class": "CatSignal",
        "label": "꼬리·귀·동공 긴장",
        "summary": "꼬리 끝, 귀 방향, 동공 크기, 몸의 낮아짐은 감정과 경계 수준을 읽는 기본 단서다.",
        "keywords": ["꼬리", "귀", "동공", "눈", "긴장", "기분", "자세"],
        "topics": ["행동/감정", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:01", "part:03"],
        "observe": ["꼬리 속도", "귀가 옆/뒤로 눕는지", "몸이 낮아지는지"],
        "beginner": "표정만 보지 말고 꼬리, 귀, 몸 높이를 같이 보면 손을 멈출 타이밍을 더 빨리 알 수 있다.",
    },
    {
        "id": "signal:hiding",
        "class": "CatSignal",
        "label": "숨기 / 숨어 있기",
        "summary": "숨는 행동은 겁쟁이 판정이 아니라 안전한 방, 냄새, 시간, 선택권의 문제일 수 있다.",
        "keywords": ["숨", "소파", "안나", "피하", "무서", "은신", "숨어"],
        "topics": ["행동/감정", "생활/돌봄", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:02"],
        "observe": ["새 환경 여부", "숨은 위치의 안정성", "식욕/배변 동반 변화"],
        "beginner": "억지로 꺼내기 전에 나올 길, 물과 화장실 접근성, 조용한 시간을 먼저 마련한다.",
    },
    {
        "id": "signal:biting",
        "class": "CatSignal",
        "label": "물기 / 깨물기",
        "summary": "무는 행동은 놀이 과열, 접촉 거절, 통증 가능성, 학습된 반응을 분리해 관찰한다.",
        "keywords": ["물", "깨물", "물렸", "공격", "싫어", "장난"],
        "topics": ["행동/감정", "건강/진료", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:03"],
        "observe": ["만지던 부위", "직전 꼬리/귀 신호", "반복성과 세기 변화"],
        "beginner": "손으로 장난을 이어가지 말고 접촉을 멈춘 뒤 놀이 도구와 거리 조절로 바꾼다.",
    },
    {
        "id": "signal:purring_kneading",
        "class": "CatSignal",
        "label": "골골송·꾹꾹이",
        "summary": "골골송과 꾹꾹이는 편안함의 단서일 수 있지만, 상황에 따라 자기 진정 신호일 수도 있다.",
        "keywords": ["골골", "꾹꾹", "꾹꾹이", "소리", "마사지"],
        "topics": ["행동/감정", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:03"],
        "observe": ["몸의 힘이 빠져 있는지", "통증/불편 상황과 겹치는지", "반복 맥락"],
        "beginner": "귀엽다는 결론 전에 몸 전체가 편한지와 다른 불편 신호가 없는지 같이 본다.",
    },
    {
        "id": "signal:vocalization",
        "class": "CatSignal",
        "label": "울음소리 / 야옹",
        "summary": "울음은 요구, 불안, 습관, 통증 관찰까지 연결될 수 있어 시간대와 동반 변화를 기록한다.",
        "keywords": ["울음", "야옹", "소리", "전화", "한국말", "말하는"],
        "topics": ["행동/감정", "건강/진료", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:03", "part:04"],
        "observe": ["갑자기 늘었는지", "식욕/배변/활력 변화", "특정 장소나 시간"],
        "beginner": "소리의 뜻을 맞히려 하기보다 언제, 어디서, 무엇과 함께 나타나는지 적는다.",
    },
    {
        "id": "signal:relaxed_presence",
        "class": "CatSignal",
        "label": "같은 방에 머무는 신뢰",
        "summary": "무릎 위 사진보다 같은 방에 남는 선택, 느린 움직임, 등을 보이는 태도가 더 조용한 신뢰일 수 있다.",
        "keywords": ["편안", "좋아", "기억", "같은 방", "잠", "자는 위치", "마중"],
        "topics": ["행동/감정", "관계/윤리", "CAT-SIGNAL 행동 신호"],
        "parts": ["part:01", "part:03"],
        "observe": ["자발적으로 가까이 오는지", "도망갈 길을 막지 않았는지", "몸이 이완됐는지"],
        "beginner": "고양이가 멀리 있더라도 같은 공간을 선택했다면 이미 관계의 신호일 수 있다.",
    },
    {
        "id": "signal:fight_or_play",
        "class": "CatSignal",
        "label": "놀이와 싸움의 경계",
        "summary": "다묘 환경에서는 소리, 추격 방향, 숨을 곳, 한쪽만 계속 밀리는지로 놀이와 갈등을 구분한다.",
        "keywords": ["싸움", "노는", "놀이", "사이", "불화", "다묘", "합사"],
        "topics": ["행동/감정", "관계/윤리", "RELATIONSHIP 관계/합사"],
        "parts": ["part:05"],
        "observe": ["서로 번갈아 추격하는지", "소리와 털 세움", "싸움 후 회복 시간"],
        "beginner": "한쪽이 계속 도망만 간다면 놀이로 단정하지 말고 공간을 나눠 회복 시간을 준다.",
    },
    {
        "id": "signal:box_seeking",
        "class": "CatSignal",
        "label": "상자·네모·좁은 곳 찾기",
        "summary": "상자나 좁은 공간 선호는 장난이 아니라 경계가 분명한 안전지대를 찾는 행동일 수 있다.",
        "keywords": ["상자", "네모", "박스", "좁", "자리"],
        "topics": ["행동/감정", "생활/돌봄"],
        "parts": ["part:01", "part:02"],
        "observe": ["새 물건 반응", "주변 소음", "숨을 곳의 선택권"],
        "beginner": "상자를 치우기보다 안전한 숨을 곳으로 인정하고 위치와 접근성을 본다.",
    },
    {
        "id": "health:vomiting",
        "class": "HealthObservation",
        "label": "구토",
        "summary": "구토는 횟수, 내용물, 활력, 식욕, 반복성을 기록해 병원 상담 기준으로 정리한다.",
        "keywords": ["구토", "토", "토한", "토했", "헤어볼"],
        "topics": ["건강/진료", "HEALTH-CHECK 건강 관찰"],
        "parts": ["part:04"],
        "observe": ["횟수", "내용물", "식욕/활력", "반복 기간"],
        "beginner": "한 번의 사건보다 반복성과 동반 변화가 중요하다. 사진과 시간을 남기면 상담에 도움이 된다.",
        "medical": True,
    },
    {
        "id": "health:litter_change",
        "class": "HealthObservation",
        "label": "배변·배뇨 변화",
        "summary": "화장실 변화는 몸이 남기는 기록이다. 양, 색, 빈도, 자세, 울음 여부를 본다.",
        "keywords": ["똥", "오줌", "소변", "배변", "배뇨", "화장실", "모래", "혈뇨", "설사", "변비"],
        "topics": ["건강/진료", "생활/돌봄", "LITTER-LOG 배변/화장실"],
        "parts": ["part:02", "part:04"],
        "observe": ["횟수", "모래 덩어리 크기", "색과 냄새", "화장실 앞 망설임"],
        "beginner": "화장실은 매일 도착하는 건강 편지처럼 보고, 달라진 점을 날짜와 함께 적는다.",
        "medical": True,
    },
    {
        "id": "health:water_change",
        "class": "HealthObservation",
        "label": "음수 변화",
        "summary": "물을 많이 또는 적게 마시는 변화는 위치 취향일 수도 있지만, 반복되면 기록과 상담이 필요하다.",
        "keywords": ["물", "음수", "물그릇", "습식", "신장", "방광"],
        "topics": ["건강/진료", "생활/돌봄"],
        "parts": ["part:02", "part:04"],
        "observe": ["물그릇 위치", "양 변화", "소변 변화", "식이 변화"],
        "beginner": "물을 마시는 양만 보지 말고 물그릇 위치, 습식 여부, 소변 변화를 함께 본다.",
        "medical": True,
    },
    {
        "id": "health:appetite_change",
        "class": "HealthObservation",
        "label": "식욕 변화",
        "summary": "밥을 안 먹거나 갑자기 먹는 양이 바뀌면 간식 취향보다 건강과 환경 변화를 함께 기록한다.",
        "keywords": ["밥", "사료", "안 먹", "먹이", "식욕", "간식", "먹보"],
        "topics": ["건강/진료", "생활/돌봄"],
        "parts": ["part:02", "part:04"],
        "observe": ["언제부터", "간식은 먹는지", "활력", "입 주변/치아 불편"],
        "beginner": "무엇을 얼마나 먹었는지보다 '평소와 얼마나 달라졌는지'가 상담의 핵심이다.",
        "medical": True,
    },
    {
        "id": "health:weight_change",
        "class": "HealthObservation",
        "label": "체중 변화",
        "summary": "체중은 귀여움 평가가 아니라 관절, 움직임, 생활 질과 연결되는 관찰 항목이다.",
        "keywords": ["비만", "다이어트", "체중", "살", "뚱냥", "칼로리"],
        "topics": ["건강/진료", "생활/돌봄"],
        "parts": ["part:04"],
        "observe": ["주기적 측정", "간식량", "움직임", "숨참/점프 변화"],
        "beginner": "사진 느낌보다 같은 조건에서 잰 숫자와 움직임 변화를 함께 본다.",
        "medical": True,
    },
    {
        "id": "health:claw_skin_fur",
        "class": "HealthObservation",
        "label": "발톱·피부·털 변화",
        "summary": "발톱, 피부, 털은 미용 문제가 아니라 통증, 스트레스, 생활 환경의 힌트가 될 수 있다.",
        "keywords": ["발톱", "피부", "털", "빗질", "턱드름", "눈곱", "귀 청소", "목욕"],
        "topics": ["건강/진료", "생활/돌봄", "품종/지식"],
        "parts": ["part:04", "part:07"],
        "observe": ["만지는 부위 반응", "반복 긁기", "털 빠짐 변화", "피부 색"],
        "beginner": "관리 기술보다 고양이가 싫어하는 신호와 몸의 변화를 먼저 본다.",
        "medical": True,
    },
    {
        "id": "health:grooming_change",
        "class": "HealthObservation",
        "label": "그루밍 변화",
        "summary": "그루밍을 너무 많이 하거나 줄어드는 변화는 털, 피부, 스트레스, 통증 가능성을 함께 기록한다.",
        "keywords": ["그루밍", "구르밍", "핥", "털관리", "목욕", "안 씻", "과도한", "나쁜 그루밍"],
        "topics": ["건강/진료", "생활/돌봄", "HEALTH-CHECK 건강 관찰", "CARE-ROUTINE 생활 돌봄"],
        "parts": ["part:03", "part:04", "part:07"],
        "observe": ["평소보다 많이/적게 하는지", "특정 부위만 반복하는지", "털 빠짐이나 피부 변화", "활력과 식욕 변화"],
        "beginner": "그루밍은 깨끗함만의 문제가 아니다. 달라진 빈도와 부위를 날짜와 함께 본다.",
        "match_requires_keyword": True,
        "medical": True,
    },
    {
        "id": "health:senior_change",
        "class": "HealthObservation",
        "label": "노묘의 느린 변화",
        "summary": "느려짐을 나이 탓으로만 넘기지 않고, 이동성, 식욕, 물, 화장실, 통증 신호를 작게 기록한다.",
        "keywords": ["노묘", "장수", "수명", "나이", "느려", "오래"],
        "topics": ["건강/진료", "관계/윤리"],
        "parts": ["part:06"],
        "observe": ["점프 높이", "잠자리 변화", "화장실 접근", "식욕/물"],
        "beginner": "노화는 단정이 아니라 관찰 방식의 변경이다. 편하게 갈 수 있는 길부터 만든다.",
        "medical": True,
    },
    {
        "id": "environment:litter_box",
        "class": "EnvironmentElement",
        "label": "화장실·모래",
        "summary": "화장실은 위치, 청결, 수, 모래 취향이 함께 작동하는 집 안 핵심 인프라다.",
        "keywords": ["화장실", "모래", "감자", "맛동산", "벽", "청소"],
        "topics": ["생활/돌봄", "LITTER-LOG 배변/화장실"],
        "parts": ["part:02", "part:04"],
        "observe": ["개수와 위치", "청결 주기", "피할 수 있는 동선", "갑작스런 실수"],
        "beginner": "화장실 문제는 성격보다 위치와 몸의 신호부터 확인한다.",
    },
    {
        "id": "environment:water_station",
        "class": "EnvironmentElement",
        "label": "물그릇·음수 동선",
        "summary": "물을 마시게 하는 일은 강요보다 위치, 재질, 개수, 조용한 동선의 문제다.",
        "keywords": ["물그릇", "물", "음수", "정수기", "습식"],
        "topics": ["생활/돌봄", "건강/진료"],
        "parts": ["part:02", "part:04"],
        "observe": ["동선", "그릇 재질", "식기와 화장실 거리", "마시는 시간대"],
        "beginner": "물그릇은 하나의 물건이 아니라 고양이가 지나가며 선택하는 여러 지점이다.",
    },
    {
        "id": "environment:food_place",
        "class": "EnvironmentElement",
        "label": "밥자리·간식 루틴",
        "summary": "밥자리는 안정감, 예측 가능성, 다른 고양이와의 거리까지 포함한다.",
        "keywords": ["간식", "밥", "사료", "츄르", "식탁", "먹이"],
        "topics": ["생활/돌봄"],
        "parts": ["part:02"],
        "observe": ["사람 동선", "다묘 거리", "시간 규칙", "간식 과잉"],
        "beginner": "먹는 양만 보지 말고 먹는 장소가 불안하지 않은지 먼저 본다.",
    },
    {
        "id": "environment:wet_food",
        "class": "EnvironmentElement",
        "label": "습식 급여",
        "summary": "습식은 수분 섭취, 기호성, 급여 루틴과 연결되지만 개체 상태에 맞춰 관찰해야 한다.",
        "keywords": ["습식", "캔", "파우치", "수분", "wet food", "wetfood"],
        "topics": ["생활/돌봄", "건강/진료", "CARE-ROUTINE 생활 돌봄"],
        "parts": ["part:02", "part:04"],
        "observe": ["먹는 양", "물 섭취 변화", "소변 변화", "보관과 위생", "기존 사료와의 전환 속도"],
        "beginner": "습식은 정답 상품이 아니라 물, 소변, 식욕 변화를 함께 보는 급여 선택지다.",
        "match_requires_keyword": True,
    },
    {
        "id": "environment:dry_food",
        "class": "EnvironmentElement",
        "label": "건식 사료",
        "summary": "건식 사료는 보관과 루틴이 쉽지만, 기호성, 음수량, 처방식 오해를 함께 조심해야 한다.",
        "keywords": ["건식", "건사료", "사료", "키블", "알갱이", "dry food", "kibble"],
        "topics": ["생활/돌봄", "건강/진료", "CARE-ROUTINE 생활 돌봄"],
        "parts": ["part:02", "part:04"],
        "observe": ["먹는 속도", "남기는 양", "물 섭취", "구토와 사료 모양", "임의 처방식 변경 여부"],
        "beginner": "사료 이름보다 평소와 다른 먹는 방식, 물, 구토, 활력 변화를 함께 본다.",
        "match_requires_keyword": True,
    },
    {
        "id": "environment:hideout",
        "class": "EnvironmentElement",
        "label": "숨을 곳",
        "summary": "안전한 숨을 곳은 회피가 아니라 회복을 가능하게 하는 선택권이다.",
        "keywords": ["숨", "소파", "집", "상자", "방", "자리"],
        "topics": ["생활/돌봄", "행동/감정"],
        "parts": ["part:02"],
        "observe": ["막히지 않은 출입구", "소음", "물/화장실 접근", "억지로 꺼내는 상황"],
        "beginner": "숨을 곳이 있으면 관계가 멀어지는 것이 아니라 돌아올 힘이 생긴다.",
    },
    {
        "id": "environment:carrier_room",
        "class": "EnvironmentElement",
        "label": "이동장",
        "summary": "이동장은 병원 가는 날만 등장하는 감옥이 아니라 평소 열려 있는 작은 방이어야 한다.",
        "keywords": ["이동장", "병원", "외출", "캐리어"],
        "topics": ["생활/돌봄", "건강/진료"],
        "parts": ["part:02"],
        "observe": ["평소 접근성", "담요/냄새", "보상 경험", "문 닫기 연습"],
        "beginner": "이동장을 평소 공간에 두면 병원 날의 공포가 조금 줄어든다.",
    },
    {
        "id": "environment:door_window",
        "class": "EnvironmentElement",
        "label": "문·창문·방묘",
        "summary": "실종 예방은 사건 후 대처보다 문, 창문, 방충망, 동선 점검에서 시작한다.",
        "keywords": ["문", "창문", "방묘", "실종", "탈출", "외출"],
        "topics": ["생활/돌봄", "관계/윤리"],
        "parts": ["part:02", "part:06"],
        "observe": ["방충망", "현관 동선", "방문 닫힘", "가족 출입 습관"],
        "beginner": "고양이가 안 나갈 것 같다는 믿음보다 문이 열리는 순간을 줄이는 구조가 중요하다.",
    },
    {
        "id": "environment:route",
        "class": "EnvironmentElement",
        "label": "동선·수직공간",
        "summary": "집 안 동선과 수직공간은 합사, 놀이, 도망갈 길, 갈등 완충에 직접 연결된다.",
        "keywords": ["동선", "캣타워", "수직", "자리", "공간", "합사"],
        "topics": ["생활/돌봄", "관계/윤리"],
        "parts": ["part:05"],
        "observe": ["막다른 길", "높은 자리", "먹고 쉬는 길", "다묘 충돌 지점"],
        "beginner": "고양이 사이가 나쁘다고 보기 전에 서로 피할 수 있는 길이 있는지 본다.",
    },
    {
        "id": "need:safety",
        "class": "Need",
        "label": "안전감",
        "summary": "고양이가 선택할 수 있는 거리, 숨을 곳, 예측 가능한 환경에서 생기는 기본 필요.",
        "keywords": ["안전", "안심", "무서", "스트레스", "편안"],
        "topics": ["행동/감정", "생활/돌봄"],
        "parts": ["part:02"],
        "observe": ["도망갈 길", "소음", "낯선 자극", "몸을 낮추는지"],
        "beginner": "고양이 돌봄의 첫 질문은 '좋아하나?'보다 '안전한가?'다.",
    },
    {
        "id": "need:distance",
        "class": "Need",
        "label": "거리 요청",
        "summary": "싫다는 표현은 관계 실패가 아니라 관계를 유지하기 위한 경계 신호다.",
        "keywords": ["거리", "싫어", "하악", "물", "손절", "경계"],
        "topics": ["행동/감정", "관계/윤리"],
        "parts": ["part:03"],
        "observe": ["손이 가까워질 때", "퇴로", "꼬리와 귀", "반복되는 접촉"],
        "beginner": "다가가는 법보다 멈추는 법을 먼저 배우면 신뢰가 빨리 무너지지 않는다.",
    },
    {
        "id": "need:energy_release",
        "class": "Need",
        "label": "에너지 배출",
        "summary": "사냥놀이와 생활 리듬이 부족하면 갑작스런 질주, 물기, 밤 활동으로 드러날 수 있다.",
        "keywords": ["놀이", "사냥", "우다다", "에너지", "장난감"],
        "topics": ["행동/감정", "생활/돌봄"],
        "parts": ["part:03"],
        "observe": ["놀이 시간", "밤 활동", "장난감 반응", "식사 전후"],
        "beginner": "혼내기 전에 놀 수 있는 시간과 방식이 충분했는지 먼저 본다.",
    },
    {
        "id": "need:hunger_satiety",
        "class": "Need",
        "label": "배고픔·포만감",
        "summary": "밥을 찾는 행동은 배고픔, 루틴 기대, 놀이 보상, 건강 변화가 섞일 수 있어 맥락을 본다.",
        "keywords": ["배고픔", "배고", "허기", "먹보", "내밥", "밥 안주", "밥시간", "식사", "밥", "먹이", "사료"],
        "topics": ["행동/감정", "생활/돌봄", "CAT-SIGNAL 행동 신호", "CARE-ROUTINE 생활 돌봄"],
        "parts": ["part:02", "part:03", "part:04"],
        "observe": ["정해진 밥시간 전후인지", "먹는 양 변화", "간식 반응", "체중과 활력", "다묘 자원 경쟁"],
        "beginner": "조르는 행동을 바로 버릇으로 보지 말고, 루틴 기대인지 식욕 변화인지 먼저 나눈다.",
        "match_requires_keyword": True,
    },
    {
        "id": "need:predictable_routine",
        "class": "Need",
        "label": "예측 가능한 루틴",
        "summary": "밥, 놀이, 화장실, 출근 전 확인처럼 반복되는 안전한 순서가 고양이의 불안을 낮춘다.",
        "keywords": ["루틴", "출근", "밥시간", "반복", "일상"],
        "topics": ["생활/돌봄"],
        "parts": ["part:02", "part:05"],
        "observe": ["갑작스런 변화", "출근 전 체크", "밥/놀이 시간", "가족 변화"],
        "beginner": "고양이는 설명보다 반복되는 순서로 집을 이해한다.",
    },
    {
        "id": "need:choice",
        "class": "Need",
        "label": "선택권",
        "summary": "고양이가 다가올지, 피할지, 쉴지 선택할 수 있어야 관계가 안전하게 유지된다.",
        "keywords": ["선택", "권리", "싫어", "좋아", "자유", "거리"],
        "topics": ["행동/감정", "관계/윤리"],
        "parts": ["part:03", "part:05"],
        "observe": ["퇴로 차단 여부", "사람의 강요", "다묘 자원 경쟁", "접촉 빈도"],
        "beginner": "고양이가 거절할 수 있어야 다시 다가올 수도 있다.",
    },
    {
        "id": "need:scent_familiarity",
        "class": "Need",
        "label": "냄새와 익숙함",
        "summary": "새 물건, 둘째, 가족 변화는 냄새와 시간의 문제로 천천히 소개해야 한다.",
        "keywords": ["냄새", "새", "낯선", "합사", "방석", "가족"],
        "topics": ["생활/돌봄", "관계/윤리"],
        "parts": ["part:01", "part:05"],
        "observe": ["새 냄새", "기존 자리 상실", "교환 시간", "갑작스런 접근"],
        "beginner": "새로운 것은 좋은 것이라도 고양이에게는 낯선 냄새부터 시작된다.",
    },
    {
        "id": "need:rest_recovery",
        "class": "Need",
        "label": "휴식과 회복",
        "summary": "싸움, 병원, 노화, 큰 변화 뒤에는 활동보다 회복할 수 있는 시간과 공간이 필요하다.",
        "keywords": ["휴식", "회복", "노묘", "싸움", "병원", "잠"],
        "topics": ["건강/진료", "관계/윤리"],
        "parts": ["part:05", "part:06"],
        "observe": ["회복 시간", "쉬는 위치", "식욕/물", "접촉 요구 감소"],
        "beginner": "좋아지게 하려고 계속 만지는 것보다 조용히 회복할 시간을 주는 일이 먼저일 수 있다.",
    },
    {
        "id": "action:context_record",
        "class": "CareAction",
        "label": "전후 맥락 기록",
        "summary": "언제, 어디서, 무엇 직후, 얼마나 자주를 남기면 행동이 패턴으로 보인다.",
        "keywords": ["기록", "관찰", "언제", "얼마나", "메모"],
        "topics": ["생활/돌봄", "건강/진료"],
        "parts": ["part:01", "part:04"],
        "observe": ["시간", "장소", "직전 사건", "반복 횟수"],
        "beginner": "처음에는 해석보다 기록이 더 강하다.",
    },
    {
        "id": "action:pause_contact",
        "class": "CareAction",
        "label": "손 멈추기",
        "summary": "하악질, 꼬리 긴장, 물기 전 신호가 보이면 접촉을 멈추고 거리를 돌려준다.",
        "keywords": ["멈추", "손", "만지", "스킨십", "싫어"],
        "topics": ["행동/감정"],
        "parts": ["part:03"],
        "observe": ["접촉 직전 신호", "꼬리/귀", "몸 회피", "반복 거절"],
        "beginner": "고양이에게 가장 다정한 행동이 손을 멈추는 일일 때가 있다.",
    },
    {
        "id": "action:play_enrichment",
        "class": "CareAction",
        "label": "놀이와 풍부화",
        "summary": "사냥놀이, 먹이퍼즐, 수직공간, 숨바꼭질로 에너지와 호기심을 안전하게 풀어준다.",
        "keywords": ["놀이", "사냥", "먹이퍼즐", "장난감", "풍부화"],
        "topics": ["생활/돌봄", "행동/감정"],
        "parts": ["part:03"],
        "observe": ["선호 장난감", "놀이 시간", "과열 신호", "마무리 간식"],
        "beginner": "놀이도 훈련이 아니라 고양이의 리듬을 읽는 대화다.",
    },
    {
        "id": "action:grooming_care",
        "class": "CareAction",
        "label": "그루밍·빗질 루틴",
        "summary": "빗질, 목욕, 털 관리는 강요보다 짧은 노출, 멈춤, 보상, 피부 관찰로 설계한다.",
        "keywords": ["그루밍", "구르밍", "빗질", "브러싱", "브러시", "목욕", "털관리", "미용"],
        "topics": ["생활/돌봄", "건강/진료", "CARE-ROUTINE 생활 돌봄"],
        "parts": ["part:03", "part:04", "part:07"],
        "observe": ["도구를 보는 반응", "한 번에 견딜 수 있는 시간", "피부와 털 상태", "싫다는 신호"],
        "beginner": "털 관리는 오래 붙잡는 기술보다 싫어할 권리를 지키며 다시 시작하는 루틴이다.",
        "match_requires_keyword": True,
    },
    {
        "id": "action:vet_notes",
        "class": "CareAction",
        "label": "병원 상담용 세 줄 메모",
        "summary": "언제부터, 무엇이, 얼마나 달라졌는지 세 줄로 정리해 진료 상담의 품질을 높인다.",
        "keywords": ["병원", "진료", "상담", "메모", "기록", "수의사"],
        "topics": ["건강/진료"],
        "parts": ["part:04", "part:06"],
        "observe": ["언제부터", "횟수", "식욕/물/화장실/활력", "사진/영상"],
        "beginner": "진단을 검색하기보다 변화 기록을 준비하는 편이 더 안전하다.",
    },
    {
        "id": "action:slow_introduction",
        "class": "CareAction",
        "label": "천천히 소개하기",
        "summary": "새 고양이, 새 물건, 새 가족은 냄새 교환, 문 사이 거리, 분리 공간부터 시작한다.",
        "keywords": ["합사", "둘째", "소개", "새", "천천히", "냄새"],
        "topics": ["관계/윤리", "생활/돌봄"],
        "parts": ["part:05"],
        "observe": ["첫째의 루틴", "냄새 반응", "식사 거리", "퇴로"],
        "beginner": "좋은 만남은 첫 대면보다 천천히 안전해지는 과정이다.",
    },
    {
        "id": "action:separate_and_reset",
        "class": "CareAction",
        "label": "분리 후 안정화",
        "summary": "싸움 직후에는 야단보다 분리, 조용한 회복, 원인 기록이 먼저다.",
        "keywords": ["분리", "싸움", "안정", "회복", "다묘"],
        "topics": ["관계/윤리", "행동/감정"],
        "parts": ["part:05"],
        "observe": ["다친 곳", "숨을 곳", "재접촉 전 시간", "반복 원인"],
        "beginner": "싸움을 말리는 것보다 다시 싸움이 시작되지 않게 회복 시간을 만드는 일이 중요하다.",
    },
    {
        "id": "action:daily_check",
        "class": "CareAction",
        "label": "30초 일상 체크",
        "summary": "물, 밥, 화장실, 문, 활력을 짧게 확인하는 반복 루틴.",
        "keywords": ["체크", "출근", "매일", "루틴", "확인"],
        "topics": ["생활/돌봄"],
        "parts": ["part:02"],
        "observe": ["물", "밥", "화장실", "문/창문", "활력"],
        "beginner": "고양이 돌봄은 대단한 지식보다 매일 같은 것을 놓치지 않는 일에서 시작한다.",
    },
    {
        "id": "action:remove_hazards",
        "class": "CareAction",
        "label": "위험물 치우기",
        "summary": "끈, 비닐, 작은 물건, 위험 식물, 열린 문처럼 사고가 되기 쉬운 요소를 먼저 줄인다.",
        "keywords": ["위험", "끈", "비닐", "식물", "문", "안전", "독성"],
        "topics": ["관계/윤리", "생활/돌봄"],
        "parts": ["part:06"],
        "observe": ["바닥 작은 물건", "식물", "문/창문", "놀이 후 끈 보관"],
        "beginner": "사고를 예측하는 것보다 사고가 날 물건을 줄이는 편이 쉽다.",
    },
    {
        "id": "action:consult_expert",
        "class": "CareAction",
        "label": "전문가에게 묻기",
        "summary": "검색으로 단정하지 않고 기록을 들고 수의사나 구조 전문가에게 묻는 행동.",
        "keywords": ["상담", "문의", "전문가", "수의사", "병원", "구조"],
        "topics": ["건강/진료", "관계/윤리"],
        "parts": ["part:06"],
        "observe": ["기록 준비", "사진/영상", "긴급성", "자가진단 유혹"],
        "beginner": "모를 때 묻는 것은 실패가 아니라 고양이에게 더 안전한 선택이다.",
    },
    {
        "id": "risk:escape",
        "class": "SafetyRisk",
        "label": "실종·탈출",
        "summary": "문과 창문, 방충망, 가족 출입 습관이 실종 예방의 핵심이다.",
        "keywords": ["실종", "탈출", "문", "창문", "방묘", "외출"],
        "topics": ["관계/윤리", "생활/돌봄"],
        "parts": ["part:06"],
        "observe": ["문 여는 순간", "방충망", "현관", "인식표"],
        "beginner": "고양이가 안 나간다는 믿음보다 나갈 수 없는 구조를 만드는 게 먼저다.",
    },
    {
        "id": "risk:hazard_object",
        "class": "SafetyRisk",
        "label": "위험한 작은 물건",
        "summary": "끈, 비닐, 작은 물건, 특정 식물은 귀여운 놀이가 아니라 사고로 이어질 수 있다.",
        "keywords": ["위험", "끈", "비닐", "독성", "식물", "먹으면", "이식증"],
        "topics": ["관계/윤리", "생활/돌봄"],
        "parts": ["part:06"],
        "observe": ["입에 넣는 습관", "혼자 있는 시간", "놀이 후 정리", "식물 접근"],
        "beginner": "고양이가 좋아한다고 안전한 것은 아니다. 삼킬 수 있는 물건은 놀이 후 치운다.",
    },
    {
        "id": "risk:self_diagnosis",
        "class": "SafetyRisk",
        "label": "자가진단·처방 단정",
        "summary": "증상을 검색해 병명으로 단정하기보다 변화 기록과 병원 상담 기준으로 옮긴다.",
        "keywords": ["자가진단", "처방", "사료", "병명", "치료", "검색"],
        "topics": ["건강/진료"],
        "parts": ["part:04", "part:06", "part:07"],
        "observe": ["검색 후 행동", "처방식 임의 변경", "반복 증상", "기록 부족"],
        "beginner": "지식그래프는 진단기가 아니라 상담 준비를 돕는 지도다.",
        "medical": True,
    },
    {
        "id": "risk:unsafe_rescue",
        "class": "SafetyRisk",
        "label": "길고양이 구조 판단",
        "summary": "감정에 끌려 바로 데려오기보다 관찰, 상황 판단, 전문가 연결 순서를 따른다.",
        "keywords": ["길고양이", "구조", "냥줍", "입양", "새끼", "보호소"],
        "topics": ["관계/윤리"],
        "parts": ["part:06"],
        "observe": ["어미 여부", "위험 정도", "지역 구조 자원", "질병/격리"],
        "beginner": "도와주고 싶은 마음은 중요하지만 순서가 틀리면 고양이에게 더 위험할 수 있다.",
    },
    {
        "id": "risk:unsafe_touch",
        "class": "SafetyRisk",
        "label": "무리한 접촉",
        "summary": "아이, 손님, 낯선 사람이 고양이의 거절 신호를 무시하면 관계와 안전이 함께 흔들린다.",
        "keywords": ["아기", "아이", "만지", "스킨십", "물림", "싫어"],
        "topics": ["관계/윤리", "행동/감정"],
        "parts": ["part:05", "part:07"],
        "observe": ["고양이 퇴로", "아이 손의 속도", "하악/꼬리 신호", "보호자 개입"],
        "beginner": "만지는 법보다 만지지 않아야 할 때를 알려주는 규칙이 먼저다.",
    },
    {
        "id": "knowledge:breed_context",
        "class": "Need",
        "label": "품종보다 생활 반응",
        "summary": "묘종 정보는 출발점일 뿐, 실제 생활 반응과 건강 관찰이 더 중요한 개체 정보다.",
        "keywords": ["묘종", "품종", "백과", "코숏", "랙돌", "샴", "페르시안"],
        "topics": ["품종/지식", "BREED-KNOWLEDGE 묘종/지식"],
        "parts": ["part:07"],
        "observe": ["개체 성격", "생활 리듬", "건강 취약성", "외모 단정"],
        "beginner": "품종 설명은 참고하고, 답은 오늘의 고양이 반응에서 다시 확인한다.",
    },
    {
        "id": "knowledge:genetics",
        "class": "Need",
        "label": "외모와 유전 책임",
        "summary": "예쁜 외모 뒤에는 관리 책임과 건강 주의가 함께 있을 수 있다.",
        "keywords": ["유전", "외모", "폴드", "먼치킨", "품종", "랙돌", "귀여"],
        "topics": ["품종/지식", "건강/진료"],
        "parts": ["part:07"],
        "observe": ["품종 특성", "움직임", "피부/털", "정기 검진"],
        "beginner": "귀여움은 끝이 아니라 돌봄 책임의 시작일 수 있다.",
    },
]


CONTEXTS = [
    {
        "id": "context:introduction",
        "class": "Need",
        "label": "합사 첫 단계",
        "summary": "첫 만남보다 냄새, 문, 밥자리, 도망갈 길을 먼저 설계한다.",
        "keywords": ["합사", "둘째", "새 고양이", "다묘"],
        "topics": ["관계/윤리", "RELATIONSHIP 관계/합사"],
        "parts": ["part:05"],
        "observe": ["냄새 교환", "분리 공간", "식사 거리", "퇴로"],
        "beginner": "사랑은 충분조건이 아니다. 합사는 동선과 시간의 설계다.",
    },
    {
        "id": "context:second_cat",
        "class": "Need",
        "label": "둘째 고민",
        "summary": "사람의 외로움이 첫째 고양이의 생활을 무너뜨리지 않도록 먼저 질문을 바꾼다.",
        "keywords": ["둘째", "한 마리", "다묘", "외로움"],
        "topics": ["관계/윤리"],
        "parts": ["part:05"],
        "observe": ["첫째 루틴", "공간 여유", "자원 수", "보호자 시간"],
        "beginner": "둘째는 첫째에게 선물이 아닐 수 있다. 첫째의 생활 안정이 먼저다.",
    },
    {
        "id": "context:baby_family",
        "class": "Need",
        "label": "아이와 고양이",
        "summary": "아이의 호기심과 고양이의 안전을 함께 지키는 접촉 규칙이 필요하다.",
        "keywords": ["아기", "아이", "가족", "임신", "출산"],
        "topics": ["관계/윤리"],
        "parts": ["part:05"],
        "observe": ["고양이 퇴로", "아이 손의 속도", "분리 공간", "감독"],
        "beginner": "좋아하는 마음도 규칙 안에서 표현해야 고양이가 덜 다친다.",
    },
    {
        "id": "context:guardian_absence",
        "class": "Need",
        "label": "보호자 부재",
        "summary": "혼자 있는 시간을 전부 불행으로 해석하지 말고 생활 리듬과 안전 자원을 함께 본다.",
        "keywords": ["부재", "혼자", "외로", "분리불안", "출근"],
        "topics": ["관계/윤리", "생활/돌봄"],
        "parts": ["part:05"],
        "observe": ["물/밥/화장실", "위험물", "놀이 전후", "반복 불안 신호"],
        "beginner": "혼자 있음보다 혼자 있는 동안 안전한 루틴과 자원이 있는지가 더 중요하다.",
    },
    {
        "id": "context:family_change",
        "class": "Need",
        "label": "가족 변화",
        "summary": "새 가족, 이사, 자리 변화는 고양이가 잃는 냄새와 길을 보완해야 한다.",
        "keywords": ["가족", "이사", "변화", "자리", "새"],
        "topics": ["관계/윤리", "생활/돌봄"],
        "parts": ["part:05"],
        "observe": ["잃은 자리", "냄새 변화", "화장실/밥자리 이동", "회복 시간"],
        "beginner": "사람에게 좋은 변화도 고양이에게는 잃어버린 길일 수 있다.",
    },
    {
        "id": "context:kitten",
        "class": "Need",
        "label": "아깽이/새끼 고양이",
        "summary": "작은 고양이는 장난감이 아니라 빠르게 변하는 몸과 높은 안전 요구를 가진 존재다.",
        "keywords": ["아깽", "새끼", "캣초딩", "어린"],
        "topics": ["건강/진료", "관계/윤리"],
        "parts": ["part:07"],
        "observe": ["식사/배변", "체온", "위험물", "무리한 접촉"],
        "beginner": "작고 귀여울수록 환경 안전과 기록이 더 필요하다.",
    },
]


NEED_ACTION_EDGES = [
    ("signal:zoomies", "MAY_INDICATE", "need:energy_release"),
    ("signal:zoomies", "OBSERVE_WITH", "health:litter_change"),
    ("signal:hissing", "MAY_INDICATE", "need:distance"),
    ("signal:hissing", "OBSERVE_WITH", "environment:route"),
    ("signal:slow_blink", "MAY_INDICATE", "need:safety"),
    ("signal:tail_ear_tension", "MAY_INDICATE", "need:distance"),
    ("signal:hiding", "MAY_INDICATE", "need:safety"),
    ("signal:hiding", "OBSERVE_WITH", "environment:hideout"),
    ("signal:biting", "MAY_INDICATE", "need:distance"),
    ("signal:biting", "OBSERVE_WITH", "health:claw_skin_fur"),
    ("signal:purring_kneading", "MAY_INDICATE", "need:rest_recovery"),
    ("signal:vocalization", "OBSERVE_WITH", "health:appetite_change"),
    ("signal:vocalization", "MAY_INDICATE", "need:hunger_satiety"),
    ("signal:relaxed_presence", "MAY_INDICATE", "need:safety"),
    ("signal:fight_or_play", "OBSERVE_WITH", "context:introduction"),
    ("signal:box_seeking", "MAY_INDICATE", "need:safety"),
    ("need:safety", "SUGGESTS", "action:daily_check"),
    ("need:safety", "SUGGESTS", "action:context_record"),
    ("need:distance", "SUGGESTS", "action:pause_contact"),
    ("need:energy_release", "SUGGESTS", "action:play_enrichment"),
    ("need:hunger_satiety", "OBSERVE_WITH", "health:appetite_change"),
    ("need:hunger_satiety", "SUGGESTS", "action:context_record"),
    ("need:predictable_routine", "SUGGESTS", "action:daily_check"),
    ("need:choice", "SUGGESTS", "action:pause_contact"),
    ("need:scent_familiarity", "SUGGESTS", "action:slow_introduction"),
    ("need:rest_recovery", "SUGGESTS", "action:context_record"),
    ("environment:litter_box", "SUPPORTS", "health:litter_change"),
    ("environment:water_station", "SUPPORTS", "health:water_change"),
    ("environment:food_place", "SUPPORTS", "health:appetite_change"),
    ("environment:food_place", "SUPPORTS", "need:hunger_satiety"),
    ("environment:wet_food", "SUPPORTS", "health:water_change"),
    ("environment:wet_food", "OBSERVE_WITH", "health:appetite_change"),
    ("environment:dry_food", "OBSERVE_WITH", "health:water_change"),
    ("environment:dry_food", "OBSERVE_WITH", "health:appetite_change"),
    ("environment:dry_food", "OBSERVE_WITH", "risk:self_diagnosis"),
    ("environment:hideout", "SUPPORTS", "need:safety"),
    ("environment:carrier_room", "SUPPORTS", "need:safety"),
    ("environment:door_window", "PREVENTS", "risk:escape"),
    ("environment:route", "SUPPORTS", "context:introduction"),
    ("health:vomiting", "REQUIRES_RECORD", "action:vet_notes"),
    ("health:litter_change", "REQUIRES_RECORD", "action:vet_notes"),
    ("health:water_change", "REQUIRES_RECORD", "action:vet_notes"),
    ("health:appetite_change", "REQUIRES_RECORD", "action:vet_notes"),
    ("health:weight_change", "REQUIRES_RECORD", "action:vet_notes"),
    ("health:claw_skin_fur", "REQUIRES_RECORD", "action:vet_notes"),
    ("health:grooming_change", "OBSERVE_WITH", "health:claw_skin_fur"),
    ("health:grooming_change", "REQUIRES_RECORD", "action:vet_notes"),
    ("health:senior_change", "REQUIRES_RECORD", "action:vet_notes"),
    ("action:grooming_care", "SUPPORTS", "health:grooming_change"),
    ("action:grooming_care", "SUPPORTS", "health:claw_skin_fur"),
    ("risk:self_diagnosis", "CONSULT_WHEN", "action:consult_expert"),
    ("risk:unsafe_rescue", "CONSULT_WHEN", "action:consult_expert"),
    ("risk:hazard_object", "CONSULT_WHEN", "action:remove_hazards"),
    ("risk:unsafe_touch", "CONSULT_WHEN", "action:pause_contact"),
    ("context:introduction", "SUGGESTS", "action:slow_introduction"),
    ("context:second_cat", "SUGGESTS", "action:slow_introduction"),
    ("context:baby_family", "SUGGESTS", "action:pause_contact"),
    ("context:guardian_absence", "SUGGESTS", "action:daily_check"),
    ("context:family_change", "SUGGESTS", "action:slow_introduction"),
    ("context:kitten", "SUGGESTS", "action:remove_hazards"),
    ("knowledge:breed_context", "OBSERVE_WITH", "health:claw_skin_fur"),
    ("knowledge:genetics", "OBSERVE_WITH", "health:claw_skin_fur"),
]


SCENARIOS = [
    {
        "id": "scenario:sudden_run",
        "label": "갑자기 뛰어요",
        "question": "고양이가 갑자기 뛰거나 밤에 우다다를 해요.",
        "start": ["signal:zoomies", "health:litter_change", "need:energy_release", "action:context_record"],
        "first_checks": ["화장실 다녀온 직후인가요?", "식욕과 활력은 평소와 같나요?", "최근 반복 횟수가 늘었나요?"],
    },
    {
        "id": "scenario:hiding",
        "label": "숨어요",
        "question": "새로 온 뒤나 갑자기 숨어서 나오지 않아요.",
        "start": ["signal:hiding", "environment:hideout", "need:safety", "action:context_record"],
        "first_checks": ["새 사람/물건/소리가 있었나요?", "물과 화장실에 갈 수 있나요?", "식욕과 배변 변화가 있나요?"],
    },
    {
        "id": "scenario:hissing",
        "label": "하악질해요",
        "question": "다가가면 하악질하거나 몸을 낮춰요.",
        "start": ["signal:hissing", "need:distance", "action:pause_contact", "environment:route"],
        "first_checks": ["퇴로가 막혀 있나요?", "새 고양이나 손님이 있나요?", "손이 너무 빨리 가까워졌나요?"],
    },
    {
        "id": "scenario:vomiting",
        "label": "토했어요",
        "question": "토했는데 괜찮은지 모르겠어요.",
        "start": ["health:vomiting", "action:vet_notes", "risk:self_diagnosis"],
        "first_checks": ["몇 번 토했나요?", "내용물과 색을 기록했나요?", "식욕과 활력은 어떤가요?"],
    },
    {
        "id": "scenario:litter",
        "label": "화장실이 달라졌어요",
        "question": "똥, 오줌, 화장실 사용이 평소와 달라요.",
        "start": ["health:litter_change", "environment:litter_box", "action:vet_notes"],
        "first_checks": ["횟수나 양이 바뀌었나요?", "화장실 앞에서 망설이나요?", "통증처럼 보이는 소리가 있나요?"],
    },
    {
        "id": "scenario:not_eating",
        "label": "밥을 안 먹어요",
        "question": "밥을 남기거나 갑자기 먹는 양이 달라졌어요.",
        "start": ["health:appetite_change", "environment:food_place", "action:vet_notes"],
        "first_checks": ["언제부터 달라졌나요?", "간식은 먹나요?", "입 주변이나 활력 변화가 있나요?"],
    },
    {
        "id": "scenario:hungry",
        "label": "배고파 보여요",
        "question": "밥을 찾거나 계속 조르는 것처럼 보여요.",
        "start": ["need:hunger_satiety", "health:appetite_change", "environment:food_place", "action:context_record"],
        "first_checks": ["정해진 밥시간 전후인가요?", "실제 먹는 양이 달라졌나요?", "간식만 찾거나 다묘 경쟁이 있나요?"],
    },
    {
        "id": "scenario:food_type",
        "label": "습식·건식이 고민돼요",
        "question": "습식, 건식, 사료 선택을 어떻게 봐야 할지 모르겠어요.",
        "start": ["environment:wet_food", "environment:dry_food", "health:water_change", "risk:self_diagnosis"],
        "first_checks": ["물 섭취와 소변 변화가 있나요?", "사료를 갑자기 바꿨나요?", "처방식이나 건강 문제를 스스로 단정하고 있나요?"],
    },
    {
        "id": "scenario:grooming",
        "label": "그루밍·빗질이 고민돼요",
        "question": "그루밍, 빗질, 털 관리 반응이 평소와 달라요.",
        "start": ["health:grooming_change", "action:grooming_care", "health:claw_skin_fur", "action:vet_notes"],
        "first_checks": ["특정 부위만 반복하나요?", "빗이나 목욕을 볼 때 도망가나요?", "피부, 털 빠짐, 식욕/활력 변화가 있나요?"],
    },
    {
        "id": "scenario:second_cat",
        "label": "둘째를 고민해요",
        "question": "둘째 고양이를 들여도 될지 모르겠어요.",
        "start": ["context:second_cat", "context:introduction", "need:choice", "action:slow_introduction"],
        "first_checks": ["첫째의 루틴은 안정적인가요?", "자원과 공간이 충분한가요?", "분리 공간을 마련할 수 있나요?"],
    },
    {
        "id": "scenario:danger",
        "label": "위험할까 걱정돼요",
        "question": "집 안 물건이나 문, 창문이 위험한지 모르겠어요.",
        "start": ["risk:hazard_object", "risk:escape", "action:remove_hazards", "environment:door_window"],
        "first_checks": ["삼킬 수 있는 물건이 바닥에 있나요?", "문/창문이 열리는 순간이 있나요?", "식물이나 끈을 치웠나요?"],
    },
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").lower())


def source_weight(item: dict) -> float:
    views = item.get("view_count")
    try:
        views = int(views or 0)
    except (TypeError, ValueError):
        views = 0
    duration = item.get("duration") or 0
    topic_bonus = len(item.get("topics") or []) * 2
    short_bonus = 7 if item.get("media_family") == "shorts" else 0
    return math.log10(max(views, 0) + 10) + topic_bonus + short_bonus + (duration or 0) / 900


def match_concepts(item: dict, concepts: list[dict]) -> list[dict]:
    title = normalize(" ".join([item.get("title") or "", item.get("default_title") or ""]))
    matches = []
    for concept in concepts:
        score = 0
        hits = []
        for keyword in concept.get("keywords", []):
            key = normalize(keyword)
            if key and key in title:
                score += 3 if len(key) >= 3 else 1
                hits.append(keyword)
        for topic in item.get("topics") or []:
            if topic in concept.get("topics", []):
                score += 1
        if concept.get("match_requires_keyword") and not hits:
            continue
        if score:
            matches.append({"id": concept["id"], "score": score, "hits": hits[:5]})
    matches.sort(key=lambda row: row["score"], reverse=True)
    return matches[:8]


def add_node(nodes: dict, node_id: str, label: str, node_class: str, **extra) -> None:
    if node_id in nodes:
        nodes[node_id].update({k: v for k, v in extra.items() if v not in (None, "", [])})
        return
    nodes[node_id] = {
        "id": node_id,
        "label": label,
        "class": node_class,
        "color": CLASSES.get(node_class, {}).get("color", "#64748B"),
        **extra,
    }


def add_edge(edges: list[dict], source: str, relation: str, target: str, **extra) -> None:
    if source == target:
        return
    edges.append(
        {
            "id": f"edge:{len(edges) + 1:05d}",
            "source": source,
            "target": target,
            "relation": relation,
            "label": RELATIONS.get(relation, relation),
            **extra,
        }
    )


def json_dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def as_int(value):
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def as_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def reset_sqlite_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = OFF;

        DROP VIEW IF EXISTS v_top_evidence_concepts;
        DROP VIEW IF EXISTS v_edge_counts_by_relation;
        DROP VIEW IF EXISTS v_node_counts_by_class;

        DROP TABLE IF EXISTS content_matches;
        DROP TABLE IF EXISTS content_topics;
        DROP TABLE IF EXISTS safety_rules;
        DROP TABLE IF EXISTS content_items;
        DROP TABLE IF EXISTS scenarios;
        DROP TABLE IF EXISTS edges;
        DROP TABLE IF EXISTS nodes;
        DROP TABLE IF EXISTS relations;
        DROP TABLE IF EXISTS classes;
        DROP TABLE IF EXISTS metadata;

        PRAGMA foreign_keys = ON;

        CREATE TABLE metadata (
          key TEXT PRIMARY KEY,
          value_json TEXT NOT NULL,
          sort_order INTEGER NOT NULL
        );

        CREATE TABLE classes (
          class_id TEXT PRIMARY KEY,
          label TEXT NOT NULL,
          description TEXT,
          color TEXT,
          sort_order INTEGER NOT NULL,
          payload_json TEXT NOT NULL
        );

        CREATE TABLE relations (
          relation_id TEXT PRIMARY KEY,
          label TEXT NOT NULL,
          sort_order INTEGER NOT NULL
        );

        CREATE TABLE nodes (
          node_id TEXT PRIMARY KEY,
          label TEXT NOT NULL,
          class_id TEXT NOT NULL,
          color TEXT,
          summary TEXT,
          beginner TEXT,
          image TEXT,
          media_family TEXT,
          url TEXT,
          watch_url TEXT,
          thumbnail_url TEXT,
          view_count INTEGER,
          duration_min REAL,
          evidence_count INTEGER,
          medical INTEGER NOT NULL DEFAULT 0,
          sort_order INTEGER NOT NULL,
          payload_json TEXT NOT NULL,
          FOREIGN KEY (class_id) REFERENCES classes(class_id)
        );

        CREATE TABLE edges (
          edge_id TEXT PRIMARY KEY,
          source_id TEXT NOT NULL,
          target_id TEXT NOT NULL,
          relation_id TEXT NOT NULL,
          label TEXT,
          confidence TEXT,
          safety TEXT,
          score REAL,
          sort_order INTEGER NOT NULL,
          payload_json TEXT NOT NULL,
          FOREIGN KEY (source_id) REFERENCES nodes(node_id),
          FOREIGN KEY (target_id) REFERENCES nodes(node_id),
          FOREIGN KEY (relation_id) REFERENCES relations(relation_id)
        );

        CREATE TABLE scenarios (
          scenario_id TEXT PRIMARY KEY,
          label TEXT NOT NULL,
          question TEXT NOT NULL,
          start_json TEXT NOT NULL,
          first_checks_json TEXT NOT NULL,
          sort_order INTEGER NOT NULL,
          payload_json TEXT NOT NULL
        );

        CREATE TABLE content_items (
          content_id TEXT PRIMARY KEY,
          title TEXT,
          default_title TEXT,
          url TEXT,
          watch_url TEXT,
          media_family TEXT,
          duration_min REAL,
          view_count INTEGER,
          book_part_candidate TEXT,
          thumbnail_url TEXT,
          source_tabs_json TEXT NOT NULL,
          topics_json TEXT NOT NULL,
          matched_concepts_json TEXT NOT NULL,
          sort_order INTEGER NOT NULL,
          payload_json TEXT NOT NULL
        );

        CREATE TABLE content_topics (
          content_id TEXT NOT NULL,
          topic TEXT NOT NULL,
          sort_order INTEGER NOT NULL,
          PRIMARY KEY (content_id, topic, sort_order),
          FOREIGN KEY (content_id) REFERENCES content_items(content_id)
        );

        CREATE TABLE content_matches (
          content_id TEXT NOT NULL,
          concept_id TEXT NOT NULL,
          score REAL NOT NULL,
          hits_json TEXT NOT NULL,
          sort_order INTEGER NOT NULL,
          PRIMARY KEY (content_id, concept_id, sort_order),
          FOREIGN KEY (content_id) REFERENCES content_items(content_id),
          FOREIGN KEY (concept_id) REFERENCES nodes(node_id)
        );

        CREATE TABLE safety_rules (
          sort_order INTEGER PRIMARY KEY,
          rule TEXT NOT NULL
        );

        CREATE INDEX idx_nodes_class ON nodes(class_id);
        CREATE INDEX idx_edges_source ON edges(source_id);
        CREATE INDEX idx_edges_target ON edges(target_id);
        CREATE INDEX idx_edges_relation ON edges(relation_id);
        CREATE INDEX idx_content_media ON content_items(media_family);
        CREATE INDEX idx_content_topics_topic ON content_topics(topic);
        CREATE INDEX idx_content_matches_concept ON content_matches(concept_id);

        CREATE VIEW v_node_counts_by_class AS
        SELECT c.class_id, c.label, COUNT(n.node_id) AS node_count
        FROM classes c
        LEFT JOIN nodes n ON n.class_id = c.class_id
        GROUP BY c.class_id, c.label, c.sort_order
        ORDER BY c.sort_order;

        CREATE VIEW v_edge_counts_by_relation AS
        SELECT r.relation_id, r.label, COUNT(e.edge_id) AS edge_count
        FROM relations r
        LEFT JOIN edges e ON e.relation_id = r.relation_id
        GROUP BY r.relation_id, r.label, r.sort_order
        ORDER BY r.sort_order;

        CREATE VIEW v_top_evidence_concepts AS
        SELECT node_id, label, class_id, evidence_count
        FROM nodes
        WHERE evidence_count IS NOT NULL AND evidence_count > 0
        ORDER BY evidence_count DESC, label
        LIMIT 50;
        """
    )


def write_sqlite(graph: dict, db_path: Path) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        reset_sqlite_schema(conn)

        for index, (key, value) in enumerate(graph["meta"].items()):
            conn.execute(
                "INSERT INTO metadata (key, value_json, sort_order) VALUES (?, ?, ?)",
                (key, json_dump(value), index),
            )

        for index, (class_id, payload) in enumerate(graph["classes"].items()):
            conn.execute(
                """
                INSERT INTO classes (class_id, label, description, color, sort_order, payload_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    class_id,
                    payload.get("label", class_id),
                    payload.get("description"),
                    payload.get("color"),
                    index,
                    json_dump(payload),
                ),
            )

        for index, (relation_id, label) in enumerate(graph["relations"].items()):
            conn.execute(
                "INSERT INTO relations (relation_id, label, sort_order) VALUES (?, ?, ?)",
                (relation_id, label, index),
            )

        for index, node in enumerate(graph["nodes"]):
            conn.execute(
                """
                INSERT INTO nodes (
                  node_id, label, class_id, color, summary, beginner, image, media_family,
                  url, watch_url, thumbnail_url, view_count, duration_min, evidence_count,
                  medical, sort_order, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node["id"],
                    node.get("label", node["id"]),
                    node["class"],
                    node.get("color"),
                    node.get("summary"),
                    node.get("beginner"),
                    node.get("image"),
                    node.get("media_family"),
                    node.get("url"),
                    node.get("watch_url"),
                    node.get("thumbnail_url"),
                    as_int(node.get("view_count")),
                    as_float(node.get("duration_min")),
                    as_int(node.get("evidence_count")),
                    1 if node.get("medical") else 0,
                    index,
                    json_dump(node),
                ),
            )

        for index, edge in enumerate(graph["edges"]):
            conn.execute(
                """
                INSERT INTO edges (
                  edge_id, source_id, target_id, relation_id, label, confidence,
                  safety, score, sort_order, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge["id"],
                    edge["source"],
                    edge["target"],
                    edge["relation"],
                    edge.get("label"),
                    edge.get("confidence"),
                    edge.get("safety"),
                    as_float(edge.get("score")),
                    index,
                    json_dump(edge),
                ),
            )

        for index, scenario in enumerate(graph["scenarios"]):
            conn.execute(
                """
                INSERT INTO scenarios (
                  scenario_id, label, question, start_json, first_checks_json,
                  sort_order, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scenario["id"],
                    scenario["label"],
                    scenario["question"],
                    json_dump(scenario.get("start", [])),
                    json_dump(scenario.get("first_checks", [])),
                    index,
                    json_dump(scenario),
                ),
            )

        for index, item in enumerate(graph["content_index"]):
            conn.execute(
                """
                INSERT INTO content_items (
                  content_id, title, default_title, url, watch_url, media_family,
                  duration_min, view_count, book_part_candidate, thumbnail_url,
                  source_tabs_json, topics_json, matched_concepts_json, sort_order,
                  payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["id"],
                    item.get("title"),
                    item.get("default_title"),
                    item.get("url"),
                    item.get("watch_url"),
                    item.get("media_family"),
                    as_float(item.get("duration_min")),
                    as_int(item.get("view_count")),
                    item.get("book_part_candidate"),
                    item.get("thumbnail_url"),
                    json_dump(item.get("source_tabs", [])),
                    json_dump(item.get("topics", [])),
                    json_dump(item.get("matched_concepts", [])),
                    index,
                    json_dump(item),
                ),
            )
            for topic_index, topic in enumerate(item.get("topics", [])):
                conn.execute(
                    "INSERT INTO content_topics (content_id, topic, sort_order) VALUES (?, ?, ?)",
                    (item["id"], topic, topic_index),
                )
            for match_index, match in enumerate(item.get("matched_concepts", [])):
                conn.execute(
                    """
                    INSERT INTO content_matches (content_id, concept_id, score, hits_json, sort_order)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        item["id"],
                        match["id"],
                        as_float(match.get("score")) or 0,
                        json_dump(match.get("hits", [])),
                        match_index,
                    ),
                )

        for index, rule in enumerate(graph["safety_rules"]):
            conn.execute(
                "INSERT INTO safety_rules (sort_order, rule) VALUES (?, ?)",
                (index, rule),
            )


def export_graph_from_sqlite(db_path: Path) -> dict:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        meta = {
            row["key"]: json.loads(row["value_json"])
            for row in conn.execute("SELECT key, value_json FROM metadata ORDER BY sort_order")
        }
        classes = {
            row["class_id"]: json.loads(row["payload_json"])
            for row in conn.execute("SELECT class_id, payload_json FROM classes ORDER BY sort_order")
        }
        relations = {
            row["relation_id"]: row["label"]
            for row in conn.execute("SELECT relation_id, label FROM relations ORDER BY sort_order")
        }
        nodes = [
            json.loads(row["payload_json"])
            for row in conn.execute("SELECT payload_json FROM nodes ORDER BY sort_order")
        ]
        edges = [
            json.loads(row["payload_json"])
            for row in conn.execute("SELECT payload_json FROM edges ORDER BY sort_order")
        ]
        scenarios = [
            json.loads(row["payload_json"])
            for row in conn.execute("SELECT payload_json FROM scenarios ORDER BY sort_order")
        ]
        content_index = [
            json.loads(row["payload_json"])
            for row in conn.execute("SELECT payload_json FROM content_items ORDER BY sort_order")
        ]
        safety_rules = [
            row["rule"]
            for row in conn.execute("SELECT rule FROM safety_rules ORDER BY sort_order")
        ]

    class_counts = Counter(node["class"] for node in nodes)
    relation_counts = Counter(edge["relation"] for edge in edges)
    content_counts = Counter(item["media_family"] for item in content_index)
    matched_content_count = sum(1 for item in content_index if item.get("matched_concepts"))

    meta["content_total"] = len(content_index)
    meta["matched_content_count"] = matched_content_count

    return {
        "meta": meta,
        "classes": classes,
        "relations": relations,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "class_counts": dict(class_counts),
            "relation_counts": dict(relation_counts),
            "content_counts": dict(content_counts),
            "matched_content_count": matched_content_count,
        },
        "nodes": nodes,
        "edges": edges,
        "scenarios": scenarios,
        "content_index": content_index,
        "safety_rules": safety_rules,
    }


def sqlite_table_counts(db_path: Path) -> dict[str, int]:
    counts = {}
    with sqlite3.connect(db_path) as conn:
        table_names = [
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            )
        ]
        for table_name in table_names:
            counts[table_name] = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return counts


def main() -> None:
    meta_path = resolve_latest_youtube_meta()
    meta = read_json(meta_path)
    atlas = read_json(ATLAS)
    atlas_by_id = {row["id"]: row for row in atlas.get("videos", [])}
    all_concepts = CONCEPTS + CONTEXTS
    concept_by_id = {concept["id"]: concept for concept in all_concepts}

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    content_index = []
    evidence_by_concept = defaultdict(list)
    source_nodes = []

    add_node(nodes, "ontology:catbook", "냥톨로지", "Scenario", summary="고양이를 전혀 모르는 사람도 질문으로 출발하는 지식 지도")

    for topic in TOPICS:
        add_node(nodes, f"topic:{topic}", topic, "Topic", summary="콘텐츠 메타와 아틀라스에서 쓰는 주제 분류")

    for part in BOOK_PARTS:
        add_node(nodes, part["id"], part["label"], "BookPart", summary=f"냥냥츄르 독서 길: {part['short']}")
        add_edge(edges, "ontology:catbook", "COVERS", part["id"], confidence="curated")
        for chapter_id, title, concept_ids in part["chapters"]:
            number = int(chapter_id.split(":")[1])
            image_name = CHAPTER_IMAGE_FILES[number]
            add_node(
                nodes,
                chapter_id,
                title,
                "Chapter",
                summary=f"{part['label']}의 {number:02d}장",
                image=f"../assets/generated/chapter-images/{image_name}",
            )
            add_edge(edges, part["id"], "COVERS", chapter_id, confidence="curated")
            for concept_id in concept_ids:
                add_edge(edges, chapter_id, "COVERS", concept_id, confidence="curated")

    for concept in all_concepts:
        add_node(
            nodes,
            concept["id"],
            concept["label"],
            concept["class"],
            summary=concept.get("summary", ""),
            beginner=concept.get("beginner", ""),
            observe=concept.get("observe", []),
            keywords=concept.get("keywords", []),
            medical=concept.get("medical", False),
        )
        add_edge(edges, "ontology:catbook", "COVERS", concept["id"], confidence="curated")
        for topic in concept.get("topics", []):
            add_edge(edges, f"topic:{topic}", "COVERS", concept["id"], confidence="curated")
        for part_id in concept.get("parts", []):
            add_edge(edges, part_id, "COVERS", concept["id"], confidence="curated")

    for source, relation, target in NEED_ACTION_EDGES:
        add_edge(edges, source, relation, target, confidence="curated", safety="non-diagnostic")

    for scenario in SCENARIOS:
        add_node(
            nodes,
            scenario["id"],
            scenario["label"],
            "Scenario",
            summary=scenario["question"],
            checks=scenario["first_checks"],
        )
        add_edge(edges, "ontology:catbook", "STARTS_WITH", scenario["id"], confidence="curated")
        for concept_id in scenario["start"]:
            add_edge(edges, scenario["id"], "STARTS_WITH", concept_id, confidence="curated")

    for item in meta.get("items", []):
        atlas_row = atlas_by_id.get(item.get("id"))
        topics = list(dict.fromkeys((item.get("topics") or []) + (atlas_row.get("dominant_topics", []) if atlas_row else [])))
        if atlas_row and atlas_row.get("book_part_candidate"):
            part_label = atlas_row["book_part_candidate"]
        else:
            part_label = ""
        matches = match_concepts({**item, "topics": topics}, all_concepts)
        row = {
            "id": item.get("id"),
            "title": item.get("title"),
            "default_title": item.get("default_title"),
            "url": item.get("url"),
            "watch_url": item.get("watch_url"),
            "media_family": item.get("media_family"),
            "source_tabs": item.get("source_tabs", []),
            "source_channels": item.get("source_channels", []),
            "source_channel_key": item.get("source_channel_key"),
            "source_channel_handle": item.get("source_channel_handle"),
            "source_channel_id": item.get("source_channel_id"),
            "source_channel_title": item.get("source_channel_title"),
            "duration_min": item.get("duration_min"),
            "view_count": item.get("view_count"),
            "topics": topics,
            "book_part_candidate": part_label,
            "thumbnail_url": item.get("thumbnail_url"),
            "matched_concepts": matches,
        }
        content_index.append(row)
        for match in matches:
            evidence_by_concept[match["id"]].append(
                {
                    **row,
                    "match_score": match.get("score", 0),
                    "match_hits": match.get("hits", []),
                }
            )
        if matches:
            source_nodes.append((source_weight(item) + sum(match["score"] for match in matches), row))

    source_nodes.sort(key=lambda pair: pair[0], reverse=True)
    for _, item in source_nodes[:260]:
        node_id = f"source:{item['id']}"
        add_node(
            nodes,
            node_id,
            item["title"] or item["id"],
            "Source",
            summary="영상/숏폼 공개 메타 근거",
            media_family=item.get("media_family"),
            url=item.get("url"),
            watch_url=item.get("watch_url"),
            source_channel_key=item.get("source_channel_key"),
            source_channel_handle=item.get("source_channel_handle"),
            source_channel_id=item.get("source_channel_id"),
            source_channel_title=item.get("source_channel_title"),
            view_count=item.get("view_count"),
            duration_min=item.get("duration_min"),
            thumbnail_url=item.get("thumbnail_url"),
        )
        for topic in item.get("topics", [])[:3]:
            add_edge(edges, node_id, "HAS_TOPIC", f"topic:{topic}", confidence="metadata")
        for match in item.get("matched_concepts", [])[:4]:
            add_edge(
                edges,
                match["id"],
                "HAS_EVIDENCE",
                node_id,
                confidence="metadata_title",
                score=match["score"],
                hits=match["hits"],
            )

    for concept_id, evidence in evidence_by_concept.items():
        evidence.sort(key=lambda item: (item.get("match_score", 0), source_weight(item)), reverse=True)
        if concept_id in nodes:
            nodes[concept_id]["evidence_count"] = len(evidence)
            nodes[concept_id]["top_evidence"] = [
                {
                    "id": item["id"],
                    "title": item["title"],
                    "url": item["url"],
                    "media_family": item["media_family"],
                    "view_count": item["view_count"],
                    "duration_min": item["duration_min"],
                    "topics": item["topics"][:4],
                    "match_score": item.get("match_score", 0),
                    "match_hits": item.get("match_hits", []),
                }
                for item in evidence[:8]
            ]

    class_counts = Counter(node["class"] for node in nodes.values())
    relation_counts = Counter(edge["relation"] for edge in edges)
    content_counts = Counter(item["media_family"] for item in content_index)
    matched_content_count = sum(1 for item in content_index if item["matched_concepts"])

    graph = {
        "meta": {
            "title": "냥톨로지",
            "description": "초보자 질문, 고양이 신호, 욕구/상태, 환경, 건강 관찰, 집사 행동, 책 챕터, 유튜브 콘텐츠 근거를 연결한 탐색형 온톨로지",
            "generated_from": [str(meta_path.name), str(ATLAS.name)],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": SCHEMA_VERSION,
            "backend": "SQLite SSOT + JSON export",
            "sqlite_path": "../data/catbook_ontology.sqlite",
            "json_export_path": "cat_ontology_graph.json",
            "content_total": len(content_index),
            "matched_content_count": matched_content_count,
            "safety_note": "건강/진료 관계는 진단/처방이 아니라 관찰, 기록, 상담 준비로만 표현한다.",
        },
        "classes": CLASSES,
        "relations": RELATIONS,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "class_counts": dict(class_counts),
            "relation_counts": dict(relation_counts),
            "content_counts": dict(content_counts),
            "matched_content_count": matched_content_count,
        },
        "nodes": list(nodes.values()),
        "edges": edges,
        "scenarios": SCENARIOS,
        "content_index": content_index,
        "safety_rules": [
            "진단, 처방, 치료 단정 관계를 만들지 않는다.",
            "건강 신호는 관찰 항목, 기록 항목, 상담 기준으로만 보여준다.",
            "자막 원문과 영상 파일은 저장하지 않는다.",
            "숏폼은 duration 미상 항목이 많으므로 근거 수준을 metadata_title로 표시한다.",
        ],
    }

    write_sqlite(graph, DB)
    exported_graph = export_graph_from_sqlite(DB)
    OUT.write_text(json.dumps(exported_graph, ensure_ascii=False, indent=2), encoding="utf-8")
    from export_cat_ontology_rdf import SHAPES_OUT, TTL_OUT, OWL_OUT, export as export_rdf

    rdf_export = export_rdf(OUT, TTL_OUT, OWL_OUT, SHAPES_OUT)
    table_counts = sqlite_table_counts(DB)

    top_concepts = sorted(
        [
            (node["label"], node.get("evidence_count", 0), node["class"])
            for node in nodes.values()
            if node["class"] not in {"Source", "Topic", "BookPart", "Chapter", "Scenario"}
        ],
        key=lambda row: row[1],
        reverse=True,
    )[:16]
    report_lines = [
        "# 냥톨로지 생성 리포트",
        "",
        "## 요약",
        "",
        f"- 노드: {len(nodes)}개",
        f"- 엣지: {len(edges)}개",
        f"- 콘텐츠 인덱스: {len(content_index)}개",
        f"- 개념 매칭 콘텐츠: {matched_content_count}개",
        f"- 그래프에 표시할 상위 근거 콘텐츠 노드: {min(260, len(source_nodes))}개",
        f"- SQLite DB: `{DB.relative_to(CATBOOK)}`",
        f"- JSON export: `{OUT.relative_to(CATBOOK)}`",
        f"- RDF Turtle: `{TTL_OUT.relative_to(CATBOOK)}`",
        f"- OWL/RDFXML: `{OWL_OUT.relative_to(CATBOOK)}`",
        f"- SHACL shapes: `{SHAPES_OUT.relative_to(CATBOOK)}`",
        f"- RDF triples: {rdf_export['triples']}개",
        f"- 스키마 버전: `{SCHEMA_VERSION}`",
        "",
        "## SQLite 테이블",
        "",
        "| 테이블 | 행 수 |",
        "| --- | ---: |",
    ]
    for table_name, count in table_counts.items():
        report_lines.append(f"| {table_name} | {count} |")
    report_lines.extend(
        [
            "",
            "## 클래스별 노드 수",
            "",
            "| 클래스 | 노드 수 |",
            "| --- | ---: |",
        ]
    )
    for class_name, count in class_counts.most_common():
        report_lines.append(f"| {class_name} | {count} |")
    report_lines.extend(["", "## 근거가 많은 개념", "", "| 개념 | 클래스 | 근거 수 |", "| --- | --- | ---: |"])
    for label, count, class_name in top_concepts:
        report_lines.append(f"| {label} | {class_name} | {count} |")
    report_lines.extend(
        [
            "",
            "## 안전 원칙",
            "",
            "- 건강/진료 관계는 진단/처방이 아니라 관찰, 기록, 상담 준비로만 표현한다.",
            "- YouTube 공개 메타만 사용하며 자막 원문과 영상 파일은 저장하지 않는다.",
        ]
    )
    OUT_REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "sqlite": str(DB),
                "graph": str(OUT),
                "report": str(OUT_REPORT),
                "rdf_turtle": str(TTL_OUT),
                "owl": str(OWL_OUT),
                "shapes": str(SHAPES_OUT),
                "rdf_triples": rdf_export["triples"],
                "nodes": len(nodes),
                "edges": len(edges),
                "content_index": len(content_index),
                "matched_content_count": matched_content_count,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
