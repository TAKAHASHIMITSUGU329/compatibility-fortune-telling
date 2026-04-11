"""マヤ暦（ツォルキン）計算エンジン
Kin番号・太陽の紋章・銀河の音から相性を分析する。
"""

from datetime import date

CATEGORY = "その他占い"

# Dreamspellの相関: 2012/12/21 = Kin 207（グレゴリオ暦からツォルキン変換の基準点）
REFERENCE_DATE = date(2012, 12, 21)
REFERENCE_KIN = 207

# 20の太陽の紋章（Solar Seal）
SOLAR_SEALS = {
    0: ("黄色い太陽", "Yellow Sun", "生命・啓発・普遍的な火"),
    1: ("赤い竜", "Red Dragon", "誕生・養育・存在"),
    2: ("白い風", "White Wind", "精神・伝達・呼吸"),
    3: ("青い夜", "Blue Night", "豊かさ・直感・夢"),
    4: ("黄色い種", "Yellow Seed", "気づき・開花・目標"),
    5: ("赤い蛇", "Red Serpent", "生命力・本能・情熱"),
    6: ("白い世界の橋渡し", "White Worldbridger", "死と再生・等しさ・機会"),
    7: ("青い手", "Blue Hand", "遂行・癒し・知る"),
    8: ("黄色い星", "Yellow Star", "芸術・優美・調和"),
    9: ("赤い月", "Red Moon", "浄化・流れ・普遍的な水"),
    10: ("白い犬", "White Dog", "愛・忠実・ハート"),
    11: ("青い猿", "Blue Monkey", "魔術・遊び・幻想"),
    12: ("黄色い人", "Yellow Human", "自由意志・知恵・影響"),
    13: ("赤い空歩く人", "Red Skywalker", "空間・探究・覚醒"),
    14: ("白い魔法使い", "White Wizard", "永遠・魅了・受容"),
    15: ("青い鷲", "Blue Eagle", "創造・ビジョン・心"),
    16: ("黄色い戦士", "Yellow Warrior", "知性・問い・大胆"),
    17: ("赤い地球", "Red Earth", "共時性・進化・案内"),
    18: ("白い鏡", "White Mirror", "果てしなさ・秩序・瞑想"),
    19: ("青い嵐", "Blue Storm", "自己発生・変容・力"),
}

# 13の銀河の音（Galactic Tone）
GALACTIC_TONES = {
    1: ("磁気の", "目的を一つにする"),
    2: ("月の", "挑戦を安定させる"),
    3: ("電気の", "奉仕を活性化する"),
    4: ("自己存在の", "形を定義する"),
    5: ("倍音の", "力を与える"),
    6: ("律動の", "平等を組織する"),
    7: ("共振の", "調律を導く"),
    8: ("銀河の", "調和を完全にする"),
    9: ("太陽の", "意図を脈動させる"),
    10: ("惑星の", "現れを仕上げる"),
    11: ("スペクトルの", "解放を溶かす"),
    12: ("水晶の", "協力を捧げる"),
    13: ("宇宙の", "存在を超越する"),
}

# 紋章の色
SEAL_COLORS = {0: "黄", 1: "赤", 2: "白", 3: "青", 4: "黄",
               5: "赤", 6: "白", 7: "青", 8: "黄", 9: "赤",
               10: "白", 11: "青", 12: "黄", 13: "赤", 14: "白",
               15: "青", 16: "黄", 17: "赤", 18: "白", 19: "青"}


def _calc_kin(birthday: date) -> int:
    """生年月日からKin番号を算出（Dreamspell）"""
    delta = (birthday - REFERENCE_DATE).days
    kin = (REFERENCE_KIN + delta - 1) % 260 + 1
    return kin


def _get_seal(kin: int) -> int:
    """Kin番号から太陽の紋章インデックス（0-19）を取得"""
    return (kin - 1) % 20


def _get_tone(kin: int) -> int:
    """Kin番号から銀河の音（1-13）を取得"""
    return (kin - 1) % 13 + 1


def _get_wavespell_seal(kin: int) -> int:
    """Kin番号からウェーブスペルの紋章インデックスを取得"""
    ws_start = ((kin - 1) // 13) * 13 + 1
    return _get_seal(ws_start)


def calculate(person_a: dict, person_b: dict) -> dict:
    """マヤ暦の相性を計算する"""
    bd_a = person_a.get('birthday')
    bd_b = person_b.get('birthday')
    if not bd_a or not bd_b:
        return None

    kin_a = _calc_kin(bd_a)
    kin_b = _calc_kin(bd_b)

    seal_a = _get_seal(kin_a)
    seal_b = _get_seal(kin_b)
    tone_a = _get_tone(kin_a)
    tone_b = _get_tone(kin_b)
    ws_a = _get_wavespell_seal(kin_a)
    ws_b = _get_wavespell_seal(kin_b)

    seal_name_a, _, seal_desc_a = SOLAR_SEALS[seal_a]
    seal_name_b, _, seal_desc_b = SOLAR_SEALS[seal_b]
    tone_name_a, tone_desc_a = GALACTIC_TONES[tone_a]
    tone_name_b, tone_desc_b = GALACTIC_TONES[tone_b]
    ws_name_a = SOLAR_SEALS[ws_a][0]
    ws_name_b = SOLAR_SEALS[ws_b][0]

    # 関係性の判定
    kin_diff = abs(kin_a - kin_b)
    seal_sum = seal_a + seal_b
    seal_diff = abs(seal_a - seal_b)
    same_ws = ws_a == ws_b

    relationship = ""
    if seal_a == seal_b:
        score, score_100 = 5, 95
        relationship = "同じ紋章（鏡の関係）"
    elif seal_diff == 10:
        score, score_100 = 4, 88
        relationship = "反対キン（正反対の補完関係）"
    elif (seal_sum % 20) == 19 or (seal_sum % 20) == 0:
        score, score_100 = 5, 92
        relationship = "神秘キン（魂が惹かれ合う関係）"
    elif same_ws:
        score, score_100 = 4, 85
        relationship = "同じウェーブスペル（同じ人生テーマを持つ仲間）"
    elif SEAL_COLORS.get(seal_a) == SEAL_COLORS.get(seal_b):
        score, score_100 = 4, 82
        relationship = "同じ色の紋章（類似した役割と使命）"
    elif kin_diff <= 5:
        score, score_100 = 4, 82
        relationship = "近いKin番号（魂の近さを示す）"
    else:
        score, score_100 = 3, 75
        relationship = "異なる紋章の組み合わせ（多様な学びの関係）"

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    ws_label = ""
    if same_ws:
        ws_label = "（同じ！）"

    return {
        "name": "マヤ暦（ツォルキン）",
        "category": "maya",
        "icon": "calendar_month",
        "score": score,
        "score_100": score_100,
        "summary": f"Kin {kin_a} x Kin {kin_b} - {relationship}",
        "details": {
            "person_a": {"kin": kin_a, "seal": seal_name_a, "tone": tone_a, "wavespell": ws_name_a},
            "person_b": {"kin": kin_b, "seal": seal_name_b, "tone": tone_b, "wavespell": ws_name_b},
        },
        "highlights": [
            f"{name_a}: Kin {kin_a} - {tone_name_a}{seal_name_a}（{seal_desc_a}）",
            f"{name_b}: Kin {kin_b} - {tone_name_b}{seal_name_b}（{seal_desc_b}）",
            f"ウェーブスペル: {name_a}={ws_name_a} / {name_b}={ws_name_b}{ws_label}",
        ],
        "advice": relationship,
    }
