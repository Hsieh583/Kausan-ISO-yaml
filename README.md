# Kausan-ISO-yaml

使用 YAML 保存表單資料的 Flask 應用程式

## 功能特點

- 📝 從 `fields.yaml` 動態生成表單
- 💾 自動將提交的資料儲存為以時間命名的 YAML 檔案
- 🎨 美觀的使用者介面
- ⚡ 簡單易用

## 安裝步驟

1. 安裝相依套件：

```bash
pip install -r requirements.txt
```

## 使用方法

1. 啟動 Flask 應用程式：

```bash
python app.py
```

2. 在瀏覽器中開啟 `http://localhost:5000`

3. 填寫表單並提交

4. 提交後的資料會儲存在 `output/` 目錄中，檔名格式為 `YYYYMMDD_HHMMSS.yaml`

## 自訂表單欄位

編輯 `fields.yaml` 檔案來自訂表單欄位：

```yaml
fields:
  - name: field_name        # 欄位名稱
    label: 欄位標籤         # 顯示標籤
    type: text              # 欄位類型 (text, email, tel, textarea)
    required: true          # 是否必填
```

### 支援的欄位類型

- `text`: 文字輸入框
- `email`: 電子郵件輸入框
- `tel`: 電話輸入框
- `textarea`: 多行文字輸入框

## 檔案結構

```
.
├── app.py              # Flask 應用程式主檔案
├── fields.yaml         # 表單欄位配置檔
├── requirements.txt    # Python 相依套件
├── templates/          # HTML 模板目錄
│   └── form.html      # 表單頁面模板
└── output/            # 儲存提交資料的目錄
```

## 範例

當你提交一個表單後，會在 `output/` 目錄產生類似以下的 YAML 檔案：

```yaml
name: 張三
email: example@example.com
phone: '0912345678'
message: 這是測試留言
submitted_at: '2024-01-31 17:35:00'
```
