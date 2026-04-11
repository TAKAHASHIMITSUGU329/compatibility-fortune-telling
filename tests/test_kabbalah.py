"""カバラ数秘術計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.kabbalah import (
    calculate, name_to_romaji, _calc_expression, _calc_soul_urge,
    _calc_personality, _reduce_to_single, _LETTER_VALUES,
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


class TestNameToRomaji:
    def test_ascii_name(self):
        """既にローマ字の名前はそのまま"""
        assert name_to_romaji("Mitsugu") == "MITSUGU"

    def test_hiragana_nao(self):
        """ひらがなのローマ字変換"""
        result = name_to_romaji("なお")
        assert result == "NAO"

    def test_katakana(self):
        """カタカナのローマ字変換"""
        result = name_to_romaji("ナオ")
        assert result == "NAO"

    def test_kanji_known_name(self):
        """辞書に登録された漢字名はローマ字変換できる"""
        result = name_to_romaji("貢")
        assert result == "MITSUGU"

    def test_kanji_unknown_returns_none(self):
        """辞書にない漢字名は変換できない"""
        result = name_to_romaji("太郎")
        assert result is None

    def test_mixed_hiragana(self):
        """ひらがなの基本変換"""
        result = name_to_romaji("さくら")
        assert result == "SAKURA"

    def test_youon(self):
        """拗音の変換"""
        result = name_to_romaji("しょう")
        assert result == "SHOU"


class TestLetterValues:
    def test_a_equals_1(self):
        assert _LETTER_VALUES['A'] == 1

    def test_i_equals_9(self):
        assert _LETTER_VALUES['I'] == 9

    def test_j_equals_1(self):
        assert _LETTER_VALUES['J'] == 1

    def test_z_equals_8(self):
        assert _LETTER_VALUES['Z'] == 8


class TestReduceToSingle:
    def test_single_digit(self):
        assert _reduce_to_single(5) == 5

    def test_two_digits(self):
        assert _reduce_to_single(15) == 6  # 1+5=6

    def test_master_number_11(self):
        assert _reduce_to_single(11) == 11

    def test_master_number_22(self):
        assert _reduce_to_single(22) == 22

    def test_master_number_33(self):
        assert _reduce_to_single(33) == 33

    def test_large_number(self):
        assert _reduce_to_single(99) == 9  # 9+9=18->1+8=9


class TestCalcExpression:
    def test_nao(self):
        """NAO: N=5, A=1, O=6 -> 12 -> 3"""
        result = _calc_expression("NAO")
        assert result == 3

    def test_mitsugu(self):
        """MITSUGU: M=4,I=9,T=2,S=1,U=3,G=7,U=3 -> 29 -> 11（マスターナンバー）"""
        assert _calc_expression("MITSUGU") == 11


class TestCalcSoulUrge:
    def test_nao(self):
        """NAO: 母音 A=1, O=6 -> 7"""
        result = _calc_soul_urge("NAO")
        assert result == 7

    def test_only_vowels_counted(self):
        """子音のみの名前はソウル数0→縮約後も0になるが通常あり得ない"""
        result = _calc_soul_urge("BCD")
        assert result == 0


class TestCalcPersonality:
    def test_nao(self):
        """NAO: 子音 N=5 -> 5"""
        result = _calc_personality("NAO")
        assert result == 5


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
        assert result["category"] == "kabbalah"
        assert result["name"] == "カバラ数秘術"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_kanji_name_uses_romaji_dict(self):
        """辞書登録済みの漢字名はローマ字辞書から変換"""
        result = calculate(MITSUGU, NAO)
        assert result is not None
        # 貢は漢字辞書に登録されているので直接変換
        assert result["details"]["person_a"]["fallback"] is False
        assert result["details"]["person_a"]["romaji"] == "MITSUGU"
        # なおはひらがななので直接変換
        assert result["details"]["person_b"]["fallback"] is False

    def test_romaji_names(self):
        """ローマ字名はそのまま使用"""
        person_a = dict(MITSUGU, name="Mitsugu")
        person_b = dict(NAO, name="Nao")
        result = calculate(person_a, person_b)
        assert result is not None
        assert result["details"]["person_a"]["fallback"] is False
        assert result["details"]["person_b"]["fallback"] is False

    def test_no_mbti_no_romaji_returns_none(self):
        """名前変換もMBTIもない場合はNone"""
        result = calculate({"name": "太郎"}, {"name": "花子"})
        assert result is None

    def test_highlights_non_empty(self):
        result = calculate(MITSUGU, NAO)
        assert len(result["highlights"]) >= 4
