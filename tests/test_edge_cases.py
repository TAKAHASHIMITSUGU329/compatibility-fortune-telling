"""エッジケーステスト — 各calculatorの境界値・異常入力への耐性を検証"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators import run_all, ALL_CALCULATORS, REQUIRED_KEYS


# --- テストデータ ---

NORMAL_A = {
    "name": "テスト男",
    "birthday": date(1979, 6, 3),
    "mbti": "INFJ",
    "blood_type": "A型",
    "enneagram": "4",
    "wing": "5",
    "birth_time": None,
    "birthplace": None,
}

NORMAL_B = {
    "name": "テスト女",
    "birthday": date(1999, 12, 22),
    "mbti": "ISFJ",
    "blood_type": "O型",
    "enneagram": "2",
    "wing": "1",
    "birth_time": None,
    "birthplace": None,
}

LEAP_YEAR_PERSON = {
    "name": "うるう",
    "birthday": date(2000, 2, 29),
    "mbti": "ENTP",
    "blood_type": "B型",
    "enneagram": "7",
    "wing": "8",
    "birth_time": None,
    "birthplace": None,
}

MINIMAL_PERSON = {
    "name": "",
    "birthday": date(1990, 1, 1),
    "mbti": None,
    "blood_type": None,
    "enneagram": None,
    "wing": None,
    "birth_time": None,
    "birthplace": None,
}

OLD_PERSON = {
    "name": "古い人",
    "birthday": date(1920, 3, 15),
    "mbti": "ISTJ",
    "blood_type": "AB型",
    "enneagram": "1",
    "wing": "9",
    "birth_time": None,
    "birthplace": None,
}

YEAR_2000_PERSON = {
    "name": "ミレニアム",
    "birthday": date(2000, 1, 1),
    "mbti": "ENFP",
    "blood_type": "A型",
    "enneagram": "3",
    "wing": "2",
    "birth_time": None,
    "birthplace": None,
}


class TestLeapYear:
    """うるう年（2/29生まれ）のテスト"""

    def test_run_all_leap_year(self):
        result = run_all(LEAP_YEAR_PERSON, NORMAL_B)
        assert len(result["results"]) > 0
        assert len(result["errors"]) == 0

    def test_leap_year_both(self):
        person_b_leap = {**NORMAL_B, "birthday": date(1996, 2, 29)}
        result = run_all(LEAP_YEAR_PERSON, person_b_leap)
        assert len(result["results"]) > 0
        assert len(result["errors"]) == 0


class TestSamePerson:
    """同一人物同士（同じ生年月日・同じMBTI）のテスト"""

    def test_same_person(self):
        result = run_all(NORMAL_A, NORMAL_A)
        assert len(result["results"]) > 0
        assert len(result["errors"]) == 0
        for r in result["results"]:
            assert 0 <= r["score_100"] <= 100

    def test_same_birthday_different_mbti(self):
        person_b = {**NORMAL_A, "name": "別人", "mbti": "ESTP"}
        result = run_all(NORMAL_A, person_b)
        assert len(result["results"]) > 0
        assert len(result["errors"]) == 0


class TestMinimalInput:
    """最小限の入力（MBTI・血液型なし）でもクラッシュしないことを検証"""

    def test_minimal_both(self):
        """MBTI・血液型なしでもクラッシュせず、生年月日ベースのcalculatorは動作する"""
        result = run_all(MINIMAL_PERSON, MINIMAL_PERSON)
        assert len(result["errors"]) == 0
        # 生年月日のみで計算可能なcalculatorが結果を返す
        assert len(result["results"]) > 0

    def test_minimal_vs_normal(self):
        result = run_all(MINIMAL_PERSON, NORMAL_B)
        assert len(result["errors"]) == 0
        assert len(result["results"]) > 0


class TestOldDates:
    """古い生年月日でもクラッシュしないことを検証"""

    def test_1920_person(self):
        result = run_all(OLD_PERSON, NORMAL_B)
        assert len(result["results"]) > 0
        assert len(result["errors"]) == 0

    def test_year_boundary(self):
        """2000年境界のテスト"""
        result = run_all(YEAR_2000_PERSON, NORMAL_A)
        assert len(result["results"]) > 0
        assert len(result["errors"]) == 0


class TestResultSchema:
    """全calculatorの戻り値が必須キーを持つことを検証"""

    def test_all_results_have_required_keys(self):
        result = run_all(NORMAL_A, NORMAL_B)
        for r in result["results"]:
            missing = REQUIRED_KEYS - r.keys()
            assert not missing, f"{r.get('name', '?')}: missing keys {missing}"

    def test_score_ranges(self):
        result = run_all(NORMAL_A, NORMAL_B)
        for r in result["results"]:
            assert 1 <= r["score"] <= 5, f"{r['name']}: score={r['score']}"
            assert 0 <= r["score_100"] <= 100, f"{r['name']}: score_100={r['score_100']}"

    def test_name_not_empty(self):
        result = run_all(NORMAL_A, NORMAL_B)
        for r in result["results"]:
            assert r["name"], f"Empty name in result: {r}"

    def test_category_is_japanese(self):
        """categoryがCATEGORY定数（日本語）で付与されていること"""
        valid_categories = {"東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"}
        result = run_all(NORMAL_A, NORMAL_B)
        for r in result["results"]:
            assert r["category"] in valid_categories, f"{r['name']}: category='{r['category']}'"
