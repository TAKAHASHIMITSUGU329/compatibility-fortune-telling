"""ゴットマンの愛の地図（Love Map）計算エンジン

既存のゴットマン四騎士に追加する形で「愛の地図」理論を実装。
MBTIとエニアグラムから「愛の地図の深さ」と「入札（Bid）への応答傾向」を推定。
"""

CATEGORY = "恋愛心理学"


# MBTI認知機能の主機能マッピング
MBTI_DOMINANT = {
    "INFJ": "Ni", "INTJ": "Ni", "ENFJ": "Fe", "ENTJ": "Te",
    "INFP": "Fi", "INTP": "Ti", "ENFP": "Ne", "ENTP": "Ne",
    "ISFJ": "Si", "ISTJ": "Si", "ESFJ": "Fe", "ESTJ": "Te",
    "ISFP": "Fi", "ISTP": "Ti", "ESFP": "Se", "ESTP": "Se",
}

# 認知機能ごとの「愛の地図の深さ」への寄与
FUNCTION_MAP_DEPTH = {
    "Ni": 85,  # 内的直観: パートナーの内面を深く理解する
    "Si": 80,  # 内的感覚: 過去の詳細を記憶し、パートナーの好みを把握
    "Fi": 78,  # 内的感情: 深い感情的理解
    "Fe": 82,  # 外的感情: パートナーの感情に敏感に反応
    "Ne": 70,  # 外的直観: 可能性は見るが詳細な記憶は弱い
    "Se": 65,  # 外的感覚: 今この瞬間に集中、過去の詳細は薄い
    "Ti": 60,  # 内的思考: 論理に集中、感情面の記憶が弱い
    "Te": 62,  # 外的思考: 効率重視、感情的な詳細を見落としがち
}

# 認知機能ごとの「入札への応答率」
FUNCTION_BID_RESPONSE = {
    "Fe": 90,  # 外的感情: 入札に最も敏感に応答
    "Fi": 75,  # 内的感情: 感情は深いが外に表しにくい
    "Ne": 72,  # 外的直観: 好奇心で応答するが気まぐれ
    "Se": 78,  # 外的感覚: 今の瞬間には応答するが持続性が課題
    "Ni": 68,  # 内的直観: 内面に集中しすぎて入札を見逃すことも
    "Si": 75,  # 内的感覚: 習慣的に応答するが新しい入札に気づきにくい
    "Ti": 55,  # 内的思考: 思考に没頭し入札を見逃しやすい
    "Te": 60,  # 外的思考: 効率を重視し感情的な入札を軽視しがち
}

# エニアグラムタイプごとの「愛の地図の深さ」補正
ENNEAGRAM_MAP_BONUS = {
    1: 5,    # 完璧主義: 理想の関係を目指して努力
    2: 15,   # 助ける人: パートナーへの関心が最も高い
    3: 0,    # 達成する人: 成功に集中、パートナーの内面は後回し
    4: 10,   # 個性的な人: 感情面の地図が非常に豊か
    5: -5,   # 調べる人: 自分の世界に没頭しがち
    6: 12,   # 忠実な人: パートナーへの関心が高い、安全を確認
    7: -3,   # 熱中する人: 新しいことに目が行き、深掘りが苦手
    8: 3,    # 挑戦する人: 保護的だが細やかさに欠ける
    9: 8,    # 平和をもたらす人: 相手に合わせる力があるが自己表現が弱い
}

# エニアグラムタイプごとの「入札応答率」補正
ENNEAGRAM_BID_BONUS = {
    1: 3,
    2: 15,
    3: -2,
    4: 8,
    5: -8,
    6: 10,
    7: 5,
    8: 0,
    9: 7,
}


def _get_mbti(person: dict) -> str:
    mbti = person.get("mbti", "")
    if not mbti:
        return ""
    return mbti.upper().replace("-A", "").replace("-T", "").strip()


def _parse_enneagram_type(person: dict) -> int:
    """エニアグラムタイプを数値で返す（1-9、不明は0）"""
    etype = person.get("enneagram", "")
    if not etype:
        return 0
    if isinstance(etype, int):
        return etype if 1 <= etype <= 9 else 0
    s = str(etype).replace("タイプ", "").strip()
    try:
        n = int(s[0])
        return n if 1 <= n <= 9 else 0
    except (ValueError, IndexError):
        return 0


def _calc_map_depth(mbti: str, enneagram_type: int) -> tuple:
    """愛の地図の深さスコア（0-100）を算出"""
    dominant = MBTI_DOMINANT.get(mbti, "")
    base_score = FUNCTION_MAP_DEPTH.get(dominant, 70)

    bonus = ENNEAGRAM_MAP_BONUS.get(enneagram_type, 0)
    score = max(0, min(100, base_score + bonus))

    # 解説
    if score >= 80:
        desc = "パートナーの内面世界を深く理解し、詳細な愛の地図を持っている"
    elif score >= 65:
        desc = "パートナーへの関心はあるが、意識的に深掘りする必要がある"
    else:
        desc = "自分の世界に集中しがち。パートナーへの質問を増やすことが大切"

    return score, desc


def _calc_bid_response(mbti: str, enneagram_type: int) -> tuple:
    """入札への応答率（0-100%）を算出"""
    dominant = MBTI_DOMINANT.get(mbti, "")
    base_rate = FUNCTION_BID_RESPONSE.get(dominant, 65)

    bonus = ENNEAGRAM_BID_BONUS.get(enneagram_type, 0)
    rate = max(0, min(100, base_rate + bonus))

    # 解説
    if rate >= 80:
        desc = "パートナーの入札（つながりの呼びかけ）に積極的に応答する"
    elif rate >= 65:
        desc = "入札への応答は平均的。意識的に向き合う姿勢が大切"
    else:
        desc = "入札を見逃しやすい。パートナーの呼びかけに気づく練習が必要"

    return rate, desc


def calculate(person_a: dict, person_b: dict) -> dict:
    """ゴットマンの愛の地図の相性を計算する"""
    mbti_a = _get_mbti(person_a)
    mbti_b = _get_mbti(person_b)
    if not mbti_a or not mbti_b:
        return None

    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    etype_a = _parse_enneagram_type(person_a)
    etype_b = _parse_enneagram_type(person_b)

    # 愛の地図の深さ
    map_depth_a, map_desc_a = _calc_map_depth(mbti_a, etype_a)
    map_depth_b, map_desc_b = _calc_map_depth(mbti_b, etype_b)

    # 入札への応答率
    bid_rate_a, bid_desc_a = _calc_bid_response(mbti_a, etype_a)
    bid_rate_b, bid_desc_b = _calc_bid_response(mbti_b, etype_b)

    # 組み合わせスコア
    # 愛の地図: 二人の平均
    combined_map = (map_depth_a + map_depth_b) / 2
    # 入札応答: 二人の平均（低い方がボトルネック）
    combined_bid = (bid_rate_a + bid_rate_b) / 2
    # 入札は低い方の影響が大きい
    bid_min = min(bid_rate_a, bid_rate_b)
    combined_bid_adj = combined_bid * 0.6 + bid_min * 0.4

    # 総合スコア（地図50% + 入札50%）
    score_100 = int(combined_map * 0.5 + combined_bid_adj * 0.5)
    score_100 = max(0, min(100, score_100))

    score = round(score_100 / 20)
    score = max(1, min(5, score))

    # 入札の応答パターン分析
    if bid_rate_a >= 75 and bid_rate_b >= 75:
        bid_pattern = "向き合い型（Turning Toward）: 二人とも入札に積極的に応答"
    elif bid_rate_a >= 75 or bid_rate_b >= 75:
        higher = name_a if bid_rate_a >= bid_rate_b else name_b
        lower = name_b if bid_rate_a >= bid_rate_b else name_a
        bid_pattern = f"{higher}が積極的に応答、{lower}は意識的な努力が必要"
    else:
        bid_pattern = "二人とも入札への応答を意識的に増やすことが大切"

    highlights = [
        f"{name_a}の愛の地図の深さ: {map_depth_a}/100 — {map_desc_a}",
        f"{name_b}の愛の地図の深さ: {map_depth_b}/100 — {map_desc_b}",
        f"{name_a}の入札応答率: {bid_rate_a}% — {bid_desc_a}",
        f"{name_b}の入札応答率: {bid_rate_b}% — {bid_desc_b}",
        f"入札パターン: {bid_pattern}",
    ]

    # アドバイス
    advice_parts = []
    if combined_map < 70:
        advice_parts.append("「愛の地図」を深めるために、パートナーに毎日1つ質問をしてみましょう（好きな食べ物、最近の悩み、将来の夢など）。")
    else:
        advice_parts.append("愛の地図は十分に深い。定期的にアップデートすることで関係を新鮮に保てます。")

    if combined_bid_adj < 70:
        advice_parts.append("入札（つながりの呼びかけ）に気づいたら「向き合う（Turning Toward）」を意識しましょう。ゴットマン博士の研究では、幸福なカップルは入札の86%に応答しています。")
    else:
        advice_parts.append("入札への応答率は良好。この姿勢を維持し、相手の小さなサインも見逃さないようにしましょう。")

    return {
        "name": "愛の地図（ゴットマン理論）",
        "category": "love_map",
        "icon": "map",
        "score": score,
        "score_100": score_100,
        "summary": f"愛の地図: {combined_map:.0f}/100、入札応答: {combined_bid_adj:.0f}%",
        "details": {
            "person_a": {
                "map_depth": map_depth_a,
                "map_description": map_desc_a,
                "bid_response_rate": bid_rate_a,
                "bid_description": bid_desc_a,
                "dominant_function": MBTI_DOMINANT.get(mbti_a, "不明"),
                "enneagram_type": etype_a,
            },
            "person_b": {
                "map_depth": map_depth_b,
                "map_description": map_desc_b,
                "bid_response_rate": bid_rate_b,
                "bid_description": bid_desc_b,
                "dominant_function": MBTI_DOMINANT.get(mbti_b, "不明"),
                "enneagram_type": etype_b,
            },
            "combined": {
                "map_average": combined_map,
                "bid_average": combined_bid,
                "bid_adjusted": combined_bid_adj,
                "bid_pattern": bid_pattern,
            },
        },
        "highlights": highlights,
        "advice": "".join(advice_parts),
    }
