from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import json
import os
import sys
from datetime import datetime

# Add parent directory to path to import agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.react_agent import ReActAgent, AddTodoTool, DeleteTodoTool, ListTodosTool

load_dotenv()

app = Flask(__name__)
CORS(app)

TODOS_FILE = os.getenv('TODOS_FILE', 'todos.json')
PORT = int(os.getenv('PORT', 5000))

def load_todos():
    if os.path.exists(TODOS_FILE):
        with open(TODOS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODOS_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

def get_next_id(todos):
    if not todos:
        return 1
    return max(todo['id'] for todo in todos) + 1

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    return jsonify({
        'message': 'Simple Todo API',
        'endpoints': {
            'GET /todos': 'Get all todos',
            'GET /todos/<id>': 'Get a specific todo',
            'POST /todos': 'Create a new todo',
            'PUT /todos/<id>': 'Update a todo',
            'DELETE /todos/<id>': 'Delete a todo'
        }
    })

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = load_todos()
    return jsonify(todos)

@app.route('/todos/<int:id>', methods=['GET'])
def get_todo(id):
    todos = load_todos()
    todo = next((t for t in todos if t['id'] == id), None)
    if todo:
        return jsonify(todo)
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    todos = load_todos()
    new_todo = {
        'id': get_next_id(todos),
        'title': data['title'],
        'completed': data.get('completed', False),
        'created_at': datetime.now().isoformat()
    }
    
    todos.append(new_todo)
    save_todos(todos)
    
    return jsonify(new_todo), 201

@app.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    todos = load_todos()
    todo = next((t for t in todos if t['id'] == id), None)
    
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    
    data = request.get_json()
    if 'title' in data:
        todo['title'] = data['title']
    if 'completed' in data:
        todo['completed'] = data['completed']
    
    save_todos(todos)
    return jsonify(todo)

@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todos = load_todos()
    todos = [t for t in todos if t['id'] != id]
    save_todos(todos)
    return jsonify({'message': 'Todo deleted'}), 200

@app.route('/agent/execute', methods=['POST'])
def execute_agent():
    """Execute a ReAct agent with a given query"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400
    
    query = data['query']
    
    # Initialize tools and agent
    tools = [
        AddTodoTool(api_url=f"http://localhost:{PORT}"),
        DeleteTodoTool(api_url=f"http://localhost:{PORT}"),
        ListTodosTool(api_url=f"http://localhost:{PORT}")
    ]
    
    agent = ReActAgent(tools, verbose=False)
    
    try:
        # Run the agent
        result = agent.run(query)
        
        return jsonify({
            'success': True,
            'query': query,
            'answer': result['answer'],
            'history': result['history']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true', port=PORT)
