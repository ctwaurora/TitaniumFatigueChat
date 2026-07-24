"""
api_keys.py — 统一 API Key 管理

优先顺序：
1. st.secrets (Streamlit Cloud 部署)
2. 环境变量 DASHSCOPE_API_KEY / QWEN_API_KEY
3. qwen_key.txt (本地开发)

登录密码：
- 本地无 .streamlit/secrets.toml 时不启用密码
- Streamlit Cloud 配置 APP_PASSWORD 后启用密码
"""

import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent


def safe_get_secret(key: str, default: str = "") -> str:
    """
    安全读取 Streamlit Secrets。
    本地没有 .streamlit/secrets.toml 时不会报错。
    优先读取 st.secrets，其次读取环境变量，最后返回 default。
    """
    try:
        import streamlit as st
        # st.secrets 在本地无 secrets.toml 时会抛出异常
        # 访问其 ._secrets 或 .get() 都可能抛异常
        value = st.secrets.get(key, None)
        if value is not None:
            return str(value)
    except Exception:
        pass

    return str(os.getenv(key, default))


def get_qwen_api_key() -> Optional[str]:
    """获取 Qwen API Key，失败返回 None。"""
    # 1. st.secrets（Streamlit Cloud）
    try:
        import streamlit as st
        key = st.secrets.get("DASHSCOPE_API_KEY") or st.secrets.get("QWEN_API_KEY")
        if key:
            return str(key).strip()
    except Exception:
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


def get_app_password() -> str:
    """
    返回访问密码。
    本地未配置时返回空字符串，表示不启用登录密码。
    """
    return safe_get_secret("APP_PASSWORD", "")


def is_password_enabled() -> bool:
    """
    是否启用登录密码。
    本地没有配置 APP_PASSWORD 时不启用，直接进入系统。
    Streamlit Cloud 配置了 APP_PASSWORD 时才启用。
    """
    pw = get_app_password().strip()
    return bool(pw)
