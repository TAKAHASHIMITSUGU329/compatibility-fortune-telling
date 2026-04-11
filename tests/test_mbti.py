"""MBTI相性計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.mbti import calculate, COGNITIVE_FUNCTIONS


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
        assert result["category"] == "mbti"
        assert result["name"] == "MBTI相性"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_infj_isfj_compatibility(self):
        result = calculate(MITSUGU, NAO)
        # INFJ_ISFJ is defined in data, should have a reasonable score
        assert result["details"]["person_a"]["type"] == "INFJ"
        assert result["details"]["person_b"]["type"] == "ISFJ"

    def test_cognitive_functions(self):
        assert COGNITIVE_FUNCTIONS["INFJ"] == ["Ni", "Fe", "Ti", "Se"]
        assert COGNITIVE_FUNCTIONS["ISFJ"] == ["Si", "Fe", "Ti", "Ne"]

    def test_missing_mbti_returns_none(self):
        person_no_mbti = {"name": "test", "birthday": date(2000, 1, 1), "mbti": ""}
        result = calculate(person_no_mbti, NAO)
        assert result is None

    def test_both_missing_returns_none(self):
        p1 = {"name": "test1", "birthday": date(2000, 1, 1), "mbti": ""}
        p2 = {"name": "test2", "birthday": date(2000, 1, 1), "mbti": ""}
        result = calculate(p1, p2)
        assert result is None
