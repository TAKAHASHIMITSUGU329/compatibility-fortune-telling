"""バイオリズム計算エンジン"""

import math
from datetime import date, timedelta

CATEGORY = "その他占い"

CYCLES = {
    "physical": {"period": 23, "name": "身体"},
    "emotional": {"period": 28, "name": "感情"},
    "intellectual": {"period": 33, "name": "知性"},
}


def _biorhythm_value(birthday: date, target_date: date, period: int) -> float:
    """特定日のバイオリズム値を計算（-1.0 ~ 1.0）"""
    days = (target_date - birthday).days
    return math.sin(2 * math.pi * days / period)


def _phase_diff(birthday_a: date, birthday_b: date, target_date: date, period: int) -> float:
    """二人のバイオリズムの位相差を計算（0.0 ~ 1.0、0が完全一致）"""
    val_a = _biorhythm_value(birthday_a, target_date, period)
    val_b = _biorhythm_value(birthday_b, target_date, period)
    # 差の絶対値を0-1に正規化（最大差は2.0）
    return abs(val_a - val_b) / 2.0


def _sync_score(phase_diff: float) -> int:
    """位相差から同期スコア（1-5）を算出

    phase_diffは0.0〜0.5の範囲（構造的位相差）。
    0.0=完全同期、0.5=完全逆位相。
    """
    if phase_diff < 0.08:
        return 5
    elif phase_diff < 0.18:
        return 4
    elif phase_diff < 0.30:
        return 3
    elif phase_diff < 0.42:
        return 2
    else:
        return 1


def _structural_phase_diff(birthday_a: date, birthday_b: date, period: int) -> float:
    """二人の誕生日差から構造的な位相差を計算（0.0〜0.5、0が完全同期）

    誕生日の差をバイオリズム周期で割った余りから位相差を算出。
    日付に依存しない安定した指標。
    """
    day_diff = abs((birthday_a - birthday_b).days)
    phase = (day_diff % period) / period  # 0.0 ~ 1.0
    # 0.5を超える場合は反対側からの距離が近い
    if phase > 0.5:
        phase = 1.0 - phase
    return phase


def calculate(person_a: dict, person_b: dict) -> dict:
    """バイオリズムの相性を計算する"""
    bd_a = person_a['birthday']
    bd_b = person_b['birthday']
    today = date.today()

    results = {}
    # 感情周期は人間関係で最も重要なため、重み付けを行う
    # 身体:感情:知性 = 1:4:1 の比率（恋愛・対人関係では感情の同期が最重要）
    weights = {"physical": 1, "emotional": 4, "intellectual": 1}
    weighted_total = 0
    weight_sum = 0

    for key, cycle in CYCLES.items():
        period = cycle["period"]
        val_a = _biorhythm_value(bd_a, today, period)
        val_b = _biorhythm_value(bd_b, today, period)
        # 構造的位相差を使い、日付に依存しない安定したスコアを算出
        struct_diff = _structural_phase_diff(bd_a, bd_b, period)
        sync = _sync_score(struct_diff)

        results[key] = {
            "name": cycle["name"],
            "period": period,
            "value_a": round(val_a, 3),
            "value_b": round(val_b, 3),
            "phase_diff": round(struct_diff, 3),
            "sync_score": sync,
        }
        w = weights[key]
        weighted_total += sync * w
        weight_sum += w

    avg_score = round(weighted_total / weight_sum)
    avg_score = max(1, min(5, avg_score))
    score_100 = {1: 40, 2: 55, 3: 70, 4: 80, 5: 95}.get(avg_score, 70)

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    highlights = []
    for key, r in results.items():
        status = "同期" if r["sync_score"] >= 4 else "ややずれ" if r["sync_score"] >= 3 else "不調和"
        highlights.append(f"{r['name']}リズム（{r['period']}日周期）: {status}")

    advice_map = {
        5: "今日はお二人のバイオリズムが完全に同期しています。何をしても息が合う最高の日です。",
        4: "バイオリズムの同期が良好です。一緒に過ごすと心地よいエネルギーを感じられるでしょう。",
        3: "バイオリズムは平均的な状態です。お互いの体調や気分に配慮すると良いでしょう。",
        2: "バイオリズムにずれがあります。相手のペースを尊重する日にしましょう。",
        1: "バイオリズムが大きくずれています。無理せず、それぞれのリズムを大切に。",
    }

    return {
        "name": "バイオリズム",
        "category": "biorhythm",
        "icon": "timeline",
        "score": avg_score,
        "score_100": score_100,
        "summary": f"本日のバイオリズム同期度",
        "details": {
            "person_a": {
                "physical": results["physical"]["value_a"],
                "emotional": results["emotional"]["value_a"],
                "intellectual": results["intellectual"]["value_a"],
            },
            "person_b": {
                "physical": results["physical"]["value_b"],
                "emotional": results["emotional"]["value_b"],
                "intellectual": results["intellectual"]["value_b"],
            },
            "compatibility": results,
            "target_date": today.isoformat(),
        },
        "highlights": highlights,
        "advice": advice_map.get(avg_score, ""),
    }
