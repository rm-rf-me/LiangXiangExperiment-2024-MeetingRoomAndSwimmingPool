import numpy as np
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

nlos_30_no_wave = {
    120: '2025-01-16-19-48-22_30度120无浪.xlsx',
    140: '2025-01-16-19-57-37_30度140无浪.xlsx',
    160: '2025-01-16-20-05-31_30度160无浪.xlsx',
    221: '2025-01-16-16-19-54_30度221水面.xlsx',
    260: '2025-01-16-16-35-11_30度260水面.xlsx',
    320: '2025-01-16-16-45-57_30度320无浪.xlsx'
}

nlos_30_little = {
    120: '2025-01-16-19-51-34_30度120小浪.xlsx',
    140: '2025-01-16-19-59-45_30度140小浪.xlsx',
    160: '2025-01-16-20-07-36_30度160小浪.xlsx',
    221: '2025-01-16-16-21-59_30度221小浪.xlsx',
    260: '2025-01-16-16-37-08_30度260小浪.xlsx',
    320: '2025-01-16-16-47-57_30度320小浪.xlsx'
}

nlos_30_high = {
    120: '2025-01-16-19-54-07_30度120大浪.xlsx',
    140: '2025-01-16-20-02-13_30度140大浪.xlsx',
    160: '2025-01-16-20-13-12_30度160大浪.xlsx',
    221: '2025-01-16-16-30-29_30度221大浪.xlsx',
    260: '2025-01-16-16-39-40_30度260大浪.xlsx',
    320: '2025-01-16-16-52-54_30度320大浪.xlsx'
}

nlos_45_no_wave = {
    120: '2025-01-16-20-39-40_45度120无浪.xlsx',
    140: '2025-01-16-20-47-53_45度140无浪.xlsx',
    160: '2025-01-16-20-55-05_45度160无浪.xlsx',
    221: '2025-01-16-17-51-08_45度221水面.xlsx',
    260: '2025-01-16-17-59-58_45度260无浪.xlsx',
    320: '2025-01-16-18-10-51_45度320无浪.xlsx'
}

nlos_45_little = {
    120: '2025-01-16-20-41-08_45度120小浪.xlsx',
    140: '2025-01-16-20-49-31_45度140小浪.xlsx',
    160: '2025-01-16-20-56-57_45度160小浪.xlsx',
    221: '2025-01-16-17-53-08_45度221小浪.xlsx',
    260: '2025-01-16-18-02-21_45度260小浪.xlsx',
    320: '2025-01-16-18-14-44_45度320小浪.xlsx'
}

nlos_45_high = {
    120: '2025-01-16-20-43-47_45度120大浪.xlsx',
    140: '2025-01-16-20-51-53_45度140大浪.xlsx',
    160: '2025-01-16-20-59-16_45度160大浪.xlsx',
    221: '2025-01-16-17-56-18_45度221大浪.xlsx',
    260: '2025-01-16-18-06-48_45度260大浪.xlsx',
    320: '2025-01-16-18-19-07_45度320大浪.xlsx'
}

all_data = {
    'nlos_30_no_wave': nlos_30_no_wave,
    'nlos_30_little_wave': nlos_30_little,
    'nlos_30_big_wave': nlos_30_high,
    'nlos_45_no_wave': nlos_45_no_wave,
    'nlos_45_little_wave': nlos_45_little,
    'nlos_45_big_wave': nlos_45_high
}

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '实验室水面实验', '时序')


def read_data(file_name):
    data = pd.read_excel(os.path.join(base_path, file_name), header=None)
    # 创建数据的副本以避免 SettingWithCopyWarning
    data = data.copy()
    # 使用 loc 来正确设置值
    for i in range(len(data)):
        if isinstance(data.loc[i, 4], float) and data.loc[i, 4] < -45:
            data.loc[i, 4] = data.loc[i-1, 4] if i > 0 else -40
    return data


def fix_time_format(time_str):
    time_str = str(time_str)
    parts = time_str.split(".")[0].split(":")
    if len(time_str.split(".")) > 1:
        parts.append(time_str.split(".")[1])
    else:
        parts.append("000")
    # 如果长度大于 3，说明有毫秒部分
    if len(parts) > 3:
        if len(parts[3][:3]) == 1:
            parts[3] = f"{parts[3][:3]}00"
        elif len(parts[3][:3]) == 2:
            parts[3] = f"{parts[3][:3]}0"
        else:
            parts[3] = f"{parts[3][:3]}"
    else:
        parts.append("000")
    return ".".join(parts)


def filter_by_time_range(df, start_time_str, end_time_str):
    # 修正时间列格式，确保毫秒部分为3位数
    df['Time'] = df['Time'].apply(fix_time_format)

    # 将 'Time' 列转换为标准的 datetime 格式
    df['Time'] = pd.to_datetime(df['Time'], format='%H.%M.%S.%f').dt.time

    # 将字符串的时间转换为 datetime.time 对象
    start_time = pd.to_datetime(start_time_str, format='%H:%M:%S.%f').time()
    end_time = pd.to_datetime(end_time_str, format='%H:%M:%S.%f').time()

    # 筛选在 start_time 和 end_time 之间的行
    filtered_df = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]

    return filtered_df


def read_all_data():
    data_dict = {}
    for key, value in all_data.items():
        if isinstance(value, dict):
            data_dict[key] = {}
            for freq, file_name in value.items():
                if isinstance(file_name, list):
                    data_dict[key][freq] = []
                    for file in file_name:
                        data = read_data(file)
                        data_dict[key][freq].append(data)
                else:
                    data = read_data(file_name)
                    data_dict[key][freq] = data

        else:
            data_dict[key] = read_data(value)
    return data_dict


def plot_data_list(data_list, title, save_path=None):
    # 设置全局字体为 Times New Roman
    plt.rcParams.update({
        'font.family': 'Times New Roman',
        'font.size': 12,
        'mathtext.fontset': 'stix'
    })
    
    # 设置图片尺寸和DPI
    plt.rcParams['figure.figsize'] = [8, 4]
    plt.rcParams['figure.dpi'] = 300
    
    # 创建图形和轴
    fig, ax1 = plt.subplots()
    
    # 定义颜色方案
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # No Wave (蓝), Small Wave (橙), Big Wave (绿)
    
    # 绘制数据
    for i, (k, data) in enumerate(data_list.items()):
        if "Time" in data:
            pass
        else:
            # 将索引转换为时间（秒）
            x_values = np.arange(len(data[4][1:])) / 7.0  # 转换为秒
            values = data[4][1:]/2  # 除以2保持原有的数据处理
            
            # 绘制半透明的原始数据
            ax1.plot(x_values, values,
                    label=k,
                    color=colors[i % len(colors)],
                    linewidth=1,
                    alpha=0.3)
            
            # 根据数据类型选择不同的处理方式
            if "No Wave" in k:
                # 无浪状态使用均值线
                mean_value = np.mean(values)
                ax1.axhline(y=mean_value, 
                          color=colors[i % len(colors)],
                          linewidth=2,
                          label=f'{k} Mean ({mean_value:.1f} dBm)')
            else:
                # 小浪和大浪状态使用滑动平均
                window_size = 100  # 调整窗口大小以改变平滑程度
                smoothed = pd.Series(values).rolling(window=window_size, center=True).mean()
                ax1.plot(x_values, smoothed, 
                        color=colors[i % len(colors)],
                        linewidth=2,
                        label=f'{k} Trend')
    
    # 设置标题
    plt.title(title, pad=10, fontsize=14, fontweight='bold')
    
    # 设置轴标签，增大字体
    ax1.set_xlabel('Time (s)', fontsize=12, labelpad=8)
    ax1.set_ylabel('Amplitude (dBm)', fontsize=12, labelpad=8)
    
    # 设置刻度，增大字体
    ax1.tick_params(axis='both', direction='in', labelsize=11)
    
    # 添加网格线
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # 优化图例位置和样式
    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1, labels1,
              loc='upper right',
              frameon=True,
              fontsize=10,
              ncol=1)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    if save_path:
        plt.savefig(save_path, 
                   bbox_inches='tight',
                   pad_inches=0.1,
                   dpi=300)
    
    plt.show()


def plot_data_list_with_wave_height(data_list, title, start_time, save_path=None):
    # make this figure wider
    start_time = pd.to_datetime(start_time)

    plt.rcParams['figure.figsize'] = [12, 4]
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    tmp_df = pd.concat(data_list.values())
    tmp_df.to_excel(os.path.join(base_path, title + str(start_time) + "tmp.xlsx"))
    print(f"file saved to {os.path.join(base_path, title + str(start_time) + 'tmp.xlsx')}")

    for k, data in data_list.items():
        # plt.plot(data[1][1:].str.split().str.get(1), data[4][1:], label=k)
        if "Time" in data:
            # 将 'Time' 列转换为 datetime，只包含时间部分
            # data['Time'] = pd.to_datetime(data['Time'], format='%H:%M:%S.%f').dt.time
            # 定义固定的日期
            fixed_date = datetime(2024, 7, 26).date()
            # 将日期和时间组合成完整的 datetime
            data['DateTime'] = data['Time'].apply(lambda t: datetime.combine(fixed_date, t))
            # 如果需要将 DateTime 列转换为时间戳
            data['Timestamp'] = data['DateTime'].apply(lambda x: x.timestamp())

            # 计算每个时间点与起始点的时间差，以秒为单位
            data['TimeDelta'] = data['DateTime'].apply(lambda x: (x - start_time).total_seconds() + 5)

            ax2.plot(data["TimeDelta"][1:], data["Value"][1:], color='blue', label=k)
        else:
            df = data[1:].copy()
            df['timestamp'] = pd.to_datetime(df[1])

            # 对每秒的数据进行分组
            df['group'] = df.groupby(df['timestamp'].dt.floor('S')).cumcount()

            # 每秒内数据点的总数
            df['count'] = df.groupby(df['timestamp'].dt.floor('S'))['timestamp'].transform('count')

            # 计算出每个数据点应增加的毫秒数
            df['milliseconds'] = (df['group'] * 1000 / df['count']).astype(int)

            # 最终的带有毫秒的时间戳
            df['new_timestamp'] = df['timestamp'] + pd.to_timedelta(df['milliseconds'], unit='ms')

            # 计算每个时间点与起始点的时间差，以秒为单位
            df['TimeDelta'] = df['new_timestamp'].apply(lambda x: (x - start_time).total_seconds())

            ax1.plot(df['TimeDelta'], data[4][1:], color='red', label=k)
    plt.title(title)
    ax1.set_xlabel('X')
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_ylabel('Amplitude (dbm)')
    ax2.set_ylabel('WaveHeight(mm)')
    ax1.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def get_indoor_data_after_cut():
    pic_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indoor_water_height_pic')
    data_dict = read_all_data()
    print(data_dict.keys())

    nlos_30_little_list = {
        120: {
            "No Wave": data_dict['nlos_30_no_wave'][120][100:300],
            "Small Wave": data_dict['nlos_30_little_wave'][120][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][120][200:600]
        },
        140: {
            "No Wave": data_dict['nlos_30_no_wave'][140][400:600],
            "Small Wave": data_dict['nlos_30_little_wave'][140][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][140][200:600]
        },
        160: {
            "No Wave": data_dict['nlos_30_no_wave'][160][350:550],
            "Small Wave": data_dict['nlos_30_little_wave'][160][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][160][100:500]
        },
        221: {
            "No Wave": data_dict['nlos_30_no_wave'][221][250:450],
            "Small Wave": data_dict['nlos_30_little_wave'][221][400:800],
            "Big Wave": data_dict['nlos_30_big_wave'][221][200:600]
        },
        260: {
            "No Wave": data_dict['nlos_30_no_wave'][260][350:450],
            "Small Wave": data_dict['nlos_30_little_wave'][260][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][260][100:500]
        },
        320: {
            "No Wave": data_dict['nlos_30_no_wave'][320][300:500],
            "Small Wave": data_dict['nlos_30_little_wave'][320][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][320][400:800]
        }
    }
    nlos_45_little_list = {
        120: {
            "No Wave": data_dict['nlos_45_no_wave'][120][150:350],
            "Small Wave": data_dict['nlos_45_little_wave'][120][100:500],
            "Big Wave": data_dict['nlos_45_big_wave'][120][100:500]
        },
        140: {
            "No Wave": data_dict['nlos_45_no_wave'][140][200:400],
            "Small Wave": data_dict['nlos_45_little_wave'][140][100:500],
            "Big Wave": data_dict['nlos_45_big_wave'][140][100:500]
        },
        160: {
            "No Wave": data_dict['nlos_45_no_wave'][160][280:380],
            "Small Wave": data_dict['nlos_45_little_wave'][160][200:600],
            "Big Wave": data_dict['nlos_45_big_wave'][160][200:600]
        },
        221: {
            "No Wave": data_dict['nlos_45_no_wave'][221][300:500],
            "Small Wave": data_dict['nlos_45_little_wave'][221][400:800],
            "Big Wave": data_dict['nlos_45_big_wave'][221][100:500]
        },
        260: {
            "No Wave": data_dict['nlos_45_no_wave'][260][480:580],
            "Small Wave": data_dict['nlos_45_little_wave'][260][600:1000],
            "Big Wave": data_dict['nlos_45_big_wave'][260][200:600]
        },
        320: {
            "No Wave": data_dict['nlos_45_no_wave'][320][800:900],
            "Small Wave": data_dict['nlos_45_little_wave'][320][600:1000],
            "Big Wave": data_dict['nlos_45_big_wave'][320][200:600]
        }
    }
    return nlos_30_little_list, nlos_45_little_list


if __name__ == '__main__':
    pic_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'indoor_water_height_pic')
    data_dict = read_all_data()
    print(data_dict.keys())

    nlos_30_little_list = {
        120: {
            "No Wave": data_dict['nlos_30_no_wave'][120][100:300],
            "Small Wave": data_dict['nlos_30_little_wave'][120][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][120][200:600]
        },
        140: {
            "No Wave": data_dict['nlos_30_no_wave'][140][400:600],
            "Small Wave": data_dict['nlos_30_little_wave'][140][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][140][200:600]
        },
        160: {
            "No Wave": data_dict['nlos_30_no_wave'][160][350:550],
            "Small Wave": data_dict['nlos_30_little_wave'][160][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][160][100:500]
        },
        221: {
            "No Wave": data_dict['nlos_30_no_wave'][221][250:450],
            "Small Wave": data_dict['nlos_30_little_wave'][221][400:800],
            "Big Wave": data_dict['nlos_30_big_wave'][221][200:600]
        },
        260: {
            "No Wave": data_dict['nlos_30_no_wave'][260][350:450],
            "Small Wave": data_dict['nlos_30_little_wave'][260][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][260][100:500]
        },
        320: {
            "No Wave": data_dict['nlos_30_no_wave'][320][300:500],
            "Small Wave": data_dict['nlos_30_little_wave'][320][200:600],
            "Big Wave": data_dict['nlos_30_big_wave'][320][400:800]
        }
    }
    plot_data_list(nlos_30_little_list[120], "N-Los 30 120GHz", os.path.join(pic_base, "nlos_30_120.png"))
    plot_data_list(nlos_30_little_list[140], "N-Los 30 140GHz", os.path.join(pic_base, "nlos_30_140.png"))
    plot_data_list(nlos_30_little_list[160], "N-Los 30 160GHz", os.path.join(pic_base, "nlos_30_160.png"))
    plot_data_list(nlos_30_little_list[221], "N-Los 30 221GHz", os.path.join(pic_base, "nlos_30_221.png"))
    plot_data_list(nlos_30_little_list[260], "N-Los 30 260GHz", os.path.join(pic_base, "nlos_30_260.png"))
    plot_data_list(nlos_30_little_list[320], "N-Los 30 320GHz", os.path.join(pic_base, "nlos_30_320.png"))
    plot_data_list(nlos_30_little_list[160], "(a) 160GHz-30°", os.path.join(pic_base, "nlos_30_160.png"))
    plot_data_list(nlos_30_little_list[221], "(b) 221GHz-30°", os.path.join(pic_base, "nlos_30_221.png"))
    plot_data_list(nlos_30_little_list[320], "(c) 320GHz-30°", os.path.join(pic_base, "nlos_30_320.png"))

    nlos_45_little_list = {
        120: {
            "No Wave": data_dict['nlos_45_no_wave'][120][150:350],
            "Small Wave": data_dict['nlos_45_little_wave'][120][100:500],
            "Big Wave": data_dict['nlos_45_big_wave'][120][100:500]
        },
        140: {
            "No Wave": data_dict['nlos_45_no_wave'][140][200:400],
            "Small Wave": data_dict['nlos_45_little_wave'][140][100:500],
            "Big Wave": data_dict['nlos_45_big_wave'][140][100:500]
        },
        160: {
            "No Wave": data_dict['nlos_45_no_wave'][160][280:380],
            "Small Wave": data_dict['nlos_45_little_wave'][160][200:600],
            "Big Wave": data_dict['nlos_45_big_wave'][160][200:600]
        },
        221: {
            "No Wave": data_dict['nlos_45_no_wave'][221][300:500],
            "Small Wave": data_dict['nlos_45_little_wave'][221][400:800],
            "Big Wave": data_dict['nlos_45_big_wave'][221][100:500]
        },
        260: {
            "No Wave": data_dict['nlos_45_no_wave'][260][480:580],
            "Small Wave": data_dict['nlos_45_little_wave'][260][600:1000],
            "Big Wave": data_dict['nlos_45_big_wave'][260][200:600]
        },
        320: {
            "No Wave": data_dict['nlos_45_no_wave'][320][800:900],
            "Small Wave": data_dict['nlos_45_little_wave'][320][600:1000],
            "Big Wave": data_dict['nlos_45_big_wave'][320][200:600]
        }
    }
    plot_data_list(nlos_45_little_list[120], "N-Los 45 120GHz", os.path.join(pic_base, "nlos_45_120.png"))
    plot_data_list(nlos_45_little_list[140], "N-Los 45 140GHz", os.path.join(pic_base, "nlos_45_140.png"))
    plot_data_list(nlos_45_little_list[160], "N-Los 45 160GHz", os.path.join(pic_base, "nlos_45_160.png"))
    plot_data_list(nlos_45_little_list[221], "N-Los 45 221GHz", os.path.join(pic_base, "nlos_45_221.png"))
    plot_data_list(nlos_45_little_list[260], "N-Los 45 260GHz", os.path.join(pic_base, "nlos_45_260.png"))
    plot_data_list(nlos_45_little_list[320], "N-Los 45 320GHz", os.path.join(pic_base, "nlos_45_320.png"))
    plot_data_list(nlos_45_little_list[160], "(d) 160GHz-45°", os.path.join(pic_base, "nlos_45_160.png"))
    plot_data_list(nlos_45_little_list[221], "(e) 221GHz-45°", os.path.join(pic_base, "nlos_45_221.png"))
    plot_data_list(nlos_45_little_list[320], "(f) 320GHz-45°", os.path.join(pic_base, "nlos_45_320.png"))
