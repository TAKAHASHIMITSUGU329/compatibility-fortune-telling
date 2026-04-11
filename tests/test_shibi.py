"""紫微斗数計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.shibi import (
    calculate, _estimate_lunar_month, _calc_meikyu_position,
    _get_fusaikyu_position, _get_star_at_position, _get_star_compat,
    JUNISHI, MAIN_STARS, STAR_LOVE_TRAITS, STAR_CATEGORIES,
)


# テストデータ
MITSUGU = {
    "name": "貢",
    "birthday": date(1979, 6, 3),
    "mbti": "INFJ",
    "enneagram": "タイプ1",
    "wing": "w4",
}

NAO = {
    "name": "なお",
    "birthday": date(1999, 5, 7),
    "mbti": "ISFJ",
    "blood_type": "B型",
    "enneagram": "タイプ2",
    "wing": "w6",
}


class TestLunarMonth:
    def test_valid_range(self):
        """旧暦月が1-12の範囲内であること"""
        for m in range(1, 13):
            lunar = _estimate_lunar_month(date(2000, m, 15))
            assert 1 <= lunar <= 12

    def test_mitsugu(self):
        lunar = _estimate_lunar_month(date(1979, 6, 3))
        assert 1 <= lunar <= 12

    def test_nao(self):
        lunar = _estimate_lunar_month(date(1999, 5, 7))
        assert 1 <= lunar <= 12


class TestMeikyuPosition:
    def test_returns_valid_junishi(self):
        """命宮位置が十二支のいずれかであること"""
        pos = _calc_meikyu_position(5, 6)
        assert pos in JUNISHI

    def test_different_months_different_positions(self):
        """異なる月で異なる命宮位置になること"""
        pos1 = _calc_meikyu_position(1, 6)
        pos2 = _calc_meikyu_position(7, 6)
        assert pos1 in JUNISHI
        assert pos2 in JUNISHI
        assert pos1 != pos2


class TestFusaikyuPosition:
    def test_returns_valid_junishi(self):
        """夫妻宮位置が十二支のいずれかであること"""
        for shi in JUNISHI:
            pos = _get_fusaikyu_position(shi)
            assert pos in JUNISHI

    def test_offset_from_meikyu(self):
        """夫妻宮は命宮から特定のオフセット位置にあること"""
        meikyu = "子"
        fusai = _get_fusaikyu_position(meikyu)
        assert fusai in JUNISHI
        assert fusai != meikyu  # 命宮と夫妻宮は異なる位置


class TestStarAtPosition:
    def test_all_positions_have_stars(self):
        """すべての十二支位置に主星が割り当てられていること"""
        for shi in JUNISHI:
            star = _get_star_at_position(shi)
            assert star in MAIN_STARS


class TestStarCompat:
    def test_valid_compat(self):
        """相性スコアが正しい範囲であること"""
        score, score_100, desc = _get_star_compat("温和", "堅実")
        assert 1 <= score <= 5
        assert 0 <= score_100 <= 100
        assert len(desc) > 0

    def test_symmetric(self):
        """順序が逆でも同じ結果"""
        r1 = _get_star_compat("主導", "温和")
        r2 = _get_star_compat("温和", "主導")
        assert r1 == r2


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
        assert result["category"] == "shibi"
        assert result["name"] == "紫微斗数"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_content(self):
        result = calculate(MITSUGU, NAO)
        assert "person_a" in result["details"]
        assert "person_b" in result["details"]
        assert "meikyu_position" in result["details"]["person_a"]
        assert "fusaikyu_star" in result["details"]["person_a"]
        assert "fusaikyu_type" in result["details"]["person_a"]

    def test_no_birthday_returns_none(self):
        result = calculate({"name": "テスト"}, NAO)
        assert result is None

    def test_highlights_non_empty(self):
        result = calculate(MITSUGU, NAO)
        assert len(result["highlights"]) >= 4
