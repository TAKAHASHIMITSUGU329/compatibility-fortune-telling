import json
import os
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent
_SECRET_KEY_FILE = _BASE_DIR / '.secret_key'
_SHEETS_CREDS_FILE = _BASE_DIR / '.sheets_creds.json'


def _load_or_generate_secret_key() -> str:
    """SECRET_KEYをファイルから読み込み、なければ生成して保存する"""
    env_key = os.environ.get('SECRET_KEY')
    if env_key:
        return env_key
    if _SECRET_KEY_FILE.exists():
        return _SECRET_KEY_FILE.read_text().strip()
    key = os.urandom(32).hex()
    _SECRET_KEY_FILE.write_text(key)
    return key


def _load_sheets_credentials():
    """Google Sheets用Service Account認証情報を読み込む"""
    env_json = os.environ.get('GOOGLE_SHEETS_CREDS_JSON')
    if env_json:
        return json.loads(env_json)
    if _SHEETS_CREDS_FILE.exists():
        return json.loads(_SHEETS_CREDS_FILE.read_text())
    return None


class Config:
    SECRET_KEY = _load_or_generate_secret_key()
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', '5001'))
    GOOGLE_SHEETS_CREDS = _load_sheets_credentials()
    GOOGLE_SHEETS_SPREADSHEET_ID = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID')
