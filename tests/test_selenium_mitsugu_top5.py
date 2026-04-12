"""Selenium E2Eテスト — 貢さん × 相性トップ5女性芸能人（RPA風ブラウザ表示）

30人の女性芸能人から相性スコア上位5名を選定。
公開情報に基づく生年月日・MBTIは一般的な推定タイプ。
"""

import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:5001"

PERSON_A = {
    "family_name": "高橋",
    "given_name": "貢",
    "family_name_kana": "タカハシ",
    "given_name_kana": "ミツグ",
    "birthday": "1979-06-03",
    "birth_time": "21:05",
    "birthplace": "秋田県大仙市",
    "mbti": "INFJ",
    "blood_type": "AB型",
}

# 相性トップ5女性芸能人（30人中の上位）
TOP5_CELEBRITIES = [
    {
        "rank": 1,
        "family_name": "永野",
        "given_name": "芽郁",
        "family_name_kana": "ナガノ",
        "given_name_kana": "メイ",
        "birthday": "1999-09-24",
        "birth_time": "",
        "birthplace": "東京都",
        "mbti": "INFP",
        "blood_type": "AB型",
        "note": "INFP × INFJ — 理想主義者同士の深い共鳴",
    },
    {
        "rank": 2,
        "family_name": "吉高",
        "given_name": "由里子",
        "family_name_kana": "ヨシタカ",
        "given_name_kana": "ユリコ",
        "birthday": "1988-07-22",
        "birth_time": "",
        "birthplace": "東京都",
        "mbti": "INFP",
        "blood_type": "O型",
        "note": "INFP × INFJ — 感性豊かな直感型ペア",
    },
    {
        "rank": 3,
        "family_name": "",
        "given_name": "波瑠",
        "family_name_kana": "",
        "given_name_kana": "ハル",
        "birthday": "1991-06-17",
        "birth_time": "",
        "birthplace": "東京都",
        "mbti": "INTJ",
        "blood_type": "O型",
        "note": "INTJ × INFJ — 戦略家と提唱者の知的パートナー",
    },
    {
        "rank": 4,
        "family_name": "川口",
        "given_name": "春奈",
        "family_name_kana": "カワグチ",
        "given_name_kana": "ハルナ",
        "birthday": "1995-02-10",
        "birth_time": "",
        "birthplace": "長崎県",
        "mbti": "ESFJ",
        "blood_type": "O型",
        "note": "ESFJ × INFJ — 献身的な支え合い",
    },
    {
        "rank": 5,
        "family_name": "戸田",
        "given_name": "恵梨香",
        "family_name_kana": "トダ",
        "given_name_kana": "エリカ",
        "birthday": "1988-08-17",
        "birth_time": "",
        "birthplace": "兵庫県神戸市",
        "mbti": "ISFJ",
        "blood_type": "A型",
        "note": "ISFJ × INFJ — なおさんと同じMBTIタイプ",
    },
]


def slow_type(element, text, delay=0.06):
    element.clear()
    for ch in text:
        element.send_keys(ch)
        time.sleep(delay)


def fill_person(driver, prefix, person, visible=True):
    """片方の人物データを入力"""
    for field_key, form_field in [("family_name", "family_name"), ("given_name", "given_name"),
                                   ("family_name_kana", "family_name_kana"), ("given_name_kana", "given_name_kana")]:
        val = person.get(field_key, "")
        if val:
            el = driver.find_element(By.NAME, f"{prefix}_{form_field}")
            if visible:
                slow_type(el, val)
                time.sleep(0.3)
            else:
                el.clear()
                el.send_keys(val)

    el = driver.find_element(By.NAME, f"{prefix}_birthday")
    driver.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
        el, person["birthday"]
    )
    if visible:
        time.sleep(0.2)

    if person.get("birth_time"):
        el = driver.find_element(By.NAME, f"{prefix}_birth_time")
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            el, person["birth_time"]
        )

    if person.get("birthplace"):
        el = driver.find_element(By.NAME, f"{prefix}_birthplace")
        if visible:
            slow_type(el, person["birthplace"])
            time.sleep(0.2)
        else:
            el.clear()
            el.send_keys(person["birthplace"])

    sel = Select(driver.find_element(By.NAME, f"{prefix}_mbti"))
    sel.select_by_value(person["mbti"])
    if visible:
        time.sleep(0.2)

    if person.get("blood_type"):
        sel = Select(driver.find_element(By.NAME, f"{prefix}_blood_type"))
        sel.select_by_value(person["blood_type"])
        if visible:
            time.sleep(0.2)


def extract_result(driver):
    """結果ページからスコア・ランクを抽出"""
    result = {}
    body_text = driver.find_element(By.TAG_NAME, "body").text
    page_source = driver.page_source

    try:
        rank_el = driver.find_element(By.ID, "rank-badge")
        result["rank"] = rank_el.get_attribute("data-rank")
    except Exception:
        result["rank"] = "unknown"

    try:
        score_el = driver.find_element(By.ID, "total-score")
        result["total_score"] = int(score_el.get_attribute("data-score"))
    except Exception:
        result["total_score"] = None

    categories = ["東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"]
    result["categories_found"] = sum(1 for c in categories if c in body_text)
    result["has_error"] = "Internal Server Error" in page_source or "Traceback" in page_source

    return result


def main():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--window-position=100,50")
    driver = webdriver.Chrome(options=opts)

    all_results = []

    try:
        print("=" * 66)
        print("  貢さん × 相性トップ5 女性芸能人 — RPA風ブラウザテスト")
        print(f"  実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 66)

        wait = WebDriverWait(driver, 10)

        for celeb in TOP5_CELEBRITIES:
            celeb_display_name = celeb["family_name"] + celeb["given_name"]
            print(f"\n--- {celeb['rank']}位: 貢さん × {celeb_display_name} ---")
            print(f"    {celeb['note']}")

            driver.get(BASE_URL)
            wait.until(EC.presence_of_element_located((By.NAME, "a_birthday")))
            time.sleep(0.5)

            # 貢さん入力
            fill_person(driver, "a", PERSON_A, visible=True)
            # 芸能人入力
            fill_person(driver, "b", celeb, visible=True)

            # 送信
            btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn
            )
            time.sleep(0.5)
            btn.click()

            wait.until(EC.url_contains("/analyze"))
            time.sleep(1.5)

            # 結果抽出
            data = extract_result(driver)
            status = "PASS" if not data["has_error"] and data["total_score"] is not None else "FAIL"

            print(f"  -> {status} | スコア: {data['total_score']}点 | ランク: {data['rank']} | カテゴリ: {data['categories_found']}/6")

            all_results.append({
                "rank_expected": celeb["rank"],
                "name": celeb["family_name"] + celeb["given_name"],
                "mbti": celeb["mbti"],
                "blood_type": celeb["blood_type"],
                "score": data["total_score"],
                "rank": data["rank"],
                "status": status,
            })

            # ゆっくりスクロールして結果を見せる
            driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            time.sleep(0.5)
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            viewport = driver.execute_script("return window.innerHeight")
            pos = 0
            while pos < scroll_height:
                pos += int(viewport * 0.5)
                driver.execute_script(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}});")
                time.sleep(0.6)
            time.sleep(2)

        # サマリ
        pass_count = sum(1 for r in all_results if r["status"] == "PASS")
        print("\n" + "=" * 66)
        print("  テスト結果サマリ")
        print("=" * 66)
        print(f"  PASS: {pass_count} / FAIL: {len(all_results) - pass_count} / 合計: {len(all_results)}")

        print("\n" + "=" * 66)
        print("  貢さん × 相性トップ5 女性芸能人 — スコア一覧")
        print("=" * 66)
        for r in all_results:
            print(f"    {r['rank_expected']}位 {r['name']:8s} ({r['mbti']}, {r['blood_type']}): {r['score']}点 (ランク {r['rank']})")

        scores = [r["score"] for r in all_results if r["score"] is not None]
        if scores:
            print(f"    --- 平均: {sum(scores) / len(scores):.1f}点 ---")

        print("=" * 66)

    finally:
        driver.quit()
        print("\nブラウザを閉じました。")


if __name__ == "__main__":
    main()
