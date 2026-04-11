"""タロット誕生日カード計算エンジン"""

import json
import os
from datetime import date

CATEGORY = "数秘・タロット"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def _life_path_number(birthday: date) -> int:
    """ライフパス数を算出（タロット用）"""
    total = sum(int(d) for d in str(birthday.year) + str(birthday.month).zfill(2) + str(birthday.day).zfill(2))
    while total > 22:
        total = sum(int(d) for d in str(total))
    return total


def _load_tarot_data() -> dict:
    filepath = os.path.join(DATA_DIR, 'tarot_cards.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate(person_a: dict, person_b: dict) -> dict:
    """タロット誕生日カードの相性を計算する"""
    bd_a = person_a['birthday']
    bd_b = person_b['birthday']

    num_a = _life_path_number(bd_a)
    num_b = _life_path_number(bd_b)

    data = _load_tarot_data()
    cards = data.get("cards", {})

    card_a = cards.get(str(num_a), {"name": "不明", "meaning": "", "keywords": []})
    card_b = cards.get(str(num_b), {"name": "不明", "meaning": "", "keywords": []})

    # 補完ペアの定義（内面×外面、直感×行動など相互補完するカード）
    complementary_pairs = {
        frozenset({8, 4}),   # 力(内なる強さ) × 皇帝(外的権威) = 補完的パワー
        frozenset({2, 11}),  # 女教皇(直感) × 正義(論理) = 知恵の融合
        frozenset({3, 9}),   # 女帝(豊穣) × 隠者(内省) = 創造と深化
        frozenset({1, 7}),   # 魔術師(意志) × 戦車(行動) = 実現力
        frozenset({6, 17}),  # 恋人(選択) × 星(希望) = 理想の関係
        frozenset({5, 14}),  # 教皇(教え) × 節制(調和) = バランスの知恵
        frozenset({10, 21}), # 運命の輪(変化) × 世界(完成) = 運命の完成
        frozenset({13, 20}), # 死神(変容) × 審判(再生) = 究極の再生
        frozenset({16, 19}), # 塔(破壊) × 太陽(再生) = 破壊と創造
        frozenset({12, 18}), # 吊るされた男(犠牲) × 月(無意識) = 深い精神的絆
        frozenset({15, 0}),  # 悪魔(束縛) × 愚者(自由) = 自由への解放
    }

    # 相性判定：同じカードなら最高、補完的なら良好
    pair = frozenset({num_a, num_b})
    if num_a == num_b:
        score = 5
        compat_text = "同じ誕生日カードを持つ、魂の共鳴が強い組み合わせです。"
    elif pair in complementary_pairs:
        score = 4
        compat_text = "補完し合うカード同士。互いの力が融合し、二人で一つの完全な物語を紡ぎます。"
    elif (num_a + num_b) == 22 or (num_a + num_b) == 21:
        score = 5
        compat_text = "補完し合うカード同士。二人で一つの完全な物語を紡ぎます。"
    elif abs(num_a - num_b) <= 2:
        score = 4
        compat_text = "近いエネルギーを持つカード同士。自然な調和が生まれます。"
    elif abs(num_a - num_b) <= 5:
        score = 4
        compat_text = "近い領域のカード同士。共鳴し合うエネルギーが強い組み合わせです。"
    elif num_a % 2 == num_b % 2:
        score = 3
        compat_text = "同じ極性のカード。似た波長で共感しやすい組み合わせです。"
    else:
        score = 3
        compat_text = "異なるエネルギーの交差。お互いに新しい視点をもたらします。"

    score_100 = {1: 20, 2: 40, 3: 60, 4: 82, 5: 95}.get(score, 60)

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    return {
        "name": "タロット誕生日カード",
        "category": "tarot",
        "icon": "style",
        "score": score,
        "score_100": score_100,
        "summary": f"{card_a['name']} × {card_b['name']}",
        "details": {
            "person_a": {
                "number": num_a,
                "card_name": card_a["name"],
                "meaning": card_a.get("meaning", ""),
                "keywords": card_a.get("keywords", []),
            },
            "person_b": {
                "number": num_b,
                "card_name": card_b["name"],
                "meaning": card_b.get("meaning", ""),
                "keywords": card_b.get("keywords", []),
            },
            "compatibility": {
                "description": compat_text,
            },
        },
        "highlights": [
            f"{name_a}のカード: {num_a}番 {card_a['name']}",
            f"{name_b}のカード: {num_b}番 {card_b['name']}",
            compat_text,
        ],
        "advice": f"{card_a['name']}と{card_b['name']}の組み合わせは、{compat_text}",
    }
