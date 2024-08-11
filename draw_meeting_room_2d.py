import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

MAX_ANGLE = 60  # 最大反射角度
MAX_REFLECTIONS = 3  # 最大反射次数
MAX_DISTANCE = 1  # 最大距离


def reflect_angle(incident_angle, wall_orientation):
    # Reflect the angle of incidence with respect to the wall's orientation
    return 2 * wall_orientation - incident_angle


def line_segment_ray_intersection(seg_start, seg_end, ray_start, ray_dir):
    x1, y1 = seg_start
    x2, y2 = seg_end
    x0, y0 = ray_start
    dx, dy = ray_dir

    # 线段方向向量
    seg_dx = x2 - x1
    seg_dy = y2 - y1

    # 解方程组求解 t 和 s
    denominator = dx * seg_dy - dy * seg_dx
    denominator = -denominator
    if denominator == 0:
        return False, None  # 平行或共线

    t = ((x0 - x1) * dy - (y0 - y1) * dx) / denominator
    s = ((x0 - x1) * seg_dy - (y0 - y1) * seg_dx) / denominator

    # 判断 t 和 s 是否满足条件
    if 0 <= t <= 1 and s > 0:
        # 计算交点坐标
        intersection_x = x1 + t * seg_dx
        intersection_y = y1 + t * seg_dy
        return True, (intersection_x, intersection_y)

    return False, None

def point_line_distance(point, line_start, line_dir):
    point = np.array(point)
    line_start = np.array(line_start)
    line_dir = np.array(line_dir)
    line_dir = line_dir / np.linalg.norm(line_dir)  # 归一化方向向量

    vec_line_to_point = point - line_start
    projection_length = np.dot(vec_line_to_point, line_dir)
    projection = projection_length * line_dir

    perpendicular_vec = vec_line_to_point - projection
    return np.linalg.norm(perpendicular_vec), projection_length


def check_point_in_path(point, point_dir, ray_start, ray_dir, max_distance, max_angle):
    # 计算点到射线的距离和投影长度
    distance, projection_length = point_line_distance(point, ray_start, ray_dir)

    if distance > max_distance:
        return False, None, None, None  # 如果距离超出范围

    # 计算射线方向和点方向向量的夹角
    point_dir = np.array(point_dir)
    point_dir = point_dir / np.linalg.norm(point_dir)  # 归一化方向向量

    ray_dir = np.array(ray_dir)
    ray_dir = ray_dir / np.linalg.norm(ray_dir)  # 归一化方向向量

    # dot_product = np.dot(ray_dir, point_dir)
    # angle = np.arccos(dot_product)  # 夹角（弧度）
    #
    # max_angle_rad = np.deg2rad(max_angle/2)
    #
    # if angle > max_angle_rad:
    #     return False, None, None, None  # 如果角度超出范围

    # 计算圆和射线的交点
    d = np.sqrt(max_distance ** 2 - distance ** 2)  # 计算从投影点到交点的距离
    intersection_point = ray_start + (projection_length - d) * ray_dir

    point_to_intersection = intersection_point - point
    point_to_intersection_dir = point_to_intersection / np.linalg.norm(point_to_intersection)  # 归一化方向向量

    angle = np.arccos(np.dot(point_dir, point_to_intersection_dir))  # 夹角（弧度）

    if angle > np.deg2rad(max_angle/2):
        return False, None, None, None  # 如果角度超出范围

    return True, distance, np.rad2deg(angle), intersection_point


def calculate_beam_path(position, angle, walls, max_reflections, point_info=None):
    beam_path = [position]
    current_position = np.array(position)
    current_angle = angle

    for _ in range(max_reflections):
        angle_rad = np.deg2rad(current_angle)
        direction = np.array([np.cos(angle_rad), np.sin(angle_rad)])
        closest_intersection = None
        closest_wall_orientation = None
        min_distance = float('inf')

        if point_info is not None:
            point_angle_rad = np.deg2rad(point_info['rx_angle'])
            point_direction = np.array([np.cos(point_angle_rad), np.sin(point_angle_rad)])
            res, distance, angle, intersection_point = check_point_in_path(point_info['rx_position'], point_direction, current_position, direction,
                                      MAX_DISTANCE,
                                      MAX_ANGLE)
            if res:
                # print('Point in beam path')
                beam_path.append(intersection_point)
                return beam_path, True

        for wall in walls:
            wall_start, wall_end = wall
            intersects, intersection_point = line_segment_ray_intersection(wall_start, wall_end, current_position,
                                                                           direction)

            if intersects:
                distance = np.linalg.norm(np.array(intersection_point) - current_position)
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = intersection_point
                    closest_wall_orientation = np.arctan2(wall_end[1] - wall_start[1], wall_end[0] - wall_start[0])

        if closest_intersection is None:
            break

        beam_path.append(closest_intersection)
        current_position = np.array(closest_intersection)
        current_angle = reflect_angle(current_angle, np.degrees(closest_wall_orientation))

    return beam_path, False


def draw_meeting_room(walls, tx_position, tx_angle, rx_position, rx_angle, max_reflections, value=None, save_path=None,
                      tx_three=False, draw_rx_beam=True, check_rx_in_tx_beam=True):
    # 计算波束路径
    rx_angle = rx_angle - 180

    tx_angle = 180 - tx_angle

    if check_rx_in_tx_beam:
        point_info = {'rx_position': rx_position, 'rx_angle': rx_angle}
    else:
        point_info = None

    tx_beam_path, res_tx_main = calculate_beam_path(tx_position, tx_angle, walls, max_reflections, point_info)
    tx_left_beam_path, res_tx_left = calculate_beam_path(tx_position, tx_angle - 13, walls, max_reflections, point_info)
    tx_right_beam_path, res_tx_right = calculate_beam_path(tx_position, tx_angle + 13, walls, max_reflections, point_info)

    rx_beam_path, _ = calculate_beam_path(rx_position, rx_angle, walls, max_reflections)

    # 创建绘图
    fig, ax = plt.subplots()

    # 绘制墙体
    for wall in walls:
        wall_start, wall_end = wall
        ax.plot([wall_start[0], wall_end[0]], [wall_start[1], wall_end[1]], 'k-', linewidth=2)

    # 绘制发射机和接收机
    ax.plot(tx_position[0], tx_position[1], 'ro', label='TX')
    ax.plot(rx_position[0], rx_position[1], 'bo', label='RX')

    if check_point_in_path:
        # 计算扇形的角度范围
        theta1 = rx_angle - MAX_ANGLE / 2
        theta2 = rx_angle + MAX_ANGLE / 2

        # 画扇形
        wedge = Wedge(center=rx_position, r=MAX_DISTANCE, theta1=theta1, theta2=theta2, color='b', fill=False)
        ax.add_patch(wedge)

    # 绘制波束路径
    tx_beam_path = np.array(tx_beam_path)
    rx_beam_path = np.array(rx_beam_path)
    if check_rx_in_tx_beam and res_tx_main:
        ax.plot(tx_beam_path[:, 0], tx_beam_path[:, 1], 'r', label='TX Beam Path Pass Rx', linewidth=3)
    else:
        ax.plot(tx_beam_path[:, 0], tx_beam_path[:, 1], 'r--', label='TX Beam Path')
    if draw_rx_beam:
        ax.plot(rx_beam_path[:, 0], rx_beam_path[:, 1], 'b--', label='RX Beam Path')
    if tx_three:
        rx_left_beam_path = np.array(tx_left_beam_path)
        if check_rx_in_tx_beam and res_tx_left:
            ax.plot(rx_left_beam_path[:, 0], rx_left_beam_path[:, 1], 'm', label='Tx Left Beam Path Pass Rx', linewidth=3)
        else:
            ax.plot(rx_left_beam_path[:, 0], rx_left_beam_path[:, 1], 'm:', label='Tx Left Beam Path')
        rx_right_beam_path = np.array(tx_right_beam_path)
        if check_rx_in_tx_beam and res_tx_right:
            ax.plot(rx_right_beam_path[:, 0], rx_right_beam_path[:, 1], 'g', label='Tx Right Beam Path Pass Rx', linewidth=3)
        else:
            ax.plot(rx_right_beam_path[:, 0], rx_right_beam_path[:, 1], 'g-.', label='Tx Right Beam Path')

    # 设置图例和显示
    # 让图例位于画外面
    ax.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0.)
    # ax.legend()
    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    if value is not None:
        ax.set_title(f'Meeting room, Rx angle: {rx_angle}°, Tx angle: {tx_angle}°\n Value: {value}')
    else:
        ax.set_title(f'Meeting room, Rx angle: {rx_angle}°, Tx angle: {tx_angle}°')
    plt.grid()
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path)

    plt.show()


def draw_meeting_room_with_angles(tx_angles, rx_angles, value=None, max_reflections=3, save_path=None, tx_three=False,
                                  draw_rx_beam=True, check_rx_in_tx_beam=True):
    walls = [
        [(0, 0), (6.93, 0)],
        [(6.93, 0), (6.93, 7.69)],
        [(6.93, 7.69), (0, 7.69)],
        [(0, 7.69), (0, 5.63)],
        [(0, 5.63), (-0.6, 5.63)],
        [(-0.6, 5.63), (-0.6, 2.1)],
        [(-0.6, 2.1), (0, 2.1)],
        [(0, 2.1), (0, 0)],
    ]

    # 发射机和接收机的位置 (x, y)
    tx_position = (3.145, 2.05)
    rx_position = (3.145, 5.86)

    draw_meeting_room(walls, tx_position, tx_angles, rx_position, rx_angles, max_reflections, value=value,
                      save_path=save_path, tx_three=tx_three, draw_rx_beam=draw_rx_beam, check_rx_in_tx_beam=True)


if __name__ == '__main__':
    draw_meeting_room_with_angles(92, 90, max_reflections=2, tx_three=True, draw_rx_beam=False,
                                  check_rx_in_tx_beam=True)
