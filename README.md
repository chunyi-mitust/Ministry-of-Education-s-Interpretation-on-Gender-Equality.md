# 性平函釋資料庫
校園性別平等教育資訊網相關**函釋、法規與概念**的 [Obsidian](https://obsidian.md) 知識庫。全資料庫以markdown格式處理，並且使用OCR處理早期為圖檔的函釋

以教育部性平資料庫中24頁共345份函釋主體，輔以相關法規與受控概念詞表，以及收錄部分函釋中提到其他函釋與相關法規(地區教育單位函釋未收錄)，並且於函釋間建立Obsidian、函釋與概念/法規之間的雙向連結，方便依主題或時間脈絡查找。

下載資料夾後，可直接用 AI agent 掛載整個資料夾作為知識庫；也可以將 `函釋按年份整理/` 內依年份彙整的 Markdown 檔匯入 NotebookLM，建立查詢資料庫。

<img width="3831" height="2088" alt="image" src="https://github.com/user-attachments/assets/e3008cb3-5abe-4073-b498-2ea648d2fd0b" />

<img width="3837" height="2080" alt="image" src="https://github.com/user-attachments/assets/a7d8e42f-4f0c-45e4-96ed-8d1c229dc775" />

## 如何使用[Obsidian]
1. 安裝 [Obsidian](https://obsidian.md)。
2. 
3. 「Open folder as vault」選擇本資料夾。
4. 
5. 從 `00_總覽/性平知識庫總覽` 進入，或用概念頁、函釋時間軸、`函釋按年份整理/` 瀏覽。
6. 
7. 若要給 AI 工具使用，可掛載整個資料夾；若只需要快速問答，可優先匯入 `函釋按年份整理/` 的年度彙整檔。

## 如何使用[NotebookLM]
1.擁有Google的NotebookLM使用權限

2.於NotebookLM創建頁面創建[新的筆記本]

<img width="520" height="418" alt="圖片" src="https://github.com/user-attachments/assets/5261b837-9110-4191-956d-846c25b0a006" />

3.上傳檔案中選擇 `函釋按年份整理/` 資料夾的所有東西上傳

<img width="1217" height="990" alt="圖片" src="https://github.com/user-attachments/assets/89538305-a96f-44b9-a529-6b1e93943968" />

<img width="1387" height="1404" alt="圖片" src="https://github.com/user-attachments/assets/bafd7a5d-bd49-4b69-93d2-316dd5bd68d2" />

4.於[NotebookLM]的對話框中詢問相關內容即可，亦可把性平相關法規、校內法規加入，建立專屬知識庫

## 其他AI工具使用方式
1.在可建立專屬AI應用的功能(chatgpt為專案 claude為projects)上傳 `函釋按年份整理/`中檔案以及法規、校內法規加入

## 資料建立流程
1.如有圖檔舊版函釋需加入更新，可以先使用gemini模型進行OCR辨識然後加入更新，如函釋量過大建議使用Antigravity批量調用gemini模型處理
2.建議使用codex或clude進行校稿以及建立[Obsidian]知識庫的關聯

## 資料來源
- 教育部性別平等教育全球資訊網「函釋目錄」(<https://www.gender.edu.tw>)
- 全國法規資料庫、教育部主管法規共用系統等公開法規來源

## 資料缺失
- 完整納入教育部性別平等教育全球資訊網「函釋目錄」中所有內容，目前資料庫缺失部分為地方教育局函釋以及函釋中提及的關聯函釋

## 著作權、授權與更新
- **函釋與法規本文**屬政府公文，依《著作權法》第 9 條不得為著作權之標的。
- 本專案的**整理、結構、概念詞表與維護腳本**以 [MIT License](LICENSE) 釋出。
- 資料由公開來源整理，OCR 與人工編修可能有誤；正式引用請以官方原文為準，本庫僅供檢索參考。
- 資料夾內容可能並非最新，請使用前再注意更新時間，以免使用到舊版資料
