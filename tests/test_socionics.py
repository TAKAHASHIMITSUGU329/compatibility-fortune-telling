"""ソシオニクス計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.socionics import (
    calculate,
    get_relation,
    MBTI_TO_SOCIONICS,
    SOCIONICS_INFO,
    RELATION_INFO,
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


class TestMbtiConversion:
    def test_infj_to_eii(self):
        """INFJ → EII"""
        assert MBTI_TO_SOCIONICS["INFJ"] == "EII"

    def test_isfj_to_esi(self):
        """ISFJ → ESI"""
        assert MBTI_TO_SOCIONICS["ISFJ"] == "ESI"

    def test_all_16_types(self):
        """全16タイプが変換テーブルに含まれること"""
        mbti_types = [
            "INTJ", "INTP", "ENTJ", "ENTP",
            "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ",
            "ISTP", "ISFP", "ESTP", "ESFP",
        ]
        for t in mbti_types:
            assert t in MBTI_TO_SOCIONICS

    def test_introvert_jp_flip(self):
        """内向型はJ/Pが反転する"""
        # INTJ(内向) → ILI (J→Pに反転、知覚型)
        assert MBTI_TO_SOCIONICS["INTJ"] == "ILI"
        # ENTJ(外向) → LIE (J→そのまま)
        assert MBTI_TO_SOCIONICS["ENTJ"] == "LIE"


class TestRelations:
    def test_eii_esi_quasi_identical(self):
        """EII × ESI = 準同一関係"""
        rel = get_relation("EII", "ESI")
        assert rel == "quasi_identical"

    def test_identity(self):
        """同じタイプ = 同一関係"""
        rel = get_relation("EII", "EII")
        assert rel == "identity"

    def test_dual(self):
        """EII × SLE = 双対関係"""
        rel = get_relation("EII", "SLE")
        assert rel == "dual"

    def test_all_relation_types_have_info(self):
        """全関係タイプに情報が定義されていること"""
        for key in ["dual", "activation", "mirror", "identity",
                     "quasi_identical", "super_ego", "conflict"]:
            assert key in RELATION_INFO
            assert "name" in RELATION_INFO[key]
            assert "score" in RELATION_INFO[key]


class TestSocionicsInfo:
    def test_all_types_have_info(self):
        """全ソシオニクスタイプに情報が定義されていること"""
        for soc_type in MBTI_TO_SOCIONICS.values():
            assert soc_type in SOCIONICS_INFO


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
        assert result["category"] == "socionics"
        assert result["name"] == "ソシオニクス"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_conversion_in_details(self):
        """詳細にソシオニクスタイプが含まれること"""
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_a"]["socionics"] == "EII"
        assert result["details"]["person_b"]["socionics"] == "ESI"

    def test_relation_in_details(self):
        """詳細に関係性が含まれること"""
        result = calculate(MITSUGU, NAO)
        assert result["details"]["relation"]["key"] == "quasi_identical"
        assert "準同一" in result["details"]["relation"]["name"]

    def test_missing_mbti_returns_none(self):
        """MBTIが未設定の場合はNoneを返す"""
        person_no_mbti = {**MITSUGU, "mbti": None}
        result = calculate(person_no_mbti, NAO)
        assert result is None

    def test_summary_contains_types(self):
        """サマリーにソシオニクスタイプ名が含まれること"""
        result = calculate(MITSUGU, NAO)
        assert "EII" in result["summary"]
        assert "ESI" in result["summary"]
