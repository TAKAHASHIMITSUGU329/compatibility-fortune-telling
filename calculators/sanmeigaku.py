"""算命学 計算エンジン"""

from datetime import date

CATEGORY = "東洋占術"

# 十干（四柱推命と共通）
JIKKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 十二支
JUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天中殺グループ（年支から判定）
# 年支のペアごとに天中殺グループが決まる
TENCHU_GROUPS = {
    "子丑天中殺": ["子", "丑"],
    "寅卯天中殺": ["寅", "卯"],
    "辰巳天中殺": ["辰", "巳"],
    "午未天中殺": ["午", "未"],
    "申酉天中殺": ["申", "酉"],
    "戌亥天中殺": ["戌", "亥"],
}

# 天中殺グループの特徴
TENCHU_TRAITS = {
    "子丑天中殺": "初代運。家系の流れを新しく作る力がある。親元を離れて独立する傾向",
    "寅卯天中殺": "夢想運。理想が高く、精神的な世界を大切にする。現実離れしやすい面も",
    "辰巳天中殺": "家庭運が不安定になりやすいが、社会的に成功しやすい。仕事に生きるタイプ",
    "午未天中殺": "末代運。家系の完成者。家庭を大切にし、伝統を守る傾向",
    "申酉天中殺": "人脈運に恵まれるが、パートナー運は注意が必要。社交的で人から好かれる",
    "戌亥天中殺": "精神的な深さがある。芸術や哲学に適性。物質より精神を重視する",
}

# 天中殺グループ同士の相性
TENCHU_COMPAT = {
    ("子丑天中殺", "子丑天中殺"): (3, 65, "同じ天中殺グループ同士。理解し合えるが同じ課題を抱えやすい"),
    ("子丑天中殺", "寅卯天中殺"): (4, 78, "現実的な子丑と理想的な寅卯が補い合う"),
    ("子丑天中殺", "辰巳天中殺"): (3, 70, "独立心の強い者同士。互いの自由を尊重すれば良好"),
    ("子丑天中殺", "午未天中殺"): (5, 90, "正反対の位置にある最高の組み合わせ。強い引力で結ばれる"),
    ("子丑天中殺", "申酉天中殺"): (4, 80, "社交的な申酉が子丑の独立心を和らげる"),
    ("子丑天中殺", "戌亥天中殺"): (3, 68, "精神的な深さと現実的な強さの組み合わせ"),
    ("寅卯天中殺", "寅卯天中殺"): (3, 62, "理想家同士で夢は大きいが、現実面の課題が残る"),
    ("寅卯天中殺", "辰巳天中殺"): (4, 78, "精神性と社会性のバランスが取れた組み合わせ"),
    ("寅卯天中殺", "午未天中殺"): (4, 86, "家庭的な午未と自由な寅卯。異なる天中殺グループが互いを補い合う"),
    ("寅卯天中殺", "申酉天中殺"): (5, 88, "正反対の位置。強い縁で結ばれた運命的な相性"),
    ("寅卯天中殺", "戌亥天中殺"): (4, 82, "精神的な世界を共有できる深い関係"),
    ("辰巳天中殺", "辰巳天中殺"): (3, 60, "仕事人間同士。家庭面の配慮が課題"),
    ("辰巳天中殺", "午未天中殺"): (4, 78, "午未の家庭力が辰巳の社会性を支える"),
    ("辰巳天中殺", "申酉天中殺"): (4, 80, "社交力と社会的成功の相乗効果"),
    ("辰巳天中殺", "戌亥天中殺"): (5, 92, "正反対の位置。最も深い縁で結ばれた組み合わせ"),
    ("午未天中殺", "午未天中殺"): (4, 75, "家庭的な者同士。穏やかで安定した関係"),
    ("午未天中殺", "申酉天中殺"): (3, 68, "社交的な申酉と家庭的な午未。価値観の調整が必要"),
    ("午未天中殺", "戌亥天中殺"): (4, 80, "精神的な深さと家庭への献身が調和"),
    ("申酉天中殺", "申酉天中殺"): (3, 65, "社交的だが深い関係の構築に時間がかかる"),
    ("申酉天中殺", "戌亥天中殺"): (3, 72, "外向的な申酉と内向的な戌亥。互いに刺激し合える"),
    ("戌亥天中殺", "戌亥天中殺"): (4, 78, "精神世界を深く共有できる。現実面の補強が課題"),
}

# 日干（十干）の特徴
NIKKAN_TRAITS = {
    "甲": "大樹。真っ直ぐで正義感が強い。リーダーシップがある",
    "乙": "草花。柔軟で適応力がある。しなやかな強さを持つ",
    "丙": "太陽。明るく活発。人を照らし温める力がある",
    "丁": "灯火。繊細で情熱的。内に秘めた強い意志がある",
    "戊": "山。どっしりと構え、信頼感がある。包容力の塊",
    "己": "大地。優しく受容的。育む力に優れる",
    "庚": "鉄。意志が強く実行力がある。鍛錬で輝く",
    "辛": "宝石。繊細で美意識が高い。磨かれて光る",
    "壬": "大海。スケールが大きく包容力がある。自由を愛する",
    "癸": "雨。繊細で感受性豊か。静かに潤す力がある",
}

# 日干同士の相性（五行ベース簡易版）
NIKKAN_GOGYO = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

GOGYO_COMPAT = {
    ("木", "木"): (3, "同質で理解し合える"),
    ("木", "火"): (4, "木が火を生む。育て合う関係"),
    ("木", "土"): (2, "木が土を剋す。葛藤の可能性"),
    ("木", "金"): (2, "金が木を剋す。試練の関係"),
    ("木", "水"): (4, "水が木を生む。自然な流れの関係"),
    ("火", "火"): (3, "情熱同士。燃え上がるが消耗も"),
    ("火", "土"): (4, "火が土を生む。温かい関係"),
    ("火", "金"): (2, "火が金を剋す。衝突の可能性"),
    ("火", "水"): (2, "水が火を剋す。対立の関係"),
    ("土", "土"): (3, "安定同士。穏やかだが変化が乏しい"),
    ("土", "金"): (4, "土が金を生む。実りある関係"),
    ("土", "水"): (2, "土が水を剋す。抑制の関係"),
    ("金", "金"): (3, "堅実同士。信頼は高いが柔軟性が課題"),
    ("金", "水"): (4, "金が水を生む。知恵が流れる関係"),
    ("水", "水"): (3, "感性豊か。深い共感だが流されやすい"),
}


def _year_shi(birthday: date) -> str:
    """年支を算出する（立春前は前年）"""
    year = birthday.year
    if birthday.month < 2 or (birthday.month == 2 and birthday.day < 4):
        year -= 1
    idx = (year - 4) % 12
    return JUNISHI[idx]


def _day_kan(birthday: date) -> str:
    """日干を算出する（四柱推命と同じ方法）"""
    base_date = date(1900, 1, 1)
    base_index = 27  # 辛卯
    delta = (birthday - base_date).days
    kanshi_idx = (base_index + delta) % 60
    kan_idx = kanshi_idx % 10
    return JIKKAN[kan_idx]


def _get_tenchu_group(year_branch: str) -> str:
    """年支から天中殺グループを判定"""
    for group_name, branches in TENCHU_GROUPS.items():
        if year_branch in branches:
            return group_name
    return "子丑天中殺"


def _is_tenchu_period(tenchu_group: str, current_year: int = None) -> tuple:
    """現在が天中殺期間中かどうかを判定

    天中殺は12年に2年間。天中殺グループの支の年が天中殺。

    Returns:
        (bool, str or None)
    """
    if current_year is None:
        current_year = date.today().year

    current_shi_idx = (current_year - 4) % 12
    current_shi = JUNISHI[current_shi_idx]

    branches = TENCHU_GROUPS.get(tenchu_group, [])
    if current_shi in branches:
        return True, f"{current_shi}年"

    return False, None


def _get_tenchu_compat(group_a: str, group_b: str) -> tuple:
    """天中殺グループ同士の相性を取得"""
    key = (group_a, group_b)
    rev_key = (group_b, group_a)
    return TENCHU_COMPAT.get(key) or TENCHU_COMPAT.get(rev_key, (3, 65, "互いの天中殺を理解し合える関係"))


def _get_gogyo_compat(gogyo_a: str, gogyo_b: str) -> tuple:
    """五行の相性を取得"""
    key = (gogyo_a, gogyo_b)
    rev_key = (gogyo_b, gogyo_a)
    return GOGYO_COMPAT.get(key) or GOGYO_COMPAT.get(rev_key, (3, "普通の関係"))


def calculate(person_a: dict, person_b: dict) -> dict:
    """算命学の相性を計算する"""
    bd_a = person_a.get("birthday")
    bd_b = person_b.get("birthday")
    if not bd_a or not bd_b:
        return None

    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    # 日干の算出
    nikkan_a = _day_kan(bd_a)
    nikkan_b = _day_kan(bd_b)

    # 年支の算出
    nenshi_a = _year_shi(bd_a)
    nenshi_b = _year_shi(bd_b)

    # 天中殺グループ
    tenchu_a = _get_tenchu_group(nenshi_a)
    tenchu_b = _get_tenchu_group(nenshi_b)

    # 天中殺の相性
    tenchu_score, tenchu_100, tenchu_desc = _get_tenchu_compat(tenchu_a, tenchu_b)

    # 日干の五行相性
    gogyo_a = NIKKAN_GOGYO[nikkan_a]
    gogyo_b = NIKKAN_GOGYO[nikkan_b]
    gogyo_score, gogyo_desc = _get_gogyo_compat(gogyo_a, gogyo_b)

    # 五行スコアを1-5段階から100点スケールへ変換
    gogyo_score_map = {1: 40, 2: 55, 3: 70, 4: 92, 5: 98}
    gogyo_100 = gogyo_score_map.get(gogyo_score, 70)

    # 総合スコア（天中殺60% + 日干五行40%）
    score_100 = int(tenchu_100 * 0.6 + gogyo_100 * 0.4)
    score_100 = max(0, min(100, score_100))

    # 天中殺期間チェック（注意喚起のみ。基本相性スコアは変えない）
    is_tenchu_a, tenchu_period_a = _is_tenchu_period(tenchu_a)
    is_tenchu_b, tenchu_period_b = _is_tenchu_period(tenchu_b)

    score = round(score_100 / 20)
    score = max(1, min(5, score))

    highlights = [
        f"{name_a}: 日干={nikkan_a}（{NIKKAN_TRAITS.get(nikkan_a, '')}）",
        f"{name_b}: 日干={nikkan_b}（{NIKKAN_TRAITS.get(nikkan_b, '')}）",
        f"{name_a}の天中殺: {tenchu_a} — {TENCHU_TRAITS.get(tenchu_a, '')}",
        f"{name_b}の天中殺: {tenchu_b} — {TENCHU_TRAITS.get(tenchu_b, '')}",
        f"日干の五行: {gogyo_a} × {gogyo_b} — {gogyo_desc}",
    ]

    if is_tenchu_a:
        highlights.append(f"⚠ {name_a}は現在天中殺期間中（{tenchu_period_a}）。新しい大きな決断は慎重に")
    if is_tenchu_b:
        highlights.append(f"⚠ {name_b}は現在天中殺期間中（{tenchu_period_b}）。新しい大きな決断は慎重に")

    advice_parts = [tenchu_desc + "。"]
    advice_parts.append(f"算命学の位相法では、日干の五行（{gogyo_a}と{gogyo_b}）の関係から二人の本質的な相性を読み解きます。{gogyo_desc}という関係性は、日常のコミュニケーションや価値観の共有に大きく影響します。")
    if is_tenchu_a or is_tenchu_b:
        advice_parts.append("天中殺は算命学における12年周期の空亡期で、この期間中は守りの姿勢が大切です。新たな大きな決断は避け、関係の土台を固める時と捉えましょう。天中殺が明けた後に大きく飛躍するための準備期間と考えると、この時期も前向きに過ごせます。")
    else:
        advice_parts.append("互いの天中殺の時期を把握し、相手が空亡期に入った際には支え合う意識を持つことで、長期的に安定した関係を育めるでしょう。")

    return {
        "name": "算命学",
        "category": "sanmeigaku",
        "icon": "auto_awesome",
        "score": score,
        "score_100": score_100,
        "summary": f"{tenchu_a} × {tenchu_b} の天中殺相性",
        "details": {
            "person_a": {
                "nikkan": nikkan_a,
                "nikkan_trait": NIKKAN_TRAITS.get(nikkan_a, ""),
                "year_branch": nenshi_a,
                "tenchu_group": tenchu_a,
                "tenchu_trait": TENCHU_TRAITS.get(tenchu_a, ""),
                "is_tenchu_period": is_tenchu_a,
            },
            "person_b": {
                "nikkan": nikkan_b,
                "nikkan_trait": NIKKAN_TRAITS.get(nikkan_b, ""),
                "year_branch": nenshi_b,
                "tenchu_group": tenchu_b,
                "tenchu_trait": TENCHU_TRAITS.get(tenchu_b, ""),
                "is_tenchu_period": is_tenchu_b,
            },
            "tenchu_compat": {
                "score": tenchu_score,
                "description": tenchu_desc,
            },
            "gogyo_compat": {
                "gogyo_a": gogyo_a,
                "gogyo_b": gogyo_b,
                "score": gogyo_score,
                "description": gogyo_desc,
            },
        },
        "highlights": highlights,
        "advice": "".join(advice_parts),
    }
