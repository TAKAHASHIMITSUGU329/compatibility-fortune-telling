"""Selenium E2Eテスト — ブラウザ画面表示版（RPA風）"""

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
    """画面表示ありのブラウザを起動"""
    opts = Options()
    # headlessなし — 画面表示してRPA風に動かす
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--window-position=100,50")
    driver = webdriver.Chrome(options=opts)
    return driver


def slow_type(element, text, delay=0.05):
    """1文字ずつ入力（RPA風の視覚効果）"""
    element.clear()
    for ch in text:
        element.send_keys(ch)
        time.sleep(delay)


def fill_and_submit(driver, pattern):
    """入力画面を開き、人間のようにデータを入力して分析実行"""
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.NAME, "a_birthday")))
    time.sleep(0.8)

    for prefix, person in [("a", pattern["a"]), ("b", pattern["b"])]:
        # 名前（姓・名・姓カナ・名カナ）
        for field_key, form_field in [("family_name", "family_name"), ("given_name", "given_name"),
                                       ("family_name_kana", "family_name_kana"), ("given_name_kana", "given_name_kana")]:
            val = person.get(field_key, "")
            if val:
                el = driver.find_element(By.NAME, f"{prefix}_{form_field}")
                slow_type(el, val)
                time.sleep(0.3)

        # 生年月日
        el = driver.find_element(By.NAME, f"{prefix}_birthday")
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            el, person["birthday"]
        )
        time.sleep(0.3)

        # 出生時刻
        if person["birth_time"]:
            el = driver.find_element(By.NAME, f"{prefix}_birth_time")
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                el, person["birth_time"]
            )
            time.sleep(0.2)

        # 出生地
        if person["birthplace"]:
            el = driver.find_element(By.NAME, f"{prefix}_birthplace")
            slow_type(el, person["birthplace"])
            time.sleep(0.3)

        # MBTI
        sel = Select(driver.find_element(By.NAME, f"{prefix}_mbti"))
        sel.select_by_value(person["mbti"])
        time.sleep(0.3)

        # 血液型
        if person["blood_type"]:
            sel = Select(driver.find_element(By.NAME, f"{prefix}_blood_type"))
            sel.select_by_value(person["blood_type"])
            time.sleep(0.2)

    # スクロールしてボタンを表示
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
    time.sleep(0.8)

    # クリック
    btn.click()

    # 結果ページ待機
    wait.until(EC.url_contains("/analyze"))
    time.sleep(1.5)

    # 結果ページをスクロールして全体を見せる
    driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
    time.sleep(0.8)
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    viewport = driver.execute_script("return window.innerHeight")
    pos = 0
    while pos < scroll_height:
        pos += int(viewport * 0.6)
        driver.execute_script(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}});")
        time.sleep(0.6)
    time.sleep(0.5)


def extract_results(driver):
    """結果ページからスコア・ランク等を抽出"""
    result = {}
    page_source = driver.page_source
    result["has_500_error"] = "Internal Server Error" in page_source
    result["has_traceback"] = "Traceback" in page_source
    result["url"] = driver.current_url

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

    categories = ["東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"]
    result["categories_found"] = sum(1 for c in categories if c in body_text)

    return result


def run_all_patterns():
    """全10パターンを画面表示しながら実行"""
    driver = create_driver()
    all_results = []

    try:
        for pattern in TEST_PATTERNS:
            print(f"\n{'='*50}")
            print(f"パターン{pattern['id']}: {pattern['label']}")
            print(f"{'='*50}")

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

                if data.get("has_500_error"):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append("500 Internal Server Error")
                if data.get("has_traceback"):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append("Python Traceback")
                if "/analyze" not in data.get("url", ""):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append(f"遷移失敗: {data.get('url')}")

                score = data.get("total_score")
                rank = data.get("rank", "不明")
                cats = data.get("categories_found", 0)
                test_result["rank"] = rank
                test_result["score"] = score

                print(f"  -> {test_result['status']} | スコア: {score}点 | ランク: {rank} | カテゴリ: {cats}/6")

            except Exception as e:
                test_result["status"] = "FAIL"
                test_result["errors"].append(f"例外: {str(e)}")
                print(f"  -> FAIL | 例外: {e}")

            all_results.append(test_result)

    finally:
        time.sleep(1)
        driver.quit()

    return all_results


if __name__ == "__main__":
    print("=" * 60)
    print("  Selenium E2Eテスト — ブラウザ画面表示版（RPA風）")
    print(f"  実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = run_all_patterns()

    print("\n" + "=" * 60)
    print("  テスト結果サマリ")
    print("=" * 60)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"  PASS: {passed} / FAIL: {failed} / 合計: {len(results)}")

    with open("/tmp/selenium_visible_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  詳細: /tmp/selenium_visible_results.json")
