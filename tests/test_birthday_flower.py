"""誕生花計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.birthday_flower import calculate


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
        assert result["category"] == "birthday_flower"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_nao_birthday_flower(self):
        """5月7日の誕生花はスターチス"""
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_b"]["flower"] == "スターチス"

    def test_mitsugu_birthday_flower(self):
        """6月3日の誕生花はアジサイ"""
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_a"]["flower"] == "アジサイ"

    def test_same_season_flowers(self):
        """同じ季節の花は高スコア"""
        # 5月と6月は隣接 — 両方夏ではないが近い
        result = calculate(MITSUGU, NAO)
        assert result["score"] >= 3
