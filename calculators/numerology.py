"""数秘術（ライフパス数・誕生日数・チャレンジ数）計算エンジン"""

from datetime import date

CATEGORY = "数秘・タロット"

MASTER_NUMBERS = {11, 22, 33}


def _reduce_to_single(n: int) -> int:
    """数字を一桁に縮約する（マスターナンバーは保持）"""
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
    return n


def _life_path_number(birthday: date) -> int:
    """ライフパス数を算出：年・月・日をそれぞれ縮約してから合算・縮約"""
    y = _reduce_to_single(sum(int(d) for d in str(birthday.year)))
    m = _reduce_to_single(birthday.month)
    d = _reduce_to_single(birthday.day)
    total = y + m + d
    return _reduce_to_single(total)


def _birthday_number(birthday: date) -> int:
    """誕生日数：日の数字を一桁に縮約"""
    return _reduce_to_single(birthday.day)


def _challenge_number(birthday: date) -> int:
    """チャレンジ数：月と日のライフパス的差分の絶対値"""
    m = _reduce_to_single(birthday.month)
    d = _reduce_to_single(birthday.day)
    return abs(m - d)


# ライフパス数同士の相性テーブル（スコア1-5）
LIFE_PATH_COMPATIBILITY = {
    (1, 1): 3, (1, 2): 4, (1, 3): 5, (1, 4): 3, (1, 5): 5,
    (1, 6): 3, (1, 7): 4, (1, 8): 4, (1, 9): 3,
    (2, 2): 3, (2, 3): 4, (2, 4): 5, (2, 5): 3, (2, 6): 5,
    (2, 7): 3, (2, 8): 4, (2, 9): 4,
    (3, 3): 3, (3, 4): 2, (3, 5): 5, (3, 6): 4, (3, 7): 3,
    (3, 8): 3, (3, 9): 5,
    (4, 4): 3, (4, 5): 2, (4, 6): 4, (4, 7): 4, (4, 8): 5,
    (4, 9): 3,
    (5, 5): 3, (5, 6): 2, (5, 7): 4, (5, 8): 3, (5, 9): 5,
    (6, 6): 3, (6, 7): 2, (6, 8): 3, (6, 9): 5,
    (7, 7): 3, (7, 8): 2, (7, 9): 4,
    (8, 8): 3, (8, 9): 3,
    (9, 9): 3,
}

# マスターナンバーの相性補正
MASTER_COMPATIBILITY = {
    (11, 11): 4, (11, 22): 5, (11, 33): 5,
    (22, 22): 4, (22, 33): 5,
    (33, 33): 4,
}

LIFE_PATH_DESCRIPTIONS = {
    1: "リーダーシップと独立心の数。自分の道を切り開く力を持つ",
    2: "調和と協力の数。人間関係を円滑にする才能がある",
    3: "創造性と表現力の数。芸術的センスと社交性に優れる",
    4: "安定と堅実さの数。地道な努力で確実に成果を上げる",
    5: "自由と変化の数。冒険心と適応力に優れる",
    6: "愛情と責任の数。家庭や人間関係を大切にする",
    7: "知性と探究心の数。深い思考と直感力を持つ",
    8: "達成と権力の数。ビジネスセンスと実行力がある",
    9: "博愛と完成の数。人類愛と精神的な成熟を示す",
    11: "直感と霊性のマスターナンバー。高い感受性と洞察力を持つ",
    22: "建設者のマスターナンバー。壮大なビジョンを現実にする力がある",
    33: "奉仕と癒しのマスターナンバー。他者を癒し導く使命を持つ",
}


def _get_compatibility_score(lp_a: int, lp_b: int) -> int:
    """ライフパス数のペアから相性スコアを取得"""
    # マスターナンバー同士
    if lp_a in MASTER_NUMBERS and lp_b in MASTER_NUMBERS:
        key = (min(lp_a, lp_b), max(lp_a, lp_b))
        return MASTER_COMPATIBILITY.get(key, 4)

    # マスターナンバーと通常数
    a = lp_a if lp_a not in MASTER_NUMBERS else _reduce_to_single(lp_a)
    b = lp_b if lp_b not in MASTER_NUMBERS else _reduce_to_single(lp_b)

    key = (min(a, b), max(a, b))
    base = LIFE_PATH_COMPATIBILITY.get(key, 3)

    # マスターナンバーがある場合はボーナス
    if lp_a in MASTER_NUMBERS or lp_b in MASTER_NUMBERS:
        base = min(base + 1, 5)

    return base


def _score_to_100(score: int) -> int:
    """1-5スコアを0-100スコアに変換"""
    return {1: 20, 2: 40, 3: 60, 4: 80, 5: 95}.get(score, 60)


def calculate(person_a: dict, person_b: dict) -> dict:
    """数秘術の相性を計算する"""
    bd_a = person_a['birthday']
    bd_b = person_b['birthday']

    lp_a = _life_path_number(bd_a)
    lp_b = _life_path_number(bd_b)
    bn_a = _birthday_number(bd_a)
    bn_b = _birthday_number(bd_b)
    ch_a = _challenge_number(bd_a)
    ch_b = _challenge_number(bd_b)

    # ライフパス数の相性
    lp_score = _get_compatibility_score(lp_a, lp_b)

    # 誕生日数の相性
    bn_score = _get_compatibility_score(bn_a, bn_b)

    # 総合スコア（ライフパス数を主軸に、100点ベースで計算）
    lp_100 = _score_to_100(lp_score)
    bn_100 = _score_to_100(bn_score)
    # ライフパス数が最高相性（5）の場合は、ほぼそのまま（最強ペアを正しく反映）
    if lp_score >= 5:
        score_100 = lp_100
    else:
        score_100 = round(lp_100 * 0.75 + bn_100 * 0.25)
    score_100 = max(0, min(100, score_100))
    score = round(score_100 / 20)
    score = max(1, min(5, score))

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    highlights = [
        f"{name_a}のライフパス数: {lp_a} — {LIFE_PATH_DESCRIPTIONS.get(lp_a, '')}",
        f"{name_b}のライフパス数: {lp_b} — {LIFE_PATH_DESCRIPTIONS.get(lp_b, '')}",
        f"誕生日数の相性: {'★' * bn_score}",
    ]

    if lp_a in MASTER_NUMBERS:
        highlights.append(f"{name_a}はマスターナンバー{lp_a}の持ち主です")
    if lp_b in MASTER_NUMBERS:
        highlights.append(f"{name_b}はマスターナンバー{lp_b}の持ち主です")

    advice_map = {
        5: "数秘術的に最高の相性です。お互いの人生の目的が調和しています。",
        4: "数秘術的にとても良い相性です。互いの強みを活かし合える関係です。",
        3: "数秘術的に平均的な相性です。お互いを理解する努力が実を結びます。",
        2: "数秘術的にはやや課題のある相性ですが、違いが成長の糧になります。",
        1: "数秘術的には挑戦的な相性ですが、乗り越えることで深い絆が生まれます。",
    }

    return {
        "name": "数秘術",
        "category": "numerology",
        "icon": "calculate",
        "score": score,
        "score_100": score_100,
        "summary": f"ライフパス数 {lp_a} × {lp_b} の相性",
        "details": {
            "person_a": {
                "life_path": lp_a,
                "birthday_number": bn_a,
                "challenge_number": ch_a,
                "description": LIFE_PATH_DESCRIPTIONS.get(lp_a, ""),
            },
            "person_b": {
                "life_path": lp_b,
                "birthday_number": bn_b,
                "challenge_number": ch_b,
                "description": LIFE_PATH_DESCRIPTIONS.get(lp_b, ""),
            },
            "compatibility": {
                "life_path_score": lp_score,
                "birthday_number_score": bn_score,
            },
        },
        "highlights": highlights,
        "advice": advice_map.get(score, ""),
    }
