from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 初始化 Flask 應用程式
# 我們指定 static_folder=None 是為了等一下可以自訂根目錄的路由
app = Flask(__name__)
CORS(app)  # 啟用 CORS，允許前端跨域請求

# --- 資料庫設定 ---
# 設定資料庫連線 URI，這裡我們使用 SQLite，它會在本機建立一個 blog.db 檔案
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# 關閉不必要的追蹤功能以節省資源
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 初始化 SQLAlchemy 物件
db = SQLAlchemy(app)

# --- 資料模型定義 ---
# 定義 'Post' 模型，對應到資料庫中的 'posts' 表格
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 文章 ID，主鍵
    title = db.Column(db.String(100), nullable=False) # 文章標題，不允許為空
    content = db.Column(db.Text, nullable=False)    # 文章內容，不允許為空

    # 將模型物件轉換為字典格式，方便轉換成 JSON
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content
        }

# --- 網頁服務路由 ---

@app.route('/')
def serve_index():
    # 當使用者訪問根目錄時，回傳 index.html 檔案
    # '.' 代表目前的工作目錄
    return send_from_directory('.', 'index.html')

# --- RESTful API 路由 ---

# [CREATE] 建立新文章
@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or not 'title' in data or not 'content' in data:
        return jsonify({'error': '缺少標題或內容'}), 400
    
    new_post = Post(title=data['title'], content=data['content'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201

# [READ] 取得所有文章列表
@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])

# [READ] 取得單篇文章
@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify({'error': '找不到文章'}), 404
    return jsonify(post.to_dict())

# [UPDATE] 更新指定文章
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify({'error': '找不到文章'}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({'error': '請求中沒有資料'}), 400

    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    
    db.session.commit()
    return jsonify(post.to_dict())

# [DELETE] 刪除指定文章
@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return jsonify({'error': '找不到文章'}), 404
        
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': '文章已成功刪除'})

# --- 主程式入口 ---
if __name__ == '__main__':
    from waitress import serve # 匯入 waitress
    with app.app_context():
        # 建立所有資料庫表格
        db.create_all()
        # 如果資料庫是空的，新增一些初始資料
        if not Post.query.first():
            print("資料庫是空的，正在新增初始文章...")
            initial_posts = [
                Post(title='歡迎來到我的部落格', content='這是第一篇文章，很高興見到你！'),
                Post(title='關於 Flask 和 SQLAlchemy', content='這是一個強大的組合，可以用來快速開發網頁應用程式。'),
                Post(title='RESTful API 設計', content='設計良好的 API 可以讓前後端分離開發更加順利。')
            ]
            db.session.bulk_save_objects(initial_posts)
            db.session.commit()
    # 使用 waitress 作為正式環境的伺服器
    print("啟動 Waitress 伺服器於 http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000)

