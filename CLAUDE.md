# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

相性占い分析Webアプリ — 二人の生年月日・MBTI等を入力すると、32種類の占い・分析手法で相性を自動計算し、6カテゴリ別スコアとランク（SSS〜D）を表示する個人用Flaskアプリ。CSRF保護あり（Flask-WTF）。

## Commands

```bash
# アプリ起動（localhost:5001）
python3 app.py

# テスト全実行（320+テスト）
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

**Flask app (`app.py`)** → 入力フォーム(`/`) と 分析結果表示(`/analyze` POST)の2画面構成。CSRF保護有効。バリデーションはフィールド単位（`field_errors` dict）。

**計算エンジン (`calculators/`)** — 各占い手法が独立モジュール。`CalculatorResult` TypedDictで型定義:
- 各モジュールは `calculate(person_a: dict, person_b: dict) -> dict` を公開
- 各モジュールに `CATEGORY = "カテゴリ名"` 定数（6カテゴリ: 東洋占術/西洋占星術/数秘・タロット/性格分析/恋愛心理学/その他占い）
- `calculators/__init__.py` の `ALL_CALCULATORS` は `(関数, モジュール)` のペアリスト
- `run_all()` → `{"results": [...], "errors": [...]}` を返す。カテゴリはモジュールのCATEGORY定数から自動付与
- calculator失敗時はlogging.warningに記録し、結果画面に警告バナー表示

**戻り値の必須キー:** `name`, `score`(1-5), `score_100`(0-100), `summary`, `details`(dict), `highlights`(list), `advice`, `icon`, `category`

**personデータ構造:**
```python
{"name": str, "birthday": date, "birth_time": str|None, "birthplace": str|None,
 "mbti": str|None, "blood_type": str|None, "enneagram": str|None, "wing": str|None}
```

**カテゴリ集計** — app.pyでは `CATEGORY_ORDER` でカテゴリ表示順を定義。各resultの `category` フィールドから自動集計（ハードコードのマッピング不要）。

**ランク判定** — 32手法平均が68〜82に集中するため閾値を調整済み（SSS:82+, SS:79+, S:76+, A:74+, B:72+, C:68+, D:<68）。

**データ (`data/`)** — 静的JSON（MBTI相性表、エニアグラム相性表、誕生花、タロット等）。

**テンプレート (`templates/`)** — Jinja2。Tailwind CSS + Chart.js をCDN使用。結果ページにランク・スコアの `data-rank`/`data-score` 属性あり（Seleniumテスト用）。

**設定 (`config.py`)** — 全項目が環境変数ベース（`FLASK_DEBUG`, `FLASK_HOST`, `FLASK_PORT`, `SECRET_KEY`）。

## Adding a New Calculator

1. `calculators/new_method.py` を作成。`CATEGORY = "カテゴリ名"` と `calculate(person_a, person_b) -> dict` を実装
2. `calculators/__init__.py` でモジュールimportし `ALL_CALCULATORS` に `(new_method.calculate, new_method)` を追加
3. `tests/test_new_method.py` を作成
4. app.pyの変更は不要（CATEGORYから自動集計される。新カテゴリの場合のみ `CATEGORY_ORDER` に追加）

## Selenium E2Eテスト

`tests/test_selenium_*.py` — Flask起動中に実行。3ファイル:
- `test_selenium_10patterns.py` — 10パターンの入力バリエーション（ヘッドレス）
- `test_selenium_visible.py` — 同上のブラウザ表示版（RPA風デモ）
- `test_selenium_celebrities.py` — 著名人カップル10組（結婚継続5組+離婚5組）のスコア比較

## Markdown Reports

ルートディレクトリの `.md` ファイル群（サマリ.md、占い・分析手法一覧.md 等）は分析レポート文書。アプリコードとは独立。対象ペア: 貢さん (INFJ) × なおさん (ISFJ)。
