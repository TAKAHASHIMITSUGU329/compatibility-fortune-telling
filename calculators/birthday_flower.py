"""誕生花・花言葉計算エンジン"""

import json
import os
from datetime import date

CATEGORY = "その他占い"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def _load_flower_data() -> dict:
    filepath = os.path.join(DATA_DIR, 'birthday_flowers.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def _get_flower(data: dict, birthday: date) -> dict:
    """月日から誕生花を取得。該当日がなければ月の代表花を返す"""
    flowers = data.get("flowers", {})
    # まず月日で検索
    key = f"{birthday.month}_{birthday.day}"
    if key in flowers:
        return flowers[key]
    # 月の代表花
    month_key = f"{birthday.month}_1"
    if month_key in flowers:
        return flowers[month_key]
    # デフォルト
    return {"name": "不明", "meaning": "", "description": ""}


def calculate(person_a: dict, person_b: dict) -> dict:
    """誕生花の相性を計算する"""
    bd_a = person_a['birthday']
    bd_b = person_b['birthday']

    data = _load_flower_data()

    flower_a = _get_flower(data, bd_a)
    flower_b = _get_flower(data, bd_b)

    # 花言葉の相性（同じ季節なら高め、意味の親和性で判定）
    season_a = _get_season(bd_a.month)
    season_b = _get_season(bd_b.month)

    if season_a == season_b:
        score = 4
        compat_text = "同じ季節に咲く花同士。自然なリズムが合う関係です。"
    elif abs(bd_a.month - bd_b.month) <= 2 or abs(bd_a.month - bd_b.month) >= 10:
        score = 4
        compat_text = "近い季節の花同士。移ろいゆく季節を共に楽しめる関係です。"
    elif abs(bd_a.month - bd_b.month) == 6:
        score = 3
        compat_text = "対照的な季節の花同士。お互いにないものを持ち合わせています。"
    else:
        score = 3
        compat_text = "異なる季節の花同士。多彩な彩りが生活を豊かにします。"

    score_100 = {1: 20, 2: 40, 3: 60, 4: 80, 5: 95}.get(score, 60)

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    return {
        "name": "誕生花・花言葉",
        "category": "birthday_flower",
        "icon": "local_florist",
        "score": score,
        "score_100": score_100,
        "summary": f"{flower_a['name']} × {flower_b['name']}",
        "details": {
            "person_a": {
                "flower": flower_a["name"],
                "meaning": flower_a.get("meaning", ""),
                "description": flower_a.get("description", ""),
            },
            "person_b": {
                "flower": flower_b["name"],
                "meaning": flower_b.get("meaning", ""),
                "description": flower_b.get("description", ""),
            },
            "compatibility": {
                "description": compat_text,
            },
        },
        "highlights": [
            f"{name_a}の誕生花: {flower_a['name']}（花言葉: {flower_a.get('meaning', '')}）",
            f"{name_b}の誕生花: {flower_b['name']}（花言葉: {flower_b.get('meaning', '')}）",
            compat_text,
        ],
        "advice": f"お二人の花を一緒に飾ると、素敵なブーケになるでしょう。{compat_text}",
    }


def _get_season(month: int) -> str:
    """月から季節を判定"""
    if month in (3, 4, 5):
        return "春"
    elif month in (6, 7, 8):
        return "夏"
    elif month in (9, 10, 11):
        return "秋"
    else:
        return "冬"
