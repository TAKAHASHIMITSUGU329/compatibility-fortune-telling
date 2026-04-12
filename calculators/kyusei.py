"""九星気学 計算エンジン"""

from datetime import date

CATEGORY = "東洋占術"

KYUSEI_NAMES = [
    "", "一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星",
    "六白金星", "七赤金星", "八白土星", "九紫火星"
]

# 五行属性
GOGYO = {
    1: "水", 2: "土", 3: "木", 4: "木", 5: "土",
    6: "金", 7: "金", 8: "土", 9: "火"
}

# 五行の相生関係（AがBを生む）
SOJO = {
    "木": "火", "火": "土", "土": "金", "金": "水", "水": "木"
}

# 五行の相剋関係（AがBを剋す）
SOKOKU = {
    "木": "土", "火": "金", "土": "水", "金": "木", "水": "火"
}


def _honmeisei(birthday: date) -> int:
    """本命星を算出する。2月4日前の生まれは前年で計算"""
    year = birthday.year
    # 立春（2月4日頃）前は前年扱い
    if birthday.month == 1 or (birthday.month == 2 and birthday.day < 4):
        year -= 1

    # 年の各桁を足して一桁にする
    digit_sum = sum(int(d) for d in str(year))
    while digit_sum > 9:
        digit_sum = sum(int(d) for d in str(digit_sum))

    # 11から引く
    result = 11 - digit_sum
    if result > 9:
        result -= 9

    return result


def _get_relationship(sei_a: int, sei_b: int) -> tuple:
    """九星同士の五行関係を判定 -> (関係名, スコア, 説明)"""
    gogyo_a = GOGYO[sei_a]
    gogyo_b = GOGYO[sei_b]

    if gogyo_a == gogyo_b:
        return ("比和", 4, f"同じ{gogyo_a}の五行属性を持つ比和の関係で、価値観や行動パターンに深い共感が生まれます。似た者同士ゆえの衝突もありますが、五行の調和を意識して互いの個性を認め合うことで安定した関係を築けるでしょう。")

    # AがBを生む
    if SOJO.get(gogyo_a) == gogyo_b:
        return ("相生（生じる側）", 5, f"五行相生の理に基づき、{KYUSEI_NAMES[sei_a]}が{KYUSEI_NAMES[sei_b]}を育てる最良の関係です。気のエネルギーが自然に流れ、支援と成長の循環が生まれます。この五行の恵みを活かし、互いの才能を伸ばし合いましょう。")

    # BがAを生む
    if SOJO.get(gogyo_b) == gogyo_a:
        return ("相生（生じられる側）", 4, f"五行相生の流れにより、{KYUSEI_NAMES[sei_b]}が{KYUSEI_NAMES[sei_a]}を育てる関係です。相手から多くのエネルギーを受け取れる恵まれた相性なので、感謝の気持ちを忘れず、受けた恩恵を周囲にも広げていくことで運気がさらに向上します。")

    # AがBを剋す
    if SOKOKU.get(gogyo_a) == gogyo_b:
        return ("相剋（剋す側）", 2, f"五行相剋の関係により、{KYUSEI_NAMES[sei_a]}が{KYUSEI_NAMES[sei_b]}を抑える力学が働きやすい組み合わせです。力関係の偏りに注意し、相手の五行の気を尊重する姿勢を持つことで、相剋のエネルギーを建設的な刺激へと転換できます。")

    # BがAを剋す
    if SOKOKU.get(gogyo_b) == gogyo_a:
        return ("相剋（剋される側）", 2, f"五行相剋の関係で、{KYUSEI_NAMES[sei_b]}が{KYUSEI_NAMES[sei_a]}を抑える力学が生じやすい組み合わせです。自分らしさを保つために、自身の五行の気を意識的に養い、対等なコミュニケーションを心がけることで関係は改善へ向かいます。")

    return ("普通", 3, "五行の関係において特別な吉凶はなく、穏やかな相性です。九星気学では中庸の関係も大切にされており、互いの本命星の特性を理解し合うことで、安定した信頼関係を自然に育んでいけるでしょう。")


def calculate(person_a: dict, person_b: dict) -> dict:
    """九星気学の相性を計算する"""
    bd_a = person_a['birthday']
    bd_b = person_b['birthday']

    sei_a = _honmeisei(bd_a)
    sei_b = _honmeisei(bd_b)

    name_sei_a = KYUSEI_NAMES[sei_a]
    name_sei_b = KYUSEI_NAMES[sei_b]
    gogyo_a = GOGYO[sei_a]
    gogyo_b = GOGYO[sei_b]

    relationship, score, description = _get_relationship(sei_a, sei_b)
    score_100 = {1: 20, 2: 40, 3: 60, 4: 80, 5: 95}.get(score, 60)

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    return {
        "name": "九星気学",
        "category": "kyusei",
        "icon": "grid_view",
        "score": score,
        "score_100": score_100,
        "summary": f"{name_sei_a} × {name_sei_b} — {relationship}",
        "details": {
            "person_a": {
                "honmeisei": sei_a,
                "honmeisei_name": name_sei_a,
                "gogyo": gogyo_a,
            },
            "person_b": {
                "honmeisei": sei_b,
                "honmeisei_name": name_sei_b,
                "gogyo": gogyo_b,
            },
            "compatibility": {
                "relationship": relationship,
                "gogyo_a": gogyo_a,
                "gogyo_b": gogyo_b,
                "description": description,
            },
        },
        "highlights": [
            f"{name_a}の本命星: {name_sei_a}（{gogyo_a}）",
            f"{name_b}の本命星: {name_sei_b}（{gogyo_b}）",
            f"五行関係: {relationship}",
        ],
        "advice": description,
    }
