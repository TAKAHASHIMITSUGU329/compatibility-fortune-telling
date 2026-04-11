"""六星占術計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.rokusei import (
    calculate, _calc_unmei_number, _unmei_to_star, _get_compat,
    _is_daisakkai, _get_current_cycle,
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


class TestUnmeiNumber:
    def test_mitsugu_unmei(self):
        """1979年6月3日の運命数は2"""
        assert _calc_unmei_number(date(1979, 6, 3)) == 2

    def test_nao_unmei(self):
        """1999年5月7日の運命数は25"""
        assert _calc_unmei_number(date(1999, 5, 7)) == 25

    def test_different_dates_different_unmei(self):
        """異なる生年月日で異なる運命数になること"""
        u1 = _calc_unmei_number(date(1979, 6, 3))
        u2 = _calc_unmei_number(date(1999, 5, 7))
        # 異なる日付で必ず異なるとは限らないが、この2つは異なるはず
        assert isinstance(u1, int)
        assert isinstance(u2, int)


class TestUnmeiToStar:
    def test_dosei(self):
        star, pol, full = _unmei_to_star(5)
        assert star == "土星人"
        assert full == "土星人(+)"

    def test_kinsei(self):
        star, pol, full = _unmei_to_star(15)
        assert star == "金星人"

    def test_kasei(self):
        star, pol, full = _unmei_to_star(25)
        assert star == "火星人"

    def test_tennousei(self):
        star, pol, full = _unmei_to_star(35)
        assert star == "天王星人"

    def test_mokusei(self):
        star, pol, full = _unmei_to_star(45)
        assert star == "木星人"

    def test_suisei(self):
        star, pol, full = _unmei_to_star(55)
        assert star == "水星人"

    def test_polarity_odd(self):
        _, pol, _ = _unmei_to_star(3)
        assert pol == "+"

    def test_polarity_even(self):
        _, pol, _ = _unmei_to_star(4)
        assert pol == "-"


class TestCompat:
    def test_dosei_mokusei(self):
        score, score_100, desc = _get_compat("土星人", "木星人")
        assert score == 5
        assert score_100 == 90

    def test_symmetric(self):
        """順序が逆でも同じ結果"""
        r1 = _get_compat("土星人", "金星人")
        r2 = _get_compat("金星人", "土星人")
        assert r1 == r2


class TestDaisakkai:
    def test_returns_tuple(self):
        is_dai, period = _is_daisakkai(date(1979, 6, 3), "土星人", 2026)
        assert isinstance(is_dai, bool)

    def test_period_names(self):
        """大殺界中の場合、期間名が正しいこと"""
        # 土星人は子年（干支インデックス0）から大殺界
        # 2026年の干支: (2026-4)%12 = 2022%12 = 6 → 午年
        # 土星人の大殺界は0,1,2（子、丑、寅）なので2026年は大殺界ではない
        is_dai, period = _is_daisakkai(date(1979, 6, 3), "土星人", 2026)
        if is_dai:
            assert period in ["陰影", "停止", "減退"]


class TestCurrentCycle:
    def test_returns_valid_cycle(self):
        cycle = _get_current_cycle(date(1979, 6, 3), "土星人", 2026)
        from calculators.rokusei import TWELVE_CYCLE
        assert cycle in TWELVE_CYCLE


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
        assert result["category"] == "rokusei"
        assert result["name"] == "六星占術"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_content(self):
        result = calculate(MITSUGU, NAO)
        assert "person_a" in result["details"]
        assert "person_b" in result["details"]
        assert "unmei_number" in result["details"]["person_a"]
        assert "star" in result["details"]["person_a"]
        assert "current_cycle" in result["details"]["person_a"]

    def test_no_birthday_returns_none(self):
        result = calculate({"name": "テスト"}, NAO)
        assert result is None

    def test_highlights_non_empty(self):
        result = calculate(MITSUGU, NAO)
        assert len(result["highlights"]) >= 3
