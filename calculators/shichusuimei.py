"""四柱推命（年柱・月柱・日柱）計算エンジン"""

from datetime import date, timedelta

CATEGORY = "東洋占術"

# 十干
JIKKAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 十二支
JUNISHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 六十干支
ROKUJU_KANSHI = []
for i in range(60):
    ROKUJU_KANSHI.append(JIKKAN[i % 10] + JUNISHI[i % 12])

# 五行の対応
JIKKAN_GOGYO = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

JUNISHI_GOGYO = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 五行の相生関係（AがBを生む）
SOSHO = {
    "木": "火", "火": "土", "土": "金", "金": "水", "水": "木",
}

# 五行の相剋関係（AがBを剋す）
SOKOKU = {
    "木": "土", "土": "水", "水": "火", "火": "金", "金": "木",
}

# 月柱の算出テーブル：年干の五行グループから月干の開始インデックス
# 甲己年→丙寅月(2)、乙庚年→戊寅月(4)、丙辛年→庚寅月(6)、丁壬年→壬寅月(8)、戊癸年→甲寅月(0)
MONTH_KAN_START = {
    "甲": 2, "己": 2,
    "乙": 4, "庚": 4,
    "丙": 6, "辛": 6,
    "丁": 8, "壬": 8,
    "戊": 0, "癸": 0,
}

# 節入り日（各月の開始日の目安、旧暦ベースではなく節気ベース）
# 寅月(1月)=立春(2/4頃)〜啓蟄前日
SETSUIRI = [
    (2, 4),   # 寅月（1月）開始
    (3, 6),   # 卯月（2月）開始
    (4, 5),   # 辰月（3月）開始
    (5, 6),   # 巳月（4月）開始
    (6, 6),   # 午月（5月）開始
    (7, 7),   # 未月（6月）開始
    (8, 8),   # 申月（7月）開始
    (9, 8),   # 酉月（8月）開始
    (10, 8),  # 戌月（9月）開始
    (11, 7),  # 亥月（10月）開始
    (12, 7),  # 子月（11月）開始
    (1, 6),   # 丑月（12月）開始
]

# 干合のペア
KANGO_PAIRS = [
    ("甲", "己"), ("乙", "庚"), ("丙", "辛"), ("丁", "壬"), ("戊", "癸"),
]

# 支合のペア
SHIGO_PAIRS = [
    ("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未"),
]

# 三合のグループ
SANGO_GROUPS = [
    ("申", "子", "辰"),  # 水局
    ("亥", "卯", "未"),  # 木局
    ("寅", "午", "戌"),  # 火局
    ("巳", "酉", "丑"),  # 金局
]

# 対冲（冲）のペア
TAICHU_PAIRS = [
    ("子", "午"), ("丑", "未"), ("寅", "申"), ("卯", "酉"), ("辰", "戌"), ("巳", "亥"),
]

# 破のペア
HA_PAIRS = [
    ("子", "酉"), ("丑", "辰"), ("寅", "亥"), ("卯", "午"), ("巳", "申"), ("未", "戌"),
]


def _year_pillar(birthday: date) -> int:
    """年柱のインデックスを算出（立春前は前年扱い）"""
    year = birthday.year
    # 立春（2月4日頃）前は前年の干支
    if birthday.month < 2 or (birthday.month == 2 and birthday.day < 4):
        year -= 1
    return (year - 4) % 60


def _month_pillar(birthday: date) -> int:
    """月柱のインデックスを算出"""
    year = birthday.year
    # 立春前は前年の年干を使う
    if birthday.month < 2 or (birthday.month == 2 and birthday.day < 4):
        year -= 1

    year_kan = JIKKAN[(year - 4) % 10]
    kan_start = MONTH_KAN_START[year_kan]

    # 節入り月の判定
    month_idx = _get_setsuiri_month(birthday)

    # 月干のインデックス = 月干開始 + (月-1)
    kan_idx = (kan_start + month_idx) % 10
    # 月支のインデックス = 寅(2)から始まる
    shi_idx = (month_idx + 2) % 12

    # 六十干支のインデックスを計算
    # 干と支の組み合わせから六十干支インデックスを求める
    for i in range(60):
        if i % 10 == kan_idx and i % 12 == shi_idx:
            return i

    return 0


def _get_setsuiri_month(birthday: date) -> int:
    """節入りに基づく月番号（0=寅月〜11=丑月）を返す"""
    m = birthday.month
    d = birthday.day

    # 各月の節入り日と比較
    # SETSUIRI[0] = (2,4) = 寅月開始
    # 丑月(12月): 1/6〜2/3
    if m == 1 and d >= 6:
        return 11  # 丑月
    if m == 1 and d < 6:
        return 10  # 子月（前月）

    for i in range(11):
        start_m, start_d = SETSUIRI[i]
        end_m, end_d = SETSUIRI[i + 1]
        if start_m <= end_m:
            if (m == start_m and d >= start_d) or (m > start_m and m < end_m) or (m == end_m and d < end_d):
                return i
        else:
            # 年をまたぐケース（12月→1月）
            if (m == start_m and d >= start_d) or (m > start_m) or (m < end_m) or (m == end_m and d < end_d):
                return i

    return 0


def _day_pillar(birthday: date) -> int:
    """日柱のインデックスを算出"""
    # 基準日: 1900年1月1日 = 辛卯 (index 27 in 六十干支)
    # 検証: 1979/6/3 = 戊午 (index 54) になることを確認済み
    base_date = date(1900, 1, 1)
    base_index = 27  # 辛卯

    delta = (birthday - base_date).days
    return (base_index + delta) % 60


def _kanshi_str(index: int) -> str:
    """六十干支のインデックスから干支文字列を返す"""
    return ROKUJU_KANSHI[index % 60]


def _gogyo_relationship(gogyo_a: str, gogyo_b: str) -> tuple:
    """二つの五行の関係を判定"""
    if gogyo_a == gogyo_b:
        return ("比和", "同じ五行同士で共鳴し合う関係")
    if SOSHO.get(gogyo_a) == gogyo_b:
        return ("相生（生む）", f"{gogyo_a}が{gogyo_b}を生む、支援的な関係")
    if SOSHO.get(gogyo_b) == gogyo_a:
        return ("相生（生まれる）", f"{gogyo_b}が{gogyo_a}を生む、助けられる関係")
    if SOKOKU.get(gogyo_a) == gogyo_b:
        return ("相剋（剋す）", f"{gogyo_a}が{gogyo_b}を剋す、チャレンジのある関係")
    if SOKOKU.get(gogyo_b) == gogyo_a:
        return ("相剋（剋される）", f"{gogyo_b}が{gogyo_a}を剋す、試練を与えられる関係")
    return ("その他", "間接的な関係")


def _check_kango(kan_a: str, kan_b: str) -> bool:
    """干合（天干の合）を判定"""
    for pair in KANGO_PAIRS:
        if (kan_a in pair and kan_b in pair and kan_a != kan_b):
            return True
    return False


def _check_shigo(shi_a: str, shi_b: str) -> bool:
    """支合を判定"""
    for pair in SHIGO_PAIRS:
        if shi_a in pair and shi_b in pair and shi_a != shi_b:
            return True
    return False


def _check_sango(shi_a: str, shi_b: str) -> list:
    """三合の一部を判定"""
    results = []
    for group in SANGO_GROUPS:
        if shi_a in group and shi_b in group:
            results.append(group)
    return results


def _check_taichu(shi_a: str, shi_b: str) -> bool:
    """対冲を判定"""
    for pair in TAICHU_PAIRS:
        if shi_a in pair and shi_b in pair:
            return True
    return False


def _check_ha(shi_a: str, shi_b: str) -> bool:
    """破を判定"""
    for pair in HA_PAIRS:
        if shi_a in pair and shi_b in pair:
            return True
    return False


def calculate(person_a: dict, person_b: dict) -> dict:
    """四柱推命の相性を計算する"""
    bd_a = person_a["birthday"]
    bd_b = person_b["birthday"]
    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    # 年柱・月柱・日柱の算出
    year_a = _year_pillar(bd_a)
    month_a = _month_pillar(bd_a)
    day_a = _day_pillar(bd_a)

    year_b = _year_pillar(bd_b)
    month_b = _month_pillar(bd_b)
    day_b = _day_pillar(bd_b)

    year_a_str = _kanshi_str(year_a)
    month_a_str = _kanshi_str(month_a)
    day_a_str = _kanshi_str(day_a)

    year_b_str = _kanshi_str(year_b)
    month_b_str = _kanshi_str(month_b)
    day_b_str = _kanshi_str(day_b)

    # 日柱の天干の五行で基本相性を判定
    day_kan_a = day_a_str[0]
    day_kan_b = day_b_str[0]
    day_gogyo_a = JIKKAN_GOGYO[day_kan_a]
    day_gogyo_b = JIKKAN_GOGYO[day_kan_b]

    relationship, rel_desc = _gogyo_relationship(day_gogyo_a, day_gogyo_b)

    # スコア算出
    base_score = 60
    bonus = 0
    highlights = []
    special_relations = []

    # 五行関係によるベーススコア
    if relationship == "比和":
        base_score = 75
    elif "相生" in relationship:
        base_score = 80
    elif "相剋" in relationship:
        base_score = 45

    highlights.append(f"{name_a}: 年柱={year_a_str}、月柱={month_a_str}、日柱={day_a_str}")
    highlights.append(f"{name_b}: 年柱={year_b_str}、月柱={month_b_str}、日柱={day_b_str}")
    highlights.append(f"日柱の五行: {name_a}={day_gogyo_a}（{day_kan_a}）、{name_b}={day_gogyo_b}（{day_kan_b}）")
    highlights.append(f"五行の関係: {relationship} — {rel_desc}")

    # 月柱一致チェック
    if month_a_str == month_b_str:
        bonus += 15
        special_relations.append("月柱完全一致")
        highlights.append(f"★ 月柱が完全一致（{month_a_str}）！ 価値観や感情面で深い共鳴があります")

    # 干合チェック（日柱同士）
    if _check_kango(day_kan_a, day_kan_b):
        bonus += 12
        special_relations.append("日干合")
        highlights.append(f"★ 日柱の天干が干合（{day_kan_a}×{day_kan_b}）！ 強い引力で結ばれる関係です")

    # 年干合チェック
    year_kan_a = year_a_str[0]
    year_kan_b = year_b_str[0]
    if _check_kango(year_kan_a, year_kan_b):
        bonus += 8
        special_relations.append("年干合")
        highlights.append(f"★ 年柱の天干が干合（{year_kan_a}×{year_kan_b}）！ 社会的な縁が深い関係です")

    # 支合チェック
    day_shi_a = day_a_str[1]
    day_shi_b = day_b_str[1]
    if _check_shigo(day_shi_a, day_shi_b):
        bonus += 10
        special_relations.append("日支合")
        highlights.append(f"★ 日柱の地支が支合（{day_shi_a}×{day_shi_b}）！ 深い情愛で結ばれます")

    year_shi_a = year_a_str[1]
    year_shi_b = year_b_str[1]
    if _check_shigo(year_shi_a, year_shi_b):
        bonus += 5
        special_relations.append("年支合")

    # 三合チェック
    sango = _check_sango(day_shi_a, day_shi_b)
    if sango:
        bonus += 8
        special_relations.append("三合")
        highlights.append(f"★ 日柱の地支が三合の一部！ 協力し合える関係です")

    # 対冲チェック
    if _check_taichu(day_shi_a, day_shi_b):
        bonus -= 10
        special_relations.append("日支対冲")
        highlights.append(f"▲ 日柱の地支が対冲（{day_shi_a}×{day_shi_b}）。衝突もありますが、強い縁を示します")

    if _check_taichu(year_shi_a, year_shi_b):
        bonus -= 5
        special_relations.append("年支対冲")

    # 破チェック
    if _check_ha(day_shi_a, day_shi_b):
        bonus -= 5
        special_relations.append("日支破")

    score_100 = max(0, min(100, base_score + bonus))
    score = round(score_100 / 20)
    score = max(1, min(5, score))

    # アドバイス
    advice_parts = []
    if "月柱完全一致" in special_relations:
        advice_parts.append("月柱の完全一致は非常に珍しく、価値観や感情面で深い共鳴がある証です。命式における月柱は社会性と内面を司るため、この一致は精神的な絆の強さを意味します。共通の価値観を土台に、互いの人生目標を支え合いましょう。")
    if "日干合" in special_relations:
        advice_parts.append("日干合は最も強い縁を示し、運命的な出会いと言えます。干合とは陰陽の天干が引き合う現象で、四柱推命において最も深い結びつきの象徴です。この特別な縁を大切にし、互いの日干が持つ五行の力を活かしてください。")
    if relationship == "比和":
        advice_parts.append("同じ五行同士の比和の関係は、自然と分かり合える安定した絆を生みます。共鳴しやすい反面、同質性ゆえに成長が停滞しないよう、新たな刺激を取り入れる工夫が大切です。")
    elif "相生" in relationship:
        advice_parts.append("五行相生の関係は、一方が他方を自然に育てる循環の力を持ちます。木→火→土→金→水の生成サイクルに基づき、互いのエネルギーが好循環を生むでしょう。与え合う関係を意識して、双方向の支え合いを大切にしてください。")
    elif "相剋" in relationship:
        advice_parts.append("五行相剋の関係は緊張感を伴いますが、その摩擦こそが互いの成長を促す原動力となります。剋する側は抑制を意識し、剋される側は柔軟さを持つことで、関係のバランスが整うでしょう。")

    if not advice_parts:
        advice_map = {
            5: "四柱推命的に最高の相性です。天干地支の組み合わせが示す強い縁を大切にしてください。命式の調和が自然な信頼関係を支えてくれるでしょう。",
            4: "四柱推命的にとても良い相性です。互いの命式が補い合い、運気を高め合える関係です。五行のバランスを意識した生活が吉を呼びます。",
            3: "四柱推命的にバランスの取れた相性です。命式上の中庸な関係は、お互いを尊重する姿勢によって確かな絆へと育ちます。日々の小さな思いやりを積み重ねましょう。",
            2: "四柱推命的にやや課題のある相性ですが、命式の相剋を乗り越える経験が絆を深めます。互いの五行の弱点を理解し、補い合う意識を持ちましょう。",
            1: "四柱推命的に試練の多い相性ですが、困難を共に超えることで大きな成長をもたらす関係です。命式の衝突を学びの機会と捉え、忍耐と対話を重ねてください。",
        }
        advice_parts.append(advice_map.get(score, ""))

    return {
        "name": "四柱推命",
        "category": "shichusuimei",
        "icon": "temple_buddhist",
        "score": score,
        "score_100": score_100,
        "summary": f"日柱 {day_a_str} × {day_b_str} の命式相性",
        "details": {
            "person_a": {
                "year_pillar": year_a_str,
                "month_pillar": month_a_str,
                "day_pillar": day_a_str,
                "day_gogyo": day_gogyo_a,
            },
            "person_b": {
                "year_pillar": year_b_str,
                "month_pillar": month_b_str,
                "day_pillar": day_b_str,
                "day_gogyo": day_gogyo_b,
            },
            "relationship": relationship,
            "special_relations": special_relations,
        },
        "highlights": highlights,
        "advice": "".join(advice_parts),
    }
