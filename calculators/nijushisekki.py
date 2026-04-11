"""二十四節気計算エンジン"""

import json
import os
from datetime import date

CATEGORY = "東洋占術"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# 二十四節気の日付範囲（おおよその固定日付）
SEKKI_DATES = [
    (1, 6, "小寒"), (1, 20, "大寒"),
    (2, 4, "立春"), (2, 19, "雨水"),
    (3, 6, "啓蟄"), (3, 21, "春分"),
    (4, 5, "清明"), (4, 20, "穀雨"),
    (5, 6, "立夏"), (5, 21, "小満"),
    (6, 6, "芒種"), (6, 21, "夏至"),
    (7, 7, "小暑"), (7, 23, "大暑"),
    (8, 7, "立秋"), (8, 23, "処暑"),
    (9, 8, "白露"), (9, 23, "秋分"),
    (10, 8, "寒露"), (10, 23, "霜降"),
    (11, 7, "立冬"), (11, 22, "小雪"),
    (12, 7, "大雪"), (12, 22, "冬至"),
]

SEKKI_GOGYO = {
    "立春": "木", "雨水": "木", "啓蟄": "木", "春分": "木", "清明": "木", "穀雨": "木",
    "立夏": "火", "小満": "火", "芒種": "火", "夏至": "火", "小暑": "火", "大暑": "火",
    "立秋": "金", "処暑": "金", "白露": "金", "秋分": "金", "寒露": "金", "霜降": "金",
    "立冬": "水", "小雪": "水", "大雪": "水", "冬至": "水", "小寒": "水", "大寒": "水",
}

GOGYO_COMPAT = {
    ("木", "木"): (4, "同じ木の気。深い共感と自然な調和が生まれる関係です。"),
    ("木", "火"): (5, "木生火。お互いの情熱を燃え上がらせる最高の組み合わせ。"),
    ("木", "土"): (2, "木剋土。価値観の違いが生じやすいですが、成長の機会です。"),
    ("木", "金"): (2, "金剋木。お互いを抑制しがち。距離感が大切です。"),
    ("木", "水"): (5, "水生木。自然な支え合いがある理想的な関係。"),
    ("火", "火"): (4, "同じ火の気。情熱が共鳴し、互いの成長を見守り育てる関係。"),
    ("火", "土"): (5, "火生土。安定した信頼関係を築けます。"),
    ("火", "金"): (2, "火剋金。衝突が生じやすい組み合わせ。"),
    ("火", "水"): (2, "水剋火。正反対の性質ですが、バランスを取れれば強い。"),
    ("土", "土"): (4, "同じ土の気。揺るぎない安定感と信頼で結ばれる関係です。"),
    ("土", "金"): (5, "土生金。お互いを磨き合える素晴らしい関係。"),
    ("土", "水"): (2, "土剋水。制約を感じやすい関係。自由を尊重して。"),
    ("金", "金"): (4, "同じ金の気。切磋琢磨し互いを高め合える関係です。"),
    ("金", "水"): (5, "金生水。自然な流れで協力し合える関係。"),
    ("水", "水"): (4, "同じ水の気。深い共感と直観的な理解で結ばれる関係です。"),
}


def _get_sekki(birthday: date) -> str:
    """月日から該当する二十四節気を判定"""
    month = birthday.month
    day = birthday.day

    # 逆順で検索して、最も近い過去の節気を見つける
    result = "冬至"  # デフォルト
    for m, d, name in SEKKI_DATES:
        if (month > m) or (month == m and day >= d):
            result = name
    return result


def _load_sekki_data() -> dict:
    filepath = os.path.join(DATA_DIR, 'nijushisekki.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate(person_a: dict, person_b: dict) -> dict:
    """二十四節気の相性を計算する"""
    bd_a = person_a['birthday']
    bd_b = person_b['birthday']

    sekki_a = _get_sekki(bd_a)
    sekki_b = _get_sekki(bd_b)

    data = _load_sekki_data()
    sekki_info = data.get("sekki", {})

    info_a = sekki_info.get(sekki_a, {"description": "", "energy": ""})
    info_b = sekki_info.get(sekki_b, {"description": "", "energy": ""})

    gogyo_a = SEKKI_GOGYO.get(sekki_a, "土")
    gogyo_b = SEKKI_GOGYO.get(sekki_b, "土")

    key = (gogyo_a, gogyo_b) if (gogyo_a, gogyo_b) in GOGYO_COMPAT else (gogyo_b, gogyo_a)
    score, compat_text = GOGYO_COMPAT.get(key, (3, "穏やかな相性です。"))

    score_100 = {1: 35, 2: 50, 3: 65, 4: 80, 5: 95}.get(score, 65)

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    return {
        "name": "二十四節気",
        "category": "nijushisekki",
        "icon": "eco",
        "score": score,
        "score_100": score_100,
        "summary": f"{sekki_a}（{gogyo_a}）× {sekki_b}（{gogyo_b}）",
        "details": {
            "person_a": {
                "sekki": sekki_a,
                "gogyo": gogyo_a,
                "description": info_a.get("description", ""),
            },
            "person_b": {
                "sekki": sekki_b,
                "gogyo": gogyo_b,
                "description": info_b.get("description", ""),
            },
            "compatibility": {
                "gogyo_relation": f"{gogyo_a} × {gogyo_b}",
                "description": compat_text,
            },
        },
        "highlights": [
            f"{name_a}の節気: {sekki_a}（{gogyo_a}の気）",
            f"{name_b}の節気: {sekki_b}（{gogyo_b}の気）",
            f"五行関係: {compat_text}",
        ],
        "advice": compat_text,
    }
