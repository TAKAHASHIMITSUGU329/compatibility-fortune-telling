"""インド占星術（ジョーティシュ）簡易版 計算エンジン

サイデリアル方式。ナクシャトラ（月の27宿）で相性判定。
"""

from datetime import date

CATEGORY = "西洋占星術"

# 西洋占星術の12星座（トロピカル）
TROPICAL_SIGNS = [
    "牡羊座", "牡牛座", "双子座", "蟹座", "獅子座", "乙女座",
    "天秤座", "蠍座", "射手座", "山羊座", "水瓶座", "魚座",
]

# サイデリアル12星座（約23.5度ずれるため概算で1つ前にずらす）
SIDEREAL_SIGNS = [
    "メーシャ（牡羊）", "ヴリシャバ（牡牛）", "ミトゥナ（双子）",
    "カルカ（蟹）", "シンハ（獅子）", "カンニャ（乙女）",
    "トゥラー（天秤）", "ヴリシュチカ（蠍）", "ダヌス（射手）",
    "マカラ（山羊）", "クンバ（水瓶）", "ミーナ（魚）",
]

# 太陽星座の期間（概算）
SIGN_DATES = [
    (3, 21), (4, 20), (5, 21), (6, 21), (7, 23), (8, 23),
    (9, 23), (10, 23), (11, 22), (12, 22), (1, 20), (2, 19),
]

# 27ナクシャトラ
NAKSHATRAS = [
    "アシュヴィニー", "バラニー", "クリッティカー",
    "ローヒニー", "ムリガシラー", "アールドラー",
    "プナルヴァス", "プシュヤ", "アーシュレーシャー",
    "マガー", "プールヴァ・ファールグニー", "ウッタラ・ファールグニー",
    "ハスタ", "チトラー", "スヴァーティー",
    "ヴィシャーカー", "アヌラーダー", "ジェーシュター",
    "ムーラ", "プールヴァ・アシャーダー", "ウッタラ・アシャーダー",
    "シュラヴァナ", "ダニシュター", "シャタビシャー",
    "プールヴァ・バードラパダー", "ウッタラ・バードラパダー", "レーヴァティー",
]

# ナクシャトラの特徴（簡易版）
NAKSHATRA_TRAITS = {
    "アシュヴィニー": "治癒と新たな始まり。素早い行動力と癒しの力",
    "バラニー": "創造と変容。強い意志と生命力",
    "クリッティカー": "浄化と鋭さ。切れ味鋭い知性",
    "ローヒニー": "豊穣と美。魅力的で芸術的センスに優れる",
    "ムリガシラー": "探求と好奇心。知的好奇心が旺盛",
    "アールドラー": "嵐と変革。激しい感情と変革の力",
    "プナルヴァス": "再生と帰還。寛容で包容力がある",
    "プシュヤ": "滋養と保護。最も吉祥なナクシャトラ",
    "アーシュレーシャー": "蛇の力。深い洞察力と神秘性",
    "マガー": "王権と威厳。リーダーシップに優れる",
    "プールヴァ・ファールグニー": "享楽と創造。芸術と恋愛の星",
    "ウッタラ・ファールグニー": "友情と助け合い。温かく協力的",
    "ハスタ": "器用さと技術。手先が器用で実用的",
    "チトラー": "輝きと美。芸術的で華やかな星",
    "スヴァーティー": "独立と自由。独立心と適応力がある",
    "ヴィシャーカー": "目的と決意。目標に向かって突き進む力",
    "アヌラーダー": "友愛と献身。深い愛情と忠誠心",
    "ジェーシュター": "長老と保護。守る力と知恵がある",
    "ムーラ": "根源と破壊。根本を見極める力",
    "プールヴァ・アシャーダー": "不敗の力。勝利と繁栄をもたらす",
    "ウッタラ・アシャーダー": "普遍的な勝利。リーダーシップと正義",
    "シュラヴァナ": "聞く力。学びと知識を重視する",
    "ダニシュター": "富と音楽。リズム感と社交性に優れる",
    "シャタビシャー": "千の治療師。癒しと秘密の知識",
    "プールヴァ・バードラパダー": "灼熱の力。二面性と変容の力",
    "ウッタラ・バードラパダー": "深みの戦士。忍耐力と精神的深さ",
    "レーヴァティー": "豊穣と旅。旅と冒険を愛する守護の星",
}

# ヴァルナ（4段階の精神性）
VARNA_LEVELS = ["シュードラ", "ヴァイシャ", "クシャトリヤ", "ブラーフマナ"]

# ナクシャトラのヴァルナ分類
NAKSHATRA_VARNA = {}
for i, n in enumerate(NAKSHATRAS):
    NAKSHATRA_VARNA[n] = VARNA_LEVELS[i % 4]

# ヴァルナ相性スコア
VARNA_COMPAT = {
    ("ブラーフマナ", "ブラーフマナ"): (5, "精神性が最も高い同士。深い理解で結ばれる"),
    ("ブラーフマナ", "クシャトリヤ"): (4, "精神性と行動力の良い組み合わせ"),
    ("ブラーフマナ", "ヴァイシャ"): (3, "知恵と実務のバランス"),
    ("ブラーフマナ", "シュードラ"): (3, "精神と現実を補い合う"),
    ("クシャトリヤ", "クシャトリヤ"): (4, "行動力のある者同士。力強いパートナーシップ"),
    ("クシャトリヤ", "ヴァイシャ"): (4, "行動と実務が噛み合う実践的な関係"),
    ("クシャトリヤ", "シュードラ"): (3, "守る者と支える者の関係"),
    ("ヴァイシャ", "ヴァイシャ"): (4, "実務能力が高い者同士。安定した生活基盤"),
    ("ヴァイシャ", "シュードラ"): (3, "堅実で地に足のついた関係"),
    ("シュードラ", "シュードラ"): (3, "素朴で温かい関係。共に歩む力"),
}


def _get_tropical_sign_index(birthday: date) -> int:
    """生年月日からトロピカル太陽星座のインデックスを返す"""
    m = birthday.month
    d = birthday.day
    for i in range(12):
        start_m, start_d = SIGN_DATES[i]
        next_m, next_d = SIGN_DATES[(i + 1) % 12]

        if start_m <= next_m:
            if (m == start_m and d >= start_d) or (m > start_m and m < next_m) or (m == next_m and d < next_d):
                return i
        else:
            if (m == start_m and d >= start_d) or (m > start_m) or (m < next_m) or (m == next_m and d < next_d):
                return i
    return 0


def _get_sidereal_sign_index(tropical_index: int) -> int:
    """トロピカルからサイデリアル星座インデックスへ（概算: 1つ前にずらす）"""
    return (tropical_index - 1) % 12


def _estimate_nakshatra(birthday: date) -> int:
    """生年月日からナクシャトラを概算する

    月の正確な位置は出生時刻が必要なため、
    誕生日ベースの概算を使用。
    年月日の数値からナクシャトラを割り当てる。
    """
    # 誕生日から概算: 月の軌道周期（約27.3日）をベースに
    day_of_year = birthday.timetuple().tm_yday
    year_factor = birthday.year % 19  # メトン周期（19年で月の位相が一巡）
    # 月の位置の概算
    moon_position = (day_of_year * 27 + year_factor * 14) % 27
    return moon_position


def _calc_tara_score(nakshatra_a: int, nakshatra_b: int) -> tuple:
    """タラ（運命的相性）を算出

    二人のナクシャトラ間の距離から9つのタラカテゴリーに分類。
    """
    distance = (nakshatra_b - nakshatra_a) % 27
    tara_index = distance % 9

    tara_names = [
        ("ジャンマ（誕生）", 3, "運命的な出会い。深い縁がある"),
        ("サンパト（繁栄）", 5, "繁栄をもたらす最高の相性"),
        ("ヴィパト（障害）", 2, "試練があるが成長をもたらす"),
        ("クシェマ（安全）", 4, "安心感と安定をもたらす相性"),
        ("プラティヤリ（障壁）", 2, "障壁があるが乗り越える力がある"),
        ("サーダカ（成就）", 5, "願いが叶う吉祥な相性"),
        ("ヴァダ（殺害）", 1, "注意が必要。意識的な努力で改善できる"),
        ("マイトラ（友情）", 4, "深い友情と信頼で結ばれる"),
        ("アティマイトラ（最高の友）", 5, "最高の友情。魂の伴侶"),
    ]

    name, score, desc = tara_names[tara_index]
    return name, score, desc


def _get_varna_compat(varna_a: str, varna_b: str) -> tuple:
    """ヴァルナ相性を取得"""
    key = (varna_a, varna_b)
    rev_key = (varna_b, varna_a)
    return VARNA_COMPAT.get(key) or VARNA_COMPAT.get(rev_key, (3, "互いの精神性を理解し合える"))


def calculate(person_a: dict, person_b: dict) -> dict:
    """インド占星術（簡易版）の相性を計算する"""
    bd_a = person_a.get("birthday")
    bd_b = person_b.get("birthday")
    if not bd_a or not bd_b:
        return None

    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    # トロピカル → サイデリアル太陽星座
    tropical_a = _get_tropical_sign_index(bd_a)
    tropical_b = _get_tropical_sign_index(bd_b)
    sidereal_a = _get_sidereal_sign_index(tropical_a)
    sidereal_b = _get_sidereal_sign_index(tropical_b)

    sidereal_name_a = SIDEREAL_SIGNS[sidereal_a]
    sidereal_name_b = SIDEREAL_SIGNS[sidereal_b]

    # ナクシャトラの概算
    nakshatra_idx_a = _estimate_nakshatra(bd_a)
    nakshatra_idx_b = _estimate_nakshatra(bd_b)

    nakshatra_a = NAKSHATRAS[nakshatra_idx_a]
    nakshatra_b = NAKSHATRAS[nakshatra_idx_b]

    trait_a = NAKSHATRA_TRAITS.get(nakshatra_a, "")
    trait_b = NAKSHATRA_TRAITS.get(nakshatra_b, "")

    # ヴァルナ
    varna_a = NAKSHATRA_VARNA[nakshatra_a]
    varna_b = NAKSHATRA_VARNA[nakshatra_b]
    varna_score, varna_desc = _get_varna_compat(varna_a, varna_b)

    # タラ（運命的相性）
    tara_name, tara_score, tara_desc = _calc_tara_score(nakshatra_idx_a, nakshatra_idx_b)

    # 総合スコア（タラ60% + ヴァルナ40%）
    score_100 = int((tara_score * 20) * 0.6 + (varna_score * 20) * 0.4)
    score_100 = max(0, min(100, score_100))

    score = round(score_100 / 20)
    score = max(1, min(5, score))

    highlights = [
        f"{name_a}: サイデリアル太陽={sidereal_name_a}、ナクシャトラ={nakshatra_a}",
        f"{name_b}: サイデリアル太陽={sidereal_name_b}、ナクシャトラ={nakshatra_b}",
        f"{name_a}のナクシャトラ: {nakshatra_a} — {trait_a}",
        f"{name_b}のナクシャトラ: {nakshatra_b} — {trait_b}",
        f"ヴァルナ: {varna_a} × {varna_b} — {varna_desc}",
        f"タラ: {tara_name} — {tara_desc}",
    ]

    advice = f"タラは「{tara_name}」で{tara_desc}。ヴァルナの観点では{varna_desc}。"
    if tara_score >= 4:
        advice += "インド占星術的に非常に良い相性です。"
    elif tara_score <= 2:
        advice += "意識的なコミュニケーションと相互理解で関係を深めましょう。"

    return {
        "name": "インド占星術",
        "category": "jyotish",
        "icon": "self_improvement",
        "score": score,
        "score_100": score_100,
        "summary": f"ナクシャトラ {nakshatra_a} × {nakshatra_b}（タラ: {tara_name}）",
        "details": {
            "person_a": {
                "tropical_sign": TROPICAL_SIGNS[tropical_a],
                "sidereal_sign": sidereal_name_a,
                "nakshatra": nakshatra_a,
                "nakshatra_trait": trait_a,
                "varna": varna_a,
            },
            "person_b": {
                "tropical_sign": TROPICAL_SIGNS[tropical_b],
                "sidereal_sign": sidereal_name_b,
                "nakshatra": nakshatra_b,
                "nakshatra_trait": trait_b,
                "varna": varna_b,
            },
            "tara": {
                "name": tara_name,
                "score": tara_score,
                "description": tara_desc,
            },
            "varna_compat": {
                "score": varna_score,
                "description": varna_desc,
            },
        },
        "highlights": highlights,
        "advice": advice,
    }
