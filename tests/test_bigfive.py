"""ビッグファイブ性格分析エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.bigfive import (
    calculate, _estimate_bigfive, _calc_similarity,
    _calc_complementarity, _get_level, _parse_enneagram_type,
)


# テストデータ
MITSUGU = {
    "name": "貢",
    "birthday": date(1979, 6, 3),
    "mbti": "INFJ",
    "enneagram": "タイプ1",
    "wing": "w4",
    "blood_type": None,
}

NAO = {
    "name": "なお",
    "birthday": date(1999, 5, 7),
    "mbti": "ISFJ",
    "blood_type": "B型",
    "enneagram": "タイプ2",
    "wing": "w6",
}


class TestParseEnneagramType:
    def test_type_japanese(self):
        assert _parse_enneagram_type({"enneagram": "タイプ1"}) == 1

    def test_type_with_wing(self):
        assert _parse_enneagram_type({"enneagram": "4w5"}) == 4

    def test_type_int(self):
        assert _parse_enneagram_type({"enneagram": 7}) == 7

    def test_type_missing(self):
        assert _parse_enneagram_type({}) == 5  # デフォルト


class TestEstimateBigfive:
    def test_infj(self):
        """INFJ: I→外向性低、N→開放性高、F→協調性高、J→誠実性高"""
        scores = _estimate_bigfive(MITSUGU)
        assert scores['extraversion'] < 50  # I = 内向的
        assert scores['openness'] > 50       # N = 開放性高
        assert scores['agreeableness'] > 50  # F = 協調性高
        assert scores['conscientiousness'] > 50  # J = 誠実性高

    def test_isfj(self):
        """ISFJ: I→外向性低、S→開放性低、F→協調性高、J→誠実性高"""
        scores = _estimate_bigfive(NAO)
        assert scores['extraversion'] < 50  # I = 内向的
        assert scores['openness'] < 50       # S = 開放性低
        assert scores['agreeableness'] > 50  # F = 協調性高
        assert scores['conscientiousness'] > 50  # J = 誠実性高

    def test_enneagram_neuroticism(self):
        """エニアグラムタイプ1は神経症的傾向やや高め"""
        scores = _estimate_bigfive(MITSUGU)
        assert scores['neuroticism'] == 55  # タイプ1

    def test_enfp(self):
        """ENFP: E→外向性高、N→開放性高、F→協調性高、P→誠実性低"""
        person = {"mbti": "ENFP", "enneagram": "タイプ7"}
        scores = _estimate_bigfive(person)
        assert scores['extraversion'] > 50
        assert scores['openness'] > 50
        assert scores['agreeableness'] > 50
        assert scores['conscientiousness'] < 50
        assert scores['neuroticism'] == 25  # タイプ7は低い

    def test_all_scores_in_range(self):
        """全因子が0-100の範囲内"""
        for mbti in ["ENFP", "ISTJ", "INTP", "ESFJ"]:
            scores = _estimate_bigfive({"mbti": mbti, "enneagram": "タイプ5"})
            for factor, value in scores.items():
                assert 0 <= value <= 100, f"{mbti} {factor}={value}"


class TestGetLevel:
    def test_high(self):
        assert _get_level(80) == 'high'

    def test_mid(self):
        assert _get_level(50) == 'mid'

    def test_low(self):
        assert _get_level(20) == 'low'

    def test_boundary_high(self):
        assert _get_level(65) == 'high'

    def test_boundary_mid(self):
        assert _get_level(40) == 'mid'


class TestSimilarity:
    def test_identical(self):
        scores = {'extraversion': 50, 'openness': 50, 'agreeableness': 50,
                   'conscientiousness': 50, 'neuroticism': 50}
        assert _calc_similarity(scores, scores) == 100

    def test_opposite(self):
        scores_a = {'extraversion': 0, 'openness': 0, 'agreeableness': 0,
                     'conscientiousness': 0, 'neuroticism': 0}
        scores_b = {'extraversion': 100, 'openness': 100, 'agreeableness': 100,
                     'conscientiousness': 100, 'neuroticism': 100}
        assert _calc_similarity(scores_a, scores_b) == 0


class TestComplementarity:
    def test_returns_valid_range(self):
        scores_a = _estimate_bigfive(MITSUGU)
        scores_b = _estimate_bigfive(NAO)
        comp = _calc_complementarity(scores_a, scores_b)
        assert 0 <= comp <= 100


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
        assert result["category"] == "bigfive"
        assert result["name"] == "ビッグファイブ性格分析"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_content(self):
        result = calculate(MITSUGU, NAO)
        assert "person_a" in result["details"]
        assert "person_b" in result["details"]
        assert "scores" in result["details"]["person_a"]
        assert "compatibility" in result["details"]
        assert "similarity" in result["details"]["compatibility"]
        assert "complementarity" in result["details"]["compatibility"]

    def test_no_mbti_returns_none(self):
        result = calculate({"name": "テスト"}, NAO)
        assert result is None

    def test_highlights_has_all_factors(self):
        result = calculate(MITSUGU, NAO)
        # 5因子 + 類似度/補完度 = 6行以上
        assert len(result["highlights"]) >= 6

    def test_infj_vs_isfj_similarity(self):
        """INFJ vs ISFJは外向性・協調性・誠実性が近いため類似度はそれなり"""
        result = calculate(MITSUGU, NAO)
        similarity = result["details"]["compatibility"]["similarity"]
        assert similarity > 40  # ある程度似ているはず
