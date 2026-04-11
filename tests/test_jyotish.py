"""インド占星術計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.jyotish import (
    calculate, _get_tropical_sign_index, _get_sidereal_sign_index,
    _estimate_nakshatra, _calc_tara_score, _get_varna_compat,
    TROPICAL_SIGNS, SIDEREAL_SIGNS, NAKSHATRAS, NAKSHATRA_VARNA,
    VARNA_LEVELS,
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


class TestTropicalSign:
    def test_mitsugu_gemini(self):
        """6月3日は双子座"""
        idx = _get_tropical_sign_index(date(1979, 6, 3))
        assert TROPICAL_SIGNS[idx] == "双子座"

    def test_nao_taurus(self):
        """5月7日は牡牛座"""
        idx = _get_tropical_sign_index(date(1999, 5, 7))
        assert TROPICAL_SIGNS[idx] == "牡牛座"

    def test_capricorn(self):
        """1月15日は山羊座(index=9)"""
        assert _get_tropical_sign_index(date(2000, 1, 15)) == 9


class TestSiderealSign:
    def test_offset(self):
        """サイデリアルはトロピカルの1つ前"""
        tropical = 2  # 双子座
        sidereal = _get_sidereal_sign_index(tropical)
        assert sidereal == 1  # 牡牛座 → ヴリシャバ

    def test_wrap_around(self):
        """牡羊座(0)のサイデリアルは魚座(11)"""
        sidereal = _get_sidereal_sign_index(0)
        assert sidereal == 11

    def test_mitsugu_sidereal(self):
        """貢: 双子座 → ヴリシャバ（牡牛）"""
        tropical = _get_tropical_sign_index(date(1979, 6, 3))
        sidereal = _get_sidereal_sign_index(tropical)
        assert "牡牛" in SIDEREAL_SIGNS[sidereal]


class TestNakshatra:
    def test_mitsugu_nakshatra(self):
        """1979年6月3日のナクシャトラはヴィシャーカー(15)"""
        assert _estimate_nakshatra(date(1979, 6, 3)) == 15
        assert NAKSHATRAS[15] == "ヴィシャーカー"

    def test_nao_nakshatra(self):
        """1999年5月7日のナクシャトラはクリッティカー(2)"""
        assert _estimate_nakshatra(date(1999, 5, 7)) == 2
        assert NAKSHATRAS[2] == "クリッティカー"


class TestTaraScore:
    def test_valid_score(self):
        """タラスコアが1-5の範囲内"""
        name, score, desc = _calc_tara_score(0, 5)
        assert 1 <= score <= 5
        assert len(name) > 0
        assert len(desc) > 0

    def test_all_tara_types(self):
        """9種類すべてのタラが出現すること"""
        tara_names = set()
        for i in range(9):
            name, _, _ = _calc_tara_score(0, i)
            tara_names.add(name)
        assert len(tara_names) == 9

    def test_sampat(self):
        """サンパト（繁栄）は最高スコア"""
        name, score, _ = _calc_tara_score(0, 1)
        assert name == "サンパト（繁栄）"
        assert score == 5


class TestVarnaCompat:
    def test_same_highest(self):
        score, desc = _get_varna_compat("ブラーフマナ", "ブラーフマナ")
        assert score == 5

    def test_symmetric(self):
        r1 = _get_varna_compat("ブラーフマナ", "クシャトリヤ")
        r2 = _get_varna_compat("クシャトリヤ", "ブラーフマナ")
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
        assert result["category"] == "jyotish"
        assert result["name"] == "インド占星術"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_content(self):
        result = calculate(MITSUGU, NAO)
        assert "person_a" in result["details"]
        assert "person_b" in result["details"]
        assert "nakshatra" in result["details"]["person_a"]
        assert "sidereal_sign" in result["details"]["person_a"]
        assert "varna" in result["details"]["person_a"]
        assert "tara" in result["details"]

    def test_no_birthday_returns_none(self):
        result = calculate({"name": "テスト"}, NAO)
        assert result is None

    def test_highlights_non_empty(self):
        result = calculate(MITSUGU, NAO)
        assert len(result["highlights"]) >= 5
