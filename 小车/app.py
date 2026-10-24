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

#）地图
GRID = [
    [0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,0,0,1,1,1,0],
    [0,1,0,0,0,0,0,0,1,0],
    [0,1,0,1,1,1,1,0,1,0],
    [0,0,0,1,0,0,1,0,0,0],
    [0,1,1,1,0,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0],
]
GRID_H = len(GRID)
GRID_W = len(GRID[0])

from collections import deque

def bfs(start, goal):
    """返回从 start 到 goal 的最短路径坐标列表；不可达返回 None。"""
    sx, sy = start
    gx, gy = goal
    # 越界或障碍直接失败
    for (px, py) in (start, goal):
        if not (0 <= px < GRID_W and 0 <= py < GRID_H):
            return None
        if GRID[py][px] == 1:
            return None

    q = deque([(sx, sy)])
    prev = {(sx, sy): None}

    while q:
        x, y = q.popleft()
        if (x, y) == (gx, gy):
            # 回溯路径
            path = []
            cur = (gx, gy)
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return path

        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H \
               and GRID[ny][nx] == 0 and (nx, ny) not in prev:
                prev[(nx, ny)] = (x, y)
                q.append((nx, ny))
    return None

@app.post('/api/bfs')
def api_bfs():
    data = request.get_json() or {}
    start = (int(data.get('sx', 0)), int(data.get('sy', 0)))
    goal  = (int(data.get('gx', 0)), int(data.get('gy', 0)))
    path = bfs(start, goal)
    return {'path': path, 'found': path is not None}

@app.get('/api/maze')
def api_maze():
    return {'w': GRID_W, 'h': GRID_H, 'maze': GRID}
if __name__ == '__main__':
    print("小车后端已启动: http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000, debug=True)