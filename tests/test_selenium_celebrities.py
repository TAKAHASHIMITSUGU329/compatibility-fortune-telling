"""Selenium E2Eテスト — 著名人カップル10組（結婚継続5組 + 離婚5組）

公開情報に基づく生年月日を使用。MBTIは一般的な推定タイプ（公式判定ではない）。
結婚継続組と離婚組でスコア傾向に差が出るかを検証する。
"""

import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:5001"

# === 結婚継続カップル（5組） ===
MARRIED_COUPLES = [
    {
        "id": 1,
        "label": "【継続】ヒロミ × 松本伊代（1993年〜）",
        "group": "married",
        "a": {"name": "ヒロミ", "birthday": "1965-02-13", "birth_time": "",
               "birthplace": "東京都八王子市", "mbti": "ESTP", "blood_type": "A型"},
        "b": {"name": "松本伊代", "birthday": "1965-06-02", "birth_time": "",
               "birthplace": "東京都大田区", "mbti": "ESFP", "blood_type": "B型"},
    },
    {
        "id": 2,
        "label": "【継続】佐々木健介 × 北斗晶（1995年〜）",
        "group": "married",
        "a": {"name": "佐々木健介", "birthday": "1966-08-04", "birth_time": "",
               "birthplace": "福岡県福岡市", "mbti": "ISFJ", "blood_type": "AB型"},
        "b": {"name": "北斗晶", "birthday": "1967-07-13", "birth_time": "",
               "birthplace": "埼玉県吉川市", "mbti": "ESTJ", "blood_type": "O型"},
    },
    {
        "id": 3,
        "label": "【継続】唐沢寿明 × 山口智子（1995年〜）",
        "group": "married",
        "a": {"name": "唐沢寿明", "birthday": "1963-06-03", "birth_time": "",
               "birthplace": "東京都", "mbti": "ISTP", "blood_type": "A型"},
        "b": {"name": "山口智子", "birthday": "1964-10-20", "birth_time": "",
               "birthplace": "栃木県栃木市", "mbti": "ENFP", "blood_type": "A型"},
    },
    {
        "id": 4,
        "label": "【継続】三浦友和 × 山口百恵（1980年〜）",
        "group": "married",
        "a": {"name": "三浦友和", "birthday": "1952-01-28", "birth_time": "",
               "birthplace": "山梨県甲府市", "mbti": "ISFP", "blood_type": "A型"},
        "b": {"name": "山口百恵", "birthday": "1959-01-17", "birth_time": "",
               "birthplace": "神奈川県横須賀市", "mbti": "INFJ", "blood_type": "A型"},
    },
    {
        "id": 5,
        "label": "【継続】DAIGO × 北川景子（2016年〜）",
        "group": "married",
        "a": {"name": "DAIGO", "birthday": "1978-04-08", "birth_time": "",
               "birthplace": "東京都", "mbti": "ENFP", "blood_type": "AB型"},
        "b": {"name": "北川景子", "birthday": "1986-08-22", "birth_time": "",
               "birthplace": "兵庫県神戸市", "mbti": "ENTJ", "blood_type": "O型"},
    },
]

# === 離婚カップル（5組） ===
DIVORCED_COUPLES = [
    {
        "id": 6,
        "label": "【離婚】東出昌大 × 杏（2015〜2020）",
        "group": "divorced",
        "a": {"name": "東出昌大", "birthday": "1988-02-01", "birth_time": "",
               "birthplace": "埼玉県", "mbti": "ISFP", "blood_type": "A型"},
        "b": {"name": "杏", "birthday": "1986-04-14", "birth_time": "",
               "birthplace": "東京都", "mbti": "ISTJ", "blood_type": "A型"},
    },
    {
        "id": 7,
        "label": "【離婚】小室哲哉 × KEIKO（2002〜2021）",
        "group": "divorced",
        "a": {"name": "小室哲哉", "birthday": "1958-11-27", "birth_time": "",
               "birthplace": "東京都府中市", "mbti": "ENTP", "blood_type": "O型"},
        "b": {"name": "KEIKO", "birthday": "1972-08-18", "birth_time": "",
               "birthplace": "大分県臼杵市", "mbti": "ESFJ", "blood_type": "A型"},
    },
    {
        "id": 8,
        "label": "【離婚】神田正輝 × 松田聖子（1985〜1997）",
        "group": "divorced",
        "a": {"name": "神田正輝", "birthday": "1950-12-21", "birth_time": "",
               "birthplace": "東京都", "mbti": "ISTJ", "blood_type": "A型"},
        "b": {"name": "松田聖子", "birthday": "1962-03-10", "birth_time": "",
               "birthplace": "福岡県久留米市", "mbti": "ESFP", "blood_type": "A型"},
    },
    {
        "id": 9,
        "label": "【離婚】陣内智則 × 藤原紀香（2007〜2009）",
        "group": "divorced",
        "a": {"name": "陣内智則", "birthday": "1974-02-22", "birth_time": "",
               "birthplace": "兵庫県加古川市", "mbti": "ENFP", "blood_type": "B型"},
        "b": {"name": "藤原紀香", "birthday": "1971-06-28", "birth_time": "",
               "birthplace": "兵庫県西宮市", "mbti": "ESTJ", "blood_type": "A型"},
    },
    {
        "id": 10,
        "label": "【離婚】高橋ジョージ × 三船美佳（1999〜2016）",
        "group": "divorced",
        "a": {"name": "高橋ジョージ", "birthday": "1958-09-26", "birth_time": "",
               "birthplace": "宮城県", "mbti": "ESTP", "blood_type": "A型"},
        "b": {"name": "三船美佳", "birthday": "1982-09-12", "birth_time": "",
               "birthplace": "東京都", "mbti": "ESFP", "blood_type": "A型"},
    },
]

ALL_PATTERNS = MARRIED_COUPLES + DIVORCED_COUPLES


def create_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,900")
    if not headless:
        opts.add_argument("--window-position=100,50")
    return webdriver.Chrome(options=opts)


def slow_type(element, text, delay=0.05):
    """1文字ずつ入力（RPA風）"""
    element.clear()
    for ch in text:
        element.send_keys(ch)
        time.sleep(delay)


def fill_and_submit(driver, pattern, visible=False):
    """入力画面にデータを入力して送信"""
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.NAME, "a_birthday")))
    if visible:
        time.sleep(0.5)

    for prefix, person in [("a", pattern["a"]), ("b", pattern["b"])]:
        # 名前
        if person["name"]:
            el = driver.find_element(By.NAME, f"{prefix}_name")
            if visible:
                slow_type(el, person["name"])
                time.sleep(0.2)
            else:
                el.clear()
                el.send_keys(person["name"])

        # 生年月日
        el = driver.find_element(By.NAME, f"{prefix}_birthday")
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            el, person["birthday"]
        )
        if visible:
            time.sleep(0.2)

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
            if visible:
                slow_type(el, person["birthplace"])
                time.sleep(0.2)
            else:
                el.clear()
                el.send_keys(person["birthplace"])

        # MBTI
        sel = Select(driver.find_element(By.NAME, f"{prefix}_mbti"))
        sel.select_by_value(person["mbti"])
        if visible:
            time.sleep(0.2)

        # 血液型
        if person["blood_type"]:
            sel = Select(driver.find_element(By.NAME, f"{prefix}_blood_type"))
            sel.select_by_value(person["blood_type"])

    # 送信
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    if visible:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
        time.sleep(0.5)
    btn.click()

    wait.until(EC.url_contains("/analyze"))
    if visible:
        time.sleep(1.0)
        # スクロールして結果を表示
        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(0.5)
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        viewport = driver.execute_script("return window.innerHeight")
        pos = 0
        while pos < scroll_height:
            pos += int(viewport * 0.6)
            driver.execute_script(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}});")
            time.sleep(0.4)
        time.sleep(0.3)
    else:
        time.sleep(0.3)


def extract_results(driver):
    """結果ページからスコア・ランク・カテゴリ数を抽出"""
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
        result["rank"] = "unknown"

    # 総合スコア抽出（data属性から正確に取得）
    try:
        score_el = driver.find_element(By.ID, "total-score")
        result["total_score"] = int(score_el.get_attribute("data-score"))
    except Exception:
        result["total_score"] = None

    # カテゴリ数
    categories = ["東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"]
    result["categories_found"] = sum(1 for c in categories if c in body_text)

    return result


def run_celebrity_tests(headless=True):
    """著名人10組テスト実行"""
    visible = not headless
    driver = create_driver(headless=headless)
    all_results = []

    try:
        for pattern in ALL_PATTERNS:
            group_tag = "継続" if pattern["group"] == "married" else "離婚"
            print(f"\n--- [{group_tag}] {pattern['label']} ---")

            test_result = {
                "id": pattern["id"],
                "label": pattern["label"],
                "group": pattern["group"],
                "status": "PASS",
                "errors": [],
            }

            try:
                fill_and_submit(driver, pattern, visible=visible)
                data = extract_results(driver)
                test_result["data"] = data

                # 判定
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
                rank = data.get("rank", "unknown")
                cats = data.get("categories_found", 0)
                test_result["score"] = score
                test_result["rank"] = rank

                if score is not None and not (0 <= score <= 100):
                    test_result["status"] = "FAIL"
                    test_result["errors"].append(f"スコアが範囲外: {score}")

                print(f"  -> {test_result['status']} | スコア: {score}点 | ランク: {rank} | カテゴリ: {cats}/6")

            except Exception as e:
                test_result["status"] = "FAIL"
                test_result["errors"].append(f"例外: {str(e)}")
                print(f"  -> FAIL | 例外: {e}")

            all_results.append(test_result)

    finally:
        if visible:
            time.sleep(1)
        driver.quit()

    return all_results


def print_comparison(results):
    """結婚継続組 vs 離婚組のスコア比較を表示"""
    married = [r for r in results if r["group"] == "married" and r.get("score") is not None]
    divorced = [r for r in results if r["group"] == "divorced" and r.get("score") is not None]

    print("\n" + "=" * 70)
    print("  結婚継続組 vs 離婚組 — スコア比較")
    print("=" * 70)

    print("\n  [結婚継続組]")
    for r in married:
        print(f"    {r['label']}: {r['score']}点 (ランク {r['rank']})")
    if married:
        avg_m = sum(r["score"] for r in married) / len(married)
        print(f"    --- 平均: {avg_m:.1f}点 ---")

    print("\n  [離婚組]")
    for r in divorced:
        print(f"    {r['label']}: {r['score']}点 (ランク {r['rank']})")
    if divorced:
        avg_d = sum(r["score"] for r in divorced) / len(divorced)
        print(f"    --- 平均: {avg_d:.1f}点 ---")

    if married and divorced:
        diff = avg_m - avg_d
        print(f"\n  差分: 継続組が {'高い' if diff > 0 else '低い'} ({abs(diff):.1f}点差)")


if __name__ == "__main__":
    import sys
    headless = "--visible" not in sys.argv

    print("=" * 70)
    print("  Selenium E2Eテスト — 著名人カップル10組")
    print(f"  モード: {'ヘッドレス' if headless else 'ブラウザ表示（RPA風）'}")
    print(f"  実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = run_celebrity_tests(headless=headless)

    # テスト結果サマリ
    print("\n" + "=" * 70)
    print("  テスト結果サマリ")
    print("=" * 70)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"  PASS: {passed} / FAIL: {failed} / 合計: {len(results)}")

    # スコア比較
    print_comparison(results)

    # JSON出力
    output_path = "/tmp/selenium_celebrity_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  詳細結果: {output_path}")
