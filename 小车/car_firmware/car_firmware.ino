#include <WiFi.h>                 // WiFi 工具箱
#include <WebServer.h>            // 网页服务器工具箱

// ========== ① 烧录前必改：你家 WiFi 的名字和密码 ==========
const char* ssid = "改成你家WiFi名";      // 注意：只支持 2.4G 频段（手机开热点默认就是）
const char* pass = "改成你的WiFi密码";    // ⚠️ 带真实密码的这个文件不要传公开仓库

// ========== ② 引脚分配（和指南 §6 / §8 接线表一一对应）==========
int IN1 = 26, IN2 = 27;           // 左电机：两个方向脚（接 L298N 的 IN1/IN2）
int IN3 = 32, IN4 = 33;           // 右电机：两个方向脚（接 L298N 的 IN3/IN4）
int TRIG = 25, ECHO = 34;         // 超声波：发令脚 / 听回声脚
int SEN_L = 35, SEN_C = 23, SEN_R = 18;   // C/R 改到丝印清晰的 D23/D18（此板未引出 36 脚）   // 循迹模块：左 / 中 / 右 三个红外眼

// ========== ③ 可调参数（先按默认跑，跑顺了再改）==========
int STOP_DIST = 20;               // 自动刹车距离：前方 20cm 内有东西就拒绝前进
int MOVE_MS  = 300;               // 点动时长：每次指令走 300 毫秒
int AUTO_MS  = 250;               // 自动巡线：每 250 毫秒修正一次方向
bool HAS_SONAR = false;               // 电阻包没到：暂无超声波回声（ECHO 悬空）——true 之后前进自动恢复 20cm 刹车
int BLACK  = LOW;                 // 黑线对应的电平。多数模块黑线=LOW；若巡线方向反了，把 LOW 改成 HIGH

WebServer server(80);             // 车上的网页服务器，80 端口
bool autoMode = false;            // 是否正在自动巡线

// ---------- 电机部分 ----------
void setMotors(int l1, int l2, int r1, int r2) {   // 一次设置四个脚
  digitalWrite(IN1, l1); digitalWrite(IN2, l2);    // HIGH=通电 LOW=断电
  digitalWrite(IN3, r1); digitalWrite(IN4, r2);
}
void forward() { setMotors(HIGH, LOW,  HIGH, LOW);  }   // 左右都正转 = 前进
void back()    { setMotors(LOW, HIGH,  LOW, HIGH);  }   // 都反转 = 后退
void left()    { setMotors(LOW, HIGH,  HIGH, LOW);  }   // 左退右进 = 左拐
void right()   { setMotors(HIGH, LOW,  LOW, HIGH);  }   // 左进右退 = 右拐
void stopCar() { setMotors(LOW, LOW,   LOW, LOW);   }   // 全断 = 停

// ---------- 传感器部分 ----------
long readDistance() {                     // 测前方距离，单位厘米
  digitalWrite(TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);   // 发一声"哨"
  digitalWrite(TRIG, LOW);
  long t = pulseIn(ECHO, HIGH, 30000);    // 听回声持续多久（微秒），最多等 30ms
  if (t == 0) return 999;                 // 没听到回声 = 前方很远，当 999cm
  return t / 58;                          // 微秒换算成厘米（去程+回程÷2）
}
bool onLine(int pin) {                    // 这个红外眼是否踩在黑线上
  return digitalRead(pin) == BLACK;
}

// ---------- 自动巡线：朴素三分支 ----------
void autoFollowStep() {                   // 每次修正一小步，跑得稳不摔跤
  if      (onLine(SEN_C)) forward();      // 中间眼在线上 → 直走
  else if (onLine(SEN_L)) left();         // 只有左眼在线上 → 线偏右了 → 左拐找回
  else if (onLine(SEN_R)) right();        // 只有右眼在线上 → 线偏左了 → 右拐找回
  else stopCar();                         // 三只眼都丢线 → 停（不会乱跑）
  delay(AUTO_MS);
  stopCar();                              // 每步走完必停，下一轮重新看路
}

// ---------- 车载控制页（浏览器打开小车 IP 看到的就是它）----------
String pageHTML() {
  return R"rawliteral(
<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>智能巡检小车</title>
<style>
body{font-family:微软雅黑;text-align:center;background:#faf9f6;margin:0;padding:16px}
button{width:70px;height:52px;font-size:22px;margin:4px;border:1px solid #0d6b60;
       background:#fff;border-radius:8px;color:#0d6b60}
button:active{background:#0d6b60;color:#fff}
.big{width:160px;color:#fff;background:#0d6b60}
p{color:#555}
</style></head><body>
<h2>🚗 智能巡检小车</h2>
<p id="st">传感器读取中...</p>
<div>
  <button onclick="go('w')">↑</button><br>
  <button onclick="go('a')">←</button>
  <button onclick="stop()">停</button>
  <button onclick="go('d')">→</button><br>
  <button onclick="go('s')">↓</button>
</div>
<div>
  <button class="big" onclick="toggleAuto()">自动巡线 开/关</button>
</div>
<script>
function go(d){ fetch('/move?dir='+d).then(refresh); }
function stop(){ fetch('/stop').then(refresh); }
function toggleAuto(){ fetch('/auto').then(refresh); }
function refresh(){
  fetch('/sensors').then(r=>r.json()).then(j=>{
    document.getElementById('st').innerHTML =
      '距离 ' + j.dist + 'cm ｜ 红外眼(左中右) ' +
      (j.l?'黑':'白') + ' ' + (j.c?'黑':'白') + ' ' + (j.r?'黑':'白') +
      ' ｜ ' + (j.auto ? '自动巡线中' : '手动模式');
  });
}
setInterval(refresh, 500);   // 每半秒刷新传感器
refresh();
</script></body></html>
)rawliteral";
}

// ---------- 各个网页接口（对照你写过的 Flask）----------
void handleRoot() {                        // 打开主页
  server.send(200, "text/html", pageHTML());
}
void handleMove() {                        // 访问 /move?dir=w 时执行
  autoMode = false;                        // 手动指令一来，自动巡线立刻退出
  String d = server.arg("dir");            // 取出指令字母
  if (HAS_SONAR && d == "w" && readDistance() < STOP_DIST) {   // 前方太近
    stopCar();                             // 拒绝前进——实物版的 can_stand()
    server.send(200, "application/json", "{\"ok\":false,\"why\":\"blocked\"}");
    return;
  }
  if      (d == "w") forward();
  else if (d == "s") back();
  else if (d == "a") left();
  else if (d == "d") right();
  delay(MOVE_MS);                          // 点动模式：只走 0.3 秒
  stopCar();                               // 然后必停——车永远不会跑丢
  server.send(200, "application/json",
              "{\"ok\":true,\"dir\":\"" + d + "\"}");
}
void handleStop() {                        // /stop：紧急刹车
  autoMode = false;
  stopCar();
  server.send(200, "application/json", "{\"ok\":true}");
}
void handleAuto() {                        // /auto：自动巡线开关
  autoMode = !autoMode;                    // 来一次翻转一次
  if (!autoMode) stopCar();
  server.send(200, "application/json", autoMode ? "{\"auto\":true}" : "{\"auto\":false}");
}
void handleSensors() {                     // /sensors：传感器读数
  String j = "{\"dist\":" + String(readDistance());
  j += ",\"l\":"  + String(onLine(SEN_L) ? 1 : 0);
  j += ",\"c\":"  + String(onLine(SEN_C) ? 1 : 0);
  j += ",\"r\":"  + String(onLine(SEN_R) ? 1 : 0);
  j += ",\"auto\":" + String(autoMode ? 1 : 0) + "}";
  server.send(200, "application/json", j);
}

void setup() {                             // 开机只执行一次的部分
  Serial.begin(115200);                    // 打开"和电脑对话的串口"
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);   // 六个脚都设为输出模式
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);                    // 34 脚只能输入，天生当"耳朵"
  pinMode(SEN_L, INPUT); pinMode(SEN_C, INPUT); pinMode(SEN_R, INPUT);
  stopCar();                               // 上电第一件事：确保车是停的
  WiFi.setTxPower(WIFI_POWER_11dBm);   // 发射功率减半：降低 WiFi 突发电流，防止 5V 轨被拉出凹陷（手机就在旁边，信号足够）
  WiFi.begin(ssid, pass);                  // 连 WiFi
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.print("\n小车 IP: ");
  Serial.println(WiFi.localIP());          // 打印车分到的 IP——记下它！
  server.on("/",         handleRoot);      // 登记：主页 = 控制页
  server.on("/move",     handleMove);      // 登记：移动指令
  server.on("/stop",     handleStop);      // 登记：急停
  server.on("/auto",     handleAuto);      // 登记：自动巡线开关
  server.on("/sensors",  handleSensors);   // 登记：传感器读数
  server.begin();                          // 开始营业
}

void loop() {                              // 待命循环
  server.handleClient();                   // 有访客就接待
  if (autoMode) autoFollowStep();          // 自动模式下修正一小步
  if (WiFi.status() != WL_CONNECTED) {     // 每 3 秒查一次 WiFi
    static unsigned long last = 0;
    if (millis() - last > 3000) {
      last = millis();
      WiFi.reconnect();                    // 掉线自动重连
    }
  }
}
