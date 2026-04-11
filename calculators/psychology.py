"""心理学系分析エンジン（6手法）
- DiSC
- 交流分析（エゴグラム）
- アタッチメント理論
- 5つの愛の言語
- シュテルンベルグの愛の三角理論
- ゴットマンの四騎士
"""

CATEGORY = "恋愛心理学"

# ===== MBTI → 各フレームワーク推定マッピング =====

# DiSC推定
MBTI_TO_DISC = {
    "INFJ": ("iS", "影響力＋安定型"),
    "ISFJ": ("Si", "安定型＋影響力"),
    "INTJ": ("CD", "誠実型＋主導型"),
    "INTP": ("CS", "誠実型＋安定型"),
    "ENTJ": ("DC", "主導型＋誠実型"),
    "ENTP": ("Di", "主導型＋影響力"),
    "INFP": ("Si", "安定型＋影響力"),
    "ENFJ": ("iD", "影響力＋主導型"),
    "ENFP": ("iS", "影響力＋安定型"),
    "ISTJ": ("CS", "誠実型＋安定型"),
    "ESTJ": ("DC", "主導型＋誠実型"),
    "ESFJ": ("iS", "影響力＋安定型"),
    "ISTP": ("CD", "誠実型＋主導型"),
    "ISFP": ("Si", "安定型＋影響力"),
    "ESTP": ("Di", "主導型＋影響力"),
    "ESFP": ("iD", "影響力＋主導型"),
}

# DiSC相性（主要タイプの1文字目同士）
DISC_COMPAT = {
    ("D", "D"): (3, 65, "衝突しやすいが互いの力を認め合う"),
    ("D", "i"): (4, 80, "Dが方向を示しiが巻き込む。アクティブな関係"),
    ("D", "S"): (4, 78, "Dの推進力をSの安定感が支える"),
    ("D", "C"): (3, 70, "結果重視と正確さ重視。補完的だが摩擦も"),
    ("i", "i"): (4, 82, "明るく楽しい関係。現実面の補強が課題"),
    ("i", "S"): (5, 90, "iの社交性をSの温かさが受け止める最良の組み合わせ"),
    ("i", "C"): (3, 65, "テンポの違いが大きい。理解に時間が必要"),
    ("S", "S"): (4, 82, "穏やかで安定した関係。変化への対応が課題"),
    ("S", "C"): (4, 78, "慎重で思慮深い組み合わせ。信頼が深い"),
    ("C", "C"): (3, 68, "互いの基準が高く緊張が生まれやすい"),
}

# アタッチメントスタイル推定
MBTI_TO_ATTACHMENT = {
    "INFJ": ("安定型", "深い共感力と安定した自己認識を持つ"),
    "ISFJ": ("不安型寄りの安定型", "献身的だが「愛されているか」の確認を求める傾向"),
    "INTJ": ("回避型寄りの安定型", "自立心が高く、過度な親密さを避ける傾向"),
    "INTP": ("回避型", "感情より論理を優先し、距離を保ちたい傾向"),
    "ENTJ": ("安定型", "自信があり、関係に対して主導的に取り組む"),
    "ENTP": ("回避型寄りの安定型", "自由を重視し、束縛を嫌う"),
    "INFP": ("不安型", "理想が高く、関係への不安を感じやすい"),
    "ENFJ": ("安定型", "他者への関心が高く、安定した絆を築ける"),
    "ENFP": ("不安型寄りの安定型", "熱中しやすいが、飽きへの不安もある"),
    "ISTJ": ("安定型", "誠実で一貫した態度。信頼を重視する"),
    "ESTJ": ("安定型", "責任感が強く、関係にコミットする"),
    "ESFJ": ("不安型寄りの安定型", "承認欲求が高く、拒絶を恐れる傾向"),
    "ISTP": ("回避型", "独立心が強く、感情表現が苦手"),
    "ISFP": ("不安型", "繊細で傷つきやすく、受容を強く求める"),
    "ESTP": ("回避型寄りの安定型", "自由奔放だが関係を楽しめる"),
    "ESFP": ("安定型", "社交的で関係を楽しみ、温かさを与える"),
}

ATTACHMENT_COMPAT = {
    ("安定型", "安定型"): (5, 95, "最も安定した組み合わせ。互いの安全基地になれる"),
    ("安定型", "不安型"): (4, 85, "安定型が不安を鎮め、不安型を安定へ導ける"),
    ("安定型", "不安型寄りの安定型"): (5, 90, "安定型が安全基地となり、不安傾向を癒す"),
    ("安定型", "回避型"): (3, 72, "安定型の忍耐が試される。回避型の壁を溶かす力がある"),
    ("安定型", "回避型寄りの安定型"): (4, 80, "安定型がリードすることで良好な関係を築ける"),
    ("不安型", "不安型"): (2, 50, "互いの不安が増幅しやすい。意識的な努力が必要"),
    ("不安型", "不安型寄りの安定型"): (3, 65, "共感し合えるが不安の連鎖に注意"),
    ("不安型", "回避型"): (2, 45, "追う側と逃げる側の悪循環に陥りやすい"),
    ("不安型寄りの安定型", "不安型寄りの安定型"): (4, 78, "共感力は高いが互いの不安に巻き込まれることも"),
    ("不安型寄りの安定型", "回避型寄りの安定型"): (3, 72, "バランスは取れるが距離感の調整が必要"),
    ("回避型", "回避型"): (2, 50, "互いに距離を取り合い、関係が深まりにくい"),
    ("回避型寄りの安定型", "回避型寄りの安定型"): (3, 68, "独立した関係。親密さの構築に意識的な努力が必要"),
}

# 5つの愛の言語推定
MBTI_TO_LOVE_LANG = {
    "INFJ": (["肯定的な言葉", "クオリティタイム"], "言葉で深い想いを伝え、二人の時間を大切にする"),
    "ISFJ": (["奉仕の行為", "肯定的な言葉"], "行動で愛を示し、感謝の言葉に心が動く"),
    "INTJ": (["クオリティタイム", "肯定的な言葉"], "知的な対話の時間を重視する"),
    "INTP": (["クオリティタイム", "肯定的な言葉"], "静かに共にいる時間を愛する"),
    "ENTJ": (["奉仕の行為", "クオリティタイム"], "相手のために動き、質の高い時間を求める"),
    "ENTP": (["肯定的な言葉", "クオリティタイム"], "刺激的な会話と冒険の共有を好む"),
    "INFP": (["肯定的な言葉", "クオリティタイム"], "心からの言葉と、静かに寄り添う時間を求める"),
    "ENFJ": (["肯定的な言葉", "奉仕の行為"], "言葉で愛を伝え、相手のために尽くす"),
    "ENFP": (["肯定的な言葉", "スキンシップ"], "言葉と触れ合いで愛情を確かめる"),
    "ISTJ": (["奉仕の行為", "クオリティタイム"], "誠実な行動で愛を示す"),
    "ESTJ": (["奉仕の行為", "肯定的な言葉"], "行動で示し、成果を認めてほしい"),
    "ESFJ": (["肯定的な言葉", "奉仕の行為"], "感謝と承認の言葉を強く求める"),
    "ISTP": (["奉仕の行為", "スキンシップ"], "言葉より行動と身体的な親密さで愛を伝える"),
    "ISFP": (["スキンシップ", "クオリティタイム"], "触れ合いと静かな共有の時間を大切にする"),
    "ESTP": (["スキンシップ", "奉仕の行為"], "体験の共有と行動で愛を示す"),
    "ESFP": (["スキンシップ", "肯定的な言葉"], "楽しい体験と温かい言葉を愛する"),
}

# ゴットマン四騎士リスクマッピング（MBTIベース）
# (批判, 侮蔑, 防衛, 石壁) のリスク度 1-5
MBTI_TO_GOTTMAN_RISK = {
    "INFJ": (2, 1, 2, 4),
    "ISFJ": (1, 1, 2, 4),
    "INTJ": (3, 2, 4, 3),
    "INTP": (2, 2, 3, 4),
    "ENTJ": (4, 3, 4, 2),
    "ENTP": (3, 3, 3, 2),
    "INFP": (2, 1, 3, 4),
    "ENFJ": (2, 1, 2, 2),
    "ENFP": (2, 1, 2, 3),
    "ISTJ": (3, 2, 3, 3),
    "ESTJ": (4, 3, 3, 2),
    "ESFJ": (2, 1, 2, 3),
    "ISTP": (2, 2, 3, 5),
    "ISFP": (1, 1, 2, 5),
    "ESTP": (3, 3, 3, 2),
    "ESFP": (2, 2, 2, 2),
}


def _get_mbti(person: dict) -> str:
    mbti = person.get('mbti', '')
    if not mbti:
        return ''
    return mbti.upper().replace("-A", "").replace("-T", "").strip()


# ===== 各calculate関数 =====

def calculate_disc(person_a: dict, person_b: dict) -> dict:
    """DiSCコミュニケーション分析"""
    mbti_a = _get_mbti(person_a)
    mbti_b = _get_mbti(person_b)
    if not mbti_a or not mbti_b:
        return None

    disc_a, desc_a = MBTI_TO_DISC.get(mbti_a, ("S", "安定型"))
    disc_b, desc_b = MBTI_TO_DISC.get(mbti_b, ("S", "安定型"))

    key = (disc_a[0], disc_b[0])
    rev_key = (disc_b[0], disc_a[0])
    score, score_100, summary = DISC_COMPAT.get(key) or DISC_COMPAT.get(rev_key, (3, 65, ""))

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    return {
        "name": "DiSC",
        "category": "psychology",
        "icon": "forum",
        "score": score,
        "score_100": score_100,
        "summary": f"{disc_a}型 × {disc_b}型 — {summary}",
        "details": {"person_a": {"disc": disc_a, "desc": desc_a}, "person_b": {"disc": disc_b, "desc": desc_b}},
        "highlights": [
            f"{name_a}: {disc_a}型（{desc_a}）",
            f"{name_b}: {disc_b}型（{desc_b}）",
        ],
        "advice": summary,
    }


def calculate_attachment(person_a: dict, person_b: dict) -> dict:
    """アタッチメント理論（愛着スタイル）分析"""
    mbti_a = _get_mbti(person_a)
    mbti_b = _get_mbti(person_b)
    if not mbti_a or not mbti_b:
        return None

    style_a, desc_a = MBTI_TO_ATTACHMENT.get(mbti_a, ("安定型", ""))
    style_b, desc_b = MBTI_TO_ATTACHMENT.get(mbti_b, ("安定型", ""))

    # 相性検索（完全一致 → 部分一致フォールバック）
    key = (style_a, style_b)
    rev_key = (style_b, style_a)
    result = ATTACHMENT_COMPAT.get(key) or ATTACHMENT_COMPAT.get(rev_key)

    if not result:
        # ベーススタイル（最初の2-3文字）でフォールバック
        base_a = style_a.split("寄り")[0] if "寄り" in style_a else style_a
        base_b = style_b.split("寄り")[0] if "寄り" in style_b else style_b
        result = ATTACHMENT_COMPAT.get((base_a, base_b)) or ATTACHMENT_COMPAT.get((base_b, base_a), (3, 70, "互いの愛着スタイルを理解し合うことが大切です"))

    score, score_100, summary = result
    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    return {
        "name": "アタッチメント理論",
        "category": "psychology",
        "icon": "favorite",
        "score": score,
        "score_100": score_100,
        "summary": f"{style_a} × {style_b} — {summary}",
        "details": {"person_a": {"style": style_a, "desc": desc_a}, "person_b": {"style": style_b, "desc": desc_b}},
        "highlights": [
            f"{name_a}: {style_a} — {desc_a}",
            f"{name_b}: {style_b} — {desc_b}",
        ],
        "advice": summary,
    }


def calculate_love_languages(person_a: dict, person_b: dict) -> dict:
    """5つの愛の言語分析"""
    mbti_a = _get_mbti(person_a)
    mbti_b = _get_mbti(person_b)
    if not mbti_a or not mbti_b:
        return None

    langs_a, desc_a = MBTI_TO_LOVE_LANG.get(mbti_a, (["クオリティタイム"], ""))
    langs_b, desc_b = MBTI_TO_LOVE_LANG.get(mbti_b, (["クオリティタイム"], ""))

    # 共通の言語があれば高スコア
    common = set(langs_a) & set(langs_b)
    if len(common) >= 2:
        score, score_100 = 5, 92
        match_text = "愛の言語が非常に近い"
    elif len(common) == 1:
        score, score_100 = 4, 82
        match_text = f"「{list(common)[0]}」が共通の愛の言語"
    else:
        score, score_100 = 3, 70
        match_text = "愛の言語が異なるが、理解し合うことで補い合える"

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    return {
        "name": "5つの愛の言語",
        "category": "psychology",
        "icon": "volunteer_activism",
        "score": score,
        "score_100": score_100,
        "summary": match_text,
        "details": {"person_a": {"languages": langs_a}, "person_b": {"languages": langs_b}},
        "highlights": [
            f"{name_a}の愛の言語: {' > '.join(langs_a)} — {desc_a}",
            f"{name_b}の愛の言語: {' > '.join(langs_b)} — {desc_b}",
            f"共通: {', '.join(common) if common else 'なし（違いを理解し合うことが大切）'}",
        ],
        "advice": f"{name_a}は「{langs_b[0]}」を意識して伝えると{name_b}に響きます。{name_b}は「{langs_a[0]}」を心がけると{name_a}が喜びます。",
    }


def calculate_sternberg(person_a: dict, person_b: dict) -> dict:
    """シュテルンベルグの愛の三角理論"""
    mbti_a = _get_mbti(person_a)
    mbti_b = _get_mbti(person_b)
    if not mbti_a or not mbti_b:
        return None

    # F型は親密さが高い、T型は低め
    intimacy_a = 4 if 'F' in mbti_a else 3
    intimacy_b = 4 if 'F' in mbti_b else 3

    # E型は情熱が高い、I型は控えめだが深い
    passion_a = 3 if 'I' in mbti_a else 4
    passion_b = 3 if 'I' in mbti_b else 4

    # J型はコミットメントが高い
    commit_a = 4 if 'J' in mbti_a else 3
    commit_b = 4 if 'J' in mbti_b else 3

    # 二人の三角形の類似度（各要素の差の小ささ）
    diff = abs(intimacy_a - intimacy_b) + abs(passion_a - passion_b) + abs(commit_a - commit_b)
    if diff <= 1:
        score, score_100 = 5, 90
        summary = "愛の三角形が非常に近い。バランスの取れた関係"
    elif diff <= 3:
        score, score_100 = 4, 80
        summary = "愛の三角形が近い。互いの強みで補い合える"
    else:
        score, score_100 = 3, 68
        summary = "愛の三角形に差がある。すり合わせが成長の鍵"

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    return {
        "name": "シュテルンベルグの愛の三角理論",
        "category": "psychology",
        "icon": "change_history",
        "score": score,
        "score_100": score_100,
        "summary": summary,
        "details": {
            "person_a": {"intimacy": intimacy_a, "passion": passion_a, "commitment": commit_a},
            "person_b": {"intimacy": intimacy_b, "passion": passion_b, "commitment": commit_b},
        },
        "highlights": [
            f"{name_a}: 親密さ{intimacy_a} / 情熱{passion_a} / コミットメント{commit_a}",
            f"{name_b}: 親密さ{intimacy_b} / 情熱{passion_b} / コミットメント{commit_b}",
            "目標: 3要素すべてが揃った「完全な愛（Consummate Love）」",
        ],
        "advice": "親密さは日々の会話で、情熱は新しい体験で、コミットメントは誠実な行動で育てられます。",
    }


def calculate_gottman(person_a: dict, person_b: dict) -> dict:
    """ゴットマンの四騎士（関係破壊の4パターン）分析"""
    mbti_a = _get_mbti(person_a)
    mbti_b = _get_mbti(person_b)
    if not mbti_a or not mbti_b:
        return None

    risk_a = MBTI_TO_GOTTMAN_RISK.get(mbti_a, (3, 2, 3, 3))
    risk_b = MBTI_TO_GOTTMAN_RISK.get(mbti_b, (3, 2, 3, 3))

    labels = ["批判", "侮蔑", "防衛", "石壁"]
    antidotes = [
        "「あなたが悪い」ではなく「私はこう感じた」で伝える",
        "日常的に感謝と尊敬を言葉にする",
        "部分的にでも「自分にも非がある」と認める",
        "「20分休憩しよう」と伝えてから離れる。黙って離れない",
    ]

    # 二人の合算リスク（高いほど危険）
    combined_risk = [(risk_a[i] + risk_b[i]) / 2 for i in range(4)]
    avg_risk = sum(combined_risk) / 4

    # リスクが低いほどスコアが高い（逆転）
    if avg_risk <= 2.0:
        score, score_100 = 5, 90
    elif avg_risk <= 2.5:
        score, score_100 = 4, 82
    elif avg_risk <= 3.0:
        score, score_100 = 3, 72
    else:
        score, score_100 = 2, 58

    # 最大リスクの騎士を特定
    max_idx = combined_risk.index(max(combined_risk))

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    highlights = []
    for i, label in enumerate(labels):
        risk_level = "低" if combined_risk[i] <= 2 else "中" if combined_risk[i] <= 3 else "高"
        highlights.append(f"{label}: リスク{risk_level}（{combined_risk[i]:.1f}/5）")

    return {
        "name": "ゴットマンの四騎士",
        "category": "psychology",
        "icon": "shield",
        "score": score,
        "score_100": score_100,
        "summary": f"最大リスク: {labels[max_idx]}。解毒剤: {antidotes[max_idx]}",
        "details": {
            "risks": {labels[i]: combined_risk[i] for i in range(4)},
            "max_risk": labels[max_idx],
        },
        "highlights": highlights,
        "advice": f"最も注意すべきは「{labels[max_idx]}」。{antidotes[max_idx]}",
    }


def calculate_transactional(person_a: dict, person_b: dict) -> dict:
    """交流分析（エゴグラム）"""
    mbti_a = _get_mbti(person_a)
    mbti_b = _get_mbti(person_b)
    if not mbti_a or not mbti_b:
        return None

    # CP/NP/A/FC/AC推定（各1-5）
    def estimate_egogram(mbti):
        cp = 4 if 'J' in mbti and 'T' in mbti else 3 if 'J' in mbti else 2
        np = 4 if 'F' in mbti else 2
        a = 4 if 'T' in mbti else 3
        fc = 4 if 'E' in mbti and 'P' in mbti else 3 if 'P' in mbti else 2
        ac = 4 if 'I' in mbti and 'F' in mbti else 3 if 'I' in mbti else 2
        return {"CP": cp, "NP": np, "A": a, "FC": fc, "AC": ac}

    ego_a = estimate_egogram(mbti_a)
    ego_b = estimate_egogram(mbti_b)

    # A（成人）が両方高いと良い
    a_balance = (ego_a["A"] + ego_b["A"]) / 2
    # NP（養育的親）の合計が高いと温かい関係
    np_warmth = (ego_a["NP"] + ego_b["NP"]) / 2
    # FC（自由な子ども）の合計が高いと楽しい関係
    fc_fun = (ego_a["FC"] + ego_b["FC"]) / 2

    total = (a_balance * 0.4 + np_warmth * 0.3 + fc_fun * 0.3)

    if total >= 3.5:
        score, score_100 = 4, 82
    elif total >= 3.0:
        score, score_100 = 4, 78
    elif total >= 2.5:
        score, score_100 = 3, 68
    else:
        score, score_100 = 2, 55

    name_a = person_a.get('name', '男性')
    name_b = person_b.get('name', '女性')

    def format_ego(ego):
        return " / ".join(f"{k}:{v}" for k, v in ego.items())

    return {
        "name": "交流分析（エゴグラム）",
        "category": "psychology",
        "icon": "psychology",
        "score": score,
        "score_100": score_100,
        "summary": f"A（成人）バランス:{a_balance:.1f} / NP（温かさ）:{np_warmth:.1f} / FC（楽しさ）:{fc_fun:.1f}",
        "details": {"person_a": ego_a, "person_b": ego_b},
        "highlights": [
            f"{name_a}: {format_ego(ego_a)}",
            f"{name_b}: {format_ego(ego_b)}",
            "目指すべきはA↔A（対等な成人同士）のコミュニケーション",
        ],
        "advice": "NP↔ACパターン（世話焼き×従順）に偏らず、対等な対話を意識しましょう。",
    }
