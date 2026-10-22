from flask import Flask, request

app = Flask(__name__)

@app.post('/api/move')
def move():
    data = request.get_json()
    direction = data.get('direction', '')
    x = int(data.get('x', 0))
    y = int(data.get('y', 0))
    
    new_x, new_y = x, y
    
    if direction == 'w': new_y -= 1
    elif direction == 's': new_y += 1
    elif direction == 'a': new_x -= 1
    elif direction == 'd': new_x += 1
    
    if 0 <= new_x < 20 and 0 <= new_y < 15:
        return {'new_x': new_x, 'new_y': new_y}
    else:
        return {'new_x': x, 'new_y': y}

@app.get('/')
def home():
    with open('index.html', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    print("小车后端已启动: http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000, debug=True)