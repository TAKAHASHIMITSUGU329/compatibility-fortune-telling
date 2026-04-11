"""干支（十二支）相性計算エンジン"""

from datetime import date

CATEGORY = "東洋占術"

JUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
JUNISHI_READING = ["ね", "うし", "とら", "う", "たつ", "み", "うま", "ひつじ", "さる", "とり", "いぬ", "い"]
JUNISHI_ANIMAL = ["ネズミ", "ウシ", "トラ", "ウサギ", "タツ", "ヘビ", "ウマ", "ヒツジ", "サル", "トリ", "イヌ", "イノシシ"]


def _get_junishi_index(birthday: date) -> int:
    """生年から十二支インデックスを算出"""
    return (birthday.year - 4) % 12


def _get_junishi(birthday: date) -> str:
    """生年から十二支を取得"""
    return JUNISHI[_get_junishi_index(birthday)]


def _get_relationship(idx_a: int, idx_b: int) -> tuple:
    """二つの十二支の関係を判定 -> (関係名, スコア1-5, 説明)"""
    diff = (idx_b - idx_a) % 12

    # 三合（最高の相性）：4つ離れた干支同士
    sango_groups = [
        {0, 4, 8},   # 子辰申（水局）
        {1, 5, 9},   # 丑巳酉（金局）
        {2, 6, 10},  # 寅午戌（火局）
        {3, 7, 11},  # 卯未亥（木局）
    ]
    for group in sango_groups:
        if idx_a in group and idx_b in group:
            return ("三合", 5, "最高の相性。互いを高め合い、大きな力を生み出す三位一体の関係です。")

    # 六合（良い相性）：特定ペア
    rokugo_pairs = {(0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)}
    pair = (min(idx_a, idx_b), max(idx_a, idx_b))
    if pair in rokugo_pairs:
        return ("六合", 4, "穏やかで安定した良縁。自然体で一緒にいられる心地よい関係です。")

    # 対冲（衝突）：6つ離れた干支
    if diff == 6:
        return ("対冲", 1, "正反対の性質を持つため衝突しやすい関係。しかし、乗り越えれば最も成長できる関係でもあります。")

    # 相破（やや悪い）
    soha_pairs = {(0, 9), (1, 4), (2, 11), (3, 6), (5, 8), (7, 10)}
    if pair in soha_pairs:
        return ("相破", 2, "摩擦が生じやすい関係。お互いの違いを認め合うことが大切です。")

    # 相刑（注意）
    sokei_pairs = {(0, 3), (1, 4), (1, 10), (2, 5), (2, 8), (3, 0), (4, 7), (5, 8), (6, 6), (7, 10), (9, 9)}
    if (idx_a, idx_b) in sokei_pairs or (idx_b, idx_a) in sokei_pairs:
        return ("相刑", 2, "試練を伴う関係ですが、お互いを磨き上げる砥石のような存在です。")

    # 相害
    sogai_pairs = {(0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10)}
    if pair in sogai_pairs:
        return ("相害", 2, "すれ違いが起きやすい関係。コミュニケーションを意識すると改善します。")

    # それ以外は普通
    return ("普通", 3, "特別な吉凶関係はありませんが、穏やかに付き合える相性です。")


def calculate(person_a: dict, person_b: dict) -> dict:
    """干支の相性を計算する"""
    bd_a = person_a['birthday']
    bd_b = person_b['birthday']

    idx_a = _get_junishi_index(bd_a)
    idx_b = _get_junishi_index(bd_b)

    eto_a = JUNISHI[idx_a]
    eto_b = JUNISHI[idx_b]
    animal_a = JUNISHI_ANIMAL[idx_a]
    animal_b = JUNISHI_ANIMAL[idx_b]
    reading_a = JUNISHI_READING[idx_a]
    reading_b = JUNISHI_READING[idx_b]

    relationship, score, description = _get_relationship(idx_a, idx_b)

    score_100 = {1: 20, 2: 40, 3: 60, 4: 80, 5: 95}.get(score, 60)

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    return {
        "name": "干支（十二支）",
        "category": "eto",
        "icon": "pets",
        "score": score,
        "score_100": score_100,
        "summary": f"{eto_a}（{animal_a}）× {eto_b}（{animal_b}）— {relationship}",
        "details": {
            "person_a": {
                "eto": eto_a,
                "reading": reading_a,
                "animal": animal_a,
            },
            "person_b": {
                "eto": eto_b,
                "reading": reading_b,
                "animal": animal_b,
            },
            "compatibility": {
                "relationship": relationship,
                "description": description,
            },
        },
        "highlights": [
            f"{name_a}の干支: {eto_a}年（{reading_a}どし）— {animal_a}",
            f"{name_b}の干支: {eto_b}年（{reading_b}どし）— {animal_b}",
            f"関係性: {relationship}",
        ],
        "advice": description,
    }
