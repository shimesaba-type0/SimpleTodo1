from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

# HTMLテンプレート
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Todo アプリケーション</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .task { 
            border: 1px solid #ddd; 
            margin: 10px 0; 
            padding: 10px; 
            border-radius: 5px;
        }
        .completed { 
            background-color: #e8ffe8; 
        }
        .task-form {
            margin-bottom: 20px;
        }
        .task-form input, .task-form textarea {
            margin: 5px 0;
            padding: 5px;
            width: 100%;
        }
    </style>
</head>
<body>
    <h1>Todo リスト</h1>
    
    <div class="task-form">
        <h2>新しいタスクの追加</h2>
        <form id="todoForm">
            <input type="text" id="title" placeholder="タイトル" required><br>
            <textarea id="description" placeholder="詳細説明"></textarea><br>
            <button type="submit">追加</button>
        </form>
    </div>

    <div id="todoList"></div>

    <script>
        // タスク一覧の取得と表示
        function loadTasks() {
            fetch('/api/todos')
                .then(response => response.json())
                .then(todos => {
                    const todoList = document.getElementById('todoList');
                    todoList.innerHTML = '';
                    todos.forEach(todo => {
                        const div = document.createElement('div');
                        div.className = `task ${todo.completed ? 'completed' : ''}`;
                        div.innerHTML = `
                            <h3>${todo.title}</h3>
                            <p>${todo.description || '説明なし'}</p>
                            <button onclick="toggleTask(${todo.id})">${todo.completed ? '未完了に戻す' : '完了にする'}</button>
                            <button onclick="deleteTask(${todo.id})">削除</button>
                        `;
                        todoList.appendChild(div);
                    });
                });
        }

        // 新しいタスクの追加
        document.getElementById('todoForm').onsubmit = function(e) {
            e.preventDefault();
            const title = document.getElementById('title').value;
            const description = document.getElementById('description').value;
            
            fetch('/api/todos', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title, description})
            }).then(() => {
                document.getElementById('title').value = '';
                document.getElementById('description').value = '';
                loadTasks();
            });
        };

        // タスクの完了状態の切り替え
        function toggleTask(id) {
            fetch(`/api/todos/${id}/toggle`, {
                method: 'POST'
            }).then(() => loadTasks());
        }

        // タスクの削除
        function deleteTask(id) {
            if (confirm('本当に削除しますか？')) {
                fetch(`/api/todos/${id}`, {
                    method: 'DELETE'
                }).then(() => loadTasks());
            }
        }

        // 初期表示
        loadTasks();
    </script>
</body>
</html>
'''

# ルート
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# API エンドポイント
@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([{
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'completed': todo.completed,
        'created_at': todo.created_at.isoformat()
    } for todo in todos])

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    todo = Todo(
        title=data['title'],
        description=data.get('description', '')
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/todos/<int:todo_id>/toggle', methods=['POST'])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

