import os
import pygame
import numpy as np
from argparse import ArgumentParser
import ai2thor
import compress_json
from ai2thor.controller import Controller
from ai2thor.hooks.procedural_asset_hook import ProceduralAssetHookRunner

OBJATHOR_ASSETS_DIR = '/home/kaiwei/.objathor-assets/2023_09_23/assets'
HOLODECK_BASE_DATA_DIR = '/home/kaiwei/.objathor-assets/holodeck/2023_09_23'
THOR_COMMIT_ID = '3213d486cd09bcbafce33561997355983bdf8d1a'

parser = ArgumentParser()
parser.add_argument(
    "--scene",
    help="the directory of the scene to be generated",
    default=os.path.join(
        HOLODECK_BASE_DATA_DIR, "olddata/scenes/a_living_room/a_living_room.json"
    ),
)
parser.add_argument(
    "--asset_dir",
    help="the directory of the assets to be used",
    default=OBJATHOR_ASSETS_DIR,
)
args = parser.parse_args()
args.scene = "data/scenes/a_home_gym-2024-12-02-00-03-04-573112/a_home_gym_revised.json"
scene = compress_json.load(args.scene)

controller = Controller(
    commit_id=THOR_COMMIT_ID,
    agentMode="default",
    makeAgentsVisible=False,
    visibilityDistance=1.5,
    scene=scene,
    width=1024,
    height=1024,
    fieldOfView=90,
    action_hook_runner=ProceduralAssetHookRunner(
        asset_directory=OBJATHOR_ASSETS_DIR,
        asset_symlink=True,
        verbose=True,
    ),
)

# 初始化 pygame
pygame.init()
screen = pygame.display.set_mode((1024, 1024))

# 初始旋转角度、位置和步长
yaw = 0
pitch = 0  # 用于控制上下旋转
step_size = 0.25
rotate_speed = 1.0  # 旋转速度（可以调整）
initial_position = {'x': 0, 'y': 0, 'z': 0}  # 初始位置 (x, y, z)

running = True
is_resetting = False  # 标记是否正在复位

# 用来检查代理是否碰撞到物体
def check_collision():
    return controller.last_event.metadata.get('lastActionSuccess', False)

# 强制移动到新的位置
def force_move(position):
    controller.step(action="Teleport", position=position)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 获取按键状态（每一帧都获取）
    keys = pygame.key.get_pressed()

    # 处理空格键复位
    if keys[pygame.K_SPACE] and not is_resetting:  # 空格键（复位）
        is_resetting = True
        yaw = 0
        pitch = 0
        force_move(initial_position)  # 复位位置
        controller.step(action="RotateLook", rotation=yaw, horizon=pitch)  # 复位视角

    if not keys[pygame.K_SPACE]:
        is_resetting = False

    # 移动控制
    if keys[pygame.K_w]:  # W键（前进）
        controller.step({'action': 'MoveAhead', 'moveMagnitude': step_size})
        if not check_collision():
            force_move({'x': controller.last_event.metadata['agent']['position']['x'] + step_size,
                        'y': controller.last_event.metadata['agent']['position']['y'],
                        'z': controller.last_event.metadata['agent']['position']['z']})

    if keys[pygame.K_s]:  # S键（后退）
        controller.step({'action': 'MoveBack', 'moveMagnitude': step_size})
        if not check_collision():
            force_move({'x': controller.last_event.metadata['agent']['position']['x'] - step_size,
                        'y': controller.last_event.metadata['agent']['position']['y'],
                        'z': controller.last_event.metadata['agent']['position']['z']})

    if keys[pygame.K_a]:  # A键（左移）
        controller.step({'action': 'MoveLeft', 'moveMagnitude': step_size})
        if not check_collision():
            force_move({'x': controller.last_event.metadata['agent']['position']['x'],
                        'y': controller.last_event.metadata['agent']['position']['y'],
                        'z': controller.last_event.metadata['agent']['position']['z'] + step_size})

    if keys[pygame.K_d]:  # D键（右移）
        controller.step({'action': 'MoveRight', 'moveMagnitude': step_size})
        if not check_collision():
            force_move({'x': controller.last_event.metadata['agent']['position']['x'],
                        'y': controller.last_event.metadata['agent']['position']['y'],
                        'z': controller.last_event.metadata['agent']['position']['z'] - step_size})

    # 控制镜头的旋转
    if keys[pygame.K_LEFT]:  # 左箭头（镜头左旋）
        yaw -= rotate_speed
    if keys[pygame.K_RIGHT]:  # 右箭头（镜头右旋）
        yaw += rotate_speed
    if keys[pygame.K_UP]:  # 上箭头（镜头上旋）
        pitch += rotate_speed
    if keys[pygame.K_DOWN]:  # 下箭头（镜头下旋）
        pitch -= rotate_speed

    # 限制垂直旋转的范围
    pitch = max(-90, min(90, pitch))

    # 更新 AI2-THOR 视角
    controller.step({'action': 'RotateLook', 'rotation': yaw, 'horizon': pitch})

    # 获取 AI2-THOR 渲染图像
    frame = controller.last_event.frame

    # 翻转图像方向
    frame = np.flip(frame, axis=0)  # 上下翻转图像（如需要）

    # 将图像缩放为 Pygame 窗口的大小 (640, 480)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (1024, 1024))

    # 旋转图像 90 度
    frame = pygame.transform.rotate(frame, 90)  # 旋转图像90度

    # 绘制图像到 Pygame 窗口
    screen.blit(frame, (0, 0))

    # 刷新 Pygame 窗口
    pygame.display.flip()

# 停止 AI2-THOR
controller.stop()
pygame.quit()
