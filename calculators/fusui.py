"""風水（居住地方角）相性分析エンジン
二人の出生地・居住地の方角関係から風水的相性を分析する。
出生地が未入力の場合はMBTIの五行推定でフォールバック。
"""

import math

CATEGORY = "その他占い"

# 主要都市の緯度経度テーブル（簡易版）
CITY_COORDS = {
    "東京": (35.6762, 139.6503),
    "東京都": (35.6762, 139.6503),
    "港区": (35.6585, 139.7514),
    "東京都港区": (35.6585, 139.7514),
    "中央区": (35.6706, 139.7720),
    "東京都中央区": (35.6706, 139.7720),
    "晴海": (35.6596, 139.7838),
    "築地": (35.6654, 139.7707),
    "新宿": (35.6938, 139.7034),
    "東京都新宿区": (35.6938, 139.7034),
    "渋谷": (35.6580, 139.7016),
    "東京都渋谷区": (35.6580, 139.7016),
    "世田谷": (35.6461, 139.6532),
    "東京都世田谷区": (35.6461, 139.6532),
    "品川": (35.6090, 139.7300),
    "東京都品川区": (35.6090, 139.7300),
    "目黒": (35.6414, 139.6982),
    "東京都目黒区": (35.6414, 139.6982),
    "豊島区": (35.7263, 139.7171),
    "東京都豊島区": (35.7263, 139.7171),
    "横浜": (35.4437, 139.6380),
    "神奈川": (35.4437, 139.6380),
    "大阪": (34.6937, 135.5023),
    "大阪府": (34.6937, 135.5023),
    "大阪府大阪市": (34.6937, 135.5023),
    "名古屋": (35.1815, 136.9066),
    "愛知": (35.1815, 136.9066),
    "福岡": (33.5902, 130.4017),
    "札幌": (43.0618, 141.3545),
    "北海道": (43.0618, 141.3545),
    "仙台": (38.2682, 140.8694),
    "宮城": (38.2682, 140.8694),
    "広島": (34.3853, 132.4553),
    "京都": (35.0116, 135.7681),
    "神戸": (34.6901, 135.1956),
    "佐賀": (33.2494, 130.2988),
    "佐賀県": (33.2494, 130.2988),
    "伊万里": (33.2645, 129.8831),
    "佐賀県伊万里市": (33.2645, 129.8831),
    "埼玉": (35.8616, 139.6455),
    "千葉": (35.6047, 140.1233),
    "千葉県千葉市": (35.6047, 140.1233),
    "月島": (35.6624, 139.7826),
    "豊洲": (35.6533, 139.7960),
    "秋田": (39.7200, 140.1025),
    "秋田県": (39.7200, 140.1025),
    "秋田県大仙市": (39.4530, 140.4770),
    "大仙市": (39.4530, 140.4770),
    "大仙": (39.4530, 140.4770),
    "沖縄": (26.3344, 127.8056),
    "沖縄県那覇市": (26.3344, 127.8056),
    "那覇": (26.3344, 127.8056),
    "長野": (36.6513, 138.1810),
    "長野県長野市": (36.6513, 138.1810),
    "新潟": (37.9026, 139.0236),
    "新潟県新潟市": (37.9026, 139.0236),
    "静岡": (34.9756, 138.3828),
    "静岡県浜松市": (34.7081, 137.7265),
    "浜松": (34.7081, 137.7265),
    "愛知県名古屋市": (35.1815, 136.9066),
    "神奈川県横浜市": (35.4437, 139.6380),
    "福岡県福岡市": (33.5902, 130.4017),
    "福岡県北九州市": (33.8835, 130.8752),
    "北九州": (33.8835, 130.8752),
    "広島県広島市": (34.3853, 132.4553),
    "宮城県仙台市": (38.2682, 140.8694),
    "京都府京都市": (35.0116, 135.7681),
    "兵庫県神戸市": (34.6901, 135.1956),
    "北海道札幌市": (43.0618, 141.3545),
    "福島": (37.7503, 140.4676),
    "福島県": (37.7503, 140.4676),
    "双葉町": (37.4514, 141.0136),
    "双葉郡": (37.4514, 141.0136),
    "福島県双葉郡双葉町": (37.4514, 141.0136),
    "福島県双葉郡": (37.4514, 141.0136),
}

# 八方位の風水的意味
DIRECTION_MEANING = {
    "北": ("水", "信頼・秘密・静寂", "深い信頼関係を築ける方角"),
    "北東": ("土", "変化・再生・山", "関係に変化と成長をもたらす方角"),
    "東": ("木", "成長・発展・希望", "関係が成長し発展する方角"),
    "東南": ("木", "縁・信用・調和", "縁結びに最も良い方角"),
    "南": ("火", "情熱・名声・輝き", "情熱的で華やかな関係になる方角"),
    "南西": ("土", "家庭・安定・母性", "家庭的で安定した関係を育む方角"),
    "西": ("金", "喜び・豊かさ・収穫", "実りある関係になる方角"),
    "北西": ("金", "天の助け・指導者", "互いを高め合う関係になる方角"),
}

# 方角の相性スコア（恋愛における吉方位）
DIRECTION_LOVE_SCORE = {
    "東南": (5, 95, "縁結びの最吉方位。出会いと信頼を司る"),
    "東": (5, 90, "成長の方位。共に発展できる関係"),
    "南": (4, 85, "情熱の方位。華やかで魅力的な関係"),
    "南西": (4, 82, "家庭の方位。安定した愛を育む"),
    "北": (3, 75, "信頼の方位。静かだが深い絆"),
    "西": (3, 75, "喜びの方位。楽しい時間を共有できる"),
    "北西": (3, 72, "成熟の方位。年長者との縁に強い"),
    "北東": (3, 70, "変化の方位。刺激はあるが不安定さも"),
}

# MBTI五行推定（出生地不明時のフォールバック）
MBTI_TO_ELEMENT = {
    "INFJ": "水", "ISFJ": "土", "INTJ": "水", "INTP": "金",
    "ENTJ": "木", "ENTP": "火", "INFP": "水", "ENFJ": "火",
    "ENFP": "火", "ISTJ": "土", "ESTJ": "金", "ESFJ": "土",
    "ISTP": "金", "ISFP": "土", "ESTP": "金", "ESFP": "火",
}

# 五行相性
ELEMENT_COMPAT = {
    ("木", "火"): (4, 82, "木生火: 木が火を育てる相生関係"),
    ("火", "土"): (4, 82, "火生土: 火が土を育てる相生関係"),
    ("土", "金"): (4, 82, "土生金: 土が金を育てる相生関係"),
    ("金", "水"): (4, 82, "金生水: 金が水を育てる相生関係"),
    ("水", "木"): (4, 82, "水生木: 水が木を育てる相生関係"),
    ("木", "土"): (2, 55, "木剋土: 木が土を剋す相剋関係"),
    ("土", "水"): (2, 55, "土剋水: 土が水を剋す相剋関係"),
    ("水", "火"): (2, 55, "水剋火: 水が火を剋す相剋関係"),
    ("火", "金"): (2, 55, "火剋金: 火が金を剋す相剋関係"),
    ("金", "木"): (2, 55, "金剋木: 金が木を剋す相剋関係"),
    ("木", "木"): (3, 72, "比和: 同じ五行。安心感はあるが刺激が少ない"),
    ("火", "火"): (3, 72, "比和: 同じ五行。情熱的だが燃え尽き注意"),
    ("土", "土"): (3, 75, "比和: 同じ五行。安定するが変化に弱い"),
    ("金", "金"): (3, 72, "比和: 同じ五行。堅実だが柔軟さが課題"),
    ("水", "水"): (3, 72, "比和: 同じ五行。深い共感力だが流されやすい"),
}


def _find_coords(place: str):
    """地名から緯度経度を検索"""
    if not place:
        return None
    place = place.strip()
    if place in CITY_COORDS:
        return CITY_COORDS[place]
    # 部分一致で検索
    for key, coords in CITY_COORDS.items():
        if key in place or place in key:
            return coords
    return None


def _calc_direction(lat1, lon1, lat2, lon2) -> str:
    """2地点間の方角を八方位で返す（地点1から見た地点2の方角）"""
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    angle = math.degrees(math.atan2(dlon, dlat))
    if angle < 0:
        angle += 360

    if 337.5 <= angle or angle < 22.5:
        return "北"
    elif 22.5 <= angle < 67.5:
        return "北東"
    elif 67.5 <= angle < 112.5:
        return "東"
    elif 112.5 <= angle < 157.5:
        return "東南"
    elif 157.5 <= angle < 202.5:
        return "南"
    elif 202.5 <= angle < 247.5:
        return "南西"
    elif 247.5 <= angle < 292.5:
        return "西"
    else:
        return "北西"


def _calc_distance_km(lat1, lon1, lat2, lon2) -> float:
    """2地点間の距離（km）を概算"""
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def calculate(person_a: dict, person_b: dict) -> dict:
    """風水的相性を計算する"""
    place_a = person_a.get('birthplace', '')
    place_b = person_b.get('birthplace', '')
    coords_a = _find_coords(place_a)
    coords_b = _find_coords(place_b)

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    # 出生地が両方判明している場合：方角ベースの分析
    if coords_a and coords_b:
        direction = _calc_direction(coords_a[0], coords_a[1], coords_b[0], coords_b[1])
        distance = _calc_distance_km(coords_a[0], coords_a[1], coords_b[0], coords_b[1])
        element, meaning, desc = DIRECTION_MEANING[direction]
        score, score_100, love_desc = DIRECTION_LOVE_SCORE[direction]

        # 距離による補正
        if 3 <= distance <= 30:
            dist_note = f"距離{distance:.0f}km: 近すぎず遠すぎない理想的な距離"
        elif distance < 3:
            dist_note = f"距離{distance:.1f}km: 非常に近い。日常的な縁が深い"
        else:
            dist_note = f"距離{distance:.0f}km: 距離がある分、会う時間が特別になる"

        return {
            "name": "風水",
            "category": "fusui",
            "icon": "explore",
            "score": score,
            "score_100": score_100,
            "summary": f"{place_a}から{place_b}は{direction}方向 - {love_desc}",
            "details": {
                "direction": direction,
                "element": element,
                "distance_km": round(distance, 1),
            },
            "highlights": [
                f"{name_a}({place_a})から{name_b}({place_b})は{direction}方向",
                f"{direction}の意味: {meaning} - {desc}",
                dist_note,
            ],
            "advice": f"二人の間の{direction}方向は「{element}」の気。{love_desc}。",
        }

    # 出生地不明の場合：MBTIの五行推定でフォールバック
    mbti_a = (person_a.get('mbti') or '').upper().replace("-A", "").replace("-T", "").strip()
    mbti_b = (person_b.get('mbti') or '').upper().replace("-A", "").replace("-T", "").strip()
    if not mbti_a or not mbti_b:
        return None

    elem_a = MBTI_TO_ELEMENT.get(mbti_a, "土")
    elem_b = MBTI_TO_ELEMENT.get(mbti_b, "土")

    key = (elem_a, elem_b)
    rev_key = (elem_b, elem_a)
    result = ELEMENT_COMPAT.get(key) or ELEMENT_COMPAT.get(rev_key, (3, 70, ""))
    score, score_100, summary = result

    return {
        "name": "風水",
        "category": "fusui",
        "icon": "explore",
        "score": score,
        "score_100": score_100,
        "summary": f"五行: {elem_a}({name_a}) x {elem_b}({name_b}) - {summary}",
        "details": {
            "element_a": elem_a,
            "element_b": elem_b,
        },
        "highlights": [
            f"{name_a}の五行(MBTI推定): {elem_a}",
            f"{name_b}の五行(MBTI推定): {elem_b}",
            "出生地を入力すると方角ベースの精密な分析が可能です",
        ],
        "advice": summary,
    }
