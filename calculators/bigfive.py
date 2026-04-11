"""ビッグファイブ性格特性推定エンジン

MBTIとエニアグラムからビッグファイブの5因子を推定し、
二人の相性を判定する。
"""

CATEGORY = "性格分析"


# エニアグラムタイプ別の神経症的傾向（Neuroticism）ベース値
ENNEAGRAM_NEUROTICISM = {
    1: 55,  # 完璧主義で内的緊張が高め
    2: 45,  # 他者への依存でやや不安定
    3: 40,  # 達成志向で比較的安定
    4: 75,  # 感情の振れ幅が大きい
    5: 50,  # 内向的だが感情的には安定
    6: 70,  # 不安傾向が高い
    7: 25,  # 楽観的で安定
    8: 30,  # 自信があり安定
    9: 35,  # 穏やかで安定
}

# エニアグラムタイプ別のその他因子への補正
ENNEAGRAM_ADJUSTMENTS = {
    1: {'conscientiousness': 10, 'agreeableness': -5},
    2: {'agreeableness': 15, 'extraversion': 5},
    3: {'extraversion': 10, 'conscientiousness': 5},
    4: {'openness': 15, 'agreeableness': -5},
    5: {'openness': 10, 'extraversion': -10},
    6: {'agreeableness': 5, 'conscientiousness': 5},
    7: {'extraversion': 10, 'openness': 10},
    8: {'extraversion': 10, 'agreeableness': -15},
    9: {'agreeableness': 15, 'conscientiousness': -5},
}

# ビッグファイブ因子名（日本語）
FACTOR_NAMES = {
    'extraversion': '外向性',
    'openness': '開放性',
    'agreeableness': '協調性',
    'conscientiousness': '誠実性',
    'neuroticism': '神経症的傾向',
}

# 各因子のスコア解釈
FACTOR_DESCRIPTIONS = {
    'extraversion': {
        'high': '社交的で活発。人との交流からエネルギーを得る',
        'mid': 'バランスの取れた社交性。状況に応じて内向・外向を切り替える',
        'low': '内省的で控えめ。一人の時間を大切にする',
    },
    'openness': {
        'high': '好奇心旺盛で創造的。新しい経験を求める',
        'mid': '伝統と革新のバランスが取れている',
        'low': '実践的で堅実。慣れた方法を好む',
    },
    'agreeableness': {
        'high': '思いやりがあり協力的。他者の感情に敏感',
        'mid': '協調性と自己主張のバランスが取れている',
        'low': '論理的で競争的。自分の意見を大切にする',
    },
    'conscientiousness': {
        'high': '計画的で責任感が強い。目標達成への意志が固い',
        'mid': '柔軟性と計画性のバランスが取れている',
        'low': '柔軟で即興的。自由な発想を好む',
    },
    'neuroticism': {
        'high': '感情の起伏が大きい。繊細で深く考える傾向',
        'mid': '感情のコントロールがまずまず',
        'low': '感情的に安定。ストレスへの耐性が高い',
    },
}


def _parse_enneagram_type(person: dict) -> int:
    """エニアグラムタイプを数値で取得"""
    enneagram = person.get('enneagram', '')
    if isinstance(enneagram, int):
        return enneagram
    if isinstance(enneagram, str):
        # 「タイプ4」「4w5」「Type 4」などから数字を抽出
        import re
        match = re.search(r'(\d)', enneagram)
        if match:
            return int(match.group(1))
    return 5  # デフォルト値


def _estimate_bigfive(person: dict) -> dict:
    """MBTIとエニアグラムからビッグファイブの5因子を推定する

    Returns:
        各因子の0-100スコア
    """
    mbti = person.get('mbti', 'XXXX').upper()

    # MBTIからベース値を設定
    # E/I → 外向性
    extraversion = 80 if mbti[0] == 'E' else 30
    # N/S → 開放性
    openness = 80 if len(mbti) > 1 and mbti[1] == 'N' else 30
    # T/F → 協調性
    agreeableness = 75 if len(mbti) > 2 and mbti[2] == 'F' else 35
    # J/P → 誠実性
    conscientiousness = 75 if len(mbti) > 3 and mbti[3] == 'J' else 35

    # エニアグラムから神経症的傾向
    ennea_type = _parse_enneagram_type(person)
    neuroticism = ENNEAGRAM_NEUROTICISM.get(ennea_type, 50)

    # エニアグラムによるその他因子の補正
    adjustments = ENNEAGRAM_ADJUSTMENTS.get(ennea_type, {})
    extraversion = max(0, min(100, extraversion + adjustments.get('extraversion', 0)))
    openness = max(0, min(100, openness + adjustments.get('openness', 0)))
    agreeableness = max(0, min(100, agreeableness + adjustments.get('agreeableness', 0)))
    conscientiousness = max(0, min(100, conscientiousness + adjustments.get('conscientiousness', 0)))

    return {
        'extraversion': extraversion,
        'openness': openness,
        'agreeableness': agreeableness,
        'conscientiousness': conscientiousness,
        'neuroticism': neuroticism,
    }


def _get_level(score: int) -> str:
    """スコアから高/中/低を判定"""
    if score >= 65:
        return 'high'
    elif score >= 40:
        return 'mid'
    else:
        return 'low'


def _calc_similarity(scores_a: dict, scores_b: dict) -> float:
    """二人の5因子の類似度を計算（0-100）

    各因子の差の絶対値の平均を100から引く
    """
    diffs = []
    for factor in ['extraversion', 'openness', 'agreeableness', 'conscientiousness', 'neuroticism']:
        diff = abs(scores_a[factor] - scores_b[factor])
        diffs.append(diff)
    avg_diff = sum(diffs) / len(diffs)
    return max(0, min(100, 100 - avg_diff))


def _calc_complementarity(scores_a: dict, scores_b: dict) -> float:
    """二人の5因子の補完度を計算（0-100）

    神経症的傾向は低い方が良い（片方が高くても片方が安定していれば補完的）。
    外向性は適度な差がプラス。
    """
    comp_scores = []

    # 外向性: 適度な差（20-40）が補完的
    e_diff = abs(scores_a['extraversion'] - scores_b['extraversion'])
    if 15 <= e_diff <= 45:
        comp_scores.append(80)
    elif e_diff < 15:
        comp_scores.append(65)
    else:
        comp_scores.append(50)

    # 開放性: 似ている方が良い
    o_diff = abs(scores_a['openness'] - scores_b['openness'])
    comp_scores.append(max(40, 100 - o_diff * 1.2))

    # 協調性: 少なくとも片方が高いと良い
    a_max = max(scores_a['agreeableness'], scores_b['agreeableness'])
    comp_scores.append(min(100, a_max + 10))

    # 誠実性: 似ている方が良い
    c_diff = abs(scores_a['conscientiousness'] - scores_b['conscientiousness'])
    comp_scores.append(max(40, 100 - c_diff * 1.0))

    # 神経症的傾向: 片方が安定していると補完的
    n_min = min(scores_a['neuroticism'], scores_b['neuroticism'])
    n_avg = (scores_a['neuroticism'] + scores_b['neuroticism']) / 2
    if n_avg <= 40:
        comp_scores.append(85)
    elif n_min <= 35:
        comp_scores.append(75)
    else:
        comp_scores.append(max(40, 90 - n_avg))

    return sum(comp_scores) / len(comp_scores)


def calculate(person_a: dict, person_b: dict) -> dict:
    """ビッグファイブ推定による相性を計算する"""
    mbti_a = person_a.get('mbti')
    mbti_b = person_b.get('mbti')
    if not mbti_a or not mbti_b:
        return None

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    # ビッグファイブ推定
    scores_a = _estimate_bigfive(person_a)
    scores_b = _estimate_bigfive(person_b)

    # 類似度と補完度
    similarity = _calc_similarity(scores_a, scores_b)
    complementarity = _calc_complementarity(scores_a, scores_b)

    # 総合スコア（類似度50%、補完度50%）
    score_100 = round(similarity * 0.5 + complementarity * 0.5)
    score_100 = max(0, min(100, score_100))
    score = round(score_100 / 20)
    score = max(1, min(5, score))

    # ハイライト生成
    highlights = []
    factors = ['extraversion', 'openness', 'agreeableness', 'conscientiousness', 'neuroticism']
    for factor in factors:
        val_a = scores_a[factor]
        val_b = scores_b[factor]
        fname = FACTOR_NAMES[factor]
        level_a = _get_level(val_a)
        level_b = _get_level(val_b)
        desc_a = FACTOR_DESCRIPTIONS[factor][level_a]
        desc_b = FACTOR_DESCRIPTIONS[factor][level_b]
        diff = abs(val_a - val_b)
        if diff <= 15:
            relation = "（近い値 → 共感しやすい）"
        elif diff >= 40:
            relation = "（差が大きい → 補完的だが摩擦も）"
        else:
            relation = "（適度な差 → バランスが良い）"
        highlights.append(f"{fname}: {name_a}={val_a} / {name_b}={val_b} {relation}")

    highlights.append(f"類似度: {similarity:.0f}点 / 補完度: {complementarity:.0f}点")

    # アドバイス生成
    advice_parts = []

    # 最も差がある因子と最も近い因子を特定
    diffs = {f: abs(scores_a[f] - scores_b[f]) for f in factors}
    max_diff_factor = max(diffs, key=diffs.get)
    min_diff_factor = min(diffs, key=diffs.get)

    advice_parts.append(
        f"{FACTOR_NAMES[min_diff_factor]}が最も近く、この点で深い共感が生まれます。"
    )
    advice_parts.append(
        f"{FACTOR_NAMES[max_diff_factor]}に最も差があり、互いの違いを理解し尊重することが大切です。"
    )

    if scores_a['neuroticism'] > 60 and scores_b['neuroticism'] > 60:
        advice_parts.append("二人とも感受性が高いため、感情の波を穏やかに受け止める姿勢が重要です。")
    elif scores_a['neuroticism'] < 40 and scores_b['neuroticism'] < 40:
        advice_parts.append("二人とも感情的に安定しており、穏やかな関係を築きやすいでしょう。")

    return {
        "name": "ビッグファイブ性格分析",
        "category": "bigfive",
        "icon": "psychology",
        "score": score,
        "score_100": score_100,
        "summary": f"性格5因子の類似度{similarity:.0f}点・補完度{complementarity:.0f}点",
        "details": {
            "person_a": {
                "mbti": mbti_a,
                "enneagram": person_a.get('enneagram', ''),
                "scores": scores_a,
                "levels": {f: _get_level(scores_a[f]) for f in factors},
            },
            "person_b": {
                "mbti": mbti_b,
                "enneagram": person_b.get('enneagram', ''),
                "scores": scores_b,
                "levels": {f: _get_level(scores_b[f]) for f in factors},
            },
            "compatibility": {
                "similarity": round(similarity, 1),
                "complementarity": round(complementarity, 1),
                "factor_diffs": {FACTOR_NAMES[f]: diffs[f] for f in factors},
            },
        },
        "highlights": highlights,
        "advice": "".join(advice_parts),
    }
