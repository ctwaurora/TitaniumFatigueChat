# TitaniumFatigueChat 部署检查报告

生成时间：2026-07-23

## 一、保留文件清单

| 类型 | 文件 | 大小 |
|------|------|------|
| ✅ 主入口 | `streamlit_app.py` | 3382 行 |
| ✅ CLI 入口 | `app.py` | 675 行 |
| ✅ 依赖 | `requirements.txt` | 11 个依赖 |
| ✅ 部署说明 | `DEPLOY_STREAMLIT.md` | 有 |
| ✅ 源码 | `src/` | 43 个 .py 文件 |
| ✅ 技能模块 | `skills/` | 14 个 .py 文件 |
| ✅ 文献数据 | `data/literature_database.csv` | 有 |
| ✅ 候选文献 | `data/candidate_papers.csv` | 有 |
| ✅ 证据片段 | `data/evidence_snippets.csv` | 50 列 |
| ✅ 变量关系 | `data/variable_relation_dataset.csv` | 有 |
| ✅ 假设数据 | `data/hypothesis_dataset.csv` | 有 |
| ✅ 研究空白 | `data/research_gap_dataset.csv` | 有 |
| ✅ 方程参数 | `data/equation_parameter_dataset.csv` | 有 |
| ✅ 配置 | `config/task_profile.yaml` | 有 |

## 二、排除文件清单

| 状态 | 文件 | 原因 |
|------|------|------|
| ❌ 排除 | `qwen_key.txt` | API Key 明文 |
| ❌ 排除 | `.env` | 环境变量 |
| ❌ 排除 | `.streamlit/secrets.toml` | 部署后手动配置 |
| ❌ 排除 | `__pycache__/` | Python 缓存 |
| ❌ 排除 | `logs/` | 本地日志 |
| ❌ 排除 | `papers/*.pdf` | 版权保护 |
| ❌ 排除 | `outputs/*.md` | 临时生成报告 |
| ❌ 排除 | `legacy_training/` | 训练脚本 |
| ❌ 排除 | `legacy_scripts/` | 历史脚本 |
| ❌ 排除 | `competition_package/` | 比赛包 |

## 三、安全检查

| 检查项 | 结果 |
|--------|------|
| API Key 硬编码 | ✅ 无 |
| qwen_key.txt 实际读取 | ✅ 仅 `api_keys.py` 作为回退方式 |
| 绝对路径 C:\Users\ctw | ✅ 无 |
| 付费 PDF | ✅ 无 |
| Secrets 配置 | ✅ 部署后在 Streamlit Cloud 配置 |
| 密码门禁 | ✅ `st.secrets["APP_PASSWORD"]` |
| 明文密码在代码中 | ✅ 无 |

## 四、功能检查

| 功能 | 状态 |
|------|------|
| `streamlit run streamlit_app.py` 启动 | ✅ 可运行 |
| 密码登录页面 | ✅ 先显示密码框 |
| 密码错误提示 | ✅ 显示"访问密码错误" |
| 侧边栏导航 | ✅ 6 项（无空页面） |
| 文献库分页 | ✅ 每页 20 条 |
| 研究空白发现 | ✅ 按钮触发 |
| 假设生成（拆分引擎） | ✅ 多变量自动拆分 H1/H2/H3 |
| 实验方案辅助 | ✅ 10 节结构化输出 |
| 公式模型解释 | ✅ 多模型对比表 |
| DEMO_MODE | ✅ 环境变量控制 |
| 文献数据预加载 | ✅ 7 个 CSV 文件 |

## 五、部署注意事项

1. **必须配置 Secrets**：在 Streamlit Cloud → Advanced settings 中配置：
   ```toml
   APP_PASSWORD = "你的密码"
   DASHSCOPE_API_KEY = "你的 API Key（可选）"
   ```

2. **无 API Key 时可运行**：文献浏览、已保存结果查看正常，仅新生成功能受限。

3. **上传前确认**：本地 `streamlit_app.py` 和 `src/api_keys.py` 中无硬编码 key。

4. **建议上传的文件**：
   ```bash
   git add streamlit_app.py app.py requirements.txt DEPLOY_STREAMLIT.md .gitignore
   git add src/ skills/ data/ config/ docs/
   git commit -m "Deployment package"
   git push
   ```
