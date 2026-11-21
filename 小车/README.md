# 智能巡检小车（二维仿真）

人工智能协会培训班统一项目「基于 Web 的智能巡检机器人二维仿真系统」的小组实现。
前身是 C 语言单机原型（explore.c，仓库内保留），现按课程要求改为前后端分离的 Web 版。

## 运行方法

1. 安装 Python 3.10+，然后安装依赖：
   pip install -r requirements.txt
2. 启动后端：
   python app.py
3. 浏览器打开 http://127.0.0.1:8000

## 玩法

- W/A/S/D 或按钮：手动开车（撞到障碍物会被挡住，不耗电）
- 点击画布任意空地：BFS 自动寻路并逐格播放动画
- 金色圆圈 = 待巡检点，开车压上去即打卡；集齐全部巡检点显示「巡检完成」
- 每走一格电量 -1，电量耗尽需点「重置」充电
- 「🤖 自动巡检」按钮：小车自动规划路线，依次打卡所有巡检点

## 接口文档

| 方法 | 路径 | 参数 | 返回 |
|---|---|---|---|
| POST | /api/move | {"direction":"w","x":1,"y":1} | {"new_x","new_y","blocked","checkpoint","checked","total"} |
| GET | /api/sensors | ?x=&y= | {"w","s","a","d"} 四方向是否被挡 |
| GET | /api/checkpoints | 无 | {"checked":[...],"total":n,"points":[[x,y]...]} |
| POST | /api/reset | 无 | 清空打卡记录 |
| POST | /api/bfs | {"sx","sy","gx","gy"} | {"path":[[x,y]...],"found"} |
| GET | /api/maze | 无 | {"w","h","maze"} |

## Docker 部署（可选）

一键启动（推荐）：
docker compose up -d
浏览器打开 http://127.0.0.1:8000（停止：docker compose down）

手动构建：
docker build -t car-web .
docker run -d -p 8000:8000 car-web

国内拉取基础镜像可先走镜像通道：
docker pull docker.m.daocloud.io/library/python:3.12-slim
docker tag docker.m.daocloud.io/library/python:3.12-slim python:3.12-slim

## Docker 镜像（已发布）

公开镜像地址（结课提交用）：

ghcr.io/jiang1-w/car-sim:v1.0

拉取并运行：
docker pull ghcr.io/jiang1-w/car-sim:v1.0
docker run -d -p 8000:8000 ghcr.io/jiang1-w/car-sim:v1.0

## 在线演示

待培训工作组统一部署公布演示域名后填入。

## 成员分工

- jiang1-w：后端控制与状态层——地图与碰撞检查、手动控制/巡检打卡/虚拟传感器/重置接口；前端手动控制与状态反馈模块（move/键盘监听/状态面板四件套/resetCar）；部署配置（Docker/Compose/CI）与文档
- zile7：前端骨架与渲染、寻路可视化与逐格动画、自动巡检（index.html 其余部分）+ BFS 最短路径算法（后端）
- AI 辅助编程：代码审查与调试（关键逻辑均经人工理解与实测验证）