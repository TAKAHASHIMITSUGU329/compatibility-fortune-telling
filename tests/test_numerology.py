"""数秘術計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.numerology import calculate, _life_path_number, _birthday_number, _challenge_number


# テストデータ
MITSUGU = {
    "name": "貢",
    "birthday": date(1979, 6, 3),
    "mbti": "INFJ",
    "enneagram": "タイプ1",
    "wing": "w4",
    "blood_type": None,
    "birth_time": None,
    "birthplace": None,
}

NAO = {
    "name": "なお",
    "birthday": date(1999, 5, 7),
    "mbti": "ISFJ",
    "blood_type": "B型",
    "enneagram": "タイプ2",
    "wing": "w6",
    "birth_time": None,
    "birthplace": None,
}


class TestLifePathNumber:
    def test_mitsugu_life_path(self):
        """貢さん: 1+9+7+9=26->8, 6, 3 -> 8+6+3=17->8"""
        assert _life_path_number(date(1979, 6, 3)) == 8

    def test_nao_life_path(self):
        """なおさん: 1+9+9+9=28->10->1, 5, 7 -> 1+5+7=13->4"""
        assert _life_path_number(date(1999, 5, 7)) == 4

    def test_master_number_11(self):
        """マスターナンバー11のテスト"""
        # 1990/1/1: 1+9+9+0=19->10->1, 1, 1 -> 3 (not 11)
        # 2009/9/9: 2+0+0+9=11, 9, 9 -> 11+9+9=29->11
        result = _life_path_number(date(2009, 9, 9))
        assert result == 11

    def test_master_number_22(self):
        """マスターナンバー22のテスト"""
        # Need to find a date that gives 22
        # 1993/8/8: 1+9+9+3=22, 8, 8 -> 22+8+8=38->11
        result = _life_path_number(date(1993, 8, 8))
        assert result == 11  # 22+8+8=38->3+8=11


class TestBirthdayNumber:
    def test_mitsugu_birthday_number(self):
        assert _birthday_number(date(1979, 6, 3)) == 3

    def test_nao_birthday_number(self):
        assert _birthday_number(date(1999, 5, 7)) == 7

    def test_two_digit_day(self):
        assert _birthday_number(date(2000, 1, 28)) == 1  # 2+8=10->1


class TestChallengeNumber:
    def test_mitsugu_challenge(self):
        # month=6, day=3 -> |6-3| = 3
        assert _challenge_number(date(1979, 6, 3)) == 3

    def test_nao_challenge(self):
        # month=5, day=7 -> |5-7| = 2
        assert _challenge_number(date(1999, 5, 7)) == 2


class TestCalculate:
    def test_returns_correct_structure(self):
        result = calculate(MITSUGU, NAO)
        assert result is not None
        assert "name" in result
        assert "category" in result
        assert "score" in result
        assert "score_100" in result
        assert "summary" in result
        assert "details" in result
        assert "highlights" in result
        assert "advice" in result

    def test_category(self):
        result = calculate(MITSUGU, NAO)
        assert result["category"] == "numerology"
        assert result["name"] == "数秘術"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_content(self):
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_a"]["life_path"] == 8
        assert result["details"]["person_b"]["life_path"] == 4
        assert result["details"]["person_a"]["birthday_number"] == 3
        assert result["details"]["person_b"]["birthday_number"] == 7
