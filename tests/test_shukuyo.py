"""宿曜占術計算エンジンのテスト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from datetime import date
from calculators.shukuyo import (
    calculate,
    _get_shuku,
    _get_relation,
    _get_shuku_index,
    NIJUSHICHI_SHUKU,
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


class TestShukuDetermination:
    def test_mitsugu_shuku(self):
        """貢さん = 張宿"""
        shuku = _get_shuku(date(1979, 6, 3))
        assert shuku["name"] == "張宿"

    def test_nao_shuku(self):
        """なおさん = 柳宿"""
        shuku = _get_shuku(date(1999, 5, 7))
        assert shuku["name"] == "柳宿"

    def test_shuku_has_reading(self):
        """宿に読みが含まれること"""
        shuku = _get_shuku(date(1979, 6, 3))
        assert shuku["reading"] == "ちょうしゅく"

    def test_shuku_has_group(self):
        """宿にグループ情報が含まれること"""
        shuku = _get_shuku(date(1979, 6, 3))
        assert shuku["group"] == "南方七宿"


class TestShukuIndex:
    def test_27_shuku_count(self):
        """27宿が定義されていること"""
        assert len(NIJUSHICHI_SHUKU) == 27

    def test_index_wraps(self):
        """インデックスが27で巻き戻ること"""
        idx = _get_shuku_index(1, 28)
        assert 0 <= idx < 27


class TestRelation:
    def test_same_shuku_is_mei(self):
        """同じ宿 = 命の関係"""
        rel = _get_relation(0, 0)
        assert rel["name"] == "命"

    def test_gyo_relation(self):
        """距離9 = 業の関係"""
        rel = _get_relation(0, 9)
        assert rel["name"] == "業"

    def test_tai_relation(self):
        """距離18 = 胎の関係"""
        rel = _get_relation(0, 18)
        assert rel["name"] == "胎"

    def test_relation_has_score(self):
        """関係にスコアが含まれること"""
        rel = _get_relation(0, 0)
        assert "score" in rel
        assert 0 <= rel["score"] <= 100


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
        assert result["category"] == "shukuyo"
        assert result["name"] == "宿曜占術"

    def test_score_range(self):
        result = calculate(MITSUGU, NAO)
        assert 1 <= result["score"] <= 5
        assert 0 <= result["score_100"] <= 100

    def test_shuku_names_in_summary(self):
        """サマリーに宿名が含まれること"""
        result = calculate(MITSUGU, NAO)
        assert "張宿" in result["summary"]
        assert "柳宿" in result["summary"]

    def test_details_contain_shuku(self):
        """詳細に宿情報が含まれること"""
        result = calculate(MITSUGU, NAO)
        assert result["details"]["person_a"]["shuku"] == "張宿"
        assert result["details"]["person_b"]["shuku"] == "柳宿"
