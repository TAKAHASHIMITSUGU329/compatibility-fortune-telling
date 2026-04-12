"""Selenium E2Eテスト — 貢さん×浩代さん 相性分析（RPA風ブラウザ表示）"""

import time
import re
import json
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
PERSON_B = {
    "family_name": "高橋",
    "given_name": "浩代",
    "family_name_kana": "タカハシ",
    "given_name_kana": "ヒロヨ",
    "birthday": "1972-11-14",
    "birth_time": "01:44",
    "birthplace": "福島県双葉郡双葉町",
    "mbti": "INFJ",
    "blood_type": "A型",
}


def slow_type(element, text, delay=0.06):
    element.clear()
    for ch in text:
        element.send_keys(ch)
        time.sleep(delay)


def main():
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--window-position=100,50")
    driver = webdriver.Chrome(options=opts)

    try:
        print("=" * 60)
        print("  貢さん × 浩代さん 相性分析 — ブラウザ実行")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        driver.get(BASE_URL)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "a_birthday")))
        time.sleep(1)

        # --- 男性（貢さん）---
        print("\n[入力中] 男性: 貢さん")
        for field_key, form_field in [("family_name", "a_family_name"), ("given_name", "a_given_name"),
                                       ("family_name_kana", "a_family_name_kana"), ("given_name_kana", "a_given_name_kana")]:
            val = PERSON_A.get(field_key, "")
            if val:
                el = driver.find_element(By.NAME, form_field)
                slow_type(el, val)
                time.sleep(0.3)

        el = driver.find_element(By.NAME, "a_birthday")
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            el, PERSON_A["birthday"]
        )
        time.sleep(0.3)

        if PERSON_A["birth_time"]:
            el = driver.find_element(By.NAME, "a_birth_time")
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                el, PERSON_A["birth_time"]
            )
            time.sleep(0.2)

        if PERSON_A["birthplace"]:
            el = driver.find_element(By.NAME, "a_birthplace")
            slow_type(el, PERSON_A["birthplace"])
            time.sleep(0.3)

        sel = Select(driver.find_element(By.NAME, "a_mbti"))
        sel.select_by_value(PERSON_A["mbti"])
        time.sleep(0.3)

        if PERSON_A["blood_type"]:
            sel = Select(driver.find_element(By.NAME, "a_blood_type"))
            sel.select_by_value(PERSON_A["blood_type"])
            time.sleep(0.2)

        # --- 女性（浩代さん）---
        print("[入力中] 女性: 浩代さん")
        for field_key, form_field in [("family_name", "b_family_name"), ("given_name", "b_given_name"),
                                       ("family_name_kana", "b_family_name_kana"), ("given_name_kana", "b_given_name_kana")]:
            val = PERSON_B.get(field_key, "")
            if val:
                el = driver.find_element(By.NAME, form_field)
                slow_type(el, val)
                time.sleep(0.3)

        el = driver.find_element(By.NAME, "b_birthday")
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
            el, PERSON_B["birthday"]
        )
        time.sleep(0.3)

        if PERSON_B["birth_time"]:
            el = driver.find_element(By.NAME, "b_birth_time")
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                el, PERSON_B["birth_time"]
            )
            time.sleep(0.2)

        if PERSON_B["birthplace"]:
            el = driver.find_element(By.NAME, "b_birthplace")
            slow_type(el, PERSON_B["birthplace"])
            time.sleep(0.3)

        sel = Select(driver.find_element(By.NAME, "b_mbti"))
        sel.select_by_value(PERSON_B["mbti"])
        time.sleep(0.3)

        if PERSON_B["blood_type"]:
            sel = Select(driver.find_element(By.NAME, "b_blood_type"))
            sel.select_by_value(PERSON_B["blood_type"])
            time.sleep(0.2)

        # 送信
        btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
        time.sleep(1)
        print("\n[実行] 分析ボタンをクリック...")
        btn.click()

        wait.until(EC.url_contains("/analyze"))
        time.sleep(1.5)

        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(1)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        page_source = driver.page_source

        score_match = re.search(r'(\d{1,3})\s*[点/]', body_text)
        total_score = int(score_match.group(1)) if score_match else "抽出失敗"

        rank = "不明"
        for r in ["SSS", "SS", "S", "A", "B", "C", "D"]:
            if r in body_text:
                rank = r
                break

        categories = ["東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"]
        found_cats = [c for c in categories if c in body_text]
        has_error = "Internal Server Error" in page_source or "Traceback" in page_source

        # スクロール
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        viewport = driver.execute_script("return window.innerHeight")
        pos = 0
        while pos < scroll_height:
            pos += int(viewport * 0.4)
            driver.execute_script(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}});")
            time.sleep(0.8)

        print("\n" + "=" * 60)
        print("  分析結果")
        print("=" * 60)
        print(f"  総合スコア : {total_score}点")
        print(f"  ランク     : {rank}")
        print(f"  カテゴリ   : {len(found_cats)}/6 表示")
        print(f"  エラー     : {'あり' if has_error else 'なし'}")
        print("=" * 60)

        print("\n結果画面を表示中（10秒）...")
        time.sleep(10)

    finally:
        driver.quit()
        print("\nブラウザを閉じました。")


if __name__ == "__main__":
    main()
