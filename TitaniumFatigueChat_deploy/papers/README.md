# PDF 文献说明

本目录用于存放 L-PBF Ti-6Al-4V 疲劳研究的 PDF 文献。

## 部署说明

部署包中不包含 PDF 文件，原因：
1. 部分 PDF 受版权保护，不可公开分发
2. 部署到 Streamlit Cloud 时无需 PDF 文件（系统使用预提取的结构化数据）

## 如何使用

**本地使用**：
将 PDF 文件放入 papers/ 目录，然后运行：
```bash
python app.py ingest
```

**仅查看已有数据**：
系统已包含 `data/literature_database.csv`、`data/evidence_snippets.csv` 等结构化数据，
无需 PDF 即可浏览文献信息和证据片段。

## 文献来源

- 开放获取（Open Access）文献：可通过 DOI 直接下载
- 付费文献：需通过机构权限或个人订阅获取
- 用户上传：通过系统上传功能添加
