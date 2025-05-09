import numpy as np
import pandas as pd
import os
from scipy.optimize import least_squares
from sklearn.cluster import KMeans
from draw_meeting_room_2d import calculate_beam_path, line_segment_ray_intersection, draw_meeting_room_with_angles
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from tqdm import tqdm
import matplotlib

# 常量定义
FREQUENCY = 140e9  # 140GHz
C = 3e8  # 光速
WAVELENGTH = C / FREQUENCY

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

def shifting_angle(df, angle200_bias, angle300_bias, reverse=False):
    """
    对角度进行偏移校正
    
    Args:
        df: 数据DataFrame
        angle200_bias: angle200的偏移量
        angle300_bias: angle300的偏移量
        reverse: 是否反向
        
    Returns:
        处理后的DataFrame
    """
    tmp = 1
    if reverse:
        tmp = -1
    df['angle200'] = df['angle200'] * tmp + angle200_bias
    df['angle300'] = df['angle300'] * tmp + angle300_bias
    return df

def load_and_preprocess_data(file_path, value_min=-39):
    """
    加载并预处理测量数据
    
    Args:
        file_path: Excel文件路径
        value_min: 信号强度阈值
        
    Returns:
        处理后的DataFrame
    """
    df = pd.read_excel(file_path)
    print(f"原始数据采样点数量: {len(df)}")
    df = df.loc[df['value'] > value_min]
    print(f"过滤后数据采样点数量: {len(df)}")
    df = df.reset_index(drop=True)
    return df

def calculate_antenna_gain(angle, is_tx=True):
    """
    计算天线方向图增益
    
    Args:
        angle: 角度（度）
        is_tx: 是否为发射天线
        
    Returns:
        天线增益值（dB）
    """
    # 这里使用简化的天线方向图模型
    # 主瓣增益为0dB，旁瓣增益为-13dB
    if abs(angle) <= 13:
        return 0
    else:
        return -13

def calculate_fspl(distance, frequency=FREQUENCY):
    """
    计算自由空间路径损耗
    
    Args:
        distance: 传播距离（米）
        frequency: 频率（Hz）
        
    Returns:
        路径损耗（dB）
    """
    wavelength = C / frequency
    return 20 * np.log10(4 * np.pi * distance / wavelength)

def calculate_fresnel_coefficient(epsilon, incident_angle):
    """
    计算菲涅耳反射系数
    
    Args:
        epsilon: 介电常数
        incident_angle: 入射角（度）
        
    Returns:
        反射系数
    """
    # 将角度转换为弧度
    theta_i = np.deg2rad(incident_angle)
    
    # 计算折射角
    n1 = 1  # 空气折射率
    n2 = np.sqrt(epsilon)  # 介质折射率
    sin_theta_t = n1 * np.sin(theta_i) / n2
    cos_theta_t = np.sqrt(1 - sin_theta_t**2)
    
    # 计算反射系数
    r_parallel = (n2 * np.cos(theta_i) - n1 * cos_theta_t) / (n2 * np.cos(theta_i) + n1 * cos_theta_t)
    r_perpendicular = (n1 * np.cos(theta_i) - n2 * cos_theta_t) / (n1 * np.cos(theta_i) + n2 * cos_theta_t)
    
    # 返回平均反射系数
    return (abs(r_parallel)**2 + abs(r_perpendicular)**2) / 2

def get_wall_info():
    """
    获取会议室墙壁信息
    
    Returns:
        walls: 墙壁列表，每个元素为((x1,y1), (x2,y2))
        wall_normals: 墙壁法向量列表
    """
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
    
    # 计算每个墙壁的法向量
    wall_normals = []
    for wall in walls:
        dx = wall[1][0] - wall[0][0]
        dy = wall[1][1] - wall[0][1]
        length = np.sqrt(dx*dx + dy*dy)
        # 法向量指向墙壁内部
        normal = (-dy/length, dx/length)
        wall_normals.append(normal)
    
    return walls, wall_normals

def check_rx_reception(path_points, rx_position, rx_angle, max_distance=1, max_angle=60):
    """
    检查路径是否被RX正确接收
    
    Args:
        path_points: 路径点列表
        rx_position: RX位置
        rx_angle: RX角度
        max_distance: 最大接收距离
        max_angle: 最大接收角度
        
    Returns:
        bool: 是否被正确接收
    """
    if len(path_points) < 2:
        return False
        
    # 获取最后一段路径
    last_point = path_points[-2]
    rx_point = path_points[-1]
    
    # 计算最后一段路径的方向
    path_dir = np.array(rx_point) - np.array(last_point)
    path_dir = path_dir / np.linalg.norm(path_dir)
    
    # 计算RX的指向方向
    rx_dir = np.array([np.cos(np.deg2rad(rx_angle)), np.sin(np.deg2rad(rx_angle))])
    
    # 计算路径方向与RX指向的夹角
    # angle = np.arccos(np.abs(np.dot(path_dir, rx_dir)))
    angle = np.arccos(np.dot(path_dir, rx_dir))
    angle = np.rad2deg(angle)
    
    # 计算RX到路径的距离
    distance = np.linalg.norm(np.array(rx_point) - np.array(rx_position))
    
    # 打印调试信息
    # print(f"  接收检查:")
    # print(f"    距离: {distance:.3f}m (阈值: {max_distance}m)")
    # print(f"    角度: {angle:.1f}° (阈值: {max_angle/2}°)")
    
    return distance <= max_distance and np.abs(180-angle) <= max_angle/2

def plot_signal_path(paths, tx_angle, rx_angle, value=None, save_path=None, is_main_lobe=True):
    """
    根据计算好的paths绘制传播路径
    
    Args:
        paths: 路径信息列表，每个元素是一个字典，包含path_points, wall_indices, incident_angles等
        tx_angle: 发射角度（0度指向x轴正方向，逆时针为正）
        rx_angle: 接收角度（0度指向x轴正方向，逆时针为正）
        value: 信号强度值
        save_path: 图片保存路径
        is_main_lobe: 是否为主瓣
    """
    walls, _ = get_wall_info()
    tx_position = (3.145, 2.05)
    rx_position = (3.145, 5.86)
    
    # 创建绘图
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 绘制墙体
    for i, wall in enumerate(walls):
        wall_start, wall_end = wall
        # 加粗、加深色
        ax.plot([wall_start[0], wall_end[0]], [wall_start[1], wall_end[1]], color='black', linewidth=4, zorder=2)
        # 墙体端点
        ax.scatter([wall_start[0], wall_end[0]], [wall_start[1], wall_end[1]], color='black', s=40, zorder=3)
        # 计算墙面中点位置
        mid_x = (wall_start[0] + wall_end[0]) / 2
        mid_y = (wall_start[1] + wall_end[1]) / 2
        # 计算墙面方向向量
        dx = wall_end[0] - wall_start[0]
        dy = wall_end[1] - wall_start[1]
        wall_angle = np.arctan2(dy, dx)
        text_angle = np.rad2deg(wall_angle)
        if text_angle > 90 or text_angle < -90:
            text_angle += 180
        # 添加墙面编号标注，使用红色加粗字体
        ax.text(mid_x, mid_y, f'W{i+1}', 
                rotation=text_angle,
                ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                color='red', fontweight='bold', fontsize=12, zorder=4)
    
    # 绘制发射机和接收机
    ax.plot(tx_position[0], tx_position[1], 'ro', label='TX')
    ax.plot(rx_position[0], rx_position[1], 'bo', label='RX')
    
    # 绘制TX的主瓣和旁瓣
    tx_main_angle = tx_angle
    tx_left_angle = tx_angle - 13
    tx_right_angle = tx_angle + 13
    
    # TX主瓣
    tx_main_dir = np.array([np.cos(np.deg2rad(tx_main_angle)), np.sin(np.deg2rad(tx_main_angle))])
    ax.arrow(tx_position[0], tx_position[1], 
             tx_main_dir[0]*0.5, tx_main_dir[1]*0.5,
             head_width=0.1, head_length=0.2, fc='r', ec='r', label='TX Main Lobe')
    
    # TX左旁瓣
    tx_left_dir = np.array([np.cos(np.deg2rad(tx_left_angle)), np.sin(np.deg2rad(tx_left_angle))])
    ax.arrow(tx_position[0], tx_position[1], 
             tx_left_dir[0]*0.3, tx_left_dir[1]*0.3,
             head_width=0.1, head_length=0.2, fc='r', ec='r', alpha=0.3, label='TX Side Lobe')
    
    # TX右旁瓣
    tx_right_dir = np.array([np.cos(np.deg2rad(tx_right_angle)), np.sin(np.deg2rad(tx_right_angle))])
    ax.arrow(tx_position[0], tx_position[1], 
             tx_right_dir[0]*0.3, tx_right_dir[1]*0.3,
             head_width=0.1, head_length=0.2, fc='r', ec='r', alpha=0.3)
    
    # 绘制RX的主瓣和旁瓣
    rx_main_angle = rx_angle
    rx_left_angle = rx_angle - 13
    rx_right_angle = rx_angle + 13
    
    # RX主瓣
    rx_main_dir = np.array([np.cos(np.deg2rad(rx_main_angle)), np.sin(np.deg2rad(rx_main_angle))])
    ax.arrow(rx_position[0], rx_position[1],
             rx_main_dir[0]*0.5, rx_main_dir[1]*0.5,
             head_width=0.1, head_length=0.2, fc='b', ec='b', label='RX Main Lobe')
    
    # RX左旁瓣
    rx_left_dir = np.array([np.cos(np.deg2rad(rx_left_angle)), np.sin(np.deg2rad(rx_left_angle))])
    ax.arrow(rx_position[0], rx_position[1],
             rx_left_dir[0]*0.3, rx_left_dir[1]*0.3,
             head_width=0.1, head_length=0.2, fc='b', ec='b', alpha=0.3, label='RX Side Lobe')
    
    # RX右旁瓣
    rx_right_dir = np.array([np.cos(np.deg2rad(rx_right_angle)), np.sin(np.deg2rad(rx_right_angle))])
    ax.arrow(rx_position[0], rx_position[1],
             rx_right_dir[0]*0.3, rx_right_dir[1]*0.3,
             head_width=0.1, head_length=0.2, fc='b', ec='b', alpha=0.3)
    
    # 绘制TX和RX的坐标和角度标注
    ax.annotate(f'TX: ({tx_position[0]:.2f}, {tx_position[1]:.2f})\n{tx_angle:.1f}°',
                (tx_position[0], tx_position[1]),
                xytext=(10, 10),
                textcoords='offset points')
    ax.annotate(f'RX: ({rx_position[0]:.2f}, {rx_position[1]:.2f})\n{rx_angle:.1f}°',
                (rx_position[0], rx_position[1]),
                xytext=(10, 10),
                textcoords='offset points')
    
    # 为每条路径使用不同的颜色
    colors = ['r', 'g', 'b', 'c', 'm', 'y']
    
    # 绘制所有路径
    for i, path in enumerate(paths):
        path_points = np.array(path['path_points'])
        wall_indices = path['wall_indices']
        incident_angles = path['incident_angles']
        
        # 选择颜色
        color = colors[i % len(colors)]
        
        # 绘制路径
        ax.plot(path_points[:, 0], path_points[:, 1], f'{color}--', 
                label=f'Path {i+1}', alpha=0.7)
        
        # 在反射点处标记墙面编号和入射角
        for j, (point, wall_idx, angle) in enumerate(zip(path_points[1:-1], wall_indices, incident_angles)):
            ax.plot(point[0], point[1], f'{color}o', alpha=0.7)  # 反射点
            ax.annotate(f'W{wall_idx+1}\n{angle:.1f}°', 
                       (point[0], point[1]),
                       xytext=(5, 5),
                       textcoords='offset points',
                       color=color)
    
    # 设置图例和显示
    ax.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0.)
    ax.set_aspect('equal')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    
    # 设置标题
    title = f'TX: {tx_angle:.1f}°, RX: {rx_angle:.1f}°'
    if value is not None:
        title += f'\nValue: {value:.1f} dB'
    # title += f'\n{"Main Lobe" if is_main_lobe else "Side Lobe"}'
    title += f'\nTotal Paths: {len(paths)}'
    ax.set_title(title)
    
    plt.grid(True)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.close()

def check_point_in_path(point, point_dir, ray_start, ray_dir, max_distance, max_angle):
    """
    判断点是否在射线路径上，且距离和角度都在阈值内
    """
    def point_line_distance(point, line_start, line_dir):
        point = np.array(point)
        line_start = np.array(line_start)
        line_dir = np.array(line_dir)
        line_dir = line_dir / np.linalg.norm(line_dir)
        vec_line_to_point = point - line_start
        projection_length = np.dot(vec_line_to_point, line_dir)
        projection = projection_length * line_dir
        perpendicular_vec = vec_line_to_point - projection
        return np.linalg.norm(perpendicular_vec), projection_length

    distance, projection_length = point_line_distance(point, ray_start, ray_dir)
    if distance > max_distance:
        return False, None, None, None
    point_dir = np.array(point_dir)
    point_dir = point_dir / np.linalg.norm(point_dir)
    ray_dir = np.array(ray_dir)
    ray_dir = ray_dir / np.linalg.norm(ray_dir)
    d = np.sqrt(max_distance ** 2 - distance ** 2)
    intersection_point = ray_start + (projection_length - d) * ray_dir
    point_to_intersection = intersection_point - point
    point_to_intersection_dir = point_to_intersection / np.linalg.norm(point_to_intersection)
    angle = np.arccos(np.dot(point_dir, point_to_intersection_dir))
    if angle > np.deg2rad(max_angle/2):
        return False, None, None, None
    return True, distance, np.rad2deg(angle), intersection_point

def calculate_single_path(tx_angle, rx_angle, max_reflections=3):
    """
    计算单条传播路径
    
    Args:
        tx_angle: 发射角度
        rx_angle: 接收角度
        max_reflections: 最大反射次数
        
    Returns:
        path_info: 路径信息字典，包含路径点、墙面编号、入射角等
    """
    walls, wall_normals = get_wall_info()
    tx_position = (3.145, 2.05)
    rx_position = (3.145, 5.86)
    max_distance = 1
    max_angle = 60
    
    path_points = [tx_position]
    wall_indices = []
    incident_angles = []
    current_position = np.array(tx_position)
    current_angle = tx_angle
    
    for reflection in range(max_reflections+1):
        angle_rad = np.deg2rad(current_angle)
        direction = np.array([np.cos(angle_rad), np.sin(angle_rad)])
        
        # 检查是否可以直接到达RX
        rx_angle_rad = np.deg2rad(rx_angle)
        rx_dir = np.array([np.cos(rx_angle_rad), np.sin(rx_angle_rad)])
        res, distance, angle, intersection_point = check_point_in_path(
            rx_position, rx_dir, current_position, direction, max_distance, max_angle)
        
        if res:
            # 找到有效路径，直接连接到RX
            path_points.append(rx_position)
            return {
                'path_points': path_points,
                'wall_indices': wall_indices,
                'incident_angles': incident_angles,
                'total_distance': calculate_total_distance(path_points)
            }
        
        # 没到达RX则找最近的墙反射
        closest_intersection = None
        closest_wall_orientation = None
        min_distance = float('inf')
        closest_wall_idx = None
        
        for j, wall in enumerate(walls):
            wall_start, wall_end = wall
            intersects, intersection = line_segment_ray_intersection(
                wall_start, wall_end, current_position, direction)
            
            if intersects:
                d = np.linalg.norm(np.array(intersection) - current_position)
                if d < min_distance:
                    min_distance = d
                    closest_intersection = intersection
                    closest_wall_orientation = np.arctan2(wall_end[1] - wall_start[1], wall_end[0] - wall_start[0])
                    closest_wall_idx = j
        
        if closest_intersection is None:
            return None
            
        path_points.append(closest_intersection)
        wall_indices.append(closest_wall_idx)
        
        # 计算入射角
        normal = wall_normals[closest_wall_idx]
        incident_angle = np.arccos(np.abs(np.dot(direction, normal)))
        incident_angles.append(np.rad2deg(incident_angle))
        
        current_position = np.array(closest_intersection)
        current_angle = 2 * np.degrees(closest_wall_orientation) - current_angle
    
    return None

def calculate_total_distance(path_points):
    """
    计算路径总长度
    
    Args:
        path_points: 路径点列表
        
    Returns:
        total_distance: 总长度（米）
    """
    total_distance = 0
    for i in range(len(path_points) - 1):
        total_distance += np.linalg.norm(np.array(path_points[i+1]) - np.array(path_points[i]))
    return total_distance

def calculate_paths_for_angle_pair(tx_angle, rx_angle, max_reflections=3):
    """
    计算特定tx-rx角度对下的所有可能路径
    
    Args:
        tx_angle: 发射角度
        rx_angle: 接收角度
        max_reflections: 最大反射次数
        
    Returns:
        paths: 包含主瓣和副瓣的所有有效路径列表
        path_powers: 每条路径的功率贡献
    """
    # 计算三个瓣的方向
    tx_angles = [tx_angle, tx_angle - 13, tx_angle + 13]
    paths = []
    path_powers = []
    
    # 对每个瓣计算路径
    for i, angle in enumerate(tx_angles):
        # 计算该瓣的路径
        path = calculate_single_path(angle, rx_angle, max_reflections)
        if path is not None:
            paths.append(path)
            # 计算该路径的功率贡献
            is_main_lobe = (i == 0)
            power = calculate_path_power(path, is_main_lobe)
            path_powers.append(power)
    
    return paths, path_powers

def calculate_path_power(path, is_main_lobe):
    """
    计算单条路径的功率贡献
    
    Args:
        path: 路径信息
        is_main_lobe: 是否为主瓣
        
    Returns:
        power: 功率贡献（dB）
    """
    # 计算天线增益
    gain = calculate_antenna_gain(0) if is_main_lobe else calculate_antenna_gain(13)
    
    # 计算FSPL
    fspl = calculate_fspl(path['total_distance'])
    
    # 计算反射损耗（这里暂时使用默认介电常数，后续会在方程组中求解）
    reflection_loss = 0
    for incident_angle in path['incident_angles']:
        r = calculate_fresnel_coefficient(4.0, incident_angle)  # 使用默认介电常数4.0
        reflection_loss += -10 * np.log10(r)
    
    return gain - fspl - reflection_loss

def build_equation_system(measurements, all_paths):
    """
    构建完整的方程组
    
    Args:
        measurements: 测量数据DataFrame
        all_paths: 所有tx-rx角度对对应的路径信息字典
        
    Returns:
        equations: 方程组列表，每个元素对应一个tx-rx角度对
        constants: 常数项列表
    """
    equations = []
    constants = []
    
    # 对每个tx-rx角度对
    for _, row in measurements.iterrows():
        tx_angle = row['angle200']
        rx_angle = row['angle300']
        measured_power = row['value']
        
        # 使用原始角度值查找路径
        key = (tx_angle, rx_angle)
        if key not in all_paths:
            continue
            
        # 获取该角度对下的所有路径
        paths, path_powers = all_paths[key]
        
        # 构建该角度对的方程
        equation = []
        constant = measured_power
        
        # 计算已知参数
        tx_gain = calculate_antenna_gain(0)  # 主瓣增益
        rx_gain = calculate_antenna_gain(0)  # 主瓣增益
        
        # 对每条路径
        for path, power in zip(paths, path_powers):
            # 计算FSPL
            fspl = calculate_fspl(path['total_distance'])
            
            # 构建反射项
            reflection_terms = []
            for wall_idx, incident_angle in zip(path['wall_indices'], path['incident_angles']):
                reflection_terms.append((wall_idx, incident_angle))
            
            equation.append((reflection_terms, power))
            constant -= (tx_gain + rx_gain + fspl + power)
        
        equations.append(equation)
        constants.append(constant)
    
    return equations, constants

def objective_function(epsilons, equations, constants):
    """
    目标函数：计算预测功率与实际功率的误差
    
    Args:
        epsilons: 各墙面的介电常数
        equations: 方程组
        constants: 常数项
        
    Returns:
        errors: 误差向量
    """
    errors = []
    for eq, const in zip(equations, constants):
        predicted_power = const
        for reflection_terms, power in eq:
            # 计算反射损耗
            reflection_loss = 0
            for wall_idx, incident_angle in reflection_terms:
                r = calculate_fresnel_coefficient(epsilons[wall_idx], incident_angle)
                reflection_loss += -10 * np.log10(r)
            predicted_power += reflection_loss
        errors.append(predicted_power)
    return errors

def estimate_wall_parameters(equations, constants, initial_guess=None):
    """
    估计墙面参数
    
    Args:
        equations: 方程组
        constants: 常数项
        initial_guess: 初始猜测值
        
    Returns:
        estimated_epsilons: 估计的介电常数
    """
    n_walls = 8  # 会议室墙壁数量
    if initial_guess is None:
        initial_guess = np.ones(n_walls) * 4  # 假设初始介电常数为4
    
    # 使用Levenberg-Marquardt算法求解
    result = least_squares(
        objective_function,
        initial_guess,
        args=(equations, constants),
        method='trf',
        bounds=(1, 20)  # 介电常数范围
    )
    
    return result.x

def cluster_similar_surfaces(estimated_epsilons, n_clusters=3):
    """
    对相似表面进行聚类
    
    Args:
        estimated_epsilons: 估计的介电常数
        n_clusters: 聚类数量
        
    Returns:
        labels: 聚类标签
    """
    # 将介电常数转换为二维特征
    features = np.column_stack((estimated_epsilons, np.zeros_like(estimated_epsilons)))
    
    # 使用K-means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(features)
    
    return labels

def identify_material_type(epsilon):
    """
    根据介电常数判断材料类型
    
    Args:
        epsilon: 介电常数
        
    Returns:
        material_type: 材料类型
    """
    if epsilon < 2:
        return "空气"
    elif epsilon < 3:
        return "木材"
    elif epsilon < 5:
        return "石膏板"
    elif epsilon < 8:
        return "混凝土"
    else:
        return "金属"

def evaluate_fitting_error(estimated_epsilons, data, all_paths):
    """
    评估拟合误差
    
    Args:
        estimated_epsilons: 估计的介电常数
        data: 测量数据
        all_paths: 所有路径信息
        
    Returns:
        mse: 均方误差
    """
    total_error = 0
    count = 0
    
    for _, row in data.iterrows():
        tx_angle = row['angle200']
        rx_angle = row['angle300']
        measured_power = row['value']
        
        # 获取该角度对下的所有路径
        if (tx_angle, rx_angle) in all_paths:
            paths, path_powers = all_paths[(tx_angle, rx_angle)]
            
            # 计算预测功率
            predicted_power = float('-inf')
            for path, power in zip(paths, path_powers):
                # 计算反射损耗
                reflection_loss = 0
                for wall_idx, incident_angle in zip(path['wall_indices'], path['incident_angles']):
                    r = calculate_fresnel_coefficient(estimated_epsilons[wall_idx], incident_angle)
                    reflection_loss += -10 * np.log10(r)
                
                # 计算总功率
                total_power = power + reflection_loss
                predicted_power = max(predicted_power, total_power)
            
            # 计算误差
            error = (predicted_power - measured_power) ** 2
            total_error += error
            count += 1
    
    return total_error / count if count > 0 else float('inf')

def preprocess_data(data, tx_threshold=1, rx_threshold=1, value_threshold=1):
    """
    预处理数据，去除相似的数据点
    
    Args:
        data: 原始数据DataFrame
        tx_threshold: TX角度阈值（度）
        rx_threshold: RX角度阈值（度）
        value_threshold: 信号强度阈值（dB）
        
    Returns:
        filtered_data: 筛选后的数据DataFrame
    """
    
    # 创建新的列用于分组
    data['tx_group'] = (data['angle200'] / tx_threshold).round() * tx_threshold
    data['rx_group'] = (data['angle300'] / rx_threshold).round() * rx_threshold
    data['value_group'] = (data['value'] / value_threshold).round() * value_threshold
    
    # 按三个维度分组并选择第一个数据点
    filtered_data = data.groupby(['tx_group', 'rx_group', 'value_group']).first().reset_index()
    
    # 删除临时分组列
    filtered_data = filtered_data.drop(['tx_group', 'rx_group', 'value_group'], axis=1)
    
    print(f"筛选后数据量：{len(filtered_data)}")
    print(f"减少数据量：{len(data) - len(filtered_data)}")
    print(f"数据减少比例：{(len(data) - len(filtered_data)) / len(data) * 100:.2f}%")
    
    return filtered_data

def analyze_paths(all_paths):
    """
    分析路径统计信息
    
    Args:
        all_paths: 所有路径信息字典
        
    Returns:
        stats: 统计信息字典
    """
    total_paths = 0
    wall_stats = {i: {'count': 0, 'positions': [], 'angles': []} for i in range(8)}  # 8面墙
    
    for (tx_angle, rx_angle), (paths, _) in all_paths.items():
        total_paths += len(paths)
        for path in paths:
            for wall_idx, incident_angle in zip(path['wall_indices'], path['incident_angles']):
                wall_stats[wall_idx]['count'] += 1
                wall_stats[wall_idx]['angles'].append(incident_angle)
                # 获取反射点位置
                reflection_point = path['path_points'][path['wall_indices'].index(wall_idx) + 1]
                wall_stats[wall_idx]['positions'].append(reflection_point)
    
    # 计算平均值
    avg_paths = total_paths / len(all_paths) if all_paths else 0
    
    # 计算每面墙的统计信息
    for wall_idx in wall_stats:
        if wall_stats[wall_idx]['count'] > 0:
            wall_stats[wall_idx]['avg_angle'] = np.mean(wall_stats[wall_idx]['angles'])
            wall_stats[wall_idx]['std_angle'] = np.std(wall_stats[wall_idx]['angles'])
            wall_stats[wall_idx]['min_angle'] = np.min(wall_stats[wall_idx]['angles'])
            wall_stats[wall_idx]['max_angle'] = np.max(wall_stats[wall_idx]['angles'])
    
    return {
        'total_paths': total_paths,
        'avg_paths': avg_paths,
        'wall_stats': wall_stats
    }

def plot_wall_reflectivity(estimated_epsilons):
    """
    绘制每面墙的反射率随入射角变化的曲线
    
    Args:
        estimated_epsilons: 估计的介电常数列表
    """
    # 创建入射角范围
    incident_angles = np.linspace(0, 89, 180)  # 0-89度，步长0.5度
    
    # 创建图形
    plt.figure(figsize=(15, 10))
    
    # 为每面墙绘制曲线
    for i, epsilon in enumerate(estimated_epsilons):
        # 计算反射率
        reflectivities = [calculate_fresnel_coefficient(epsilon, angle) for angle in incident_angles]
        
        # 绘制曲线
        plt.plot(incident_angles, reflectivities, 
                label=f'Wall {i+1} (ε={epsilon:.2f})',
                linewidth=2)
    
    # 设置图形属性
    plt.xlabel('入射角 (度)')
    plt.ylabel('反射率')
    plt.title('墙面反射率随入射角的变化')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # 保存图片
    save_path = os.path.join(os.path.dirname(__file__), "ray_tracing_meeting_room", "wall_reflectivity.png")
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()

def plot_wall_incident_angles(wall_stats):
    """
    绘制每面墙的入射角分布直方图
    
    Args:
        wall_stats: 墙面统计信息
    """
    n_walls = len(wall_stats)
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    axes = axes.flatten()
    
    for i in range(n_walls):
        if wall_stats[i]['count'] > 0:
            # 绘制直方图
            axes[i].hist(wall_stats[i]['angles'], bins=30, alpha=0.7)
            axes[i].set_title(f'Wall {i+1}\nCount: {wall_stats[i]["count"]}')
            axes[i].set_xlabel('入射角 (度)')
            axes[i].set_ylabel('频次')
            axes[i].grid(True)
            
            # 添加统计信息
            stats_text = f'Mean: {wall_stats[i]["avg_angle"]:.1f}°\n'
            stats_text += f'Std: {wall_stats[i]["std_angle"]:.1f}°\n'
            stats_text += f'Min: {wall_stats[i]["min_angle"]:.1f}°\n'
            stats_text += f'Max: {wall_stats[i]["max_angle"]:.1f}°'
            axes[i].text(0.95, 0.95, stats_text,
                        transform=axes[i].transAxes,
                        verticalalignment='top',
                        horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    save_path = os.path.join(os.path.dirname(__file__), "ray_tracing_meeting_room", "wall_incident_angles.png")
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()

def main(draw_debug=False):
    """
    主函数
    
    Args:
        draw_debug: 是否绘制调试图片
    """
    # 创建保存图片的目录
    save_path_base = os.path.join(os.path.dirname(__file__), "ray_tracing_meeting_room")
    os.makedirs(save_path_base, exist_ok=True)
    
    # 加载数据
    file_path = "meeting_room_data_2/2024-10-07-19-06-37_all.xlsx"
    raw_data = load_and_preprocess_data(file_path)
    
    # 角度校正和坐标系转换
    data = raw_data.copy()
    data['angle200'] = 225 - data['angle200']
    data['angle300'] = data['angle300'] - 225
    
    # 数据预处理，去除相似的数据点
    data = preprocess_data(data, tx_threshold=2, rx_threshold=2, value_threshold=1)
    
    # 对每个tx-rx角度对计算路径
    print("\n开始计算传播路径...")
    all_paths = {}
    valid_paths_count = 0
    total_paths_checked = 0
    
    # 使用tqdm显示进度，设置正确的总数
    for idx, row in tqdm(data.iterrows(), total=len(data), desc="处理测量点"):
        tx_angle = row['angle200']
        rx_angle = row['angle300']
        value = row['value']
        
        # 计算该角度对下的所有路径
        paths, path_powers = calculate_paths_for_angle_pair(tx_angle, rx_angle)
        
        if paths:
            valid_paths_count += 1
            # 使用原始角度值作为键
            all_paths[(tx_angle, rx_angle)] = (paths, path_powers)
            total_paths_checked += len(paths)
            
            # 如果需要绘制调试图片
            if draw_debug:
                save_path = os.path.join(save_path_base, "debug_pics", f"path_{idx}.png")
                is_main_lobe = True
                plot_signal_path(paths, tx_angle, rx_angle, value, save_path, is_main_lobe)
    
    print(f"\n路径统计：")
    print(f"有效测量点数：{valid_paths_count}")
    print(f"总检查路径数：{total_paths_checked}")
    
    if len(all_paths) == 0:
        print("\n警告：没有找到有效路径！")
        print("可能的原因：")
        print("1. RX接收条件太严格")
        print("2. 角度转换有误")
        print("3. 路径计算有误")
        return
    
    # 分析路径统计信息
    print("\n分析路径统计信息...")
    stats = analyze_paths(all_paths)
    print(f"\n平均每条路径数量：{stats['avg_paths']:.2f}")
    print("\n墙面统计：")
    for i in range(8):
        wall_stat = stats['wall_stats'][i]
        if wall_stat['count'] > 0:
            print(f"\n墙面 {i+1}:")
            print(f"  出现次数：{wall_stat['count']}")
            print(f"  平均入射角：{wall_stat['avg_angle']:.1f}°")
            print(f"  入射角标准差：{wall_stat['std_angle']:.1f}°")
            print(f"  最小入射角：{wall_stat['min_angle']:.1f}°")
            print(f"  最大入射角：{wall_stat['max_angle']:.1f}°")
    
    # 构建方程组
    print("\n开始构建方程组...")
    equations, constants = build_equation_system(data, all_paths)
    
    if not equations:
        print("\n警告：没有构建出有效的方程组！")
        return
    
    # 参数拟合
    print("\n开始参数拟合...")
    estimated_epsilons = estimate_wall_parameters(equations, constants)
    
    # 对相似表面进行聚类
    print("\n开始表面聚类...")
    labels = cluster_similar_surfaces(estimated_epsilons)
    
    # 评估拟合误差
    print("\n评估拟合误差...")
    mse = evaluate_fitting_error(estimated_epsilons, data, all_paths)
    
    # 输出结果
    print("\n估计结果：")
    for i, epsilon in enumerate(estimated_epsilons):
        material_type = identify_material_type(epsilon)
        print(f"墙面 {i+1}: 介电常数 = {epsilon:.2f}, 材料类型 = {material_type}")
    
    print(f"\n拟合误差 (MSE): {mse:.2f} dB")
    
    # 输出聚类结果
    print("\n聚类结果：")
    for i, label in enumerate(labels):
        print(f"墙面 {i+1} 属于类别 {label+1}")
    
    # 绘制墙面反射率曲线
    print("\n绘制墙面反射率曲线...")
    plot_wall_reflectivity(estimated_epsilons)
    
    # 绘制入射角分布
    print("\n绘制入射角分布...")
    plot_wall_incident_angles(stats['wall_stats'])

if __name__ == '__main__':
    # 设置是否绘制调试图片
    DRAW_DEBUG = True
    main(draw_debug=DRAW_DEBUG)
