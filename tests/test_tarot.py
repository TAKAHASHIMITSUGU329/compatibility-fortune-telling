"""タロット誕生日カード計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.tarot import calculate, _life_path_number


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


class TestLifePathForTarot:
    def test_mitsugu_tarot_number(self):
        """1979年6月3日: 1+9+7+9+0+6+0+3 = 35 -> 3+5 = 8"""
        assert _life_path_number(date(1979, 6, 3)) == 8

    def test_nao_tarot_number(self):
        """1999年5月7日: 1+9+9+9+0+5+0+7 = 40 -> 4+0 = 4"""
        assert _life_path_number(date(1999, 5, 7)) == 4


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
        assert result["category"] == "tarot"
        assert result["name"] == "タロット誕生日カード"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_card_names_present(self):
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_a"]["card_name"] != "不明"
        assert result["details"]["person_b"]["card_name"] != "不明"
