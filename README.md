# 性平函釋資料庫

校園性別平等教育資訊網相關**函釋、法規與概念**的 [Obsidian](https://obsidian.md) 知識庫。以教育部歷年函釋為主體，輔以相關法規與受控概念詞表，以及收錄部分函釋中提到其他函釋與相關法規，並且於函釋間建立Obsidian、函釋與概念/法規之間的雙向連結，方便依主題或時間脈絡查找。

下載資料夾後，可直接用 AI agent 掛載整個資料夾作為知識庫；也可以將 `函釋按年份整理/` 內依年份彙整的 Markdown 檔匯入 NotebookLM，建立年份脈絡清楚的查詢資料庫。

<img width="3831" height="2088" alt="image" src="https://github.com/user-attachments/assets/e3008cb3-5abe-4073-b498-2ea648d2fd0b" />


<img width="3837" height="2080" alt="image" src="https://github.com/user-attachments/assets/a7d8e42f-4f0c-45e4-96ed-8d1c229dc775" />


## 如何使用

1. 安裝 [Obsidian](https://obsidian.md)。
2. 「Open folder as vault」選擇本資料夾。
3. 從 `00_總覽/性平知識庫總覽` 進入，或用概念頁、函釋時間軸、`函釋按年份整理/` 瀏覽。
4. 若要給 AI 工具使用，可掛載整個資料夾；若只需要快速問答，可優先匯入 `函釋按年份整理/` 的年度彙整檔。

不使用 Obsidian 也可以——所有內容都是純 Markdown，可直接在 GitHub 或任何編輯器閱讀，`[[雙向連結]]` 為 Obsidian 語法。

## 維護腳本（`99_維護/`）
需 Python 3.10+。於資料庫**根目錄**執行：

```bash
pip install -r requirements.txt          # 只有 PDF 重建需要 pdfplumber
python 99_維護/process_obsidian_vault.py  # 重建索引、概念頁、時間軸、關聯表、frontmatter
python 99_維護/strip_boilerplate.py       # 精簡函釋正文（預設 dry-run，加 --apply 才寫入）
python 99_維護/crawl_catalog_diff.py      # 比對教育部官方函釋目錄，列出本庫尚缺的函釋
```
三支腳本皆具冪等性；新增函釋 Markdown 後，依序跑 `process_obsidian_vault.py` 與 `strip_boilerplate.py --apply` 即可整併。
## 資料來源
- 教育部性別平等教育全球資訊網「函釋目錄」(<https://www.gender.edu.tw>)
- 全國法規資料庫、教育部主管法規共用系統等公開法規來源

## 著作權與授權
- **函釋與法規本文**屬政府公文，依《著作權法》第 9 條不得為著作權之標的，本即可自由使用。
- 本專案的**整理、結構、概念詞表與維護腳本**以 [MIT License](LICENSE) 釋出。
- 資料由公開來源整理，OCR 與人工編修可能有誤；正式引用請以官方原文為準，本庫僅供檢索參考。
