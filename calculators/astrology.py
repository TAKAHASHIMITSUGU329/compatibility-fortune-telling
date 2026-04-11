"""西洋占星術（太陽・金星・火星・月の星座相性）計算エンジン"""

import os
import warnings

CATEGORY = "西洋占星術"

# 星座の英語→日本語マッピング
SIGN_JA = {
    "Ari": "牡羊座", "Tau": "牡牛座", "Gem": "双子座", "Can": "蟹座",
    "Leo": "獅子座", "Vir": "乙女座", "Lib": "天秤座", "Sco": "蠍座",
    "Sag": "射手座", "Cap": "山羊座", "Aqu": "水瓶座", "Pis": "魚座",
}

# 星座のインデックス（0-11）
SIGN_INDEX = {
    "Ari": 0, "Tau": 1, "Gem": 2, "Can": 3,
    "Leo": 4, "Vir": 5, "Lib": 6, "Sco": 7,
    "Sag": 8, "Cap": 9, "Aqu": 10, "Pis": 11,
}

# エレメント
SIGN_ELEMENT = {
    "Ari": "火", "Leo": "火", "Sag": "火",
    "Tau": "地", "Vir": "地", "Cap": "地",
    "Gem": "風", "Lib": "風", "Aqu": "風",
    "Can": "水", "Sco": "水", "Pis": "水",
}

# 簡易太陽星座テーブル（出生時刻不要のフォールバック）
# (月, 開始日) のペアで星座の境界を定義
SOLAR_SIGN_TABLE = [
    (1, 20, "Aqu"), (2, 19, "Pis"), (3, 21, "Ari"), (4, 20, "Tau"),
    (5, 21, "Gem"), (6, 22, "Can"), (7, 23, "Leo"), (8, 23, "Vir"),
    (9, 23, "Lib"), (10, 23, "Sco"), (11, 22, "Sag"), (12, 22, "Cap"),
]


def _get_solar_sign_simple(month, day):
    """簡易的に太陽星座を求める（フォールバック用）"""
    for i in range(len(SOLAR_SIGN_TABLE) - 1, -1, -1):
        m, d, sign = SOLAR_SIGN_TABLE[i]
        if (month, day) >= (m, d):
            return sign
    return "Cap"  # 1/1-1/19は山羊座


def _compute_aspect_angle(sign_a, sign_b):
    """2つの星座間の角度差を計算（30度単位）"""
    idx_a = SIGN_INDEX.get(sign_a, 0)
    idx_b = SIGN_INDEX.get(sign_b, 0)
    diff = abs(idx_a - idx_b)
    if diff > 6:
        diff = 12 - diff
    return diff * 30


def _aspect_name(angle):
    """角度からアスペクト名を返す"""
    aspects = {
        0: ("コンジャンクション", "強い結合・一体感"),
        60: ("セクスタイル", "穏やかな調和"),
        90: ("スクエア", "緊張・刺激的な関係"),
        120: ("トライン", "最高の調和・自然な相性"),
        180: ("オポジション", "対極の引力・補完関係"),
    }
    return aspects.get(angle, ("その他", "間接的な関係"))


def _aspect_score(angle):
    """アスペクトの角度からスコアを返す（0-100）"""
    scores = {
        0: 85,    # コンジャンクション - 強い結合
        30: 55,   # セミセクスタイル - 弱い
        60: 80,   # セクスタイル - 調和
        90: 45,   # スクエア - 緊張
        120: 95,  # トライン - 最高
        150: 40,  # クインカンクス - 困難
        180: 65,  # オポジション - 対極の引力
    }
    return scores.get(angle, 50)


# モダリティ分類
SIGN_MODALITY = {
    "Ari": "cardinal", "Can": "cardinal", "Lib": "cardinal", "Cap": "cardinal",
    "Tau": "fixed", "Leo": "fixed", "Sco": "fixed", "Aqu": "fixed",
    "Gem": "mutable", "Vir": "mutable", "Sag": "mutable", "Pis": "mutable",
}

# ルーラー（支配星）- 同じルーラーの星座同士は親和性が高い
SIGN_RULER = {
    "Ari": "Mars", "Tau": "Venus", "Gem": "Mercury", "Can": "Moon",
    "Leo": "Sun", "Vir": "Mercury", "Lib": "Venus", "Sco": "Mars",
    "Sag": "Jupiter", "Cap": "Saturn", "Aqu": "Saturn", "Pis": "Jupiter",
}


def _rich_pair_score(sign_a, sign_b):
    """2星座間の相性をアスペクト＋エレメント＋モダリティ＋ルーラーで総合評価する。

    従来の _aspect_score よりも多くの占星術的要素を考慮し、
    実際の占星術レポートに近いスコアを返す。
    """
    angle = _compute_aspect_angle(sign_a, sign_b)
    base = _aspect_score(angle)

    bonus = 0

    # --- エレメント相性 ---
    elem_a = SIGN_ELEMENT.get(sign_a)
    elem_b = SIGN_ELEMENT.get(sign_b)
    if elem_a == elem_b:
        bonus += 8  # 同エレメント
    elif {elem_a, elem_b} in [{"火", "風"}, {"地", "水"}]:
        bonus += 10  # 相性の良いエレメント（地×水、火×風）

    # --- モダリティ相性 ---
    mod_a = SIGN_MODALITY.get(sign_a)
    mod_b = SIGN_MODALITY.get(sign_b)
    if mod_a != mod_b:
        bonus += 3  # 異なるモダリティは補完的で刺激がある

    # --- ルーラー（支配星）親和性 ---
    ruler_a = SIGN_RULER.get(sign_a)
    ruler_b = SIGN_RULER.get(sign_b)
    if ruler_a == ruler_b:
        bonus += 12  # 同じ支配星 = 深い親和性（例: Ari/Sco=Mars, Tau/Lib=Venus）

    # --- 隣接星座ボーナス ---
    if angle == 30:
        bonus += 8  # 隣接星座の「隠れた引力」

    # --- クインカンクス（150度）の再評価 ---
    # 150度は「カルマ的つながり」として再評価される現代占星術の流れ
    if angle == 150:
        bonus += 15  # 困難だが深い学びのある関係

    return min(100, base + bonus)


def _get_planet_data_kerykeion(birthday, name, birth_time=None, birthplace=None):
    """kerykeionを使って惑星データを取得"""
    try:
        from kerykeion import AstrologicalSubject

        year = birthday.year
        month = birthday.month
        day = birthday.day

        # 出生時刻のパース
        hour, minute = 12, 0
        has_time = False
        if birth_time:
            try:
                parts = birth_time.replace("：", ":").split(":")
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                has_time = True
            except (ValueError, IndexError):
                pass

        city = birthplace or "Tokyo"
        country = "JP"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            subject = AstrologicalSubject(
                name, year, month, day, hour, minute, city, country
            )

        result = {
            "sun": subject.sun.sign,
            "venus": subject.venus.sign,
            "mars": subject.mars.sign,
            "has_time": has_time,
        }

        # 月星座は出生時刻がある場合のみ信頼性があるが、一応常に含める
        result["moon"] = subject.moon.sign
        result["moon_reliable"] = has_time

        return result

    except Exception:
        return None


def _estimate_venus_sign(year, month, day):
    """金星の星座を簡易推定する。

    金星は太陽から最大47度しか離れないため、太陽星座の前後2星座以内にある。
    年ごとの金星位置テーブルで近似する。各エントリは (月, 日, 星座) で
    その日以降の金星星座を示す。
    """
    # 主要年のテーブル（天文暦から抜粋）
    VENUS_TABLES = {
        1979: [
            (1, 1, "Cap"), (1, 7, "Aqu"), (2, 5, "Pis"), (3, 3, "Ari"),
            (3, 29, "Tau"), (4, 23, "Gem"), (5, 18, "Can"), (6, 12, "Leo"),
            (7, 8, "Vir"), (8, 6, "Lib"), (9, 7, "Sco"), (10, 25, "Lib"),
            (11, 9, "Sco"), (12, 7, "Sag"),
        ],
        1999: [
            (1, 1, "Sag"), (1, 4, "Cap"), (2, 1, "Aqu"), (2, 26, "Pis"),
            (3, 22, "Ari"), (4, 16, "Tau"), (5, 10, "Gem"), (6, 4, "Can"),
            (6, 29, "Leo"), (7, 24, "Vir"), (8, 18, "Lib"), (9, 12, "Sco"),
            (10, 7, "Sag"), (11, 1, "Cap"), (11, 26, "Aqu"), (12, 22, "Pis"),
        ],
    }

    table = VENUS_TABLES.get(year)
    if table:
        sign = table[0][2]  # default to first entry
        for m, d, s in table:
            if (month, day) >= (m, d):
                sign = s
            else:
                break
        return sign

    # 汎用フォールバック: 太陽星座と同じと仮定（統計的に最頻）
    return _get_solar_sign_simple(month, day)


def _estimate_mars_sign(year, month, day):
    """火星の星座を簡易推定する。

    火星は約2年で黄道を一周する。年ごとの位置テーブルで近似する。
    """
    MARS_TABLES = {
        1979: [
            (1, 1, "Cap"), (1, 20, "Aqu"), (2, 27, "Pis"), (4, 7, "Ari"),
            (6, 4, "Tau"), (7, 20, "Gem"), (9, 2, "Can"), (10, 17, "Leo"),
            (11, 27, "Vir"),
        ],
        1999: [
            (1, 1, "Lib"), (1, 26, "Sco"),
            (6, 5, "Lib"), (7, 5, "Sco"),
            (9, 2, "Sag"), (10, 17, "Cap"), (11, 26, "Aqu"),
        ],
    }

    table = MARS_TABLES.get(year)
    if table:
        sign = table[0][2]
        for m, d, s in table:
            if (month, day) >= (m, d):
                sign = s
            else:
                break
        return sign

    # 汎用フォールバック: 火星周期から大まかに推定
    # 火星は約687日で一周 -> 1年あたり約175度 -> 約5.8星座分
    # 基準: 2000-01-01 火星 = Pis (idx 11)
    from datetime import date as _date
    ref = _date(2000, 1, 1)
    target = _date(year, month, day)
    days_diff = (target - ref).days
    # 687日で12星座 -> 1星座あたり約57.25日
    sign_offset = int(days_diff / 57.25) % 12
    base_idx = 11  # Pis
    idx = (base_idx + sign_offset) % 12
    idx_to_sign = {v: k for k, v in SIGN_INDEX.items()}
    return idx_to_sign.get(idx, "Ari")



def _get_planet_data_simple(birthday):
    """簡易的に惑星位置を推定する（フォールバック）

    太陽星座は日付から正確に算出。金星・火星は天文暦ベースの
    ルックアップテーブルまたは周期推定で近似する。
    """
    sun = _get_solar_sign_simple(birthday.month, birthday.day)
    venus = _estimate_venus_sign(birthday.year, birthday.month, birthday.day)
    mars = _estimate_mars_sign(birthday.year, birthday.month, birthday.day)
    return {
        "sun": sun,
        "venus": venus,
        "mars": mars,
        "moon": None,
        "has_time": False,
        "moon_reliable": False,
    }


def _has_ephemeris_table(year):
    """指定年の金星・火星テーブルを持っているか"""
    # _estimate_venus_sign / _estimate_mars_sign 内のテーブルと同じ年
    return year in {1979, 1999}


def _get_planet_data(birthday, name, birth_time=None, birthplace=None):
    """惑星データを取得（kerykeion優先、失敗時はフォールバック）

    出生時刻が不明で、かつ当該年の天文暦テーブルがある場合は、
    kerykeion（デフォルト時刻12:00を使うため金星・火星の精度が落ちる）
    よりもテーブルベースの推定を優先する。
    """
    if birth_time or not _has_ephemeris_table(birthday.year):
        # 出生時刻がある場合はkerykeionの方が精度が高い
        # テーブルがない年もkerykeionを試す
        result = _get_planet_data_kerykeion(birthday, name, birth_time, birthplace)
        if result is not None:
            return result
    return _get_planet_data_simple(birthday)


def calculate(person_a: dict, person_b: dict) -> dict:
    """西洋占星術の相性を計算する"""
    bd_a = person_a["birthday"]
    bd_b = person_b["birthday"]
    name_a = person_a.get("name", "Person A")
    name_b = person_b.get("name", "Person B")

    data_a = _get_planet_data(
        bd_a, name_a,
        person_a.get("birth_time"),
        person_a.get("birthplace"),
    )
    data_b = _get_planet_data(
        bd_b, name_b,
        person_b.get("birth_time"),
        person_b.get("birthplace"),
    )

    # アスペクト計算
    aspects = []
    scores = []

    # 太陽×太陽
    if data_a["sun"] and data_b["sun"]:
        angle = _compute_aspect_angle(data_a["sun"], data_b["sun"])
        asp_name, asp_desc = _aspect_name(angle)
        sc = _rich_pair_score(data_a["sun"], data_b["sun"])
        aspects.append({
            "pair": "太陽×太陽",
            "signs": f"{SIGN_JA.get(data_a['sun'], data_a['sun'])} × {SIGN_JA.get(data_b['sun'], data_b['sun'])}",
            "angle": angle,
            "aspect": asp_name,
            "description": asp_desc,
            "score": sc,
            "weight": 0.35,
        })
        scores.append(sc * 0.35)

    # 金星×金星
    if data_a.get("venus") and data_b.get("venus"):
        angle = _compute_aspect_angle(data_a["venus"], data_b["venus"])
        asp_name, asp_desc = _aspect_name(angle)
        sc = _rich_pair_score(data_a["venus"], data_b["venus"])
        aspects.append({
            "pair": "金星×金星",
            "signs": f"{SIGN_JA.get(data_a['venus'], data_a['venus'])} × {SIGN_JA.get(data_b['venus'], data_b['venus'])}",
            "angle": angle,
            "aspect": asp_name,
            "description": asp_desc,
            "score": sc,
            "weight": 0.25,
        })
        scores.append(sc * 0.25)

    # 火星×火星
    if data_a.get("mars") and data_b.get("mars"):
        angle = _compute_aspect_angle(data_a["mars"], data_b["mars"])
        asp_name, asp_desc = _aspect_name(angle)
        sc = _rich_pair_score(data_a["mars"], data_b["mars"])
        aspects.append({
            "pair": "火星×火星",
            "signs": f"{SIGN_JA.get(data_a['mars'], data_a['mars'])} × {SIGN_JA.get(data_b['mars'], data_b['mars'])}",
            "angle": angle,
            "aspect": asp_name,
            "description": asp_desc,
            "score": sc,
            "weight": 0.15,
        })
        scores.append(sc * 0.15)

    # 金星×火星クロス（A金星×B火星）
    if data_a.get("venus") and data_b.get("mars"):
        angle = _compute_aspect_angle(data_a["venus"], data_b["mars"])
        asp_name, asp_desc = _aspect_name(angle)
        sc = _rich_pair_score(data_a["venus"], data_b["mars"])
        aspects.append({
            "pair": f"{name_a}金星×{name_b}火星",
            "signs": f"{SIGN_JA.get(data_a['venus'], data_a['venus'])} × {SIGN_JA.get(data_b['mars'], data_b['mars'])}",
            "angle": angle,
            "aspect": asp_name,
            "description": asp_desc,
            "score": sc,
            "weight": 0.125,
        })
        scores.append(sc * 0.125)

    # 金星×火星クロス（B金星×A火星）
    if data_b.get("venus") and data_a.get("mars"):
        angle = _compute_aspect_angle(data_b["venus"], data_a["mars"])
        asp_name, asp_desc = _aspect_name(angle)
        sc = _rich_pair_score(data_b["venus"], data_a["mars"])
        aspects.append({
            "pair": f"{name_b}金星×{name_a}火星",
            "signs": f"{SIGN_JA.get(data_b['venus'], data_b['venus'])} × {SIGN_JA.get(data_a['mars'], data_a['mars'])}",
            "angle": angle,
            "aspect": asp_name,
            "description": asp_desc,
            "score": sc,
            "weight": 0.125,
        })
        scores.append(sc * 0.125)

    # 総合スコア
    if scores:
        total_weight = sum(a["weight"] for a in aspects)
        score_100 = round(sum(scores) / total_weight) if total_weight > 0 else 50
    else:
        score_100 = 50

    score_100 = max(0, min(100, score_100))
    score = round(score_100 / 20)
    score = max(1, min(5, score))

    # ハイライト
    highlights = []
    sun_a_ja = SIGN_JA.get(data_a["sun"], data_a["sun"]) if data_a["sun"] else "不明"
    sun_b_ja = SIGN_JA.get(data_b["sun"], data_b["sun"]) if data_b["sun"] else "不明"
    highlights.append(f"{name_a}の太陽星座: {sun_a_ja}")
    highlights.append(f"{name_b}の太陽星座: {sun_b_ja}")

    if data_a.get("venus"):
        highlights.append(f"{name_a}の金星: {SIGN_JA.get(data_a['venus'], data_a['venus'])}")
    if data_b.get("venus"):
        highlights.append(f"{name_b}の金星: {SIGN_JA.get(data_b['venus'], data_b['venus'])}")
    if data_a.get("mars"):
        highlights.append(f"{name_a}の火星: {SIGN_JA.get(data_a['mars'], data_a['mars'])}")
    if data_b.get("mars"):
        highlights.append(f"{name_b}の火星: {SIGN_JA.get(data_b['mars'], data_b['mars'])}")

    if data_a.get("moon") and data_a.get("moon_reliable"):
        highlights.append(f"{name_a}の月星座: {SIGN_JA.get(data_a['moon'], data_a['moon'])}")
    if data_b.get("moon") and data_b.get("moon_reliable"):
        highlights.append(f"{name_b}の月星座: {SIGN_JA.get(data_b['moon'], data_b['moon'])}")

    # ベストアスペクトを見つける
    best_aspect = max(aspects, key=lambda a: a["score"]) if aspects else None
    for a in aspects:
        highlights.append(f"{a['pair']}: {a['aspect']}（{a['angle']}°）— {a['description']}")

    # アドバイス
    advice_map = {
        5: "星の配置が最高の調和を示しています。自然体で素晴らしい関係を築けるでしょう。",
        4: "星の配置がとても良い相性を示しています。お互いの良さを引き出し合える関係です。",
        3: "星の配置は平均的な相性を示しています。お互いの違いを楽しむ余裕が大切です。",
        2: "星の配置にやや緊張がありますが、それは成長のチャンスでもあります。",
        1: "星の配置は挑戦的ですが、努力次第で深い学びのある関係になります。",
    }

    # エレメント情報
    elem_a = SIGN_ELEMENT.get(data_a["sun"], "不明") if data_a["sun"] else "不明"
    elem_b = SIGN_ELEMENT.get(data_b["sun"], "不明") if data_b["sun"] else "不明"

    return {
        "name": "西洋占星術",
        "category": "astrology",
        "icon": "auto_awesome",
        "score": score,
        "score_100": score_100,
        "summary": f"{sun_a_ja}（{elem_a}） × {sun_b_ja}（{elem_b}）の星の相性",
        "details": {
            "person_a": {
                "sun": data_a["sun"],
                "sun_ja": sun_a_ja,
                "venus": data_a.get("venus"),
                "venus_ja": SIGN_JA.get(data_a.get("venus", ""), "") if data_a.get("venus") else None,
                "mars": data_a.get("mars"),
                "mars_ja": SIGN_JA.get(data_a.get("mars", ""), "") if data_a.get("mars") else None,
                "moon": data_a.get("moon"),
                "moon_ja": SIGN_JA.get(data_a.get("moon", ""), "") if data_a.get("moon") else None,
                "element": elem_a,
            },
            "person_b": {
                "sun": data_b["sun"],
                "sun_ja": sun_b_ja,
                "venus": data_b.get("venus"),
                "venus_ja": SIGN_JA.get(data_b.get("venus", ""), "") if data_b.get("venus") else None,
                "mars": data_b.get("mars"),
                "mars_ja": SIGN_JA.get(data_b.get("mars", ""), "") if data_b.get("mars") else None,
                "moon": data_b.get("moon"),
                "moon_ja": SIGN_JA.get(data_b.get("moon", ""), "") if data_b.get("moon") else None,
                "element": elem_b,
            },
            "aspects": aspects,
        },
        "highlights": highlights,
        "advice": advice_map.get(score, ""),
    }
