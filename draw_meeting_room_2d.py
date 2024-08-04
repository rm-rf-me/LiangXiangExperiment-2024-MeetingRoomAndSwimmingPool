import numpy as np
import matplotlib.pyplot as plt


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


def calculate_beam_path(position, angle, walls, max_reflections):
    beam_path = [position]
    current_position = np.array(position)
    current_angle = angle

    for _ in range(max_reflections):
        angle_rad = np.deg2rad(current_angle)
        direction = np.array([np.cos(angle_rad), np.sin(angle_rad)])
        closest_intersection = None
        closest_wall_orientation = None
        min_distance = float('inf')

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

    return beam_path


def draw_meeting_room(walls, tx_position, tx_angle, rx_position, rx_angle, max_reflections, value=None, save_path=None, tx_three=False):
    # 计算波束路径
    rx_angle = rx_angle - 180

    tx_angle = 180 - tx_angle
    tx_beam_path = calculate_beam_path(tx_position, tx_angle, walls, max_reflections)
    tx_left_beam_path = calculate_beam_path(tx_position, tx_angle - 13, walls, max_reflections)
    tx_right_beam_path = calculate_beam_path(tx_position, tx_angle + 13, walls, max_reflections)
    rx_beam_path = calculate_beam_path(rx_position, rx_angle, walls, max_reflections)

    # 创建绘图
    fig, ax = plt.subplots()

    # 绘制墙体
    for wall in walls:
        wall_start, wall_end = wall
        ax.plot([wall_start[0], wall_end[0]], [wall_start[1], wall_end[1]], 'k-', linewidth=2)

    # 绘制发射机和接收机
    ax.plot(tx_position[0], tx_position[1], 'ro', label='TX')
    ax.plot(rx_position[0], rx_position[1], 'bo', label='RX')

    # 绘制波束路径
    tx_beam_path = np.array(tx_beam_path)
    rx_beam_path = np.array(rx_beam_path)
    ax.plot(tx_beam_path[:, 0], tx_beam_path[:, 1], 'r--', label='TX Beam Path')
    ax.plot(rx_beam_path[:, 0], rx_beam_path[:, 1], 'b--', label='RX Beam Path')
    if tx_three:
        rx_left_beam_path = np.array(tx_left_beam_path)
        ax.plot(rx_left_beam_path[:, 0], rx_left_beam_path[:, 1], 'g:', label='Tx Left Beam Path')
        rx_right_beam_path = np.array(tx_right_beam_path)
        ax.plot(rx_right_beam_path[:, 0], rx_right_beam_path[:, 1], 'g-.', label='Tx Right Beam Path')

    # 设置图例和显示
    # 让图例位于画外面
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    # ax.legend()
    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    if value is not None:
        ax.set_title(f'Meeting room, Rx angle: {rx_angle}°, Tx angle: {tx_angle}°\n Value: {value}')
    else:
        ax.set_title(f'Meeting room, Rx angle: {rx_angle}°, Tx angle: {tx_angle}°')
    plt.grid()

    if save_path is not None:
        plt.savefig(save_path)

    plt.show()


def draw_meeting_room_with_angles(tx_angles, rx_angles, value=None, max_reflections=3, save_path=None, tx_three=False):
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
                      save_path=save_path, tx_three=tx_three)


if __name__ == '__main__':
    draw_meeting_room_with_angles(142, 151, tx_three=True)
