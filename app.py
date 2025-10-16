import re
from flask import Flask, render_template, request, redirect, url_for
# --- 修正點 START ---
# 在新版 Jinja2/Flask 中，Markup 和 escape 已移至 markupsafe 套件
from jinja2 import pass_eval_context
from markupsafe import Markup, escape
# --- 修正點 END ---

# 初始化 Flask 應用
app = Flask(__name__)


# 定義 nl2br 過濾器，將換行符號轉換成 <br> 標籤
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
# 使用新版的 @pass_eval_context 裝飾器
@pass_eval_context
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


# 使用一個簡單的 Python 列表來模擬資料庫
# 在真實世界的應用中，你會使用像 SQLite, PostgreSQL 這樣的資料庫
posts = [
    {
        'id': 1,
        'author': '小明',
        'title': 'Flask 初體驗',
        'content': '今天我開始學習 Flask，這是一個輕量又強大的 Python 網站框架。\n感覺很不錯！'
    },
    {
        'id': 2,
        'author': '小華',
        'title': '關於模板繼承',
        'content': 'Jinja2 的模板繼承功能真的很好用。\n可以讓我省下很多重複的 HTML 程式碼。'
    }
]
# 用於生成新文章 ID 的計數器
next_id = 3

# 主頁路由: 顯示所有文章列表
@app.route('/')
def index():
    # 渲染 index.html 模板，並傳入 posts 列表
    return render_template('index.html', posts=posts)

# 新增文章的路由: 支援 GET 和 POST 請求
@app.route('/create', methods=('GET', 'POST'))
def create():
    global next_id
    # 如果是 POST 請求 (使用者提交了表單)
    if request.method == 'POST':
        # 從表單中獲取資料
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']

        # 簡單的驗證，確保標題和內容不為空
        if not title or not content or not author:
            # 在此可以加入錯誤訊息提示，此處為簡化範例
            print("錯誤：標題、作者和內容為必填項！")
        else:
            # 創建新的文章字典
            new_post = {
                'id': next_id,
                'author': author,
                'title': title,
                'content': content
            }
            # 將新文章加入到 posts 列表中
            posts.append(new_post)
            # 更新下一個可用的 ID
            next_id += 1
            # 重新導向到主頁
            return redirect(url_for('index'))

    # 如果是 GET 請求，就顯示創建文章的頁面
    return render_template('create.html')

# 讓這個 Python 檔案可以直接被執行
if __name__ == '__main__':
    # 改用 waitress 伺服器來運行 app，徹底繞過 Werkzeug 的編碼問題
    from waitress import serve
    print("伺服器已啟動於 http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000)

