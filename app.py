from flask import Flask, render_template, request, redirect, url_for, flash, abort
import yaml
from datetime import datetime, timedelta
import os
from random import randint, choice

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用於 flash 訊息
app.jinja_env.globals.update(max=max, min=min)

# 確保輸出目錄存在
OUTPUT_DIR = 'output'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def load_fields():
    """讀取 fields.yaml 配置檔"""
    with open('fields.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config.get('fields', [])


def list_yaml_files():
    """列出 output 目錄下所有 YAML 檔案（依檔名降序）"""
    if not os.path.exists(OUTPUT_DIR):
        return []
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.yaml')]
    return sorted(files, reverse=True)


def resolve_entry_path(filename):
    """避免路徑穿越，僅允許 output 目錄內的 YAML 檔"""
    if not filename or '/' in filename or '\\' in filename:
        abort(404)
    if not filename.endswith('.yaml'):
        abort(404)
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(filepath):
        abort(404)
    return filepath


def load_entry(filename):
    filepath = resolve_entry_path(filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data


def save_entry(filename, data):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def generate_test_data(count=100):
    """生成測試資料"""
    names = ['王小明', '李美麗', '張大偉', '劉小紅', '陳小剛', '楊小青', '黃小金', '周小銀', '吳小春', '徐小夏']
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'example.com', 'test.com']
    messages = ['這是測試留言', '很滿意', '需要改進', '非常好', '中等', '一般般', '不錯', '還可以', '值得推薦', '普通']
    
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        name = choice(names)
        email = f"{name.replace(' ', '')}_test{i}@{choice(domains)}"
        phone = f"09{randint(10000000, 99999999)}"
        message = choice(messages)
        submit_time = start_date + timedelta(hours=i * (24 / count))
        
        data = {
            'name': name,
            'email': email,
            'phone': phone,
            'message': message,
            'submitted_at': submit_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        filename = submit_time.strftime('%Y%m%d_%H%M%S.yaml')
        save_entry(filename, data)


@app.route('/')
def index():
    """入口改導向清單"""
    return redirect(url_for('entries'))


@app.route('/form')
def form():
    """顯示表單頁面"""
    fields = load_fields()
    return render_template('form.html', fields=fields)


@app.route('/entries')
def entries():
    """顯示已儲存 YAML 清單，支援搜尋過濾與分頁"""
    files = list_yaml_files()
    items = []
    for filename in files:
        try:
            data = load_entry(filename)
        except Exception:
            data = {}
        items.append({
            'filename': filename,
            'submitted_at': data.get('submitted_at', ''),
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', '')
        })
    
    # 搜尋過濾
    search = request.args.get('search', '').strip().lower()
    if search:
        items = [item for item in items if 
                 search in item['name'].lower() or
                 search in item['email'].lower() or
                 search in item['phone'].lower() or
                 search in item['submitted_at'].lower()]
    
    # 分頁
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(items)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = items[start_idx:end_idx]
    
    # 計算分頁範圍
    page_range = list(range(max(1, page-2), min(total_pages+1, page+3))) if total_pages > 1 else []
    
    return render_template('list.html', items=page_items, search=search, page=page, total_pages=total_pages, total=total, page_range=page_range)


@app.route('/entries/<filename>')
def view_entry(filename):
    """讀取單一 YAML"""
    entry = load_entry(filename)
    return render_template('view.html', entry=entry, filename=filename)


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
    return redirect(url_for('entries'))


@app.route('/entries/<filename>/edit', methods=['GET', 'POST'])
def edit_entry(filename):
    """編輯既有 YAML"""
    fields = load_fields()
    entry = load_entry(filename)

    if request.method == 'POST':
        updated = {}
        for field in fields:
            field_name = field['name']
            updated[field_name] = request.form.get(field_name, '')

        if entry.get('submitted_at'):
            updated['submitted_at'] = entry['submitted_at']
        else:
            updated['submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        save_entry(filename, updated)
        flash(f'已更新 {filename}', 'success')
        return redirect(url_for('entries'))

    return render_template('edit.html', fields=fields, entry=entry, filename=filename)


@app.route('/entries/<filename>/delete', methods=['POST'])
def delete_entry(filename):
    """刪除 YAML"""
    filepath = resolve_entry_path(filename)
    os.remove(filepath)
    flash(f'已刪除 {filename}', 'success')
    return redirect(url_for('entries'))


@app.route('/generate-test-data')
def generate_test():
    """生成 100 筆測試資料"""
    generate_test_data(100)
    flash('已生成 100 筆測試資料', 'success')
    return redirect(url_for('entries'))


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(debug=True, host='0.0.0.0', port=port)
