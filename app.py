from flask import Flask, render_template, request, redirect, url_for, flash
import yaml
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用於 flash 訊息

# 確保輸出目錄存在
OUTPUT_DIR = 'output'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def load_fields():
    """讀取 fields.yaml 配置檔"""
    with open('fields.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config.get('fields', [])


@app.route('/')
def index():
    """顯示表單頁面"""
    fields = load_fields()
    return render_template('form.html', fields=fields)


@app.route('/submit', methods=['POST'])
def submit():
    """處理表單提交"""
    # 獲取表單資料
    form_data = {}
    fields = load_fields()
    
    for field in fields:
        field_name = field['name']
        form_data[field_name] = request.form.get(field_name, '')
    
    # 加入提交時間
    form_data['submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 生成檔名（使用當前時間）
    filename = datetime.now().strftime('%Y%m%d_%H%M%S.yaml')
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # 儲存為 YAML 檔案
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(form_data, f, allow_unicode=True, default_flow_style=False)
    
    flash(f'表單已成功儲存至 {filename}', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
