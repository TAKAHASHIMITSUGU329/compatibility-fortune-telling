"""姓名判断（五格）相性計算エンジン

漢字の画数から天格・人格・地格・外格・総格を算出し、
二人の姓名判断結果の相性を判定する。
"""

import unicodedata

CATEGORY = "その他占い"

# 主要漢字の画数辞書（康熙字典準拠の旧字体画数）
# 一般的な姓名判断では旧字体の画数を使用する流派が多い
KANJI_STROKES = {
    # 数字
    '一': 1, '二': 2, '三': 3, '四': 5, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '百': 6, '千': 3, '万': 15,
    # 人名・姓に頻出する漢字（康熙字典画数）
    '高': 10, '橋': 16, '貢': 10, '浩': 11, '代': 5, '田': 5, '中': 4, '山': 3, '川': 3,
    '木': 4, '林': 8, '森': 12, '石': 5, '井': 4, '口': 3, '島': 10, '崎': 11, '谷': 7,
    '村': 7, '松': 8, '竹': 6, '梅': 11, '藤': 21, '鈴': 13, '佐': 7, '伊': 6, '加': 5,
    '小': 3, '大': 3, '上': 3, '下': 3, '前': 9, '後': 9, '北': 5, '南': 9, '東': 8, '西': 6,
    '野': 11, '原': 10, '池': 7, '河': 9, '海': 11, '岡': 8, '丘': 5, '坂': 7,
    '長': 8, '永': 5, '吉': 6, '福': 14, '徳': 15, '明': 8, '光': 6, '和': 8, '平': 5,
    '正': 5, '安': 6, '幸': 8, '美': 9, '愛': 13, '真': 10, '信': 9, '義': 13, '仁': 4,
    '勇': 9, '智': 12, '賢': 16, '優': 17, '雅': 13, '健': 11, '康': 11, '豊': 18,
    '太': 4, '郎': 14, '男': 7, '子': 3, '女': 3, '人': 2, '夫': 4, '妻': 8,
    '花': 10, '桜': 21, '菜': 14, '葉': 15, '実': 14, '果': 8, '香': 9, '風': 9,
    '月': 4, '日': 4, '星': 9, '空': 8, '雨': 8, '雪': 11, '雲': 12, '天': 4, '地': 6,
    '水': 4, '火': 4, '金': 8, '土': 3, '玉': 5,
    '春': 9, '夏': 10, '秋': 9, '冬': 5,
    '心': 4, '志': 7, '恵': 12, '慶': 15, '祥': 11,
    '龍': 16, '虎': 8, '鳳': 14, '亀': 11,
    '国': 11, '都': 16, '京': 8, '市': 5, '町': 7, '県': 9,
    '藍': 21, '紫': 12, '紅': 9, '白': 5, '黒': 12, '青': 8, '赤': 7, '緑': 14,
    '翔': 12, '陽': 17, '悠': 11, '蓮': 17, '結': 12, '咲': 9, '凛': 15,
    '奈': 8, '良': 7, '雄': 12, '彦': 9, '介': 4, '助': 7, '輔': 14,
    '裕': 13, '博': 12, '哲': 10, '誠': 14, '剛': 10, '隆': 17, '昭': 9,
    '恒': 10, '浩': 11, '洋': 10, '清': 12, '渡': 13, '辺': 22, '部': 15,
    '内': 4, '外': 5, '左': 5, '右': 5,
    '秀': 7, '英': 11, '俊': 9, '敏': 10, '直': 8, '純': 10, '修': 10,
    '達': 16, '進': 15, '道': 16, '通': 14, '理': 12, '文': 4, '史': 5,
    '学': 16, '教': 11, '政': 8, '治': 9, '経': 13, '済': 18,
    '宮': 10, '本': 5, '杉': 7, '柳': 9, '桑': 10,
    '工': 3, '手': 4, '足': 7, '目': 5, '耳': 6, '鼻': 14,
    '新': 13, '古': 5, '若': 11, '老': 6,
    '生': 5, '死': 6, '食': 9, '飲': 13,
    '立': 5, '座': 10, '走': 7, '歩': 8,
    '見': 7, '聞': 14, '言': 7, '話': 13, '読': 22, '書': 10, '記': 10,
    '名': 6, '字': 6, '音': 9, '色': 6, '形': 7,
    '力': 2, '体': 23, '気': 10, '元': 4, '先': 6, '次': 6,
    '年': 6, '歳': 13, '時': 10, '分': 4, '秒': 9,
    '朝': 12, '昼': 11, '夜': 8, '夕': 3, '暁': 16,
    '早': 6, '遅': 16, '速': 14, '急': 9, '緩': 15,
    '重': 9, '軽': 14, '強': 12, '弱': 10, '深': 12, '浅': 12,
    '広': 15, '狭': 10, '多': 6, '少': 4, '全': 6, '半': 5,
    '開': 12, '閉': 11, '入': 2, '出': 5, '来': 8, '行': 6, '帰': 18,
    '寺': 6, '神': 10, '仏': 4, '社': 8, '堂': 11,
    '王': 4, '皇': 9, '帝': 9, '后': 6, '姫': 10, '君': 7, '臣': 7,
    '父': 4, '母': 5, '兄': 5, '弟': 7, '姉': 8, '妹': 8, '息': 10,
    '友': 4, '親': 16, '知': 8, '会': 13, '合': 6,
    '家': 10, '室': 9, '屋': 9, '店': 8, '館': 16,
    '車': 7, '船': 11, '飛': 9, '機': 16,
    '衣': 6, '服': 10, '袋': 11,
    '米': 6, '麦': 11, '茶': 12, '酒': 10,
    '犬': 4, '猫': 12, '馬': 10, '牛': 4, '羊': 6, '豚': 16, '鳥': 11, '魚': 11,
    '草': 12, '樹': 16, '根': 10, '枝': 8, '苗': 11,
    '種': 14, '芽': 8, '実': 14,
    '成': 7, '完': 7, '始': 8, '終': 11, '続': 21,
    '思': 9, '想': 13, '感': 13, '情': 12, '意': 13, '念': 8,
    '喜': 12, '怒': 9, '哀': 9, '楽': 15,
    '望': 11, '希': 7, '夢': 14, '願': 19,
    '笑': 10, '泣': 9, '歌': 14, '舞': 14, '遊': 16,
    '紀': 9, '世': 5, '代': 5, '期': 12, '際': 19,
    '回': 6, '度': 9, '番': 12, '号': 5,
    '組': 11, '団': 14, '群': 13, '集': 12,
    '伸': 7, '延': 8, '張': 11, '拡': 9,
    '断': 18, '決': 8, '選': 19, '択': 17,
    '転': 18, '変': 9, '換': 13, '替': 12,
    '守': 6, '攻': 7, '防': 7, '戦': 16, '闘': 18,
    '勝': 12, '負': 9, '引': 4, '押': 9,
    '持': 10, '待': 9, '受': 8, '送': 13, '届': 8,
    '取': 8, '捨': 12, '拾': 10, '置': 13,
    '作': 7, '造': 14, '建': 9, '設': 11, '構': 14,
    '移': 11, '動': 11, '止': 4, '静': 16, '固': 8,
    '付': 5, '着': 12, '離': 19, '放': 8, '解': 13,
    '切': 4, '折': 8, '割': 12, '裂': 12, '破': 10,
    '結': 12, '束': 7, '縛': 16, '絡': 12,
    '紗': 10, '綾': 14, '織': 18, '紡': 10, '糸': 6,
    '瑞': 14, '珠': 11, '琴': 13, '瑠': 15, '璃': 16,
    '彩': 11, '絵': 12, '描': 12, '画': 12,
    '那': 11, '沙': 8, '里': 7, '乃': 2, '之': 4, '也': 3,
    '芝': 10, '菊': 14, '蘭': 22, '百合': None, '薫': 20,
    '尚': 8, '恭': 10, '敬': 13, '慎': 14, '謙': 17,
}

# ひらがな→画数（音の数をベースにした簡易マッピング）
HIRAGANA_STROKES = {
    'あ': 3, 'い': 2, 'う': 2, 'え': 2, 'お': 3,
    'か': 3, 'き': 4, 'く': 1, 'け': 3, 'こ': 2,
    'さ': 3, 'し': 1, 'す': 2, 'せ': 3, 'そ': 2,
    'た': 4, 'ち': 2, 'つ': 1, 'て': 1, 'と': 2,
    'な': 4, 'に': 3, 'ぬ': 4, 'ね': 4, 'の': 1,
    'は': 3, 'ひ': 1, 'ふ': 4, 'へ': 1, 'ほ': 4,
    'ま': 3, 'み': 2, 'む': 3, 'め': 2, 'も': 3,
    'や': 3, 'ゆ': 2, 'よ': 2,
    'ら': 2, 'り': 2, 'る': 1, 'れ': 2, 'ろ': 3,
    'わ': 2, 'を': 3, 'ん': 1,
    'が': 4, 'ぎ': 5, 'ぐ': 2, 'げ': 4, 'ご': 3,
    'ざ': 4, 'じ': 2, 'ず': 3, 'ぜ': 4, 'ぞ': 3,
    'だ': 5, 'ぢ': 3, 'づ': 2, 'で': 2, 'ど': 3,
    'ば': 4, 'び': 2, 'ぶ': 5, 'べ': 2, 'ぼ': 5,
    'ぱ': 4, 'ぴ': 2, 'ぷ': 5, 'ぺ': 2, 'ぽ': 5,
    'ゃ': 3, 'ゅ': 2, 'ょ': 2, 'っ': 1,
}


def _get_strokes(char):
    """1文字の画数を返す"""
    if char in KANJI_STROKES and KANJI_STROKES[char] is not None:
        return KANJI_STROKES[char]
    if char in HIRAGANA_STROKES:
        return HIRAGANA_STROKES[char]
    # カタカナ→ひらがな変換
    cp = ord(char)
    if 0x30A1 <= cp <= 0x30F6:
        hira = chr(cp - 0x60)
        if hira in HIRAGANA_STROKES:
            return HIRAGANA_STROKES[hira]
    # CJK統合漢字のフォールバック: unicodedataのストローク数
    try:
        name = unicodedata.name(char, '')
        # CJK漢字で辞書にない場合、総画数を推定（画数7をデフォルト）
        if 'CJK' in name:
            return 7
    except ValueError:
        pass
    return 3  # その他の文字のデフォルト


def _calc_strokes(text):
    """文字列の総画数を返す"""
    return sum(_get_strokes(c) for c in text if c.strip())


def _five_grids(family_name, given_name):
    """五格を算出する
    天格: 姓の総画数
    人格: 姓の最後の字 + 名の最初の字の画数
    地格: 名の総画数
    外格: 天格 + 地格 - 人格
    総格: 姓 + 名の総画数
    """
    if not family_name or not given_name:
        return None

    family_strokes = [_get_strokes(c) for c in family_name]
    given_strokes = [_get_strokes(c) for c in given_name]

    tenkaku = sum(family_strokes)  # 天格
    jinkaku = family_strokes[-1] + given_strokes[0]  # 人格
    chikaku = sum(given_strokes)  # 地格
    soukaku = tenkaku + chikaku  # 総格
    gaikaku = soukaku - jinkaku  # 外格
    if gaikaku <= 0:
        gaikaku = 1

    return {
        'tenkaku': tenkaku,
        'jinkaku': jinkaku,
        'chikaku': chikaku,
        'gaikaku': gaikaku,
        'soukaku': soukaku,
    }


# 画数の吉凶判定（1-81の画数に対する吉凶）
_KICHI_NUMBERS = {
    1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25,
    29, 31, 32, 33, 35, 37, 38, 39, 41, 45, 47, 48, 52, 57, 58,
    61, 63, 65, 67, 68, 73, 75, 81,
}
_DAI_KICHI_NUMBERS = {1, 3, 5, 6, 8, 11, 13, 15, 16, 21, 23, 24, 31, 32, 33, 37, 41, 45, 47, 48, 52, 57, 63, 65, 67, 81}
_KYOU_NUMBERS = {2, 4, 9, 10, 12, 14, 19, 20, 22, 26, 27, 28, 30, 34, 36, 40, 42, 43, 44, 46, 49, 50, 51, 53, 54, 55, 56, 59, 60, 62, 64, 66, 69, 70, 71, 72, 74, 76, 77, 78, 79, 80}


def _luck_score(number):
    """画数から運勢スコア(0-100)を返す"""
    n = number % 81 or 81
    if n in _DAI_KICHI_NUMBERS:
        return 90
    elif n in _KICHI_NUMBERS:
        return 75
    elif n in _KYOU_NUMBERS:
        return 35
    return 55


def _grid_label(key):
    labels = {
        'tenkaku': '天格（家系運）',
        'jinkaku': '人格（主運）',
        'chikaku': '地格（初年運）',
        'gaikaku': '外格（対人運）',
        'soukaku': '総格（総合運）',
    }
    return labels.get(key, key)


def calculate(person_a, person_b):
    """二人の姓名判断相性を計算する"""
    family_a = person_a.get('family_name') or ''
    given_a = person_a.get('given_name') or ''
    family_b = person_b.get('family_name') or ''
    given_b = person_b.get('given_name') or ''

    # 姓名が入力されていない場合はスキップ
    if not (family_a and given_a) or not (family_b and given_b):
        return None

    grids_a = _five_grids(family_a, given_a)
    grids_b = _five_grids(family_b, given_b)

    if not grids_a or not grids_b:
        return None

    name_a = person_a.get('name', f'{family_a}{given_a}')
    name_b = person_b.get('name', f'{family_b}{given_b}')

    # 各格の運勢スコア
    scores_a = {k: _luck_score(v) for k, v in grids_a.items()}
    scores_b = {k: _luck_score(v) for k, v in grids_b.items()}

    # 相性計算: 人格同士の相性を重視
    # 1) 各格の平均運勢の近さ（バランス）
    avg_a = sum(scores_a.values()) / 5
    avg_b = sum(scores_b.values()) / 5
    balance_score = 100 - abs(avg_a - avg_b)

    # 2) 人格（主運）の組み合わせ相性
    jin_a = grids_a['jinkaku']
    jin_b = grids_b['jinkaku']
    # 五行相性（画数の末尾で五行を決定）
    gogyou_a = jin_a % 10
    gogyou_b = jin_b % 10
    # 五行: 1,2=木 3,4=火 5,6=土 7,8=金 9,0=水
    def _to_gogyou(n):
        n = n % 10
        if n in (1, 2): return '木'
        if n in (3, 4): return '火'
        if n in (5, 6): return '土'
        if n in (7, 8): return '金'
        return '水'

    g_a = _to_gogyou(jin_a)
    g_b = _to_gogyou(jin_b)

    # 五行相生（良い組み合わせ）
    soushou = {('木', '火'), ('火', '土'), ('土', '金'), ('金', '水'), ('水', '木')}
    # 五行相剋（悪い組み合わせ）
    soukoku = {('木', '土'), ('土', '水'), ('水', '火'), ('火', '金'), ('金', '木')}

    if (g_a, g_b) in soushou or (g_b, g_a) in soushou:
        gogyou_score = 90
        gogyou_text = f"{g_a}と{g_b}は相生の関係（良い相性）"
    elif (g_a, g_b) in soukoku or (g_b, g_a) in soukoku:
        gogyou_score = 40
        gogyou_text = f"{g_a}と{g_b}は相剋の関係（対立しやすい）"
    elif g_a == g_b:
        gogyou_score = 70
        gogyou_text = f"同じ{g_a}同士（似た者同士で安定）"
    else:
        gogyou_score = 60
        gogyou_text = f"{g_a}と{g_b}は中性的な関係"

    # 3) 総格同士の調和
    sou_diff = abs(grids_a['soukaku'] - grids_b['soukaku'])
    harmony_score = max(40, 100 - sou_diff * 3)

    # 4) 二人の名前を合わせた総画数の吉凶
    combined_strokes = grids_a['soukaku'] + grids_b['soukaku']
    combined_luck = _luck_score(combined_strokes)

    # 総合スコア（重み付き平均）
    total = (
        balance_score * 0.15 +
        gogyou_score * 0.30 +
        harmony_score * 0.20 +
        combined_luck * 0.20 +
        (avg_a + avg_b) / 2 * 0.15
    )
    score_100 = max(0, min(100, round(total)))
    score = max(1, min(5, round(score_100 / 20)))

    # 詳細情報
    highlights = []
    highlights.append(f"{name_a}の総格{grids_a['soukaku']}画 × {name_b}の総格{grids_b['soukaku']}画")
    highlights.append(f"人格の五行: {gogyou_text}")
    highlights.append(f"二人の合計画数: {combined_strokes}画（{'吉' if combined_strokes % 81 in _KICHI_NUMBERS else '凶'}）")

    details_a = {f"{_grid_label(k)}": f"{v}画（{'吉' if _luck_score(v) >= 70 else '凶'}）" for k, v in grids_a.items()}
    details_b = {f"{_grid_label(k)}": f"{v}画（{'吉' if _luck_score(v) >= 70 else '凶'}）" for k, v in grids_b.items()}

    if score_100 >= 80:
        advice = "姓名判断では非常に良い相性です。互いの名前が持つエネルギーが調和しています。"
    elif score_100 >= 60:
        advice = "姓名判断では良好な相性です。五行のバランスを意識すると、さらに良い関係を築けます。"
    else:
        advice = "姓名判断では課題がある相性ですが、画数だけで全てが決まるわけではありません。互いの理解が大切です。"

    return {
        'name': '姓名判断（五格）',
        'score': score,
        'score_100': score_100,
        'summary': f"{name_a}と{name_b}の姓名判断相性。人格の五行は{g_a}と{g_b}で{gogyou_text}。",
        'details': {
            f'{name_a}の五格': details_a,
            f'{name_b}の五格': details_b,
            '五行相性': gogyou_text,
            '合計画数': f'{combined_strokes}画',
        },
        'highlights': highlights,
        'advice': advice,
        'icon': '📝',
    }
