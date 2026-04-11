"""相性占い分析Webアプリ — Flask本体"""

import logging
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from datetime import date
from config import Config
from sheets import save_to_sheet

logging.basicConfig(level=logging.INFO)
from calculators import run_all

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP",
]

BLOOD_TYPES = ["A型", "B型", "O型", "AB型"]


def _parse_person(prefix: str) -> dict:
    """フォームデータからpersonデータを抽出"""
    name = request.form.get(f"{prefix}_name", "").strip()
    birthday_str = request.form.get(f"{prefix}_birthday", "")
    birth_time = request.form.get(f"{prefix}_birth_time", "").strip()
    birthplace = request.form.get(f"{prefix}_birthplace", "").strip()
    mbti = request.form.get(f"{prefix}_mbti", "").strip()
    blood_type = request.form.get(f"{prefix}_blood_type", "").strip()
    enneagram = request.form.get(f"{prefix}_enneagram", "").strip()
    wing = request.form.get(f"{prefix}_wing", "").strip()

    # 生年月日のパース
    birthday = None
    if birthday_str:
        try:
            parts = birthday_str.split("-")
            birthday = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            pass

    return {
        "name": name or ("男性" if prefix == "a" else "女性"),
        "birthday": birthday,
        "birth_time": birth_time or None,
        "birthplace": birthplace or None,
        "mbti": mbti or None,
        "blood_type": blood_type or None,
        "enneagram": enneagram or None,
        "wing": wing or None,
    }


@app.route("/", methods=["GET"])
def index():
    """入力画面を表示"""
    return render_template(
        "input.html",
        mbti_types=MBTI_TYPES,
        blood_types=BLOOD_TYPES,
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    """分析を実行して結果画面を表示"""
    person_a = _parse_person("a")
    person_b = _parse_person("b")

    # バリデーション（フィールド単位）
    field_errors = {}
    if not person_a["birthday"]:
        field_errors["a_birthday"] = "生年月日を入力してください"
    elif person_a["birthday"] > date.today():
        field_errors["a_birthday"] = "未来の日付は入力できません"
    if not person_b["birthday"]:
        field_errors["b_birthday"] = "生年月日を入力してください"
    elif person_b["birthday"] > date.today():
        field_errors["b_birthday"] = "未来の日付は入力できません"
    if not person_a["mbti"]:
        field_errors["a_mbti"] = "MBTIを選択してください"
    if not person_b["mbti"]:
        field_errors["b_mbti"] = "MBTIを選択してください"

    if field_errors:
        return render_template(
            "input.html",
            mbti_types=MBTI_TYPES,
            blood_types=BLOOD_TYPES,
            errors=list(field_errors.values()),
            field_errors=field_errors,
            person_a=person_a,
            person_b=person_b,
        )

    # 全計算エンジンを実行
    run_result = run_all(person_a, person_b)
    results = run_result["results"]
    calc_errors = run_result["errors"]

    # 総合スコアの算出
    if results:
        raw_avg = sum(r["score_100"] for r in results) / len(results)
    else:
        raw_avg = 0

    # スコア正規化（32手法平均の68-82帯を30-95に引き伸ばし、直感的な数字にする）
    RAW_MIN, RAW_MAX = 68, 82
    NORM_MIN, NORM_MAX = 30, 95
    if raw_avg <= RAW_MIN:
        total_score_100 = NORM_MIN
    elif raw_avg >= RAW_MAX:
        total_score_100 = NORM_MAX
    else:
        total_score_100 = (raw_avg - RAW_MIN) / (RAW_MAX - RAW_MIN) * (NORM_MAX - NORM_MIN) + NORM_MIN
    total_score_100 = max(0, min(100, round(total_score_100)))

    total_score = round(total_score_100 / 20)
    total_score = max(1, min(5, total_score))

    # カテゴリ別に分類（各calculatorの CATEGORY 定数から自動集計）
    CATEGORY_ORDER = ["東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"]
    cat_buckets: dict[str, list] = {}
    for r in results:
        cat_name = r.get("category", "その他占い")
        cat_buckets.setdefault(cat_name, []).append(r)

    categories = []
    for cat_name in CATEGORY_ORDER:
        cat_results = cat_buckets.pop(cat_name, [])
        if cat_results:
            avg = sum(r["score_100"] for r in cat_results) / len(cat_results)
            categories.append({
                "name": cat_name,
                "score": round(avg),
                "count": len(cat_results),
                "results": cat_results,
            })
    # 未知のカテゴリがあれば末尾に追加
    for cat_name, cat_results in cat_buckets.items():
        avg = sum(r["score_100"] for r in cat_results) / len(cat_results)
        categories.append({
            "name": cat_name,
            "score": round(avg),
            "count": len(cat_results),
            "results": cat_results,
        })

    # レーダーチャート用データ（カテゴリ別6軸）
    chart_labels = [c["name"] for c in categories]
    chart_data = [c["score"] for c in categories]

    # ランク判定（正規化後の直感的な閾値）
    s100 = total_score_100
    if s100 >= 92:
        rank, rank_color = "SSS", "#ff6b00"
    elif s100 >= 85:
        rank, rank_color = "SS", "#e91e63"
    elif s100 >= 76:
        rank, rank_color = "S", "#9c27b0"
    elif s100 >= 66:
        rank, rank_color = "A", "#1a237e"
    elif s100 >= 55:
        rank, rank_color = "B", "#0277bd"
    elif s100 >= 42:
        rank, rank_color = "C", "#2e7d32"
    else:
        rank, rank_color = "D", "#757575"

    # Google Spreadsheet に自動保存
    try:
        save_to_sheet(person_a, person_b, results, categories, s100, rank, Config)
    except Exception as e:
        logging.warning("Spreadsheet保存エラー: %s", e)

    return render_template(
        "result.html",
        person_a=person_a,
        person_b=person_b,
        results=results,
        categories=categories,
        total_score=total_score,
        total_score_100=s100,
        chart_labels=chart_labels,
        chart_data=chart_data,
        rank=rank,
        rank_color=rank_color,
        calc_errors=calc_errors,
    )


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
