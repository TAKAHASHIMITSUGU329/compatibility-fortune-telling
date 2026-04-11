"""西洋占星術計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.astrology import (
    calculate,
    _get_solar_sign_simple,
    _compute_aspect_angle,
    _aspect_name,
    _aspect_score,
    SIGN_JA,
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


class TestSolarSignSimple:
    def test_gemini(self):
        """6月3日 = ふたご座"""
        assert _get_solar_sign_simple(6, 3) == "Gem"

    def test_taurus(self):
        """5月7日 = おうし座"""
        assert _get_solar_sign_simple(5, 7) == "Tau"

    def test_capricorn_early_jan(self):
        """1月5日 = やぎ座"""
        assert _get_solar_sign_simple(1, 5) == "Cap"

    def test_aquarius(self):
        """2月1日 = みずがめ座"""
        assert _get_solar_sign_simple(2, 1) == "Aqu"

    def test_aries(self):
        """4月1日 = おひつじ座"""
        assert _get_solar_sign_simple(4, 1) == "Ari"


class TestAspectAngle:
    def test_same_sign(self):
        """同じ星座 = 0度"""
        assert _compute_aspect_angle("Gem", "Gem") == 0

    def test_adjacent_signs(self):
        """隣接星座 = 30度"""
        assert _compute_aspect_angle("Gem", "Tau") == 30

    def test_trine(self):
        """トライン = 120度"""
        assert _compute_aspect_angle("Ari", "Leo") == 120

    def test_opposition(self):
        """オポジション = 180度"""
        assert _compute_aspect_angle("Ari", "Lib") == 180

    def test_sextile(self):
        """セクスタイル = 60度"""
        assert _compute_aspect_angle("Ari", "Gem") == 60

    def test_square(self):
        """スクエア = 90度"""
        assert _compute_aspect_angle("Ari", "Can") == 90


class TestAspectName:
    def test_conjunction(self):
        name, desc = _aspect_name(0)
        assert name == "コンジャンクション"

    def test_trine(self):
        name, desc = _aspect_name(120)
        assert name == "トライン"

    def test_opposition(self):
        name, desc = _aspect_name(180)
        assert name == "オポジション"


class TestAspectScore:
    def test_trine_highest(self):
        """トラインが最高スコア"""
        assert _aspect_score(120) == 95

    def test_square_low(self):
        """スクエアは低スコア"""
        assert _aspect_score(90) == 45


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
        assert result["category"] == "astrology"
        assert result["name"] == "西洋占星術"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_sun_signs(self):
        """太陽星座が正しく算出されること"""
        result = calculate(MITSUGU, NAO)
        details = result["details"]
        # 貢さん = ふたご座、なおさん = おうし座
        assert details["person_a"]["sun"] == "Gem"
        assert details["person_b"]["sun"] == "Tau"

    def test_aspects_present(self):
        """アスペクトが計算されていること"""
        result = calculate(MITSUGU, NAO)
        aspects = result["details"]["aspects"]
        assert len(aspects) > 0
        # 太陽×太陽は必ず含まれる
        pair_names = [a["pair"] for a in aspects]
        assert "太陽×太陽" in pair_names

    def test_with_birth_time(self):
        """出生時刻付きでも正常動作すること"""
        person = {**MITSUGU, "birth_time": "12:00"}
        result = calculate(person, NAO)
        assert result is not None
        assert result["score_100"] >= 0
