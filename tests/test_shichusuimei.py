"""四柱推命計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.shichusuimei import (
    calculate,
    _year_pillar,
    _month_pillar,
    _day_pillar,
    _kanshi_str,
    _check_kango,
    _check_taichu,
    _gogyo_relationship,
    JIKKAN_GOGYO,
)


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


class TestYearPillar:
    def test_mitsugu_year(self):
        """貢さん: 年柱 = 己未"""
        assert _kanshi_str(_year_pillar(date(1979, 6, 3))) == "己未"

    def test_nao_year(self):
        """なおさん: 年柱 = 己卯"""
        assert _kanshi_str(_year_pillar(date(1999, 5, 7))) == "己卯"

    def test_before_setsubun(self):
        """立春前は前年の干支"""
        # 2000年1月15日 → 1999年の干支
        result = _kanshi_str(_year_pillar(date(2000, 1, 15)))
        assert result == _kanshi_str(_year_pillar(date(1999, 6, 1)))


class TestMonthPillar:
    def test_mitsugu_month(self):
        """貢さん: 月柱 = 己巳"""
        assert _kanshi_str(_month_pillar(date(1979, 6, 3))) == "己巳"

    def test_nao_month(self):
        """なおさん: 月柱 = 己巳"""
        assert _kanshi_str(_month_pillar(date(1999, 5, 7))) == "己巳"

    def test_month_match(self):
        """貢さんとなおさんの月柱が一致"""
        m_a = _kanshi_str(_month_pillar(date(1979, 6, 3)))
        m_b = _kanshi_str(_month_pillar(date(1999, 5, 7)))
        assert m_a == m_b == "己巳"


class TestDayPillar:
    def test_mitsugu_day(self):
        """貢さん: 日柱 = 戊午"""
        assert _kanshi_str(_day_pillar(date(1979, 6, 3))) == "戊午"


class TestGogyo:
    def test_biwa(self):
        """同じ五行 = 比和"""
        rel, desc = _gogyo_relationship("木", "木")
        assert rel == "比和"

    def test_sosho(self):
        """相生関係"""
        rel, desc = _gogyo_relationship("木", "火")
        assert "相生" in rel

    def test_sokoku(self):
        """相剋関係"""
        rel, desc = _gogyo_relationship("木", "土")
        assert "相剋" in rel


class TestSpecialRelations:
    def test_kango(self):
        """干合の判定"""
        assert _check_kango("甲", "己") is True
        assert _check_kango("甲", "乙") is False

    def test_taichu(self):
        """対冲の判定"""
        assert _check_taichu("子", "午") is True
        assert _check_taichu("子", "丑") is False


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
        assert result["category"] == "shichusuimei"
        assert result["name"] == "四柱推命"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_pillars_correct(self):
        """年柱・月柱・日柱が正しいこと"""
        result = calculate(MITSUGU, NAO)
        details = result["details"]
        assert details["person_a"]["year_pillar"] == "己未"
        assert details["person_a"]["month_pillar"] == "己巳"
        assert details["person_a"]["day_pillar"] == "戊午"
        assert details["person_b"]["year_pillar"] == "己卯"
        assert details["person_b"]["month_pillar"] == "己巳"

    def test_month_match_detected(self):
        """月柱の一致が検出されること"""
        result = calculate(MITSUGU, NAO)
        assert "月柱完全一致" in result["details"]["special_relations"]

    def test_taichu_detected(self):
        """日柱の対冲（午×子）が検出されること"""
        result = calculate(MITSUGU, NAO)
        assert "日支対冲" in result["details"]["special_relations"]
