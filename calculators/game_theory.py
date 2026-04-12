"""ゲーム理論的関係分析エンジン
囚人のジレンマ・しっぺ返し戦略・ナッシュ均衡の観点から二人の関係を分析。
"""

CATEGORY = "恋愛心理学"

# MBTI → 協力傾向スコア（1-5、高いほど協力的）
MBTI_COOPERATION = {
    "INFJ": 5, "ISFJ": 5, "ENFJ": 5, "ESFJ": 4,
    "INFP": 4, "ISFP": 4, "ENFP": 4, "ESFP": 3,
    "INTJ": 3, "ISTJ": 4, "ENTJ": 3, "ESTJ": 3,
    "INTP": 3, "ISTP": 2, "ENTP": 3, "ESTP": 2,
}

# MBTI → 報復傾向（裏切りへの反応の強さ 1-5）
MBTI_RETALIATION = {
    "INFJ": 4, "ISFJ": 4, "ENFJ": 3, "ESFJ": 3,
    "INFP": 3, "ISFP": 3, "ENFP": 2, "ESFP": 2,
    "INTJ": 5, "ISTJ": 5, "ENTJ": 4, "ESTJ": 4,
    "INTP": 4, "ISTP": 4, "ENTP": 3, "ESTP": 3,
}

# MBTI → 許容度（裏切り後に再び信頼するまでの速さ 1-5、高いほど早い）
MBTI_FORGIVENESS = {
    "INFJ": 2, "ISFJ": 2, "ENFJ": 4, "ESFJ": 3,
    "INFP": 3, "ISFP": 3, "ENFP": 4, "ESFP": 4,
    "INTJ": 1, "ISTJ": 2, "ENTJ": 2, "ESTJ": 2,
    "INTP": 3, "ISTP": 3, "ENTP": 4, "ESTP": 4,
}


def calculate(person_a: dict, person_b: dict) -> dict:
    """ゲーム理論的な関係分析"""
    mbti_a = (person_a.get('mbti') or '').upper().replace("-A", "").replace("-T", "").strip()
    mbti_b = (person_b.get('mbti') or '').upper().replace("-A", "").replace("-T", "").strip()
    if not mbti_a or not mbti_b:
        return None

    coop_a = MBTI_COOPERATION.get(mbti_a, 3)
    coop_b = MBTI_COOPERATION.get(mbti_b, 3)
    ret_a = MBTI_RETALIATION.get(mbti_a, 3)
    ret_b = MBTI_RETALIATION.get(mbti_b, 3)
    forg_a = MBTI_FORGIVENESS.get(mbti_a, 3)
    forg_b = MBTI_FORGIVENESS.get(mbti_b, 3)

    # 双方の協力度が高い＝安定したナッシュ均衡
    coop_avg = (coop_a + coop_b) / 2
    # 報復と許容のバランス
    balance = ((5 - abs(ret_a - forg_b)) + (5 - abs(ret_b - forg_a))) / 2

    total = coop_avg * 0.5 + balance * 0.5

    if total >= 4.0:
        score, score_100 = 5, 90
        strategy = "誠実さの継続がナッシュ均衡。駆け引き不要の理想的な関係"
    elif total >= 3.5:
        score, score_100 = 4, 82
        strategy = "基本的に協力的。小さな誤解への対処力がある"
    elif total >= 3.0:
        score, score_100 = 3, 72
        strategy = "協力可能だが、信頼の構築に意識的な努力が必要"
    elif total >= 2.5:
        score, score_100 = 3, 65
        strategy = "駆け引きに陥りやすい。オープンなコミュニケーションが鍵"
    else:
        score, score_100 = 2, 55
        strategy = "信頼の構築に時間がかかる。小さな約束から積み上げる"

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    # ISFJの特性を特別に注記
    isfj_note = []
    if mbti_b == "ISFJ" or mbti_a == "ISFJ":
        isfj_note = ["ISFJのSi主機能は過去の行動をすべて記録する。一度の不誠実が長期間影響する"]

    return {
        "name": "ゲーム理論",
        "category": "game_theory",
        "icon": "strategy",
        "score": score,
        "score_100": score_100,
        "summary": strategy,
        "details": {
            "person_a": {"cooperation": coop_a, "retaliation": ret_a, "forgiveness": forg_a},
            "person_b": {"cooperation": coop_b, "retaliation": ret_b, "forgiveness": forg_b},
        },
        "highlights": [
            f"{name_a}: 協力度{coop_a} / 報復傾向{ret_a} / 許容度{forg_a}",
            f"{name_b}: 協力度{coop_b} / 報復傾向{ret_b} / 許容度{forg_b}",
        ] + isfj_note,
        "advice": f"ゲーム理論の囚人のジレンマモデルに基づく分析結果です。{strategy}。ナッシュ均衡の観点では、互いに協力を選び続ける「しっぺ返し戦略」が長期的に最も高い利得をもたらします。信頼の積み重ねと適度な許容が、二人の協力関係を安定させる鍵です。",
    }
