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
    ("木", "木"): (4, "同じ木の季節エネルギーを持ち、成長と発展への志向が共鳴する関係です。春の芽吹きのような生命力を共有しているため、互いの挑戦を自然に応援し合えるでしょう。"),
    ("木", "火"): (5, "木生火の相生関係で、木の節気が持つ成長力が火の情熱を燃え上がらせる最高の組み合わせです。季節の気が自然に循環するように、互いのエネルギーを高め合い共に輝けるでしょう。"),
    ("木", "土"): (2, "木剋土の相剋関係で、季節エネルギーの方向性に違いが生じやすい組み合わせです。しかし自然界では剋す関係も生態系の一部であり、互いの違いを受け入れることで成長の糧にできます。"),
    ("木", "金"): (2, "金剋木の相剋関係で、互いの季節エネルギーが抑制し合いやすい組み合わせです。自然の理では金は木を切り整える役割も担うため、適度な距離感を保ちつつ建設的な関係を目指しましょう。"),
    ("木", "水"): (5, "水生木の相生関係で、水の節気が持つ潤いが木の成長を促す理想的な組み合わせです。自然界の恵みの循環のように、相手から受けた支えが自身の開花につながるでしょう。"),
    ("火", "火"): (4, "同じ火の季節エネルギーを持ち、情熱と活力が共鳴する関係です。夏の陽気のような明るさを共有しているため、互いの熱意を認め合い、燃え尽きないよう適度な休息も大切にしましょう。"),
    ("火", "土"): (5, "火生土の相生関係で、火の節気の情熱が土の安定を生み出す好相性です。季節の循環が自然に実りをもたらすように、二人の関係にも着実な信頼と安心感が育まれるでしょう。"),
    ("火", "金"): (2, "火剋金の相剋関係で、季節エネルギーの衝突が起きやすい組み合わせです。しかし鍛冶が金を鍛えるように、この緊張関係を互いを磨く力に変えることで、より強い絆が生まれます。"),
    ("火", "水"): (2, "水剋火の相剋関係で、正反対の季節エネルギーを持つ組み合わせです。自然界では水と火のバランスが生命を育むように、互いの強みを活かし弱みを補い合う意識が関係改善の鍵です。"),
    ("土", "土"): (4, "同じ土の季節エネルギーを持ち、揺るぎない安定感と信頼で結ばれる関係です。大地のような包容力を共有しているため、焦らず着実に関係を深め、互いの土台を支え合いましょう。"),
    ("土", "金"): (5, "土生金の相生関係で、土の節気が持つ包容力が金の輝きを引き出す素晴らしい組み合わせです。大地が宝石を育むように、互いの才能を磨き合い高め合える関係を大切にしてください。"),
    ("土", "水"): (2, "土剋水の相剋関係で、季節エネルギーの制約が生じやすい組み合わせです。しかし堤防が水を導くように、適切な形で関係を整えることが大切です。相手の自由を尊重しつつ信頼関係を築きましょう。"),
    ("金", "金"): (4, "同じ金の季節エネルギーを持ち、切磋琢磨して互いを高め合える関係です。秋の実りのような成熟した関係を築ける素養があるため、互いの成果を認め合い共に洗練を目指しましょう。"),
    ("金", "水"): (5, "金生水の相生関係で、金の節気が持つ明晰さが水の流れを生み出す好相性です。自然の循環が新たな生命を育むように、二人の協力から創造的な成果が自然と生まれるでしょう。"),
    ("水", "水"): (4, "同じ水の季節エネルギーを持ち、深い共感と直観的な理解で結ばれる関係です。冬の静けさのような内省の力を共有しているため、言葉を超えた心の交流を大切にしていきましょう。"),
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
