"""カバラ数秘術計算エンジン

名前のローマ字から運命数（Expression）・ソウル数（Soul Urge）・人格数（Personality）を算出し、
二人の相性を判定する。
"""

import re
import unicodedata

CATEGORY = "数秘・タロット"

# ひらがな→ローマ字変換テーブル（ヘボン式基本）
_KANA_TO_ROMAJI = {
    'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
    'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
    'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
    'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
    'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
    'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
    'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
    'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
    'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
    'わ': 'wa', 'を': 'wo', 'ん': 'n',
    'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
    'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
    'だ': 'da', 'ぢ': 'di', 'づ': 'du', 'で': 'de', 'ど': 'do',
    'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
    'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
    # 拗音
    'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
    'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
    'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
    'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
    'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
    'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
    'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
    'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
    'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
    'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
    'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo',
    # 小文字
    'ぁ': 'a', 'ぃ': 'i', 'ぅ': 'u', 'ぇ': 'e', 'ぉ': 'o',
    'ゃ': 'ya', 'ゅ': 'yu', 'ょ': 'yo',
    'っ': '',  # 促音は次の子音を重ねる（簡易版では無視）
}

# カタカナ→ひらがな変換用オフセット
_KATAKANA_OFFSET = ord('ァ') - ord('ぁ')

# アルファベット→数値変換（カバラ数秘術）
# A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9
# J=1, K=2, L=3, M=4, N=5, O=6, P=7, Q=8, R=9
# S=1, T=2, U=3, V=4, W=5, X=6, Y=7, Z=8
_LETTER_VALUES = {}
for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    _LETTER_VALUES[c] = (i % 9) + 1

VOWELS = set('AEIOU')

# マスターナンバー
MASTER_NUMBERS = {11, 22, 33}

# 数字の意味
NUMBER_MEANINGS = {
    1: "リーダーシップ・独立・開拓精神",
    2: "協調・調和・感受性",
    3: "創造性・表現力・社交性",
    4: "安定・誠実・堅実さ",
    5: "自由・変化・冒険心",
    6: "愛情・責任・奉仕",
    7: "探究心・直感・内省",
    8: "達成・権威・実行力",
    9: "博愛・完成・精神性",
    11: "霊感・直感・インスピレーション",
    22: "大志・建設力・マスタービルダー",
    33: "奉仕・癒し・マスターティーチャー",
}

# 運命数同士の相性テーブル（スコア0-100）
EXPRESSION_COMPAT = {
    (1, 1): 60, (1, 2): 75, (1, 3): 85, (1, 4): 55, (1, 5): 90,
    (1, 6): 65, (1, 7): 70, (1, 8): 80, (1, 9): 70,
    (2, 2): 65, (2, 3): 75, (2, 4): 80, (2, 5): 55, (2, 6): 90,
    (2, 7): 60, (2, 8): 70, (2, 9): 75,
    (3, 3): 70, (3, 4): 50, (3, 5): 85, (3, 6): 80, (3, 7): 60,
    (3, 8): 65, (3, 9): 90,
    (4, 4): 65, (4, 5): 50, (4, 6): 75, (4, 7): 70, (4, 8): 85,
    (4, 9): 55,
    (5, 5): 65, (5, 6): 50, (5, 7): 75, (5, 8): 70, (5, 9): 80,
    (6, 6): 70, (6, 7): 55, (6, 8): 65, (6, 9): 85,
    (7, 7): 65, (7, 8): 55, (7, 9): 75,
    (8, 8): 65, (8, 9): 60,
    (9, 9): 70,
}

# ソウル数同士の相性テーブル
SOUL_COMPAT = {
    (1, 1): 55, (1, 2): 80, (1, 3): 75, (1, 4): 50, (1, 5): 85,
    (1, 6): 70, (1, 7): 65, (1, 8): 75, (1, 9): 65,
    (2, 2): 70, (2, 3): 80, (2, 4): 75, (2, 5): 60, (2, 6): 90,
    (2, 7): 65, (2, 8): 60, (2, 9): 80,
    (3, 3): 65, (3, 4): 55, (3, 5): 80, (3, 6): 85, (3, 7): 55,
    (3, 8): 60, (3, 9): 85,
    (4, 4): 60, (4, 5): 55, (4, 6): 80, (4, 7): 75, (4, 8): 80,
    (4, 9): 60,
    (5, 5): 60, (5, 6): 55, (5, 7): 70, (5, 8): 65, (5, 9): 75,
    (6, 6): 75, (6, 7): 60, (6, 8): 70, (6, 9): 85,
    (7, 7): 70, (7, 8): 60, (7, 9): 75,
    (8, 8): 60, (8, 9): 65,
    (9, 9): 70,
}


def _katakana_to_hiragana(text: str) -> str:
    """カタカナをひらがなに変換"""
    result = []
    for ch in text:
        cp = ord(ch)
        # カタカナ範囲: U+30A1 - U+30F6
        if 0x30A1 <= cp <= 0x30F6:
            result.append(chr(cp - _KATAKANA_OFFSET))
        else:
            result.append(ch)
    return ''.join(result)


def _is_ascii_alpha(text: str) -> bool:
    """テキストがASCIIアルファベットのみか判定"""
    return bool(re.match(r'^[A-Za-z\s\-]+$', text))


def _kana_to_romaji(text: str) -> str:
    """ひらがな/カタカナのテキストをローマ字に変換（ヘボン式簡易版）"""
    text = _katakana_to_hiragana(text)
    result = []
    i = 0
    while i < len(text):
        # 2文字の拗音を先にチェック
        if i + 1 < len(text):
            pair = text[i:i+2]
            if pair in _KANA_TO_ROMAJI:
                result.append(_KANA_TO_ROMAJI[pair])
                i += 2
                continue
        # 1文字
        ch = text[i]
        if ch in _KANA_TO_ROMAJI:
            result.append(_KANA_TO_ROMAJI[ch])
        elif ch == 'ー':
            pass  # 長音記号は無視
        elif re.match(r'[a-zA-Z]', ch):
            result.append(ch.lower())
        i += 1
    return ''.join(result)


# 常用漢字名のローマ字変換辞書
_KANJI_NAME_ROMAJI = {
    '貢': 'MITSUGU',
    '浩代': 'HIROYO',
    '翔': 'SHOU',
    '蓮': 'REN',
    '陽': 'YOU',
    '結': 'YUI',
    '愛': 'AI',
    '咲': 'SAKI',
    '凛': 'RIN',
    '葵': 'AOI',
    '悠': 'YUU',
    '樹': 'ITSUKI',
    '颯': 'HAYATE',
    '湊': 'MINATO',
    '朝': 'ASAHI',
    '奏': 'KANADE',
    '誠': 'MAKOTO',
    '健': 'KEN',
    '勇': 'ISAMU',
    '優': 'YUU',
    '直': 'NAO',
    '尚': 'NAO',
}


def name_to_romaji(name: str) -> str:
    """名前をローマ字に変換する

    既にローマ字ならそのまま返す。
    ひらがな/カタカナの場合はヘボン式に変換。
    漢字の場合は辞書を参照し、見つからなければNoneを返す。
    """
    name = name.strip()
    if _is_ascii_alpha(name):
        return name.upper().replace(' ', '').replace('-', '')

    # ひらがな/カタカナチェック
    hiragana = _katakana_to_hiragana(name)
    has_kana = any(ch in _KANA_TO_ROMAJI or ch == 'ー' for ch in hiragana)
    if has_kana:
        romaji = _kana_to_romaji(name)
        if romaji:
            return romaji.upper()

    # 漢字名の辞書参照
    if name in _KANJI_NAME_ROMAJI:
        return _KANJI_NAME_ROMAJI[name]

    return None


def _reduce_to_single(n: int) -> int:
    """数字を一桁に縮約する（マスターナンバーは保持）"""
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
    return n


def _calc_expression(romaji: str) -> int:
    """運命数（Expression Number）: 全文字の合計を一桁に"""
    total = sum(_LETTER_VALUES.get(c, 0) for c in romaji.upper() if c in _LETTER_VALUES)
    return _reduce_to_single(total)


def _calc_soul_urge(romaji: str) -> int:
    """ソウル数（Soul Urge Number）: 母音のみの合計を一桁に"""
    total = sum(_LETTER_VALUES.get(c, 0) for c in romaji.upper() if c in VOWELS)
    return _reduce_to_single(total)


def _calc_personality(romaji: str) -> int:
    """人格数（Personality Number）: 子音のみの合計を一桁に"""
    total = sum(_LETTER_VALUES.get(c, 0) for c in romaji.upper()
                if c in _LETTER_VALUES and c not in VOWELS)
    return _reduce_to_single(total)


def _master_to_single(n: int) -> int:
    """マスターナンバーを一桁に強制縮約する（テーブル参照用）"""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def _get_compat_score(num_a: int, num_b: int, table: dict) -> int:
    """相性テーブルからスコアを取得"""
    # テーブル参照用に一桁に縮約（マスターナンバーも縮約）
    a = _master_to_single(num_a)
    b = _master_to_single(num_b)
    key = (min(a, b), max(a, b))
    base = table.get(key, 65)
    # マスターナンバー補正（+10で高めに評価）
    if num_a in MASTER_NUMBERS or num_b in MASTER_NUMBERS:
        base = min(100, base + 10)
    if num_a in MASTER_NUMBERS and num_b in MASTER_NUMBERS:
        base = min(100, base + 5)  # 両方マスターなら追加ボーナス
    return base


def _mbti_fallback(mbti: str) -> str:
    """MBTIタイプから擬似的なローマ字列を生成（名前のローマ字変換ができない場合の代替）"""
    # MBTIの4文字をそのまま使う
    return mbti.upper() if mbti else "XXXX"


def calculate(person_a: dict, person_b: dict) -> dict:
    """カバラ数秘術の相性を計算する"""
    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    # ローマ字変換を試みる
    romaji_a = name_to_romaji(name_a)
    romaji_b = name_to_romaji(name_b)

    # 変換できない場合はMBTIから代替
    fallback_a = False
    fallback_b = False
    if not romaji_a:
        mbti_a = person_a.get("mbti", "")
        if mbti_a:
            romaji_a = _mbti_fallback(mbti_a)
            fallback_a = True
        else:
            return None
    if not romaji_b:
        mbti_b = person_b.get("mbti", "")
        if mbti_b:
            romaji_b = _mbti_fallback(mbti_b)
            fallback_b = True
        else:
            return None

    # 各数値の算出
    expr_a = _calc_expression(romaji_a)
    expr_b = _calc_expression(romaji_b)
    soul_a = _calc_soul_urge(romaji_a)
    soul_b = _calc_soul_urge(romaji_b)
    pers_a = _calc_personality(romaji_a)
    pers_b = _calc_personality(romaji_b)

    # 相性計算
    expr_compat = _get_compat_score(expr_a, expr_b, EXPRESSION_COMPAT)
    soul_compat = _get_compat_score(soul_a, soul_b, SOUL_COMPAT)

    # 総合スコア（運命数70%、ソウル数30%）
    score_100 = round(expr_compat * 0.7 + soul_compat * 0.3)
    score_100 = max(0, min(100, score_100))
    score = round(score_100 / 20)
    score = max(1, min(5, score))

    source_a = f"ローマ字「{romaji_a}」" if not fallback_a else f"MBTI「{romaji_a}」から算出"
    source_b = f"ローマ字「{romaji_b}」" if not fallback_b else f"MBTI「{romaji_b}」から算出"

    highlights = [
        f"{name_a}: 運命数={expr_a}、ソウル数={soul_a}、人格数={pers_a}（{source_a}）",
        f"{name_b}: 運命数={expr_b}、ソウル数={soul_b}、人格数={pers_b}（{source_b}）",
        f"運命数の相性: {expr_compat}点 — 人生の方向性の調和度",
        f"ソウル数の相性: {soul_compat}点 — 内面的な共鳴度",
    ]

    # マスターナンバー検出
    for num, label, name in [(expr_a, "運命数", name_a), (soul_a, "ソウル数", name_a),
                              (expr_b, "運命数", name_b), (soul_b, "ソウル数", name_b)]:
        if num in MASTER_NUMBERS:
            highlights.append(f"✨ {name}の{label}はマスターナンバー{num}（{NUMBER_MEANINGS.get(num, '')}）")

    # アドバイス生成
    if score >= 4:
        advice = "カバラ数秘術の生命の樹（セフィロトの木）において、二人の運命数とソウル数が強く共鳴し非常に良い相性を示しています。運命数は生命の樹の各セフィラ（球体）に対応し、互いの数が調和する配置は魂レベルでの深い結びつきを意味します。この神聖な数の共鳴を大切にし、共に精神的な成長を目指しましょう。"
    elif score >= 3:
        advice = "カバラ数秘術の生命の樹の観点では、二人の数秘的エネルギーは均衡の取れた配置にあり平均的な相性です。各セフィラが象徴する知恵（コクマー）や理解（ビナー）の力を意識し、互いの数字が持つ固有の振動エネルギーを理解し合うことで関係が深まります。生命の樹の中央柱が示すバランスの道を二人で歩む意識を持ちましょう。"
    elif score >= 2:
        advice = "カバラ数秘術ではやや課題のある相性ですが、生命の樹において異なるセフィラに位置する数同士は互いの欠けた側面を補い合う成長の可能性を秘めています。運命数の差異は峻厳（ゲブラー）と慈悲（ケセド）のように対極の力が創造的緊張を生む関係を示唆します。異なる数秘エネルギーを脅威ではなく魂の進化の糧と捉えましょう。"
    else:
        advice = "カバラ数秘術では挑戦的な相性ですが、生命の樹の最も離れたセフィラ同士は王冠（ケテル）から王国（マルクト）への全経路を包含する最も深い学びの関係です。異なる数秘的振動は互いの未発達な霊的側面を照らし出し、魂の変容を促す触媒となります。違いを受け入れ、生命の樹が示す統合の道を共に歩むことで新しい可能性が開けるでしょう。"

    # 人格数の関係も加味したアドバイス
    if pers_a == pers_b:
        advice += "人格数が同じため、生命の樹における外的表現のセフィラが一致し社会的な調和が非常に高い関係です。"
    elif abs(pers_a - pers_b) <= 2:
        advice += "人格数が近いため、生命の樹の隣接するセフィラのように自然な親和性があり周囲から調和の取れたペアに映ります。"

    return {
        "name": "カバラ数秘術",
        "category": "kabbalah",
        "icon": "auto_awesome",
        "score": score,
        "score_100": score_100,
        "summary": f"運命数 {expr_a} × {expr_b} の相性",
        "details": {
            "person_a": {
                "romaji": romaji_a,
                "expression": expr_a,
                "soul_urge": soul_a,
                "personality": pers_a,
                "fallback": fallback_a,
                "expression_meaning": NUMBER_MEANINGS.get(expr_a, ""),
                "soul_meaning": NUMBER_MEANINGS.get(soul_a, ""),
            },
            "person_b": {
                "romaji": romaji_b,
                "expression": expr_b,
                "soul_urge": soul_b,
                "personality": pers_b,
                "fallback": fallback_b,
                "expression_meaning": NUMBER_MEANINGS.get(expr_b, ""),
                "soul_meaning": NUMBER_MEANINGS.get(soul_b, ""),
            },
            "compatibility": {
                "expression_compat": expr_compat,
                "soul_compat": soul_compat,
            },
        },
        "highlights": highlights,
        "advice": advice,
    }
