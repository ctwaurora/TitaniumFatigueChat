# TitaniumFatigueChat — Streamlit Community Cloud 部署说明

## 一、前期准备

### 1.1 创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击 **New repository**
3. 仓库名称：`TitaniumFatigueChat`（或其他名称）
4. 设置为 **Private**（私有仓库，保护文献数据）
5. 不要勾选 "Add a README"（已存在）
6. 点击 **Create repository**

### 1.2 推送代码

```bash
# 在项目目录下执行
git init
git add .
git commit -m "Initial commit: TitaniumFatigueChat deployment"
git branch -M main
git remote add origin https://github.com/你的用户名/TitaniumFatigueChat.git
git push -u origin main
```

### 1.3 确认不上传的文件

以下文件已被 `.gitignore` 排除，不会上传：

| 文件 | 原因 |
|------|------|
| `qwen_key.txt` | API Key 明文 |
| `.env` | 环境变量 |
| `.streamlit/secrets.toml` | 部署后手动配置 |
| `__pycache__/` | Python 缓存 |
| `logs/` | 本地日志 |
| `papers/private/` | 未授权文献 |
| `papers/paid_papers/` | 付费 PDF |
| `legacy_training/` | 训练脚本，非部署必需 |
| `legacy_scripts/` | 历史脚本，非部署必需 |
| `competition_package/` | 比赛包，非部署必需 |

---

## 二、部署到 Streamlit Community Cloud

### 2.1 登录 Streamlit Cloud

1. 访问 https://streamlit.io/cloud
2. 点击 **Sign in with GitHub**
3. 授权后进入 Streamlit Cloud Dashboard

### 2.2 创建新 App

1. 点击 **New app**
2. Repository：选择 `你的用户名/TitaniumFatigueChat`
3. Branch：`main`
4. Main file path：`streamlit_app.py`
5. 点击 **Advanced settings...**

### 2.3 配置 Secrets

在 Advanced settings 的 Secrets 区域，粘贴以下内容：

```toml
# .streamlit/secrets.toml
APP_PASSWORD = "给老师的访问密码，例如 fatigue2024"
DASHSCOPE_API_KEY = "你的阿里云 DashScope API Key，例如 sk-xxxxx"
```

如果暂时没有 API Key，至少配置 `APP_PASSWORD`：

```toml
APP_PASSWORD = "你的密码"
```

### 2.4 部署

1. 点击 **Deploy**
2. 等待 3-5 分钟，Streamlit Cloud 会自动安装依赖并启动
3. 部署完成后会生成一个公网链接，如：
   `https://titaniumfatiguechat-你的用户名.streamlit.app`

---

## 三、老师访问方式

### 3.1 登录流程

1. 打开部署后的公网链接
2. 页面显示 **TitaniumFatigueChat** 标题和密码输入框
3. 输入你在 Secrets 中配置的 `APP_PASSWORD`
4. 点击 **登录**
5. 进入系统主界面

### 3.2 注意事项

- 密码错误时页面提示"访问密码错误"
- 登录状态保存在浏览器会话中，关闭浏览器标签后需重新登录
- 一个密码供所有老师共用（简单演示场景）

---

## 四、无 API Key 时的系统能力

如果未配置 `DASHSCOPE_API_KEY`，系统仍可使用：

| 功能 | 可用性 |
|------|--------|
| 文献库浏览 | ✅ 完全可用 |
| 文献列表分页查看 | ✅ 完全可用 |
| 已有研究空白查看 | ✅ 可用（读取已保存结果） |
| 已有假设查看 | ✅ 可用（读取已保存结果） |
| 公式模型解释 | ✅ 可用（基于规则，不依赖 API） |
| 文献分类筛选 | ✅ 完全可用 |
| 新生成研究空白 | ⚠️ 依赖本地规则，效果有限 |
| 新生成假设 | ⚠️ 依赖本地规则，效果有限 |

---

## 五、常见错误处理

### 5.1 部署后页面空白

可能原因：
- `requirements.txt` 中缺少依赖
- Secrets 中 `APP_PASSWORD` 未正确配置

查看 Streamlit Cloud 的 Logs（Deploy ⚙️ → Logs）确认具体错误。

### 5.2 部署后密码不对

确认 Secrets 格式：
```toml
APP_PASSWORD = "你的密码"
```
注意：等号两侧有空格，密码用双引号包裹，不要有额外换行。

### 5.3 "No module named xxx"

在 `requirements.txt` 中添加缺失的包，重新 push 即可自动重新部署。

### 5.4 API Key 无效

检查阿里云 DashScope API Key：
1. 登录 https://dashscope.aliyun.com
2. 创建或查看 API Key
3. 确保 Key 以 `sk-` 开头
4. 确保账户有可用额度

### 5.5 文献数据为空

`data/literature_database.csv` 和 `data/evidence_snippets.csv` 需要随代码一起上传。
如果本地已有数据，确保这些文件在 git add 时被包含。

---

## 六、本地开发命令

```bash
# 启动本地服务
streamlit run streamlit_app.py --server.port 8501

# 使用 DEMO_MODE（限制功能，加速演示）
set DEMO_MODE=True
streamlit run streamlit_app.py --server.port 8501

# 检查编译
python -m py_compile streamlit_app.py
```

---

## 七、文件清单（部署所需）

| 文件/目录 | 必需 | 说明 |
|-----------|------|------|
| `streamlit_app.py` | ✅ | 主入口 |
| `src/` | ✅ | 源码模块 |
| `skills/` | ✅ | 技能模块（PDF/RAG） |
| `data/` | ✅ | 文献库和证据数据（不含付费PDF） |
| `requirements.txt` | ✅ | Python 依赖 |
| `.gitignore` | ✅ | 排除敏感文件 |
| `config/` | ⚠️ | 如有则上传 |
| `docs/` | ⚠️ | 如有则上传 |

---

*生成日期：2026-07-23*
*TitaniumFatigueChat — 面向 L-PBF Ti-6Al-4V 疲劳机制发现的领域科研助手系统*
