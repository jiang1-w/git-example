from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

car = {"x": 1, "y": 1}          # 小车状态放在后端（这就是"联机"的核心）

@app.get("/api/move")
def move():
    cmd = request.args.get("cmd", "")        # 前端发来的字符指令
    if cmd == "w": car["y"] -= 1             # 上
    elif cmd == "s": car["y"] += 1           # 下
    elif cmd == "a": car["x"] -= 1           # 左
    elif cmd == "d": car["x"] += 1           # 右
    else: return jsonify(error="invalid cmd"), 400
    return jsonify(x=car["x"], y=car["y"])   # 返回 {"x": 2, "y": 3}

@app.get("/api/reset")
def reset():
    car["x"] = 1
    car["y"] = 1
    return jsonify(x=car["x"], y=car["y"])

@app.get("/")
def home():
    return send_file("index.html")           # 前端页面也由后端提供

if __name__ == "__main__":
    app.run(debug=True, port=5000)