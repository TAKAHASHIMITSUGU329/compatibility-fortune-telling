"""Selenium E2Eテスト — ランダム10パターンの相性分析"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:5001"

TEST_PATTERNS = [
    {
        "id": 1,
        "label": "全項目入力・黄金ペア(INTJ×ENFP)",
        "a": {"family_name": "", "given_name": "太郎", "family_name_kana": "", "given_name_kana": "タロウ",
               "birthday": "1990-04-15", "birth_time": "08:30",
               "birthplace": "東京都新宿区", "mbti": "INTJ", "blood_type": "A型"},
        "b": {"family_name": "", "given_name": "花子", "family_name_kana": "", "given_name_kana": "ハナコ",
               "birthday": "1992-08-23", "birth_time": "14:00",
               "birthplace": "大阪府大阪市", "mbti": "ENFP", "blood_type": "O型"},
    },
    {
        "id": 2,
        "label": "必須項目のみ（任意項目すべて空）",
        "a": {"family_name": "", "given_name": "", "family_name_kana": "", "given_name_kana": "",
               "birthday": "1985-12-01", "birth_time": "",
               "birthplace": "", "mbti": "ISFJ", "blood_type": ""},
        "b": {"family_name": "", "given_name": "", "family_name_kana": "", "given_name_kana": "",
               "birthday": "1987-03-14", "birth_time": "",
               "birthplace": "", "mbti": "ESFP", "blood_type": ""},
    },
    {
        "id": 3,
        "label": "同じMBTI同士(INFP×INFP)",
        "a": {"family_name": "", "given_name": "健一", "family_name_kana": "", "given_name_kana": "ケンイチ",
               "birthday": "1995-01-10", "birth_time": "06:00",
               "birthplace": "北海道札幌市", "mbti": "INFP", "blood_type": "B型"},
        "b": {"family_name": "", "given_name": "美咲", "family_name_kana": "", "given_name_kana": "ミサキ",
               "birthday": "1996-01-10", "birth_time": "22:30",
               "birthplace": "沖縄県那覇市", "mbti": "INFP", "blood_type": "AB型"},
    },
    {
        "id": 4,
        "label": "年齢差が大きいペア(28歳差)",
        "a": {"family_name": "", "given_name": "正雄", "family_name_kana": "", "given_name_kana": "マサオ",
               "birthday": "1970-07-07", "birth_time": "12:00",
               "birthplace": "福岡県福岡市", "mbti": "ESTJ", "blood_type": "O型"},
        "b": {"family_name": "", "given_name": "さくら", "family_name_kana": "", "given_name_kana": "サクラ",
               "birthday": "1998-11-22", "birth_time": "03:15",
               "birthplace": "東京都渋谷区", "mbti": "INFJ", "blood_type": "A型"},
    },
    {
        "id": 5,
        "label": "2000年代生まれ（若年層）",
        "a": {"family_name": "", "given_name": "蓮", "family_name_kana": "", "given_name_kana": "レン",
               "birthday": "2001-05-05", "birth_time": "",
               "birthplace": "神奈川県横浜市", "mbti": "ENTP", "blood_type": "AB型"},
        "b": {"family_name": "", "given_name": "陽葵", "family_name_kana": "", "given_name_kana": "ヒマリ",
               "birthday": "2003-09-30", "birth_time": "",
               "birthplace": "愛知県名古屋市", "mbti": "ISFJ", "blood_type": "B型"},
    },
    {
        "id": 6,
        "label": "うるう年・境界日(2/29×12/31)",
        "a": {"family_name": "", "given_name": "翔", "family_name_kana": "", "given_name_kana": "ショウ",
               "birthday": "2000-02-29", "birth_time": "00:00",
               "birthplace": "京都府京都市", "mbti": "ISTP", "blood_type": "A型"},
        "b": {"family_name": "", "given_name": "凛", "family_name_kana": "", "given_name_kana": "リン",
               "birthday": "1999-12-31", "birth_time": "23:59",
               "birthplace": "兵庫県神戸市", "mbti": "ENFJ", "blood_type": "O型"},
    },
    {
        "id": 7,
        "label": "同じ誕生日（完全一致）",
        "a": {"family_name": "", "given_name": "大翔", "family_name_kana": "", "given_name_kana": "ヒロト",
               "birthday": "1993-06-21", "birth_time": "10:00",
               "birthplace": "広島県広島市", "mbti": "ENTJ", "blood_type": "O型"},
        "b": {"family_name": "", "given_name": "結衣", "family_name_kana": "", "given_name_kana": "ユイ",
               "birthday": "1993-06-21", "birth_time": "16:00",
               "birthplace": "宮城県仙台市", "mbti": "ISFP", "blood_type": "A型"},
    },
    {
        "id": 8,
        "label": "昭和生まれ（高年齢・1950年代）",
        "a": {"family_name": "", "given_name": "義男", "family_name_kana": "", "given_name_kana": "ヨシオ",
               "birthday": "1955-03-03", "birth_time": "05:45",
               "birthplace": "新潟県新潟市", "mbti": "ISTJ", "blood_type": "B型"},
        "b": {"family_name": "", "given_name": "和子", "family_name_kana": "", "given_name_kana": "カズコ",
               "birthday": "1958-10-18", "birth_time": "11:30",
               "birthplace": "長野県長野市", "mbti": "ESFJ", "blood_type": "A型"},
    },
    {
        "id": 9,
        "label": "正反対のMBTI(ESTP×INFJ)",
        "a": {"family_name": "", "given_name": "悠真", "family_name_kana": "", "given_name_kana": "ユウマ",
               "birthday": "1988-08-08", "birth_time": "15:20",
               "birthplace": "千葉県千葉市", "mbti": "ESTP", "blood_type": "O型"},
        "b": {"family_name": "", "given_name": "芽依", "family_name_kana": "", "given_name_kana": "メイ",
               "birthday": "1991-02-14", "birth_time": "09:45",
               "birthplace": "福岡県北九州市", "mbti": "INFJ", "blood_type": "AB型"},
    },
    {
        "id": 10,
        "label": "血液型のみ異なる類似ペア",
        "a": {"family_name": "", "given_name": "湊", "family_name_kana": "", "given_name_kana": "ミナト",
               "birthday": "1997-11-11", "birth_time": "07:00",
               "birthplace": "静岡県浜松市", "mbti": "ENFJ", "blood_type": "A型"},
        "b": {"family_name": "", "given_name": "杏", "family_name_kana": "", "given_name_kana": "アン",
               "birthday": "1997-11-12", "birth_time": "07:00",
               "birthplace": "静岡県浜松市", "mbti": "ENFJ", "blood_type": "B型"},
    },
]


def create_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,1024")
    return webdriver.Chrome(options=opts)


def fill_and_submit(driver, pattern):
    """入力画面を開き、データを入力して分析実行"""
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.NAME, "a_birthday")))

    for prefix, person in [("a", pattern["a"]), ("b", pattern["b"])]:
        # 名前（姓・名・姓カナ・名カナ）
        for field_key, form_field in [("family_name", "family_name"), ("given_name", "given_name"),
                                       ("family_name_kana", "family_name_kana"), ("given_name_kana", "given_name_kana")]:
            val = person.get(field_key, "")
            if val:
                el = driver.find_element(By.NAME, f"{prefix}_{form_field}")
                el.clear()
                el.send_keys(val)

        # 生年月日
        el = driver.find_element(By.NAME, f"{prefix}_birthday")
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            el, person["birthday"]
        )

        # 出生時刻
        if person["birth_time"]:
            el = driver.find_element(By.NAME, f"{prefix}_birth_time")
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                el, person["birth_time"]
            )

        # 出生地
        if person["birthplace"]:
            el = driver.find_element(By.NAME, f"{prefix}_birthplace")
            el.clear()
            el.send_keys(person["birthplace"])

        # MBTI
        sel = Select(driver.find_element(By.NAME, f"{prefix}_mbti"))
        sel.select_by_value(person["mbti"])

        # 血液型
        if person["blood_type"]:
            sel = Select(driver.find_element(By.NAME, f"{prefix}_blood_type"))
            sel.select_by_value(person["blood_type"])

    # 送信
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    btn.click()

    # 結果ページ待機
    wait.until(EC.url_contains("/analyze"))
    time.sleep(0.5)


def extract_results(driver):
    """結果ページからスコア・ランク等を抽出"""
    result = {}

    # ページソースにエラーがないか
    page_source = driver.page_source
    result["has_500_error"] = "Internal Server Error" in page_source
    result["has_traceback"] = "Traceback" in page_source

    # URL確認
    result["url"] = driver.current_url

    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        result["body_text_length"] = len(body_text)

        # ランク抽出（data属性から正確に取得）
        try:
            rank_el = driver.find_element(By.ID, "rank-badge")
            result["rank"] = rank_el.get_attribute("data-rank")
        except Exception:
            result["rank"] = "不明"

        # 総合スコア抽出（data属性から正確に取得）
        try:
            score_el = driver.find_element(By.ID, "total-score")
            result["total_score"] = int(score_el.get_attribute("data-score"))
        except Exception:
            result["total_score"] = None

        # カテゴリ数カウント
        categories = ["東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"]
        result["categories_found"] = sum(1 for c in categories if c in body_text)

    except Exception as e:
        result["extraction_error"] = str(e)

    return result


def run_all_patterns():
    """全10パターンを実行"""
    driver = create_driver()
    all_results = []

    try:
        for pattern in TEST_PATTERNS:
            print(f"\n--- パターン{pattern['id']}: {pattern['label']} ---")
            test_result = {
                "id": pattern["id"],
                "label": pattern["label"],
                "status": "PASS",
                "errors": [],
            }

            try:
                fill_and_submit(driver, pattern)
                data = extract_results(driver)
                test_result["data"] = data

                # 判定
                if data.get("has_500_error"):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append("500 Internal Server Error が発生")

                if data.get("has_traceback"):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append("Python Traceback が発生")

                if "/analyze" not in data.get("url", ""):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append(f"結果ページに遷移していない: {data.get('url')}")

                if data.get("categories_found", 0) < 6:
                    test_result["errors"].append(f"カテゴリ表示数: {data.get('categories_found')}/6")

                score = data.get("total_score")
                if score is not None and not (0 <= score <= 100):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append(f"スコアが範囲外: {score}")

                rank = data.get("rank", "不明")
                test_result["rank"] = rank
                test_result["score"] = score

                print(f"  結果: {test_result['status']} | スコア: {score} | ランク: {rank}")
                if test_result["errors"]:
                    for err in test_result["errors"]:
                        print(f"  注意: {err}")

            except Exception as e:
                test_result["status"] = "FAIL"
                test_result["errors"].append(f"例外発生: {str(e)}")
                print(f"  結果: FAIL | 例外: {e}")

            all_results.append(test_result)

    finally:
        driver.quit()

    return all_results


if __name__ == "__main__":
    print("=" * 60)
    print("Selenium E2Eテスト — ランダム10パターン")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = run_all_patterns()

    # サマリ出力
    print("\n" + "=" * 60)
    print("テスト結果サマリ")
    print("=" * 60)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"PASS: {passed} / FAIL: {failed} / 合計: {len(results)}")

    # JSON出力（仕様書更新用）
    with open("/tmp/selenium_test_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n詳細結果: /tmp/selenium_test_results.json")
