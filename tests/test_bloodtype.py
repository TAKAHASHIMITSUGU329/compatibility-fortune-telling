"""血液型相性計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.bloodtype import calculate


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


class TestCalculate:
    def test_missing_blood_type_returns_none(self):
        """血液型が未入力の場合はNoneを返す"""
        result = calculate(MITSUGU, NAO)
        assert result is None  # MITSUGUの血液型がNone

    def test_both_blood_types(self):
        """両方の血液型がある場合"""
        person_a = {**MITSUGU, "blood_type": "A型"}
        result = calculate(person_a, NAO)
        assert result is not None
        assert result["category"] == "bloodtype"

    def test_returns_correct_structure(self):
        person_a = {**MITSUGU, "blood_type": "A型"}
        result = calculate(person_a, NAO)
        assert "name" in result
        assert "category" in result
        assert "score" in result
        assert "score_100" in result
        assert "summary" in result
        assert "details" in result
        assert "highlights" in result
        assert "advice" in result

    def test_score_range(self):
        person_a = {**MITSUGU, "blood_type": "O型"}
        result = calculate(person_a, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_a_b_compatibility(self):
        person_a = {**MITSUGU, "blood_type": "A型"}
        result = calculate(person_a, NAO)
        assert result["details"]["person_a"]["blood_type"] == "A"
        assert result["details"]["person_b"]["blood_type"] == "B"

    def test_normalize_blood_type_without_gata(self):
        """「型」なしでも正規化できる"""
        person_a = {**MITSUGU, "blood_type": "A"}
        person_b = {**NAO, "blood_type": "B"}
        result = calculate(person_a, person_b)
        assert result is not None
