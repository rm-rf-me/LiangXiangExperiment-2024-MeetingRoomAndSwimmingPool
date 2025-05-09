import numpy as np
import pandas as pd
import os
from scipy.optimize import least_squares
from sklearn.cluster import KMeans
from draw_meeting_room_2d import calculate_beam_path, line_segment_ray_intersection, draw_meeting_room_with_angles
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

# 常量定义
FREQUENCY = 140e9  # 140GHz
C = 3e8  # 光速
WAVELENGTH = C / FREQUENCY

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

def plot_signal_path(path, tx_angle, rx_angle, value=None, save_path=None, is_main_lobe=True):
    """
    根据计算好的path绘制传播路径
    
    Args:
        path: 路径信息 (path_points, wall_indices, incident_angles)
        tx_angle: 发射角度（0度指向x轴正方向，逆时针为正）
        rx_angle: 接收角度（0度指向x轴正方向，逆时针为正）
        value: 信号强度值
        save_path: 图片保存路径
        is_main_lobe: 是否为主瓣
    """
    path_points, wall_indices, incident_angles = path
    walls, _ = get_wall_info()
    tx_position = (3.145, 2.05)
    rx_position = (3.145, 5.86)
    
    # 创建绘图
    fig, ax = plt.subplots()
    
    # 绘制墙体
    for wall in walls:
        wall_start, wall_end = wall
        ax.plot([wall_start[0], wall_end[0]], [wall_start[1], wall_end[1]], 'k-', linewidth=2)
    
    # 绘制发射机和接收机
    ax.plot(tx_position[0], tx_position[1], 'ro', label='TX')
    ax.plot(rx_position[0], rx_position[1], 'bo', label='RX')
    
    # 绘制TX和RX的方向
    tx_dir = np.array([np.cos(np.deg2rad(tx_angle)), np.sin(np.deg2rad(tx_angle))])
    rx_dir = np.array([np.cos(np.deg2rad(rx_angle)), np.sin(np.deg2rad(rx_angle))])
    
    # 绘制TX方向
    ax.arrow(tx_position[0], tx_position[1], 
             tx_dir[0]*0.5, tx_dir[1]*0.5,
             head_width=0.1, head_length=0.2, fc='r', ec='r')
    
    # 绘制RX方向
    ax.arrow(rx_position[0], rx_position[1],
             rx_dir[0]*0.5, rx_dir[1]*0.5,
             head_width=0.1, head_length=0.2, fc='b', ec='b')
    
    # 绘制TX和RX的坐标和角度标注
    ax.annotate(f'TX: ({tx_position[0]:.2f}, {tx_position[1]:.2f})\n{tx_angle:.1f}°',
                (tx_position[0], tx_position[1]),
                xytext=(10, 10),
                textcoords='offset points')
    ax.annotate(f'RX: ({rx_position[0]:.2f}, {rx_position[1]:.2f})\n{rx_angle:.1f}°',
                (rx_position[0], rx_position[1]),
                xytext=(10, 10),
                textcoords='offset points')
    
    # 绘制路径
    path_points = np.array(path_points)
    ax.plot(path_points[:, 0], path_points[:, 1], 'r--', label='Signal Path')
    
    # 在反射点处标记墙面编号和入射角
    for i, (point, wall_idx, angle) in enumerate(zip(path_points[1:-1], wall_indices, incident_angles)):
        ax.plot(point[0], point[1], 'go')  # 反射点
        ax.annotate(f'W{wall_idx+1}\n{angle:.1f}°', 
                   (point[0], point[1]),
                   xytext=(5, 5),
                   textcoords='offset points')
    
    # 设置图例和显示
    ax.legend(bbox_to_anchor=(1.03, 1), loc='upper left', borderaxespad=0.)
    ax.set_aspect('equal')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    
    # 设置标题
    title = f'TX: {tx_angle:.1f}°, RX: {rx_angle:.1f}°'
    if value is not None:
        title += f'\nValue: {value:.1f} dB'
    title += f'\n{"Main Lobe" if is_main_lobe else "Side Lobe"}'
    ax.set_title(title)
    
    plt.grid(True)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    
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

def get_all_possible_paths(tx_angle, rx_angle, max_reflections=3, draw_path=False, save_path=None, value=None):
    """
    获取所有可能的传播路径（每次反射后都判断是否到达RX）
    """
    walls, wall_normals = get_wall_info()
    tx_position = (3.145, 2.05)
    rx_position = (3.145, 5.86)
    max_distance = 1
    max_angle = 60
    tx_angles = [tx_angle, tx_angle - 13, tx_angle + 13]
    paths = []
    for i, tx_angle_ in enumerate(tx_angles):
        path_points = [tx_position]
        current_position = np.array(tx_position)
        current_angle = tx_angle_
        found = False
        for reflection in range(max_reflections+1):
            angle_rad = np.deg2rad(current_angle)
            direction = np.array([np.cos(angle_rad), np.sin(angle_rad)])
            # 每次反射后都判断是否到达RX
            rx_angle_rad = np.deg2rad(rx_angle)
            rx_dir = np.array([np.cos(rx_angle_rad), np.sin(rx_angle_rad)])
            res, distance, angle, intersection_point = check_point_in_path(
                rx_position, rx_dir, current_position, direction, max_distance, max_angle)
            if res:
                path_points.append(intersection_point)
                found = True
                break
            # 没到达RX则找最近的墙反射
            closest_intersection = None
            closest_wall_orientation = None
            min_distance = float('inf')
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
                break
            path_points.append(closest_intersection)
            current_position = np.array(closest_intersection)
            current_angle = 2 * np.degrees(closest_wall_orientation) - current_angle
        if found:
            # 计算路径上的墙面编号和入射角
            wall_indices, incident_angles = calculate_path_parameters(path_points, walls, wall_normals)
            path = (path_points, wall_indices, incident_angles)
            paths.append(path)
            if draw_path:
                is_main_lobe = (i == 0)
                plot_signal_path(path, tx_angle_, rx_angle, value, save_path, is_main_lobe)
    return paths

def calculate_path_parameters(path_points, walls, wall_normals):
    """
    计算路径参数
    
    Args:
        path_points: 路径点列表
        walls: 墙壁列表
        wall_normals: 墙壁法向量列表
        
    Returns:
        wall_indices: 路径上的墙面编号列表
        incident_angles: 入射角列表
    """
    wall_indices = []
    incident_angles = []
    
    for i in range(len(path_points) - 1):
        start_point = path_points[i]
        end_point = path_points[i + 1]
        direction = np.array(end_point) - np.array(start_point)
        direction = direction / np.linalg.norm(direction)
        
        # 找到与路径相交的墙面
        for j, wall in enumerate(walls):
            intersects, intersection = line_segment_ray_intersection(
                wall[0], wall[1], start_point, direction)
            
            if intersects:
                wall_indices.append(j)
                # 计算入射角
                normal = wall_normals[j]
                incident_angle = np.arccos(np.abs(np.dot(direction, normal)))
                incident_angles.append(np.rad2deg(incident_angle))
                break
    
    return wall_indices, incident_angles

def calculate_path_loss(path, wall_epsilons):
    """
    计算路径损耗
    
    Args:
        path: 路径信息 (path_points, wall_indices, incident_angles)
        wall_epsilons: 各墙面的介电常数列表
        
    Returns:
        total_loss: 总路径损耗（dB）
    """
    path_points, wall_indices, incident_angles = path
    
    # 计算距离
    total_distance = 0
    for i in range(len(path_points) - 1):
        total_distance += np.linalg.norm(np.array(path_points[i+1]) - np.array(path_points[i]))
    
    # 计算FSPL
    fspl = calculate_fspl(total_distance)
    
    # 计算反射损耗
    reflection_loss = 0
    for wall_idx, incident_angle in zip(wall_indices, incident_angles):
        r = calculate_fresnel_coefficient(wall_epsilons[wall_idx], incident_angle)
        reflection_loss += -10 * np.log10(r)
    
    return fspl + reflection_loss

def build_equation_system(measurements, paths):
    """
    构建非线性方程组
    
    Args:
        measurements: 测量数据DataFrame
        paths: 所有可能的传播路径
        
    Returns:
        A: 系数矩阵
        b: 常数向量
    """
    # 初始化方程组
    equations = []
    constants = []
    
    for _, row in measurements.iterrows():
        tx_angle = row['angle200']
        rx_angle = row['angle300']
        measured_power = row['value']
        
        # 获取该角度组合的所有可能路径
        possible_paths = get_all_possible_paths(tx_angle, rx_angle)
        
        # 计算天线增益
        tx_gain = calculate_antenna_gain(0)  # 主瓣增益
        rx_gain = calculate_antenna_gain(0)  # 主瓣增益
        
        # 构建方程
        for path in possible_paths:
            path_points, wall_indices, incident_angles = path
            equation = []
            constant = measured_power - tx_gain - rx_gain
            
            # 添加每个墙面的反射项
            for wall_idx, incident_angle in zip(wall_indices, incident_angles):
                equation.append((wall_idx, incident_angle))
            
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
        for wall_idx, incident_angle in eq:
            r = calculate_fresnel_coefficient(epsilons[wall_idx], incident_angle)
            predicted_power += -10 * np.log10(r)
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

def evaluate_fitting_error(estimated_epsilons, measurements, paths):
    """
    评估拟合误差
    
    Args:
        estimated_epsilons: 估计的介电常数
        measurements: 测量数据
        paths: 传播路径
        
    Returns:
        mse: 均方误差
    """
    total_error = 0
    count = 0
    
    for _, row in measurements.iterrows():
        tx_angle = row['angle200']
        rx_angle = row['angle300']
        measured_power = row['value']
        
        # 获取该角度组合的所有可能路径
        possible_paths = get_all_possible_paths(tx_angle, rx_angle)
        
        # 计算预测功率
        predicted_power = float('-inf')
        for path in possible_paths:
            path_loss = calculate_path_loss(path, estimated_epsilons)
            predicted_power = max(predicted_power, -path_loss)
        
        # 计算误差
        error = (predicted_power - measured_power) ** 2
        total_error += error
        count += 1
    
    return total_error / count if count > 0 else float('inf')

def main(draw_debug=False):
    """
    主函数
    
    Args:
        draw_debug: 是否绘制调试图片
    """
    # 创建保存图片的目录
    if draw_debug:
        save_path_base = os.path.join(os.path.dirname(__file__), "ray_tracing_meeting_room", "debug_pics")
        os.makedirs(save_path_base, exist_ok=True)
    
    # 加载数据
    file_path = "meeting_room_data_2/2024-10-08-17-02-44_有窗帘 140ghz 发射和接收都扫270度.xlsx"
    raw_data = load_and_preprocess_data(file_path)
    
    # 统计原始数据
    total_measurements = len(raw_data)
    print(f"\n原始测量数据统计：")
    print(f"总测量点数：{total_measurements}")
    
    # 角度校正和坐标系转换
    # 原始数据中：
    # TX: 0度指向左下角偏离中线45度，顺时针为正
    # RX: 0度指向左上角偏离中线45度，逆时针为正
    # 转换为：0度指向x轴正方向，逆时针为正
    data = raw_data.copy()
    # TX角度转换：原始角度 + 45度（因为原始0度是左下45度）
    data['angle200'] = 225 - data['angle200']
    # RX角度转换：原始角度 - 45度（因为原始0度是左上45度）
    data['angle300'] = data['angle300'] - 225
    
    # 获取所有可能的传播路径
    paths = []
    valid_paths_count = 0
    total_paths_checked = 0
    
    for idx, row in data.iterrows():
        tx_angle = row['angle200']
        rx_angle = row['angle300']
        value = row['value']
        
        # 打印一些调试信息
        if tx_angle < 92 and tx_angle > 88 and rx_angle < -87 and rx_angle > -88:  # 只打印前5个点的详细信息
            print(f"\n检查点 {idx}:")
            print(f"TX角度: {tx_angle:.1f}°, RX角度: {rx_angle:.1f}°, 信号强度: {value:.1f} dB")
        
        save_path = os.path.join(save_path_base, f"path_{idx}.png") if draw_debug else None
        possible_paths = get_all_possible_paths(
            tx_angle, 
            rx_angle, 
            draw_path=draw_debug,
            save_path=save_path,
            value=value
        )
        
        total_paths_checked += len(possible_paths)
        if possible_paths:
            valid_paths_count += 1
            paths.extend(possible_paths)
            
            if idx < 5:  # 只打印前5个点的路径信息
                print(f"找到 {len(possible_paths)} 条有效路径")
                for i, path in enumerate(possible_paths):
                    path_points, wall_indices, incident_angles = path
                    print(f"路径 {i+1}:")
                    print(f"  反射点数量: {len(wall_indices)}")
                    print(f"  墙面编号: {wall_indices}")
                    print(f"  入射角: {[f'{angle:.1f}°' for angle in incident_angles]}")
    
    print(f"\n路径统计：")
    print(f"有效测量点数：{valid_paths_count}")
    print(f"总检查路径数：{total_paths_checked}")
    print(f"总有效路径数：{len(paths)}")
    
    if len(paths) == 0:
        print("\n警告：没有找到有效路径！")
        print("可能的原因：")
        print("1. RX接收条件太严格")
        print("2. 角度转换有误")
        print("3. 路径计算有误")
        return
    
    # 构建方程组
    equations, constants = build_equation_system(data, paths)
    
    # 估计墙面参数
    estimated_epsilons = estimate_wall_parameters(equations, constants)
    
    # 对相似表面进行聚类
    labels = cluster_similar_surfaces(estimated_epsilons)
    
    # 评估拟合误差
    mse = evaluate_fitting_error(estimated_epsilons, data, paths)
    
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

if __name__ == '__main__':
    # 设置是否绘制调试图片
    DRAW_DEBUG = True
    main(draw_debug=DRAW_DEBUG)
