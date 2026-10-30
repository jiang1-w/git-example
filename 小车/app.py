from collections import deque
from flask import Flask, request

app = Flask(__name__)

# ---------- 地图：0=可通行 1=障碍物 2=巡检点（全程序唯一权威来源） ----------
GRID = [
    [0,0,0,0,2,0,0,0,0,0],
    [0,0,1,1,0,0,1,1,1,0],
    [0,1,0,0,0,0,0,0,1,0],
    [0,1,0,1,1,1,1,0,1,0],
    [0,0,0,1,2,0,1,0,0,0],
    [0,1,1,1,0,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,2,0],
]
GRID_H = len(GRID)
GRID_W = len(GRID[0])

TOTAL = 0                       # 巡检点总数
for row in GRID:
    TOTAL = TOTAL + row.count(2)

POINTS = []                     # 所有巡检点的坐标，供前端自动巡检排队用
for yy in range(GRID_H):
    for xx in range(GRID_W):
        if GRID[yy][xx] == 2:
            POINTS.append([xx, yy])

checked = []                    # 已打卡账本（存在后端，多个浏览器共享）

def can_stand(x, y):
    """越界不行；障碍物(1)不行；空地(0)和巡检点(2)都可以站"""
    if 0 <= x < GRID_W and 0 <= y < GRID_H:
        return GRID[y][x] != 1
    return False

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

    blocked = not can_stand(new_x, new_y)
    hit = False
    if not blocked:
        x, y = new_x, new_y
        if GRID[y][x] == 2:
            key = str(x) + ',' + str(y)
            if key not in checked:
                checked.append(key)
                hit = True
    return {'new_x': x, 'new_y': y, 'blocked': blocked,
            'checkpoint': hit, 'checked': checked, 'total': TOTAL}

@app.get('/api/sensors')
def sensors():
    """虚拟传感器：四个方向有没有被挡（true = 那边走不了）"""
    x = int(request.args.get('x', 0))
    y = int(request.args.get('y', 0))
    return {'w': not can_stand(x, y - 1),
            's': not can_stand(x, y + 1),
            'a': not can_stand(x - 1, y),
            'd': not can_stand(x + 1, y)}

@app.get('/api/checkpoints')
def checkpoints():
    return {'checked': checked, 'total': TOTAL, 'points': POINTS}

@app.post('/api/reset')
def reset():
    checked.clear()
    return {'checked': checked, 'total': TOTAL}

@app.get('/')
def home():
    with open('index.html', encoding='utf-8') as f:
        return f.read()

def bfs(start, goal):
    """返回从 start 到 goal 的最短路径坐标列表；不可达返回 None。"""
    sx, sy = start
    gx, gy = goal
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
            path = []
            cur = (gx, gy)
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return path

        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H \
               and GRID[ny][nx] != 1 and (nx, ny) not in prev:
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
    print("小车后端已启动: http://127.0.0.1:8000  巡检点共 %d 个" % TOTAL)
    app.run(host='0.0.0.0', port=8000, debug=True)