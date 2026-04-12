"""占い計算エンジンパッケージ"""

import logging
import sys
from datetime import date

if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    try:
        from typing_extensions import TypedDict
    except ImportError:
        from typing import TypedDict

logger = logging.getLogger(__name__)

REQUIRED_KEYS = {"name", "score", "score_100", "summary", "details", "highlights", "advice", "icon"}


class CalculatorResult(TypedDict):
    """各calculatorが返すべき結果の型定義"""
    name: str
    category: str
    icon: str
    score: int
    score_100: int
    summary: str
    details: dict
    highlights: list
    advice: str


def _ensure_date(person: dict) -> dict:
    """birthdayが文字列の場合はdateオブジェクトに変換する"""
    p = dict(person)
    bd = p.get('birthday')
    if isinstance(bd, str) and bd:
        try:
            parts = bd.split('-')
            p['birthday'] = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            pass
    return p


from calculators import (
    numerology, mbti, eto, kyusei, bloodtype, enneagram, tarot,
    birthday_flower, nijushisekki, biorhythm, astrology, shichusuimei,
    shukuyo, socionics, psychology, doubutsu, maya, love_style,
    game_theory, fusui, rokusei, kabbalah, bigfive, sanmeigaku,
    shibi, jyotish, love_map, seimei,
)

# (calculate関数, 所属モジュール) のペアリスト
# モジュールの CATEGORY 定数からカテゴリを自動取得する
ALL_CALCULATORS = [
    # Phase 1
    (numerology.calculate, numerology),
    (mbti.calculate, mbti),
    (eto.calculate, eto),
    (kyusei.calculate, kyusei),
    (bloodtype.calculate, bloodtype),
    (enneagram.calculate, enneagram),
    (tarot.calculate, tarot),
    (birthday_flower.calculate, birthday_flower),
    (nijushisekki.calculate, nijushisekki),
    (biorhythm.calculate, biorhythm),
    # Phase 2
    (astrology.calculate, astrology),
    (shichusuimei.calculate, shichusuimei),
    (shukuyo.calculate, shukuyo),
    (socionics.calculate, socionics),
    # Phase 3
    (psychology.calculate_disc, psychology),
    (psychology.calculate_attachment, psychology),
    (psychology.calculate_love_languages, psychology),
    (psychology.calculate_sternberg, psychology),
    (psychology.calculate_gottman, psychology),
    (psychology.calculate_transactional, psychology),
    (doubutsu.calculate, doubutsu),
    (maya.calculate, maya),
    (love_style.calculate, love_style),
    (game_theory.calculate, game_theory),
    (fusui.calculate, fusui),
    # Phase 4
    (rokusei.calculate, rokusei),
    (kabbalah.calculate, kabbalah),
    (bigfive.calculate, bigfive),
    (sanmeigaku.calculate, sanmeigaku),
    (shibi.calculate, shibi),
    (jyotish.calculate, jyotish),
    (love_map.calculate, love_map),
    # Phase 5
    (seimei.calculate, seimei),
]


def run_all(person_a: dict, person_b: dict) -> dict:
    """全計算エンジンを実行し、結果と失敗情報を返す"""
    # 文字列のbirthdayをdateオブジェクトに変換
    person_a = _ensure_date(person_a)
    person_b = _ensure_date(person_b)

    results = []
    errors = []
    for calc_fn, module in ALL_CALCULATORS:
        try:
            result = calc_fn(person_a, person_b)
            if result is not None:
                # モジュールの CATEGORY 定数からカテゴリを付与
                result["category"] = getattr(module, "CATEGORY", "その他占い")
                # 必須キーの欠落チェック
                missing = REQUIRED_KEYS - result.keys()
                if missing:
                    logger.warning("Calculator %s: missing keys %s", module.__name__, missing)
                results.append(result)
        except Exception as e:
            module_name = module.__name__.replace("calculators.", "")
            logger.warning("Calculator error (%s): %s", module.__name__, e)
            errors.append(module_name)
    return {"results": results, "errors": errors}
