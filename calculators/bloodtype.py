"""血液型相性計算エンジン"""

import json
import os

CATEGORY = "その他占い"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

BLOOD_TYPE_TRAITS = {
    "A": "几帳面で責任感が強い。繊細で思いやりがある",
    "B": "マイペースで自由奔放。好奇心旺盛で行動力がある",
    "O": "大らかでリーダーシップがある。情熱的で面倒見が良い",
    "AB": "二面性があり知的。冷静な分析力とクリエイティビティを持つ",
}


def _normalize_blood_type(bt: str) -> str:
    """血液型文字列を正規化"""
    if not bt:
        return ""
    bt = bt.upper().replace("型", "").strip()
    if bt in ("A", "B", "O", "AB"):
        return bt
    return ""


def _load_compatibility_data() -> dict:
    filepath = os.path.join(DATA_DIR, 'bloodtype_compatibility.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate(person_a: dict, person_b: dict) -> dict:
    """血液型の相性を計算する"""
    bt_a = _normalize_blood_type(person_a.get('blood_type', ''))
    bt_b = _normalize_blood_type(person_b.get('blood_type', ''))

    if not bt_a or not bt_b:
        return None

    data = _load_compatibility_data()
    key = f"{bt_a}_{bt_b}"
    compat = data.get("compatibility", {}).get(key, {})

    score = compat.get("score", 3)
    score_100 = compat.get("score_100", 60)
    summary_text = compat.get("summary", f"{bt_a}型と{bt_b}型の相性")
    trait_desc_a = BLOOD_TYPE_TRAITS.get(bt_a, "")
    trait_desc_b = BLOOD_TYPE_TRAITS.get(bt_b, "")
    if score >= 4:
        advice_text = f"{bt_a}型の「{trait_desc_a}」と{bt_b}型の「{trait_desc_b}」が自然に補い合う好相性です。血液型が示す気質の親和性が高いため、互いの長所を認め合い、リラックスした関係を楽しんでください。"
    elif score >= 3:
        advice_text = f"{bt_a}型の「{trait_desc_a}」と{bt_b}型の「{trait_desc_b}」は異なる特性を持ちますが、その違いが新鮮な刺激になります。血液型の気質差を理解した上で歩み寄ることで、バランスの取れた良い関係が築けるでしょう。"
    else:
        advice_text = f"{bt_a}型の「{trait_desc_a}」と{bt_b}型の「{trait_desc_b}」は気質に違いがあり、すれ違いが生じやすい面があります。しかし血液型の違いは多様な視点をもたらす強みでもあるため、相手の行動原理を理解する努力が関係改善の鍵です。"

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    return {
        "name": "血液型相性",
        "category": "bloodtype",
        "icon": "bloodtype",
        "score": score,
        "score_100": score_100,
        "summary": f"{bt_a}型 × {bt_b}型 — {summary_text}",
        "details": {
            "person_a": {
                "blood_type": bt_a,
                "traits": BLOOD_TYPE_TRAITS.get(bt_a, ""),
            },
            "person_b": {
                "blood_type": bt_b,
                "traits": BLOOD_TYPE_TRAITS.get(bt_b, ""),
            },
            "compatibility": {
                "summary": summary_text,
            },
        },
        "highlights": [
            f"{name_a}: {bt_a}型 — {BLOOD_TYPE_TRAITS.get(bt_a, '')}",
            f"{name_b}: {bt_b}型 — {BLOOD_TYPE_TRAITS.get(bt_b, '')}",
        ],
        "advice": advice_text,
    }
