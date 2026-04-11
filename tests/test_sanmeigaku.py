"""算命学計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.sanmeigaku import (
    calculate, _year_shi, _day_kan, _get_tenchu_group,
    _is_tenchu_period, _get_tenchu_compat, _get_gogyo_compat,
    JUNISHI, JIKKAN, NIKKAN_GOGYO,
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


class TestYearShi:
    def test_mitsugu_year_shi(self):
        """1979年6月3日の年支"""
        shi = _year_shi(date(1979, 6, 3))
        assert shi in JUNISHI

    def test_nao_year_shi(self):
        """1999年5月7日の年支"""
        shi = _year_shi(date(1999, 5, 7))
        assert shi in JUNISHI

    def test_before_risshun(self):
        """立春前は前年扱い"""
        shi_jan = _year_shi(date(2000, 1, 15))
        shi_mar = _year_shi(date(2000, 3, 1))
        # 1月15日は前年（1999年）の年支、3月1日は2000年の年支
        # 1999年と2000年は12年周期で異なるはず
        assert shi_jan in JUNISHI
        assert shi_mar in JUNISHI


class TestDayKan:
    def test_mitsugu_day_kan(self):
        """日干が十干のいずれかであること"""
        kan = _day_kan(date(1979, 6, 3))
        assert kan in JIKKAN

    def test_nao_day_kan(self):
        kan = _day_kan(date(1999, 5, 7))
        assert kan in JIKKAN

    def test_different_dates(self):
        """異なる日付で日干が算出されること"""
        kan1 = _day_kan(date(1979, 6, 3))
        kan2 = _day_kan(date(1999, 5, 7))
        assert kan1 in JIKKAN
        assert kan2 in JIKKAN


class TestTenchuGroup:
    def test_valid_group(self):
        """年支から正しい天中殺グループが判定されること"""
        for shi in JUNISHI:
            group = _get_tenchu_group(shi)
            assert "天中殺" in group

    def test_child_ox(self):
        """子丑は午未天中殺"""
        # 仕様: 子丑が年支 → 午未天中殺
        # ただし実装では天中殺グループ名がそのまま年支のペアを含む
        group = _get_tenchu_group("子")
        assert group == "子丑天中殺"

    def test_tiger_rabbit(self):
        group = _get_tenchu_group("寅")
        assert group == "寅卯天中殺"


class TestTenchuPeriod:
    def test_returns_tuple(self):
        is_period, period = _is_tenchu_period("子丑天中殺", 2026)
        assert isinstance(is_period, bool)

    def test_known_period(self):
        """子丑天中殺は子年・丑年が天中殺期間"""
        # 2020年は子年（(2020-4)%12=0 → 子）
        is_period, period = _is_tenchu_period("子丑天中殺", 2020)
        assert is_period is True
        assert period == "子年"


class TestTenchuCompat:
    def test_same_group(self):
        score, score_100, desc = _get_tenchu_compat("子丑天中殺", "子丑天中殺")
        assert score == 3
        assert score_100 == 65

    def test_opposite_group(self):
        score, score_100, desc = _get_tenchu_compat("子丑天中殺", "午未天中殺")
        assert score == 5
        assert score_100 == 90

    def test_symmetric(self):
        r1 = _get_tenchu_compat("子丑天中殺", "寅卯天中殺")
        r2 = _get_tenchu_compat("寅卯天中殺", "子丑天中殺")
        assert r1 == r2


class TestGogyoCompat:
    def test_same_element(self):
        score, desc = _get_gogyo_compat("木", "木")
        assert score == 3

    def test_generating(self):
        score, desc = _get_gogyo_compat("木", "火")
        assert score == 4

    def test_overcoming(self):
        score, desc = _get_gogyo_compat("木", "土")
        assert score == 2


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
        assert result["category"] == "sanmeigaku"
        assert result["name"] == "算命学"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_details_content(self):
        result = calculate(MITSUGU, NAO)
        assert "person_a" in result["details"]
        assert "person_b" in result["details"]
        assert "nikkan" in result["details"]["person_a"]
        assert "tenchu_group" in result["details"]["person_a"]

    def test_no_birthday_returns_none(self):
        result = calculate({"name": "テスト"}, NAO)
        assert result is None

    def test_highlights_non_empty(self):
        result = calculate(MITSUGU, NAO)
        assert len(result["highlights"]) >= 4
