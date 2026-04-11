"""六星占術（細木数子式）計算エンジン"""

from datetime import date

CATEGORY = "その他占い"

# 運命星の定義
UNMEI_STARS = [
    "土星人(+)", "土星人(-)",
    "金星人(+)", "金星人(-)",
    "火星人(+)", "火星人(-)",
    "天王星人(+)", "天王星人(-)",
    "木星人(+)", "木星人(-)",
    "水星人(+)", "水星人(-)",
]

# 運命星の短い名前
STAR_NAMES = ["土星人", "金星人", "火星人", "天王星人", "木星人", "水星人"]

# 運命星の特徴
STAR_TRAITS = {
    "土星人": "忍耐力と信頼感に優れ、着実に物事を進めるタイプ。堅実で責任感が強い",
    "金星人": "華やかで社交的。美的センスに優れ、人を惹きつける魅力がある",
    "火星人": "情熱的で行動力がある。リーダーシップに優れ、困難に立ち向かう勇気を持つ",
    "天王星人": "独創的で自由な発想の持ち主。型にはまらない生き方を好む",
    "木星人": "温厚で協調性があり、人望が厚い。バランス感覚に優れる",
    "水星人": "知性的で頭の回転が速い。コミュニケーション能力に優れる",
}

# 大殺界の12年周期パターン（運命星ごとの大殺界開始年の干支インデックス）
# 大殺界は3年間（陰影、停止、減退）
# 各運命星の大殺界の開始支（12年周期で3年間）
DAISAKKKAI_START_SHI = {
    "土星人": 0,   # 子年から3年間
    "金星人": 2,   # 寅年から3年間
    "火星人": 4,   # 辰年から3年間
    "天王星人": 6, # 午年から3年間
    "木星人": 8,   # 申年から3年間
    "水星人": 10,  # 戌年から3年間
}

# 運命星相性テーブル（星名同士、+-は別途計算）
# スコア: 1-5
STAR_COMPAT = {
    ("土星人", "土星人"): (3, 65, "似た者同士で安心感があるが、刺激が少なくなりがち"),
    ("土星人", "金星人"): (4, 80, "土星人の堅実さを金星人が華やかに彩る好相性"),
    ("土星人", "火星人"): (4, 78, "土星人の堅実さと火星人の行動力が噛み合う。互いの強さを認め尊重し合えれば強固な絆に"),
    ("土星人", "天王星人"): (2, 50, "価値観の違いが大きい。新しい視点を得られる関係"),
    ("土星人", "木星人"): (5, 90, "最高の組み合わせの一つ。安定と調和の理想的な関係"),
    ("土星人", "水星人"): (4, 78, "堅実さと知性が補い合う。信頼感のある関係"),
    ("金星人", "金星人"): (3, 62, "華やかだが互いに譲れない部分で衝突しやすい"),
    ("金星人", "火星人"): (5, 88, "情熱と華やかさが融合する魅力的な組み合わせ"),
    ("金星人", "天王星人"): (4, 82, "自由を愛する者同士で刺激的な関係"),
    ("金星人", "木星人"): (4, 80, "社交的な金星人を温厚な木星人が支える"),
    ("金星人", "水星人"): (3, 70, "知性と美意識の組み合わせ。深い会話ができる"),
    ("火星人", "火星人"): (2, 55, "情熱がぶつかり合う。互いに一歩引く姿勢が大切"),
    ("火星人", "天王星人"): (3, 68, "個性的な二人。互いの自由を尊重すれば良い関係に"),
    ("火星人", "木星人"): (4, 82, "火星人の行動力を木星人が穏やかに支える"),
    ("火星人", "水星人"): (4, 78, "行動力と知性の組み合わせ。目標に向かって協力できる"),
    ("天王星人", "天王星人"): (3, 60, "自由人同士で理解し合えるが、まとまりにくい"),
    ("天王星人", "木星人"): (4, 80, "天王星人の独創性を木星人がバランスよく支える"),
    ("天王星人", "水星人"): (5, 88, "知性と独創性が化学反応を起こす最高の組み合わせ"),
    ("木星人", "木星人"): (4, 78, "穏やかで安定した関係。平和だが変化を恐れないように"),
    ("木星人", "水星人"): (4, 80, "バランスの取れた組み合わせ。互いの長所を活かせる"),
    ("水星人", "水星人"): (3, 65, "知的な会話が弾むが、感情面の表現を忘れずに"),
}

# 12運気の周期名
TWELVE_CYCLE = [
    "種子", "緑生", "立花", "健弱", "達成", "乾燥",
    "陰影", "停止", "減退", "再会", "財成", "安定",
]


def _calc_unmei_number(birthday: date) -> int:
    """運命数を算出する（簡易版）

    運命数 = (年数 + 月日数) % 61
    年数: 西暦の各桁の合計を繰り返し足して1桁にした後、特定のテーブルで変換
    月日数: 月×2 + 日 を基本とした値
    """
    # 簡易算出法：生年月日の全桁合計を61で割った余り
    y = birthday.year
    m = birthday.month
    d = birthday.day

    # 年の運命数要素（年の各桁の合計 × 特定の係数）
    year_sum = sum(int(c) for c in str(y))
    # 月日の運命数要素
    md_val = m * 3 + d

    unmei = (year_sum * 11 + md_val) % 61
    if unmei == 0:
        unmei = 61

    return unmei


def _unmei_to_star(unmei: int) -> tuple:
    """運命数から運命星と陰陽を返す

    Returns:
        (星名, 陰陽, フル名)
    """
    # 運命数の範囲で星を割り当て
    # 1-10: 土星人, 11-20: 金星人, 21-30: 火星人,
    # 31-40: 天王星人, 41-50: 木星人, 51-61: 水星人
    if unmei <= 10:
        star = "土星人"
    elif unmei <= 20:
        star = "金星人"
    elif unmei <= 30:
        star = "火星人"
    elif unmei <= 40:
        star = "天王星人"
    elif unmei <= 50:
        star = "木星人"
    else:
        star = "水星人"

    # 奇数=陽(+)、偶数=陰(-)
    polarity = "+" if unmei % 2 == 1 else "-"
    full_name = f"{star}({polarity})"

    return star, polarity, full_name


def _is_daisakkai(birthday: date, star: str, current_year: int = None) -> tuple:
    """現在が大殺界かどうかを判定

    Returns:
        (bool, str or None) — 大殺界中かどうか、期間名
    """
    if current_year is None:
        current_year = date.today().year

    # 現在の年の十二支インデックス
    current_shi = (current_year - 4) % 12

    # この星の大殺界開始支
    start_shi = DAISAKKKAI_START_SHI.get(star, 0)

    # 大殺界の3年間（陰影、停止、減退）
    daisakkai_shis = [(start_shi + i) % 12 for i in range(3)]

    if current_shi in daisakkai_shis:
        idx = daisakkai_shis.index(current_shi)
        period_names = ["陰影", "停止", "減退"]
        return True, period_names[idx]

    return False, None


def _get_current_cycle(birthday: date, star: str, current_year: int = None) -> str:
    """現在の運気の位置を返す"""
    if current_year is None:
        current_year = date.today().year

    # 基準年からの経過年数で12運気の周期を判定
    # 運命星ごとに周期の開始がずれる
    star_offset = list(STAR_NAMES).index(star) * 2 if star in STAR_NAMES else 0
    cycle_idx = (current_year - birthday.year + star_offset) % 12
    return TWELVE_CYCLE[cycle_idx]


def _get_compat(star_a: str, star_b: str) -> tuple:
    """二つの星の相性を取得"""
    key = (star_a, star_b)
    rev_key = (star_b, star_a)
    return STAR_COMPAT.get(key) or STAR_COMPAT.get(rev_key, (3, 65, "互いを理解し合うことで良い関係が築ける"))


def calculate(person_a: dict, person_b: dict) -> dict:
    """六星占術の相性を計算する"""
    bd_a = person_a.get("birthday")
    bd_b = person_b.get("birthday")
    if not bd_a or not bd_b:
        return None

    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    # 運命数と運命星の算出
    unmei_a = _calc_unmei_number(bd_a)
    unmei_b = _calc_unmei_number(bd_b)

    star_a, pol_a, full_a = _unmei_to_star(unmei_a)
    star_b, pol_b, full_b = _unmei_to_star(unmei_b)

    # 相性判定
    score, score_100, compat_desc = _get_compat(star_a, star_b)

    # 陰陽の補正
    if pol_a != pol_b:
        score_100 = min(100, score_100 + 5)  # 陰陽が異なると補完的

    # 大殺界判定
    is_dai_a, dai_period_a = _is_daisakkai(bd_a, star_a)
    is_dai_b, dai_period_b = _is_daisakkai(bd_b, star_b)

    # 現在の運気
    cycle_a = _get_current_cycle(bd_a, star_a)
    cycle_b = _get_current_cycle(bd_b, star_b)

    # 大殺界中はスコア微減点（基本相性を大きく変えない）
    if is_dai_a and is_dai_b:
        score_100 = max(0, score_100 - 8)
    elif is_dai_a or is_dai_b:
        score_100 = max(0, score_100 - 5)

    score = round(score_100 / 20)
    score = max(1, min(5, score))

    highlights = [
        f"{name_a}: {full_a}（運命数 {unmei_a}）— {STAR_TRAITS.get(star_a, '')}",
        f"{name_b}: {full_b}（運命数 {unmei_b}）— {STAR_TRAITS.get(star_b, '')}",
        f"現在の運気: {name_a}={cycle_a}、{name_b}={cycle_b}",
    ]

    if is_dai_a:
        highlights.append(f"⚠ {name_a}は現在「大殺界（{dai_period_a}）」の期間中。慎重な行動が求められます")
    if is_dai_b:
        highlights.append(f"⚠ {name_b}は現在「大殺界（{dai_period_b}）」の期間中。慎重な行動が求められます")

    # アドバイス
    advice_parts = [compat_desc + "。"]
    if is_dai_a or is_dai_b:
        advice_parts.append("大殺界の期間中は大きな決断を避け、現状維持を心がけましょう。")
    if pol_a != pol_b:
        advice_parts.append("陰陽が異なるため、互いに補い合える良い組み合わせです。")

    return {
        "name": "六星占術",
        "category": "rokusei",
        "icon": "brightness_6",
        "score": score,
        "score_100": score_100,
        "summary": f"{full_a} × {full_b} の相性",
        "details": {
            "person_a": {
                "unmei_number": unmei_a,
                "star": full_a,
                "base_star": star_a,
                "polarity": pol_a,
                "current_cycle": cycle_a,
                "daisakkai": is_dai_a,
                "daisakkai_period": dai_period_a,
            },
            "person_b": {
                "unmei_number": unmei_b,
                "star": full_b,
                "base_star": star_b,
                "polarity": pol_b,
                "current_cycle": cycle_b,
                "daisakkai": is_dai_b,
                "daisakkai_period": dai_period_b,
            },
        },
        "highlights": highlights,
        "advice": "".join(advice_parts),
    }
