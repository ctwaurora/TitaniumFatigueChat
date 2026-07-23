"""
api_keys.py — 统一 API Key 管理

优先顺序：
1. st.secrets (Streamlit Cloud 部署)
2. 环境变量 DASHSCOPE_API_KEY / QWEN_API_KEY
3. qwen_key.txt (本地开发)
"""

import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


def get_qwen_api_key() -> Optional[str]:
    """获取 Qwen API Key，失败返回 None。"""
    # 1. st.secrets（Streamlit Cloud）
    try:
        import streamlit as st
        key = st.secrets.get("DASHSCOPE_API_KEY") or st.secrets.get("QWEN_API_KEY")
        if key:
            return str(key).strip()
    except (ImportError, AttributeError, KeyError):
        pass

    # 2. 环境变量
    key = os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_API_KEY")
    if key:
        return key.strip()

    # 3. qwen_key.txt（本地开发）
    key_path = BASE_DIR / "qwen_key.txt"
    if key_path.exists():
        key = key_path.read_text(encoding="utf-8").strip()
        if key:
            return key

    return None


def has_qwen_api_key() -> bool:
    """检查是否有可用的 API Key。"""
    return get_qwen_api_key() is not None


def get_app_password() -> Optional[str]:
    """获取访问密码，失败返回 None。"""
    try:
        import streamlit as st
        pw = st.secrets.get("APP_PASSWORD")
        if pw:
            return str(pw).strip()
    except (ImportError, AttributeError, KeyError):
        pass

    pw = os.environ.get("APP_PASSWORD")
    return pw.strip() if pw else None
