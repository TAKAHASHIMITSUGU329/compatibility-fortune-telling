# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

相性占い分析Webアプリ — 二人の姓名・生年月日・MBTI等を入力すると、34種類の占い・分析手法で相性を自動計算し、6カテゴリ別スコアとランク（SSS〜D）を表示する個人用Flaskアプリ。CSRF保護あり（Flask-WTF）。分析結果はGoogle Sheetsへ自動保存（設定時）。

## Commands

```bash
# アプリ起動（localhost:5001）
python3 app.py

# テスト全実行
python3 -m pytest tests/

# 単一テスト実行（例: 数秘術）
python3 -m pytest tests/test_numerology.py

# Selenium E2Eテスト（要: Flask起動中 + ChromeDriver）
python3 tests/test_selenium_celebrities.py           # ヘッドレス
python3 tests/test_selenium_celebrities.py --visible  # ブラウザ表示RPA風

# 依存インストール
pip install -r requirements.txt
```

## Architecture

**Flask app (`app.py`)** → 入力フォーム(`/`) と 分析結果表示(`/analyze` POST)の2画面構成。CSRF保護有効。バリデーションはフィールド単位（`field_errors` dict）。`_parse_person()` でフォーム値をperson dictに変換。

**計算エンジン (`calculators/`)** — 34関数（28モジュール）。各占い手法が独立モジュール。`CalculatorResult` TypedDictで型定義:
- 各モジュールは `calculate(person_a: dict, person_b: dict) -> dict` を公開
- 各モジュールに `CATEGORY = "カテゴリ名"` 定数（6カテゴリ: 東洋占術/西洋占星術/数秘・タロット/性格分析/恋愛心理学/その他占い）
- `calculators/__init__.py` の `ALL_CALCULATORS` は `(関数, モジュール)` のペアリスト
- `run_all()` → `{"results": [...], "errors": [...]}` を返す。カテゴリはモジュールのCATEGORY定数から自動付与
- `psychology.py` は6つのcalculate関数を持つ特殊モジュール（DISC, 愛着理論, ラブランゲージ, スタンバーグ, ゴットマン, 交流分析）
- calculator失敗時はlogging.warningに記録し、結果画面に警告バナー表示

**戻り値の必須キー:** `name`, `score`(1-5), `score_100`(0-100), `summary`, `details`(dict), `highlights`(list), `advice`, `icon`, `category`

**personデータ構造:**
```python
{"name": str,                       # 表示用（family_name + given_name から自動生成）
 "family_name": str|None,           # 姓
 "given_name": str|None,            # 名
 "family_name_kana": str|None,      # 姓カナ
 "given_name_kana": str|None,       # 名カナ
 "birthday": date,
 "birth_time": str|None,
 "birthplace": str|None,
 "mbti": str|None,
 "blood_type": str|None,
 "enneagram": str|None,             # パース対応済み・UI未実装
 "wing": str|None}                  # パース対応済み・UI未実装
```

**フォームフィールド名:** `{a|b}_family_name`, `{a|b}_given_name`, `{a|b}_family_name_kana`, `{a|b}_given_name_kana`, `{a|b}_birthday`, `{a|b}_birth_time`, `{a|b}_birthplace`, `{a|b}_mbti`, `{a|b}_blood_type`

**スコア正規化** — 34手法のscore_100平均(raw_avg)を正規化:
- raw_avg 68〜82 → 30〜95にリニア補間
- 68未満は30にフロア、82超は95にシーリング

**ランク判定（正規化後スコア基準）:** SSS:92+, SS:85+, S:76+, A:66+, B:55+, C:42+, D:<42

**カテゴリ集計** — app.pyの `CATEGORY_ORDER` で表示順を定義。各resultの `category` フィールドから自動集計。

**Google Sheets連携 (`sheets.py`)** — 分析結果を自動保存。gspreadサービスアカウント認証。未設定時はスキップ。

**データ (`data/`)** — 静的JSON（MBTI相性表、エニアグラム相性表、誕生花、タロット等）。

**テンプレート (`templates/`)** — Jinja2（base.html, input.html, result.html）。Tailwind CSS + Chart.js をCDN使用。結果ページに `id="rank-badge"` (`data-rank`) と `id="total-score"` (`data-score`) 属性あり（Seleniumテスト用）。

**設定 (`config.py`)** — 環境変数ベース: `FLASK_DEBUG`, `FLASK_HOST`, `FLASK_PORT`, `SECRET_KEY`（自動生成/.secret_key永続化）, `GOOGLE_SHEETS_CREDS`, `GOOGLE_SHEETS_SPREADSHEET_ID`

## Adding a New Calculator

1. `calculators/new_method.py` を作成。`CATEGORY = "カテゴリ名"` と `calculate(person_a, person_b) -> dict` を実装
2. `calculators/__init__.py` でモジュールimportし `ALL_CALCULATORS` に `(new_method.calculate, new_method)` を追加
3. `tests/test_new_method.py` を作成
4. app.pyの変更は不要（CATEGORYから自動集計される。新カテゴリの場合のみ `CATEGORY_ORDER` に追加）

## Selenium E2Eテスト

`tests/test_selenium_*.py` — Flask起動中に実行。6ファイル:
- `test_selenium_10patterns.py` — 10パターンの入力バリエーション（ヘッドレス）
- `test_selenium_visible.py` — 同上のブラウザ表示版（RPA風デモ）
- `test_selenium_celebrities.py` — 著名人カップル10組（結婚継続5組+離婚5組）のスコア比較
- `test_selenium_mitsugu_nao.py` — 貢さん×なおさん相性分析
- `test_selenium_mitsugu_hiroyo.py` — 貢さん×浩代さん相性分析
- `test_selenium_mitsugu_top5.py` — 貢さん×相性トップ5女性芸能人

Seleniumテストのpersonデータは `family_name`, `given_name`, `family_name_kana`, `given_name_kana` の4フィールドで姓名を指定。

## Markdown Reports

ルートディレクトリの `.md` ファイル群（サマリ.md、占い・分析手法一覧.md 等）は分析レポート文書。アプリコードとは独立。対象ペア: 貢さん (INFJ) × なおさん (ISFJ)。
