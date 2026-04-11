"""Google Spreadsheet 自動保存モジュール"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ヘッダ定義
_INPUT_HEADERS = [
    "タイムスタンプ",
    "A:名前", "A:生年月日", "A:出生時刻", "A:出生地", "A:MBTI", "A:血液型",
    "B:名前", "B:生年月日", "B:出生時刻", "B:出生地", "B:MBTI", "B:血液型",
    "総合スコア", "ランク",
    "東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い",
]


def _build_row(person_a, person_b, results, categories, total_score_100, rank):
    """スプレッドシート1行分のデータを組み立てる"""
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # Person A
        person_a.get("name", ""),
        str(person_a.get("birthday", "")),
        person_a.get("birth_time", "") or "",
        person_a.get("birthplace", "") or "",
        person_a.get("mbti", "") or "",
        person_a.get("blood_type", "") or "",
        # Person B
        person_b.get("name", ""),
        str(person_b.get("birthday", "")),
        person_b.get("birth_time", "") or "",
        person_b.get("birthplace", "") or "",
        person_b.get("mbti", "") or "",
        person_b.get("blood_type", "") or "",
        # 総合
        total_score_100,
        rank,
    ]

    # カテゴリ別スコア（順序固定）
    cat_order = ["東洋占術", "西洋占星術", "数秘・タロット", "性格分析", "恋愛心理学", "その他占い"]
    cat_scores = {c["name"]: c["score"] for c in categories}
    for cat_name in cat_order:
        row.append(cat_scores.get(cat_name, ""))

    # 32手法個別: score_100, summary
    for r in results:
        row.append(r.get("score_100", ""))
        row.append(r.get("summary", ""))

    return row


def _build_headers(results):
    """ヘッダ行を組み立てる（結果の手法名を含む動的部分あり）"""
    headers = list(_INPUT_HEADERS)
    for r in results:
        name = r.get("name", "不明")
        headers.append(f"{name}:スコア")
        headers.append(f"{name}:サマリ")
    return headers


def save_to_sheet(person_a, person_b, results, categories, total_score_100, rank, config):
    """分析結果をGoogle Spreadsheetに1行追加する

    認証情報未設定やAPI障害時は警告ログのみで処理を中断しない。
    """
    creds = config.GOOGLE_SHEETS_CREDS
    spreadsheet_id = config.GOOGLE_SHEETS_SPREADSHEET_ID

    if not creds or not spreadsheet_id:
        logger.info("Google Sheets: 認証情報またはスプレッドシートIDが未設定のためスキップ")
        return

    try:
        import gspread

        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.sheet1

        # ヘッダ行がなければ挿入
        existing = worksheet.row_values(1)
        if not existing:
            headers = _build_headers(results)
            worksheet.append_row(headers, value_input_option="RAW")

        # データ行を追加
        row = _build_row(person_a, person_b, results, categories, total_score_100, rank)
        worksheet.append_row(row, value_input_option="USER_ENTERED")

        logger.info("Google Sheets: スプレッドシートに保存しました")

    except Exception as e:
        logger.warning("Google Sheets: 保存に失敗しました — %s", e)
