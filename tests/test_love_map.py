"""愛の地図（ゴットマン理論）計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.love_map import (
    calculate, _calc_map_depth, _calc_bid_response,
    _parse_enneagram_type, _get_mbti,
    MBTI_DOMINANT, FUNCTION_MAP_DEPTH, FUNCTION_BID_RESPONSE,
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


class TestGetMbti:
    def test_normal(self):
        assert _get_mbti({"mbti": "INFJ"}) == "INFJ"

    def test_with_suffix(self):
        assert _get_mbti({"mbti": "INFJ-A"}) == "INFJ"

    def test_lowercase(self):
        assert _get_mbti({"mbti": "infj"}) == "INFJ"

    def test_empty(self):
        assert _get_mbti({"mbti": ""}) == ""

    def test_missing(self):
        assert _get_mbti({}) == ""


class TestParseEnneagramType:
    def test_string_format(self):
        assert _parse_enneagram_type({"enneagram": "タイプ1"}) == 1

    def test_int_format(self):
        assert _parse_enneagram_type({"enneagram": 2}) == 2

    def test_empty(self):
        assert _parse_enneagram_type({"enneagram": ""}) == 0

    def test_missing(self):
        assert _parse_enneagram_type({}) == 0

    def test_invalid(self):
        assert _parse_enneagram_type({"enneagram": "無効"}) == 0


class TestMapDepth:
    def test_infj_high_depth(self):
        """INFJはNi主機能で愛の地図が深い"""
        score, desc = _calc_map_depth("INFJ", 1)
        assert score >= 80
        assert len(desc) > 0

    def test_isfj_high_depth(self):
        """ISFJはSi主機能で愛の地図が深い"""
        score, desc = _calc_map_depth("ISFJ", 2)
        assert score >= 80

    def test_enneagram_2_bonus(self):
        """タイプ2は最もパートナーへの関心が高い"""
        score_no_bonus, _ = _calc_map_depth("ISFJ", 0)
        score_with_bonus, _ = _calc_map_depth("ISFJ", 2)
        assert score_with_bonus > score_no_bonus

    def test_score_range(self):
        """スコアが0-100の範囲内"""
        for mbti in MBTI_DOMINANT:
            for etype in range(1, 10):
                score, _ = _calc_map_depth(mbti, etype)
                assert 0 <= score <= 100


class TestBidResponse:
    def test_fe_dominant_high(self):
        """Fe主機能（ESFJ等）は入札応答率が高い"""
        rate, desc = _calc_bid_response("ESFJ", 2)
        assert rate >= 80

    def test_ti_dominant_low(self):
        """Ti主機能（INTP等）は入札応答率が低い"""
        rate, desc = _calc_bid_response("INTP", 5)
        assert rate < 60

    def test_rate_range(self):
        """応答率が0-100の範囲内"""
        for mbti in MBTI_DOMINANT:
            for etype in range(1, 10):
                rate, _ = _calc_bid_response(mbti, etype)
                assert 0 <= rate <= 100


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
        assert result["category"] == "love_map"
        assert "愛の地図" in result["name"]

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_content(self):
        result = calculate(MITSUGU, NAO)
        assert "person_a" in result["details"]
        assert "person_b" in result["details"]
        assert "map_depth" in result["details"]["person_a"]
        assert "bid_response_rate" in result["details"]["person_a"]
        assert "combined" in result["details"]

    def test_no_mbti_returns_none(self):
        result = calculate({"name": "テスト"}, NAO)
        assert result is None

    def test_highlights_non_empty(self):
        result = calculate(MITSUGU, NAO)
        assert len(result["highlights"]) >= 4

    def test_infj_isfj_map_depth(self):
        """INFJ(1w4) × ISFJ(2w6) はどちらも愛の地図が深い"""
        result = calculate(MITSUGU, NAO)
        depth_a = result["details"]["person_a"]["map_depth"]
        depth_b = result["details"]["person_b"]["map_depth"]
        # Ni主機能 + タイプ1、Si主機能 + タイプ2、どちらも高い
        assert depth_a >= 75
        assert depth_b >= 85  # タイプ2のボーナスが大きい

    def test_bid_pattern_in_highlights(self):
        """入札パターンがhighlightsに含まれること"""
        result = calculate(MITSUGU, NAO)
        bid_highlight = [h for h in result["highlights"] if "入札パターン" in h]
        assert len(bid_highlight) == 1
