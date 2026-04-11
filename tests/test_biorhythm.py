"""バイオリズム計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.biorhythm import calculate, _biorhythm_value


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


class TestBiorhythmValue:
    def test_birthday_is_zero(self):
        """誕生日当日のバイオリズムは0"""
        bd = date(1979, 6, 3)
        assert abs(_biorhythm_value(bd, bd, 23)) < 0.001
        assert abs(_biorhythm_value(bd, bd, 28)) < 0.001
        assert abs(_biorhythm_value(bd, bd, 33)) < 0.001

    def test_value_range(self):
        """バイオリズム値は-1から1の範囲"""
        bd = date(1979, 6, 3)
        for days_offset in range(100):
            target = date(2024, 1, 1)
            val = _biorhythm_value(bd, target, 23)
            assert -1.001 <= val <= 1.001


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
        assert result["category"] == "biorhythm"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_have_three_cycles(self):
        result = calculate(MITSUGU, NAO)
        compat = result["details"]["compatibility"]
        assert "physical" in compat
        assert "emotional" in compat
        assert "intellectual" in compat

    def test_target_date(self):
        result = calculate(MITSUGU, NAO)
        assert "target_date" in result["details"]
