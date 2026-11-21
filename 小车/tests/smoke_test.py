# -*- coding: utf-8 -*-
"""结课 CI 接口冒烟测试：对运行中的后端断言全部 6 个接口。
用法：先启动后端（python app.py 或 docker run），再运行 python tests/smoke_test.py
环境变量 SMOKE_BASE 可覆盖目标地址（默认 http://127.0.0.1:8000）。"""
import json
import os
import time
import urllib.request

BASE = os.environ.get("SMOKE_BASE", "http://127.0.0.1:8000")


def call(method, path, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def wait_server(seconds=30):
    for _ in range(seconds * 2):
        try:
            call("GET", "/api/maze")
            return
        except Exception:
            time.sleep(0.5)
    raise SystemExit("后端 30 秒内未就绪：" + BASE)


def main():
    wait_server()
    ok = []

    st, maze = call("GET", "/api/maze")
    assert st == 200 and maze.get("w", 0) > 0 and maze.get("h", 0) > 0 and isinstance(maze.get("maze"), list)
    ok.append("/api/maze %dx%d" % (maze["w"], maze["h"]))

    st, cps = call("GET", "/api/checkpoints")
    assert st == 200 and cps.get("total", 0) > 0 and cps.get("points")
    ok.append("/api/checkpoints total=%d" % cps["total"])

    goal = cps["points"][0]
    st, bfs = call("POST", "/api/bfs", {"sx": 1, "sy": 1, "gx": goal[0], "gy": goal[1]})
    assert st == 200 and bfs.get("found") is True and bfs.get("path")
    ok.append("/api/bfs 最短 %d 步" % len(bfs["path"]))

    st, mv = call("POST", "/api/move", {"direction": "d", "x": 1, "y": 1})
    assert st == 200 and all(k in mv for k in ("new_x", "new_y", "blocked", "checkpoint", "checked", "total"))
    ok.append("/api/move blocked=%s" % mv["blocked"])

    st, sn = call("GET", "/api/sensors?x=1&y=1")
    assert st == 200 and all(k in sn for k in ("w", "s", "a", "d"))
    ok.append("/api/sensors 四向")

    st, rs = call("POST", "/api/reset")
    assert st == 200
    ok.append("/api/reset")

    print("SMOKE PASS: " + " | ".join(ok))


if __name__ == "__main__":
    main()
