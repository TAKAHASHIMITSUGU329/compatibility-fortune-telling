"""エニアグラム相性計算エンジン"""

import json
import os

CATEGORY = "性格分析"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

TYPE_NAMES = {
    1: "改革する人",
    2: "助ける人",
    3: "達成する人",
    4: "個性的な人",
    5: "調べる人",
    6: "忠実な人",
    7: "熱中する人",
    8: "挑戦する人",
    9: "平和をもたらす人",
}


def _parse_type(value) -> int:
    """エニアグラムタイプを数値に変換"""
    if not value:
        return 0
    if isinstance(value, int):
        return value if 1 <= value <= 9 else 0
    s = str(value).replace("タイプ", "").strip()
    try:
        n = int(s)
        return n if 1 <= n <= 9 else 0
    except (ValueError, TypeError):
        return 0


def _parse_wing(value) -> int:
    """ウィングを数値に変換"""
    if not value:
        return 0
    s = str(value).replace("w", "").replace("W", "").strip()
    try:
        n = int(s)
        return n if 1 <= n <= 9 else 0
    except (ValueError, TypeError):
        return 0


# MBTI → エニアグラム推定マッピング
# (第1候補タイプ, 推定ウィング)
MBTI_TO_ENNEAGRAM = {
    "INFJ": (1, 4),
    "ISFJ": (2, 6),
    "INTJ": (5, 6),
    "INTP": (5, 4),
    "ENTJ": (8, 7),
    "ENTP": (7, 8),
    "INFP": (4, 5),
    "ENFJ": (2, 3),
    "ENFP": (7, 6),
    "ISTJ": (1, 9),
    "ESTJ": (1, 2),
    "ESFJ": (2, 1),
    "ISTP": (5, 6),
    "ISFP": (9, 8),
    "ESTP": (7, 8),
    "ESFP": (7, 6),
}


def _estimate_from_mbti(mbti: str) -> tuple:
    """MBTIタイプからエニアグラムタイプとウィングを推定する"""
    if not mbti:
        return 0, 0
    key = mbti.upper().replace("-A", "").replace("-T", "").strip()
    result = MBTI_TO_ENNEAGRAM.get(key, (0, 0))
    return result


def _load_compatibility_data() -> dict:
    filepath = os.path.join(DATA_DIR, 'enneagram_compatibility.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate(person_a: dict, person_b: dict) -> dict:
    """エニアグラム相性を計算する"""
    type_a = _parse_type(person_a.get('enneagram', ''))
    type_b = _parse_type(person_b.get('enneagram', ''))
    wing_a = _parse_wing(person_a.get('wing', ''))
    wing_b = _parse_wing(person_b.get('wing', ''))

    # 手動入力がなければMBTIから自動推定
    if not type_a:
        type_a, wing_a = _estimate_from_mbti(person_a.get('mbti', ''))
    if not type_b:
        type_b, wing_b = _estimate_from_mbti(person_b.get('mbti', ''))

    if not type_a or not type_b:
        return None

    data = _load_compatibility_data()
    key = f"{type_a}_{type_b}"
    reverse_key = f"{type_b}_{type_a}"
    compat = data.get("compatibility", {}).get(key) or data.get("compatibility", {}).get(reverse_key, {})

    score = compat.get("score", 3)
    score_100 = compat.get("score_100", 60)
    summary_text = compat.get("summary", "")
    advice_text = compat.get("advice", "")

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    type_label_a = f"タイプ{type_a}"
    type_label_b = f"タイプ{type_b}"
    if wing_a:
        type_label_a += f"w{wing_a}"
    if wing_b:
        type_label_b += f"w{wing_b}"

    highlights = [
        f"{name_a}: {type_label_a}（{TYPE_NAMES.get(type_a, '')}）",
        f"{name_b}: {type_label_b}（{TYPE_NAMES.get(type_b, '')}）",
    ]

    # ウィングの影響
    wing_note = ""
    if wing_a and wing_b:
        if wing_a == type_b or wing_b == type_a:
            wing_note = "ウィングの影響で相手のタイプへの理解が深まっています。"
            highlights.append(wing_note)

    return {
        "name": "エニアグラム",
        "category": "enneagram",
        "icon": "diversity_2",
        "score": score,
        "score_100": score_100,
        "summary": f"{type_label_a} × {type_label_b} — {summary_text}",
        "details": {
            "person_a": {
                "type": type_a,
                "wing": wing_a,
                "type_name": TYPE_NAMES.get(type_a, ""),
                "label": type_label_a,
            },
            "person_b": {
                "type": type_b,
                "wing": wing_b,
                "type_name": TYPE_NAMES.get(type_b, ""),
                "label": type_label_b,
            },
            "compatibility": {
                "summary": summary_text,
                "wing_note": wing_note,
            },
        },
        "highlights": highlights,
        "advice": advice_text,
    }
