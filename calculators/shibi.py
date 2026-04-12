"""紫微斗数（簡易版）計算エンジン

台湾系の占星術。命宮と夫妻宮に焦点を当てた簡易実装。
"""

from datetime import date

CATEGORY = "東洋占術"

# 十二支（宮の位置）
JUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 14主星のうち代表的な6主星（簡易版）
MAIN_STARS = [
    "紫微", "天機", "太陽", "武曲", "天同", "廉貞",
    "天府", "太陰", "貪狼", "巨門", "天相", "天梁",
    "七殺", "破軍",
]

# 命宮の主星テーブル（簡易版: 命宮の十二支位置 → 主星）
MEIKYU_STAR_TABLE = {
    "子": "貪狼",
    "丑": "天相",
    "寅": "天梁",
    "卯": "七殺",
    "辰": "廉貞",
    "巳": "天府",
    "午": "太陰",
    "未": "貪狼",
    "申": "巨門",
    "酉": "天機",
    "戌": "紫微",
    "亥": "破軍",
}

# 夫妻宮の主星テーブル（命宮から時計回りに2つ先の宮）
# 夫妻宮は命宮の位置から決定される
FUSAIKYU_OFFSET = -1  # 命宮から反時計回りに1つ（簡易版）

# 主星の恋愛傾向
STAR_LOVE_TRAITS = {
    "紫微": ("帝王の星。プライドが高く、相手を守りたい気持ちが強い。理想が高い",
             "リーダーシップ型", 70),
    "天機": ("知性の星。繊細で頭が良く、知的な相手を好む。計算高い面も",
             "知性重視型", 65),
    "太陽": ("輝きの星。明るく温かく、誰にでも優しい。八方美人になりやすい",
             "博愛型", 75),
    "武曲": ("財星。真面目で実直。不器用だが一途な愛情を持つ",
             "一途型", 72),
    "天同": ("福星。穏やかで優しい。受動的で決断が遅い面がある",
             "癒し型", 78),
    "廉貞": ("情の星。情熱的で嫉妬深い。恋愛に全力を注ぐタイプ",
             "情熱型", 68),
    "天府": ("庫の星。包容力があり安定志向。物質的な豊かさを重視",
             "安定型", 80),
    "太陰": ("月の星。感受性が豊かでロマンチスト。理想と現実のギャップに悩む",
             "ロマンチスト型", 73),
    "貪狼": ("欲望の星。魅力的で社交的。恋愛運は強いが移り気な面も",
             "魅力型", 70),
    "巨門": ("口舌の星。言葉が鋭く誤解されやすい。深い愛情を内に秘める",
             "秘めた愛型", 62),
    "天相": ("補佐の星。協調性があり相手を立てる。自分を犠牲にしがち",
             "献身型", 82),
    "天梁": ("蔭の星。面倒見が良く、年長者から愛される。恋愛より使命感",
             "保護者型", 68),
    "七殺": ("将軍の星。行動力があり大胆。恋愛も積極的だが衝突も多い",
             "大胆型", 65),
    "破軍": ("変革の星。波乱万丈な恋愛運。変化を恐れず新しい関係を求める",
             "変革型", 60),
}

# 夫妻宮の主星同士の相性（簡易マトリクス）
# 同系列で相性を判定
STAR_CATEGORIES = {
    "リーダーシップ型": "主導",
    "知性重視型": "知性",
    "博愛型": "温和",
    "一途型": "堅実",
    "癒し型": "温和",
    "情熱型": "情熱",
    "安定型": "堅実",
    "ロマンチスト型": "情熱",
    "魅力型": "情熱",
    "秘めた愛型": "知性",
    "献身型": "温和",
    "保護者型": "守護",
    "大胆型": "行動",
    "変革型": "情熱",
}

CATEGORY_COMPAT = {
    ("主導", "主導"): (3, 62, "リーダー同士でぶつかりやすいが、互いの強さを認め合える"),
    ("主導", "知性"): (4, 78, "知性が主導力を導き、戦略的なパートナーシップに"),
    ("主導", "温和"): (5, 88, "主導する側と支える側の理想的な組み合わせ"),
    ("主導", "堅実"): (4, 80, "安定した基盤の上に力強いリーダーシップが活きる"),
    ("主導", "情熱"): (4, 78, "情熱と行動力が噛み合えば最強のカップル"),
    ("主導", "守護"): (4, 82, "守護する力とリーダーシップが融合する頼もしい関係"),
    ("主導", "行動"): (4, 80, "大胆な行動力とリーダーシップが共鳴する"),
    ("知性", "知性"): (3, 68, "知的な会話は楽しいが、感情面の交流が課題"),
    ("知性", "温和"): (4, 80, "温かさが知性の冷たさを溶かし、バランスの良い関係に"),
    ("知性", "堅実"): (4, 78, "堅実さと知性が融合し、計画的な人生を歩める"),
    ("知性", "情熱"): (3, 70, "冷静と情熱のギャップ。理解し合えれば深い関係に"),
    ("知性", "守護"): (4, 80, "守護者の安定感と知性が調和する関係"),
    ("知性", "行動"): (4, 78, "行動力と知性が戦略的に融合する"),
    ("温和", "温和"): (4, 82, "穏やかで温かい関係。刺激が欲しくなることも"),
    ("温和", "堅実"): (5, 90, "安定と温かさの最高の組み合わせ。家庭円満"),
    ("温和", "情熱"): (4, 78, "情熱を温かく受け止め、安らぎを与える関係"),
    ("温和", "守護"): (5, 90, "守護と癒しの理想的な組み合わせ"),
    ("温和", "行動"): (4, 80, "大胆さを温かく受け止め、バランスの取れた関係"),
    ("堅実", "堅実"): (4, 80, "安定感抜群。変化への柔軟性が課題"),
    ("堅実", "情熱"): (3, 72, "堅実さが情熱を支えるが、温度差に注意"),
    ("堅実", "守護"): (5, 88, "守護者の面倒見と堅実さが安定した絆を築く"),
    ("堅実", "行動"): (4, 78, "行動力を堅実さが支え、実りある関係に"),
    ("情熱", "情熱"): (3, 68, "燃え上がるが消耗も激しい。クールダウンの工夫を"),
    ("情熱", "守護"): (4, 82, "情熱を守護者が包み込む、深い愛情の関係"),
    ("情熱", "行動"): (4, 80, "行動力と情熱が共鳴し合うダイナミックな関係"),
    ("守護", "守護"): (4, 80, "互いを守り合う安心感のある関係"),
    ("守護", "行動"): (5, 90, "保護者の包容力と大胆な行動力が融合する最高の補完関係"),
    ("行動", "行動"): (3, 65, "大胆者同士で衝突しやすいが、互いの勇気を尊重できる"),
}


def _estimate_lunar_month(birthday: date) -> int:
    """生年月日から旧暦月を概算する（簡易版）

    新暦から約1ヶ月引く概算。正確には太陰暦変換が必要。
    """
    m = birthday.month
    d = birthday.day
    # 概算: 新暦の日付から1ヶ月弱ずらす
    if d < 22:
        lunar_month = m - 1
    else:
        lunar_month = m
    if lunar_month <= 0:
        lunar_month += 12
    return lunar_month


def _estimate_birth_hour_shi() -> int:
    """出生時辰を返す（不明の場合は午時=6）"""
    return 6  # 午時（昼12時）をデフォルト


def _calc_meikyu_position(lunar_month: int, hour_shi: int) -> str:
    """命宮の十二支位置を算出する

    命宮 = 寅(index=2)を正月として、月を足し、時辰を引く
    簡易式: (14 - lunar_month + hour_shi) % 12
    """
    idx = (14 - lunar_month + hour_shi) % 12
    return JUNISHI[idx]


def _get_fusaikyu_position(meikyu_pos: str) -> str:
    """命宮から夫妻宮の位置を求める"""
    idx = JUNISHI.index(meikyu_pos)
    fusai_idx = (idx + FUSAIKYU_OFFSET) % 12
    return JUNISHI[fusai_idx]


def _get_star_at_position(position: str) -> str:
    """宮の位置から主星を取得"""
    return MEIKYU_STAR_TABLE.get(position, "天同")


def _get_star_compat(cat_a: str, cat_b: str) -> tuple:
    """カテゴリー同士の相性を取得"""
    key = (cat_a, cat_b)
    rev_key = (cat_b, cat_a)
    return CATEGORY_COMPAT.get(key) or CATEGORY_COMPAT.get(rev_key, (3, 70, "互いの個性を尊重し合える関係"))


def calculate(person_a: dict, person_b: dict) -> dict:
    """紫微斗数（簡易版）の相性を計算する"""
    bd_a = person_a.get("birthday")
    bd_b = person_b.get("birthday")
    if not bd_a or not bd_b:
        return None

    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    # 旧暦月の概算
    lunar_a = _estimate_lunar_month(bd_a)
    lunar_b = _estimate_lunar_month(bd_b)

    # 出生時辰（不明なので午時）
    hour_shi = _estimate_birth_hour_shi()

    # 命宮の位置
    meikyu_pos_a = _calc_meikyu_position(lunar_a, hour_shi)
    meikyu_pos_b = _calc_meikyu_position(lunar_b, hour_shi)

    # 夫妻宮の位置
    fusai_pos_a = _get_fusaikyu_position(meikyu_pos_a)
    fusai_pos_b = _get_fusaikyu_position(meikyu_pos_b)

    # 命宮の主星
    meikyu_star_a = _get_star_at_position(meikyu_pos_a)
    meikyu_star_b = _get_star_at_position(meikyu_pos_b)

    # 夫妻宮の主星
    fusai_star_a = _get_star_at_position(fusai_pos_a)
    fusai_star_b = _get_star_at_position(fusai_pos_b)

    # 主星の恋愛傾向
    fusai_trait_a = STAR_LOVE_TRAITS.get(fusai_star_a, ("不明", "不明", 70))
    fusai_trait_b = STAR_LOVE_TRAITS.get(fusai_star_b, ("不明", "不明", 70))

    meikyu_trait_a = STAR_LOVE_TRAITS.get(meikyu_star_a, ("不明", "不明", 70))
    meikyu_trait_b = STAR_LOVE_TRAITS.get(meikyu_star_b, ("不明", "不明", 70))

    # カテゴリー相性
    cat_a = STAR_CATEGORIES.get(fusai_trait_a[1], "温和")
    cat_b = STAR_CATEGORIES.get(fusai_trait_b[1], "温和")

    compat_score, compat_100, compat_desc = _get_star_compat(cat_a, cat_b)

    # 夫妻宮の基礎スコアも加味
    base_avg = (fusai_trait_a[2] + fusai_trait_b[2]) / 2
    score_100 = int(compat_100 * 0.7 + base_avg * 0.3)
    score_100 = max(0, min(100, score_100))

    score = round(score_100 / 20)
    score = max(1, min(5, score))

    highlights = [
        f"{name_a}: 命宮={meikyu_pos_a}宮（{meikyu_star_a}）、夫妻宮={fusai_pos_a}宮（{fusai_star_a}）",
        f"{name_b}: 命宮={meikyu_pos_b}宮（{meikyu_star_b}）、夫妻宮={fusai_pos_b}宮（{fusai_star_b}）",
        f"{name_a}の夫妻宮: {fusai_star_a}（{fusai_trait_a[1]}） — {fusai_trait_a[0]}",
        f"{name_b}の夫妻宮: {fusai_star_b}（{fusai_trait_b[1]}） — {fusai_trait_b[0]}",
        f"夫妻宮の相性: {cat_a} × {cat_b} — {compat_desc}",
    ]

    advice = f"紫微斗数では、命盤の夫妻宮に入る主星から恋愛・結婚の傾向を読み解きます。お二人の夫妻宮は「{cat_a} × {cat_b}」の組み合わせで、{compat_desc}。"
    if fusai_star_a == fusai_star_b:
        advice += f"さらに夫妻宮に同じ{fusai_star_a}星が入っており、恋愛観や結婚に求めるものが自然と一致しやすい稀有な組み合わせです。互いの価値観を尊重し合うことで、より深い信頼関係を築いていけるでしょう。"
    else:
        advice += f"{fusai_star_a}星の「{fusai_trait_a[1]}」と{fusai_star_b}星の「{fusai_trait_b[1]}」は、互いに異なる魅力を持ち合わせています。この違いを補い合うことで、バランスの取れたパートナーシップを育むことができるでしょう。"

    return {
        "name": "紫微斗数",
        "category": "shibi",
        "icon": "brightness_7",
        "score": score,
        "score_100": score_100,
        "summary": f"夫妻宮 {fusai_star_a}（{fusai_trait_a[1]}） × {fusai_star_b}（{fusai_trait_b[1]}）",
        "details": {
            "person_a": {
                "meikyu_position": meikyu_pos_a,
                "meikyu_star": meikyu_star_a,
                "meikyu_trait": meikyu_trait_a[0],
                "fusaikyu_position": fusai_pos_a,
                "fusaikyu_star": fusai_star_a,
                "fusaikyu_type": fusai_trait_a[1],
                "fusaikyu_trait": fusai_trait_a[0],
            },
            "person_b": {
                "meikyu_position": meikyu_pos_b,
                "meikyu_star": meikyu_star_b,
                "meikyu_trait": meikyu_trait_b[0],
                "fusaikyu_position": fusai_pos_b,
                "fusaikyu_star": fusai_star_b,
                "fusaikyu_type": fusai_trait_b[1],
                "fusaikyu_trait": fusai_trait_b[0],
            },
            "compat_category": f"{cat_a} × {cat_b}",
            "compat_description": compat_desc,
        },
        "highlights": highlights,
        "advice": advice,
    }
