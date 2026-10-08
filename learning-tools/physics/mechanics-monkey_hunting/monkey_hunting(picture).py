import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage
from matplotlib.offsetbox import AnnotationBbox
#初期パラメータ
dt=0.01
#ボールの初速
ball_v = 300
#開始位置
monkey_x_initial=100
monkey_y_initial=100
ball_angle_deg = 45

(fig, ax) = plt.subplots(1,1)  # (1,1)は省略して　plt.subplots() でも可
img_ball = plt.imread("ball.png")
ball_box = OffsetImage(img_ball, zoom=0.03)
ball = AnnotationBbox(
    ball_box,
    (0, 0),
    frameon=False
)

img_monkey = plt.imread("monkey.png")

monkey_box = OffsetImage(img_monkey, zoom=0.03)

monkey = AnnotationBbox(
    monkey_box,
    (0, 0),
    frameon=False
)
plt.rcParams["font.family"] = "Meiryo"
ax.add_artist(ball)
ax.add_artist(monkey)
x=0
y=0

time_text = ax.text(0.05, 0.95, '', transform=ax.transAxes)
distance_text = ax.text(0.05, 0.90, '', transform=ax.transAxes)
plt.xlim(0, 105)
plt.ylim(0, 105)
plt.xlabel("x")
plt.ylabel("y")

def update(frame):
    time =frame*dt
    ball_angle_rad = ball_angle_deg/180 *np.pi
    rakka=0.5*9.8*time**2
    length = time*ball_v
    ball_x = length*np.cos(ball_angle_rad)
    ball_y = length*np.sin(ball_angle_rad)-rakka
    monkey_y=monkey_y_initial-rakka
    ball.xy = (ball_x, ball_y)
    monkey.xy = (monkey_x_initial, monkey_y)
    ball.xybox = (ball_x, ball_y)
    monkey.xybox = (monkey_x_initial, monkey_y)
    distance = np.sqrt((ball_x-monkey_x_initial)**2+(ball_y-monkey_y)**2)

    time_text.set_text(f'time = {time:.2f}')
    distance_text.set_text(f'距離 = {distance:.2f}')
    if distance <= 1:
        ani.event_source.stop()

ani = FuncAnimation(
    fig,
    update,          #関数名
    frames=200,      # 100種類 0から99まで１ずつ変える
    interval=50     # 100ms = 0.1秒間隔
)
plt.show()
