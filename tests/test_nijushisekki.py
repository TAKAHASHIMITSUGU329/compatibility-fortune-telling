"""二十四節気計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.nijushisekki import calculate, _get_sekki


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


class TestGetSekki:
    def test_mitsugu_sekki(self):
        """6月3日は小満（5/21）の後、芒種（6/6）の前"""
        assert _get_sekki(date(1979, 6, 3)) == "小満"

    def test_nao_sekki(self):
        """5月7日は立夏（5/6）の後、小満（5/21）の前"""
        assert _get_sekki(date(1999, 5, 7)) == "立夏"

    def test_winter_solstice(self):
        """12月25日は冬至"""
        assert _get_sekki(date(2000, 12, 25)) == "冬至"

    def test_spring_equinox(self):
        """3月21日は春分"""
        assert _get_sekki(date(2000, 3, 21)) == "春分"


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
        assert result["category"] == "nijushisekki"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_gogyo(self):
        result = calculate(MITSUGU, NAO)
        # 小満(6月) = 火, 立夏(5月) = 火
        assert result["details"]["person_a"]["gogyo"] == "火"
        assert result["details"]["person_b"]["gogyo"] == "火"
