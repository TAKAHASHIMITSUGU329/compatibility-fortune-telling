"""エニアグラム相性計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.enneagram import calculate, _parse_type, _parse_wing


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


class TestParsing:
    def test_parse_type_with_prefix(self):
        assert _parse_type("タイプ1") == 1
        assert _parse_type("タイプ9") == 9

    def test_parse_type_number(self):
        assert _parse_type(1) == 1
        assert _parse_type(9) == 9

    def test_parse_type_empty(self):
        assert _parse_type("") == 0
        assert _parse_type(None) == 0

    def test_parse_wing(self):
        assert _parse_wing("w4") == 4
        assert _parse_wing("w6") == 6

    def test_parse_wing_empty(self):
        assert _parse_wing("") == 0
        assert _parse_wing(None) == 0


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
        assert result["category"] == "enneagram"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_type1_type2_compatibility(self):
        """タイプ1とタイプ2の相性"""
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_a"]["type"] == 1
        assert result["details"]["person_b"]["type"] == 2
        assert result["details"]["person_a"]["wing"] == 4
        assert result["details"]["person_b"]["wing"] == 6

    def test_missing_enneagram_estimates_from_mbti(self):
        person_no_ennea = {**MITSUGU, "enneagram": ""}
        result = calculate(person_no_ennea, NAO)
        # MBTIから自動推定されるのでNoneにはならない
        assert result is not None
        assert result["category"] == "enneagram"
