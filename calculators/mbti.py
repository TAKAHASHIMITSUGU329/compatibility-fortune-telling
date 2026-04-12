"""MBTI相性計算エンジン"""

import json
import os

CATEGORY = "性格分析"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# 認知機能スタック定義
COGNITIVE_FUNCTIONS = {
    "INTJ": ["Ni", "Te", "Fi", "Se"],
    "INTP": ["Ti", "Ne", "Si", "Fe"],
    "ENTJ": ["Te", "Ni", "Se", "Fi"],
    "ENTP": ["Ne", "Ti", "Fe", "Si"],
    "INFJ": ["Ni", "Fe", "Ti", "Se"],
    "INFP": ["Fi", "Ne", "Si", "Te"],
    "ENFJ": ["Fe", "Ni", "Se", "Ti"],
    "ENFP": ["Ne", "Fi", "Te", "Si"],
    "ISTJ": ["Si", "Te", "Fi", "Ne"],
    "ISFJ": ["Si", "Fe", "Ti", "Ne"],
    "ESTJ": ["Te", "Si", "Ne", "Fi"],
    "ESFJ": ["Fe", "Si", "Ne", "Ti"],
    "ISTP": ["Ti", "Se", "Ni", "Fe"],
    "ISFP": ["Fi", "Se", "Ni", "Te"],
    "ESTP": ["Se", "Ti", "Fe", "Ni"],
    "ESFP": ["Se", "Fi", "Te", "Ni"],
}

TYPE_DESCRIPTIONS = {
    "INTJ": "建築家 — 戦略的思考と独立心の持ち主",
    "INTP": "論理学者 — 知的好奇心と分析力の持ち主",
    "ENTJ": "指揮官 — リーダーシップと決断力の持ち主",
    "ENTP": "討論者 — 創造性と知的挑戦を愛する",
    "INFJ": "提唱者 — 洞察力と理想主義の持ち主",
    "INFP": "仲介者 — 共感力と創造性の持ち主",
    "ENFJ": "主人公 — カリスマ性と思いやりの持ち主",
    "ENFP": "広報運動家 — 情熱と社交性の持ち主",
    "ISTJ": "管理者 — 責任感と誠実さの持ち主",
    "ISFJ": "擁護者 — 献身と温かさの持ち主",
    "ESTJ": "幹部 — 組織力と実行力の持ち主",
    "ESFJ": "領事官 — 社交性と協調性の持ち主",
    "ISTP": "巨匠 — 冷静な分析力と実践力の持ち主",
    "ISFP": "冒険家 — 感受性と柔軟性の持ち主",
    "ESTP": "起業家 — 行動力とリスクテイクの持ち主",
    "ESFP": "エンターテイナー — 楽観性と社交性の持ち主",
}


def _load_compatibility_data() -> dict:
    """相性データをJSONから読み込む"""
    filepath = os.path.join(DATA_DIR, 'mbti_compatibility.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def _calculate_function_compatibility(type_a: str, type_b: str) -> dict:
    """認知機能から相性を分析"""
    funcs_a = COGNITIVE_FUNCTIONS.get(type_a, [])
    funcs_b = COGNITIVE_FUNCTIONS.get(type_b, [])

    if not funcs_a or not funcs_b:
        return {"shared": [], "complementary": [], "score_bonus": 0}

    # 共通する認知機能
    shared = list(set(funcs_a) & set(funcs_b))

    # 補完的な機能（相手の弱い機能が自分の強い機能）
    complementary = []
    if funcs_a[0] in funcs_b[2:]:
        complementary.append(f"{type_a}の主機能{funcs_a[0]}が{type_b}を補完")
    if funcs_b[0] in funcs_a[2:]:
        complementary.append(f"{type_b}の主機能{funcs_b[0]}が{type_a}を補完")

    return {
        "shared": shared,
        "complementary": complementary,
        "functions_a": funcs_a,
        "functions_b": funcs_b,
    }


def calculate(person_a: dict, person_b: dict) -> dict:
    """MBTI相性を計算する"""
    type_a = (person_a.get('mbti') or '').upper()
    type_b = (person_b.get('mbti') or '').upper()

    if not type_a or not type_b:
        return None

    data = _load_compatibility_data()

    # 相性テーブルから取得
    key = f"{type_a}_{type_b}"
    reverse_key = f"{type_b}_{type_a}"
    compat = data.get("compatibility", {}).get(key) or data.get("compatibility", {}).get(reverse_key)

    if compat:
        score = compat.get("score", 3)
        score_100 = compat.get("score_100", 60)
        summary_text = compat.get("summary", "")
    else:
        # フォールバック: 共通文字数から簡易計算
        common = sum(1 for a, b in zip(type_a, type_b) if a == b)
        score = {0: 3, 1: 3, 2: 4, 3: 4, 4: 3}.get(common, 3)
        score_100 = {1: 20, 2: 40, 3: 60, 4: 80, 5: 95}.get(score, 60)
        summary_text = f"{type_a}と{type_b}の組み合わせ"

    # 認知機能に基づくスコア別アドバイス
    if score >= 4:
        advice_text = f"{type_a}と{type_b}は認知機能の配列において高い親和性を持つ組み合わせです。主機能と補助機能が自然に補完し合うため、深い理解と共感が生まれやすいでしょう。互いの強みを活かした役割分担を意識するとさらに関係が発展します。"
    elif score >= 3:
        advice_text = f"{type_a}と{type_b}の認知機能には共通点と相違点がバランスよく存在します。異なる判断機能や知覚機能が新たな視点をもたらすため、相手の情報処理スタイルを尊重し、対話を通じて互いの世界観を広げていくことが関係深化の鍵です。"
    else:
        advice_text = f"{type_a}と{type_b}は認知機能の優先順位が大きく異なり、情報の捉え方や意思決定の方法に差が出やすい組み合わせです。しかしユング心理学では対極の機能こそ成長を促すとされるため、相手の視点を学ぶ姿勢が深い人間的成長につながります。"

    func_compat = _calculate_function_compatibility(type_a, type_b)

    name_a = person_a.get('name', 'Person A')
    name_b = person_b.get('name', 'Person B')

    highlights = [
        f"{name_a}: {type_a} — {TYPE_DESCRIPTIONS.get(type_a, '')}",
        f"{name_b}: {type_b} — {TYPE_DESCRIPTIONS.get(type_b, '')}",
    ]
    if func_compat["shared"]:
        highlights.append(f"共通認知機能: {', '.join(func_compat['shared'])}")
    if func_compat.get("complementary"):
        highlights.extend(func_compat["complementary"])

    return {
        "name": "MBTI相性",
        "category": "mbti",
        "icon": "psychology",
        "score": score,
        "score_100": score_100,
        "summary": f"{type_a} × {type_b} — {summary_text}",
        "details": {
            "person_a": {
                "type": type_a,
                "description": TYPE_DESCRIPTIONS.get(type_a, ""),
                "functions": COGNITIVE_FUNCTIONS.get(type_a, []),
            },
            "person_b": {
                "type": type_b,
                "description": TYPE_DESCRIPTIONS.get(type_b, ""),
                "functions": COGNITIVE_FUNCTIONS.get(type_b, []),
            },
            "compatibility": {
                "function_analysis": func_compat,
                "summary": summary_text,
            },
        },
        "highlights": highlights,
        "advice": advice_text,
    }
