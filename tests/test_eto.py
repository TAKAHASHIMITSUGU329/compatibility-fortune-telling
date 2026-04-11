"""干支計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.eto import calculate, _get_junishi, _get_junishi_index


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


class TestJunishi:
    def test_mitsugu_eto(self):
        """1979年は未年"""
        assert _get_junishi(date(1979, 6, 3)) == "未"

    def test_nao_eto(self):
        """1999年は卯年"""
        assert _get_junishi(date(1999, 5, 7)) == "卯"

    def test_2000_eto(self):
        """2000年は辰年"""
        assert _get_junishi(date(2000, 1, 1)) == "辰"

    def test_2024_eto(self):
        """2024年は辰年"""
        assert _get_junishi(date(2024, 1, 1)) == "辰"


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
        assert result["category"] == "eto"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_mitsugu_nao_eto(self):
        """未と卯の相性 — 三合（卯未亥の木局）"""
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_a"]["eto"] == "未"
        assert result["details"]["person_b"]["eto"] == "卯"
        # 卯(3)と未(7)は三合（卯未亥 = {3, 7, 11}）
        assert result["details"]["compatibility"]["relationship"] == "三合"
        assert result["score"] == 5
