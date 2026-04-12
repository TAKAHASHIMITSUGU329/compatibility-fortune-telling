"""宿曜占術（27宿）計算エンジン"""

import json
import os
from datetime import date, datetime

CATEGORY = "東洋占術"

# 27宿の定義
NIJUSHICHI_SHUKU = [
    {"name": "角宿", "reading": "かくしゅく", "group": "東方七宿"},
    {"name": "亢宿", "reading": "こうしゅく", "group": "東方七宿"},
    {"name": "氐宿", "reading": "ていしゅく", "group": "東方七宿"},
    {"name": "房宿", "reading": "ぼうしゅく", "group": "東方七宿"},
    {"name": "心宿", "reading": "しんしゅく", "group": "東方七宿"},
    {"name": "尾宿", "reading": "びしゅく", "group": "東方七宿"},
    {"name": "箕宿", "reading": "きしゅく", "group": "東方七宿"},
    {"name": "斗宿", "reading": "としゅく", "group": "北方七宿"},
    {"name": "牛宿", "reading": "ぎゅうしゅく", "group": "北方七宿"},
    {"name": "女宿", "reading": "じょしゅく", "group": "北方七宿"},
    {"name": "虚宿", "reading": "きょしゅく", "group": "北方七宿"},
    {"name": "危宿", "reading": "きしゅく", "group": "北方七宿"},
    {"name": "室宿", "reading": "しつしゅく", "group": "北方七宿"},
    {"name": "壁宿", "reading": "へきしゅく", "group": "北方七宿"},
    {"name": "奎宿", "reading": "けいしゅく", "group": "西方七宿"},
    {"name": "婁宿", "reading": "ろうしゅく", "group": "西方七宿"},
    {"name": "胃宿", "reading": "いしゅく", "group": "西方七宿"},
    {"name": "昴宿", "reading": "ぼうしゅく", "group": "西方七宿"},
    {"name": "畢宿", "reading": "ひつしゅく", "group": "西方七宿"},
    {"name": "觜宿", "reading": "ししゅく", "group": "西方七宿"},
    {"name": "参宿", "reading": "さんしゅく", "group": "西方七宿"},
    {"name": "井宿", "reading": "せいしゅく", "group": "南方七宿"},
    {"name": "鬼宿", "reading": "きしゅく", "group": "南方七宿"},
    {"name": "柳宿", "reading": "りゅうしゅく", "group": "南方七宿"},
    {"name": "星宿", "reading": "せいしゅく", "group": "南方七宿"},
    {"name": "張宿", "reading": "ちょうしゅく", "group": "南方七宿"},
    {"name": "翼宿", "reading": "よくしゅく", "group": "南方七宿"},
]

# 宿名からインデックスへのマッピング
SHUKU_NAME_TO_IDX = {s["name"]: i for i, s in enumerate(NIJUSHICHI_SHUKU)}

# 宿の性格概要
SHUKU_PERSONALITY = {
    "角宿": "社交的で華やかなリーダータイプ。正義感が強い",
    "亢宿": "プライドが高く真面目。完璧主義的な面がある",
    "氐宿": "温和で協調性がある。地道な努力家",
    "房宿": "情熱的でエネルギッシュ。リーダーシップがある",
    "心宿": "繊細で感受性が強い。芸術的センスに優れる",
    "尾宿": "忍耐強く責任感がある。最後までやり遂げる力",
    "箕宿": "自由奔放で好奇心旺盛。独立心が強い",
    "斗宿": "信念が強くストイック。高い目標を持つ",
    "牛宿": "温厚で包容力がある。縁の下の力持ち",
    "女宿": "賢明で計算が得意。現実的な判断力がある",
    "虚宿": "理想主義で夢見がち。精神的な世界を大切にする",
    "危宿": "行動力があり冒険好き。波乱万丈な人生",
    "室宿": "積極的で開拓精神旺盛。新しいことに挑む",
    "壁宿": "知的で学問好き。文化的な活動に長ける",
    "奎宿": "芸術的センスに優れ、美意識が高い",
    "婁宿": "人望があり仲間に恵まれる。調整力がある",
    "胃宿": "負けず嫌いで競争心が強い。パワフル",
    "昴宿": "上品で気高い。人を惹きつける魅力がある",
    "畢宿": "堅実で粘り強い。信頼される存在",
    "觜宿": "知的で弁が立つ。分析力に優れる",
    "参宿": "華やかで目立つ存在。カリスマ性がある",
    "井宿": "計画性があり合理的。知恵者",
    "鬼宿": "直感力に優れ、霊感が強い。独特の感性",
    "柳宿": "情熱的で感情豊か。芸術的な才能がある",
    "星宿": "華やかでプライドが高い。自分の信念を貫く",
    "張宿": "社交的で魅力的。人間関係を大切にする",
    "翼宿": "堅実で努力家。コツコツと成果を積み上げる",
}

# 旧暦の月日から27宿を求めるテーブル
# 旧暦月ごとの1日の宿インデックス（0-26）
# このテーブルは伝統的な宿曜経に基づく
LUNAR_MONTH_BASE_SHUKU = {
    1: 14,   # 1月1日 = 奎宿(14)
    2: 22,   # 2月1日 = 鬼宿(22)
    3: 2,    # 3月1日 = 氐宿(2)
    4: 10,   # 4月1日 = 虚宿(10)
    5: 17,   # 5月1日 = 昴宿(17)
    6: 25,   # 6月1日 = 張宿(25)
    7: 5,    # 7月1日 = 心宿(5)
    8: 13,   # 8月1日 = 壁宿(13)
    9: 20,   # 9月1日 = 参宿(20)
    10: 1,   # 10月1日 = 亢宿(1)
    11: 8,   # 11月1日 = 牛宿(8)
    12: 16,  # 12月1日 = 胃宿(16)
}


def _get_lunar_date(birthday: date):
    """旧暦の月日を取得（cnlunarライブラリを使用）"""
    try:
        import cnlunar
        dt = datetime(birthday.year, birthday.month, birthday.day)
        lunar = cnlunar.Lunar(dt)
        return lunar.lunarMonth, lunar.lunarDay
    except Exception:
        pass

    # フォールバック：新暦→旧暦の近似変換
    # 旧暦は新暦より概ね30〜50日遅れ。年によって異なるため
    # 精度は限定的だが、cnlunarが使えない場合の代替手段。
    # 旧暦新年は概ね1月下旬〜2月中旬に来るため、約35日の遅延を仮定する。
    from datetime import timedelta
    approx_lunar_date = birthday - timedelta(days=35)
    approx_month = approx_lunar_date.month
    approx_day = approx_lunar_date.day
    # 旧暦の月は1-12
    if approx_month < 1:
        approx_month = 12
    return approx_month, approx_day


def _get_shuku_index(lunar_month: int, lunar_day: int) -> int:
    """旧暦の月日から27宿のインデックスを求める"""
    base = LUNAR_MONTH_BASE_SHUKU.get(lunar_month, 0)
    # 1日を基準に日を加算
    idx = (base + lunar_day - 1) % 27
    return idx


def _get_shuku(birthday: date) -> dict:
    """生年月日から宿を判定"""
    lunar_month, lunar_day = _get_lunar_date(birthday)
    idx = _get_shuku_index(lunar_month, lunar_day)
    shuku = NIJUSHICHI_SHUKU[idx]
    return {
        "index": idx,
        "name": shuku["name"],
        "reading": shuku["reading"],
        "group": shuku["group"],
        "personality": SHUKU_PERSONALITY.get(shuku["name"], ""),
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
    }


# 宿縁関係の定義
# 自分の宿から相手の宿までの距離（0-26）に基づく関係
SHUKUEN_RELATIONS = {
    0: {"name": "命", "reading": "めい", "desc": "同じ宿同士。最も深い因縁で結ばれた関係。良くも悪くも強い影響を与え合う", "score": 85},
    9: {"name": "業", "reading": "ごう", "desc": "前世からの業（カルマ）で結ばれた関係。深い学びがある", "score": 70},
    18: {"name": "胎", "reading": "たい", "desc": "来世への種まきの関係。未来に向かって発展する可能性を秘める", "score": 93},
    # 栄親（近距離）
    1: {"name": "栄（近距離）", "reading": "えい", "desc": "互いに栄え合う良い関係。近距離で特に効果的", "score": 90},
    26: {"name": "親（近距離）", "reading": "しん", "desc": "親しみやすく自然と仲良くなれる関係", "score": 88},
    # 栄親（中距離）
    5: {"name": "栄（中距離）", "reading": "えい", "desc": "栄え合う関係。中距離でバランスが良い", "score": 85},
    22: {"name": "親（中距離）", "reading": "しん", "desc": "親しみのある関係。適度な距離感", "score": 83},
    # 栄親（遠距離）
    10: {"name": "栄（遠距離）", "reading": "えい", "desc": "栄え合う関係だが距離があり発展に時間がかかる", "score": 78},
    17: {"name": "親（遠距離）", "reading": "しん", "desc": "親しみはあるが深い関係になるには努力が必要", "score": 76},
    # 友衰（近距離）
    2: {"name": "友（近距離）", "reading": "ゆう", "desc": "友人として最適。気楽で楽しい関係", "score": 82},
    25: {"name": "衰（近距離）", "reading": "すい", "desc": "相手に尽くしがちな関係。バランスに注意", "score": 55},
    # 友衰（中距離）
    6: {"name": "友（中距離）", "reading": "ゆう", "desc": "友人関係として安定。信頼し合える", "score": 78},
    21: {"name": "衰（中距離）", "reading": "すい", "desc": "やや消耗しやすい関係。休息が大切", "score": 50},
    # 友衰（遠距離）
    11: {"name": "友（遠距離）", "reading": "ゆう", "desc": "友好的だが深い関係になりにくい", "score": 72},
    16: {"name": "衰（遠距離）", "reading": "すい", "desc": "距離を保つことで良好な関係が維持できる", "score": 48},
    # 安壊（近距離）
    3: {"name": "安（近距離）", "reading": "あん", "desc": "安らぎを感じる関係だが、相手を壊す可能性も", "score": 65},
    24: {"name": "壊（近距離）", "reading": "かい", "desc": "壊される側。強烈な引力があるが危険も伴う", "score": 45},
    # 安壊（中距離）
    7: {"name": "安（中距離）", "reading": "あん", "desc": "安心感のある関係。適度な距離で安定", "score": 62},
    20: {"name": "壊（中距離）", "reading": "かい", "desc": "壊される関係だが学びも大きい", "score": 42},
    # 安壊（遠距離）
    12: {"name": "安（遠距離）", "reading": "あん", "desc": "遠くから見守る安心感。穏やかな関係", "score": 60},
    15: {"name": "壊（遠距離）", "reading": "かい", "desc": "影響は弱いが注意が必要な関係", "score": 40},
    # 成危（近距離）
    4: {"name": "危（近距離）", "reading": "き", "desc": "危うさを含む刺激的な関係。スリルがある", "score": 58},
    23: {"name": "成（近距離）", "reading": "せい", "desc": "成し遂げる力が生まれる関係。発展的", "score": 80},
    # 成危（中距離）
    8: {"name": "危（中距離）", "reading": "き", "desc": "やや不安定な関係。慎重さが必要", "score": 55},
    19: {"name": "成（中距離）", "reading": "せい", "desc": "互いに成長を促す関係", "score": 75},
    # 成危（遠距離）
    13: {"name": "危（遠距離）", "reading": "き", "desc": "影響は弱いがやや不安定", "score": 52},
    14: {"name": "成（遠距離）", "reading": "せい", "desc": "成長の関係だが距離があり実感しにくい", "score": 70},
}


# 同一七宿グループ内の特別な胎宿関係
# 宿曜占術では、同じ七宿グループ（同じ方角の守護神獣を持つ宿同士）で
# 近距離にある宿は「胎宿（たいしゅく）」の縁とされ、前世からの魂の繋がりを持つ。
# これは三九の秘法（距離9/18）とは別系統の胎の判定で、
# 同一グループ内の近接宿に適用される特別な関係性。
SAME_GROUP_TAI = {
    "name": "胎（近距離）",
    "reading": "たい",
    "desc": "同じ七宿グループに属する近距離の胎宿関係。前世からの魂の縁で結ばれ、来世でも再び出会う約束をした関係。日常レベルで魂が共鳴する",
    "score": 95,
}


def _get_relation(shuku_a_idx: int, shuku_b_idx: int) -> dict:
    """二人の宿の関係を判定"""
    shuku_a = NIJUSHICHI_SHUKU[shuku_a_idx]
    shuku_b = NIJUSHICHI_SHUKU[shuku_b_idx]

    # 同一七宿グループ内の近距離（1〜3宿差）は胎宿の関係
    if shuku_a["group"] == shuku_b["group"] and shuku_a_idx != shuku_b_idx:
        dist_forward = (shuku_b_idx - shuku_a_idx) % 27
        dist_backward = (shuku_a_idx - shuku_b_idx) % 27
        min_dist = min(dist_forward, dist_backward)
        if 1 <= min_dist <= 3:
            result = dict(SAME_GROUP_TAI)
            result["distance"] = dist_forward
            return result

    # A→Bの距離
    dist_ab = (shuku_b_idx - shuku_a_idx) % 27
    relation = SHUKUEN_RELATIONS.get(dist_ab)

    if relation is None:
        return {
            "name": "不明",
            "reading": "",
            "desc": "関係性を判定できません",
            "score": 50,
            "distance": dist_ab,
        }

    result = dict(relation)
    result["distance"] = dist_ab
    return result


def calculate(person_a: dict, person_b: dict) -> dict:
    """宿曜占術の相性を計算する"""
    bd_a = person_a["birthday"]
    bd_b = person_b["birthday"]
    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    shuku_a = _get_shuku(bd_a)
    shuku_b = _get_shuku(bd_b)

    # 関係を判定（A→BとB→Aの両方を見る）
    relation_ab = _get_relation(shuku_a["index"], shuku_b["index"])
    relation_ba = _get_relation(shuku_b["index"], shuku_a["index"])

    # 総合スコア（両方向の平均）
    score_100 = round((relation_ab["score"] + relation_ba["score"]) / 2)
    score_100 = max(0, min(100, score_100))
    score = round(score_100 / 20)
    score = max(1, min(5, score))

    highlights = [
        f"{name_a}の宿: {shuku_a['name']}（{shuku_a['reading']}）— {shuku_a['group']}",
        f"{name_b}の宿: {shuku_b['name']}（{shuku_b['reading']}）— {shuku_b['group']}",
        f"{shuku_a['personality']}",
        f"{shuku_b['personality']}",
        f"{name_a}→{name_b}: {relation_ab['name']}（{relation_ab['reading']}）の関係",
        f"　{relation_ab['desc']}",
    ]

    if relation_ab["name"] != relation_ba["name"]:
        highlights.append(f"{name_b}→{name_a}: {relation_ba['name']}（{relation_ba['reading']}）の関係")
        highlights.append(f"　{relation_ba['desc']}")

    # 特別な関係のハイライト
    if relation_ab["name"] == "命":
        highlights.append("★ 命の関係：最も深い因縁で結ばれた運命的な関係です")
    elif "栄" in relation_ab["name"] or "栄" in relation_ba["name"]:
        highlights.append("★ 栄親の関係：互いに栄え合い、発展する素晴らしい関係です")
    elif relation_ab["name"] == "業" or relation_ba["name"] == "業":
        highlights.append("★ 業の関係：前世からの深い縁で結ばれています")
    elif "胎" in relation_ab["name"] or "胎" in relation_ba["name"]:
        highlights.append("★ 胎宿の関係：前世からの魂の縁で結ばれた、来世まで続く深い関係です")

    # アドバイス
    advice_map = {
        5: f"{shuku_a['name']}と{shuku_b['name']}の宿縁は、27宿（ナクシャトラ）の配置において最も深い因縁で結ばれた関係です。宿曜経では「{relation_ab['name']}」の関係は前世からのカルマ（業）の成熟を示し、魂レベルでの強い共鳴が認められます。この天与の縁を大切にし、互いの宿が持つ守護力を信頼しながら共に歩んでいきましょう。",
        4: f"{shuku_a['name']}と{shuku_b['name']}は宿曜経における27宿の相関図で良好な宿縁を結んでいます。インド占星術のナクシャトラ理論では、栄親・友衰の関係性が互いのエネルギーを高め合う配置とされます。二人の宿が属する{shuku_a['group']}と{shuku_b['group']}の方位的な特性を活かし、互いの長所を引き出し合うことを心がけてください。",
        3: f"{shuku_a['name']}と{shuku_b['name']}の関係は、宿曜経の三九の秘法に基づくとバランスの取れた配置にあります。27宿（ナクシャトラ）はそれぞれ固有の守護星と性質を持ち、異なる宿同士の組み合わせが互いの成長を促すとされます。お互いの宿の性格的特徴を理解し、違いを補完し合う意識を持つことで関係がさらに深まるでしょう。",
        2: f"{shuku_a['name']}と{shuku_b['name']}は宿曜経において緊張をはらむ宿縁関係にありますが、これはカルマ的な学びの機会を意味します。27宿のナクシャトラ体系では、安壊や衰の関係も前世からの課題を克服するための必然的な出会いとされます。相手との距離感を適切に保ちつつ、互いの宿が示す課題に真摯に向き合うことで魂の成長が得られます。",
        1: f"{shuku_a['name']}と{shuku_b['name']}の宿縁は宿曜経で試練的な配置とされますが、最も大きな魂の成長をもたらす関係でもあります。インド由来の27宿（ナクシャトラ）理論では、壊や危の関係はカルマの精算と変容の契機を象徴します。困難を恐れず互いの宿が持つ本質的な力を認め合い、この関係から得られる深い気づきを人生の糧としてください。",
    }

    return {
        "name": "宿曜占術",
        "category": "shukuyo",
        "icon": "brightness_7",
        "score": score,
        "score_100": score_100,
        "summary": f"{shuku_a['name']} × {shuku_b['name']} の宿縁",
        "details": {
            "person_a": {
                "shuku": shuku_a["name"],
                "reading": shuku_a["reading"],
                "group": shuku_a["group"],
                "personality": shuku_a["personality"],
                "lunar_month": shuku_a["lunar_month"],
                "lunar_day": shuku_a["lunar_day"],
            },
            "person_b": {
                "shuku": shuku_b["name"],
                "reading": shuku_b["reading"],
                "group": shuku_b["group"],
                "personality": shuku_b["personality"],
                "lunar_month": shuku_b["lunar_month"],
                "lunar_day": shuku_b["lunar_day"],
            },
            "relation_ab": {
                "name": relation_ab["name"],
                "reading": relation_ab["reading"],
                "description": relation_ab["desc"],
                "distance": relation_ab["distance"],
            },
            "relation_ba": {
                "name": relation_ba["name"],
                "reading": relation_ba["reading"],
                "description": relation_ba["desc"],
                "distance": relation_ba["distance"],
            },
        },
        "highlights": highlights,
        "advice": advice_map.get(score, ""),
    }
