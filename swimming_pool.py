import numpy as np
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

los_high_no_wave = {
    220: '2024-07-26-11-37-30_220GHz_swmmingpool_los_3.xlsx',
    225: '2024-07-26-11-44-34_225GHz_swmmingpool_los_3.xlsx',
    229: '2024-07-26-11-49-03_229GHz_swmmingpool_los_3.xlsx'
}

los_high_little_wave = {
    220: '2024-07-26-12-13-20_220GHZ_swimmingpool_los_little_wave.xlsx',
    225: '2024-07-26-12-11-03_225GHZ_swimmingpool_los_little_wave.xlsx',
    229: '2024-07-26-12-00-20_229GHz_swmmingpool_los_little_wave.xlsx'
}
los_high_big_wave = {
    220: '2024-07-26-12-18-03_220GHZ_swimmingpool_los_big_wave.xlsx',
    225: '2024-07-26-12-20-40_225GHZ_swimmingpool_los_big_wave.xlsx',
    229: '2024-07-26-12-24-11_229GHZ_swimmingpool_los_big_wave.xlsx'
}

nlos_high_no_wave = {
    220: '2024-07-26-14-14-02_220GHz_swimmingpool_nLos_1.xlsx',
    225: '2024-07-26-14-18-02_225GHz_swimmingpool_nLos_1.xlsx',
    229: '2024-07-26-14-23-01_229GHz_swimmingpool_nLos_1.xlsx'
}

nlos_high_little_wave = {
    220: '2024-07-26-14-31-13_220GHz swimmingpool nlos little wave.xlsx',
    225: '2024-07-26-14-34-32_225GHz swimmingpool nlos little wave.xlsx',
    229: '2024-07-26-14-37-00_229GHz swimmingpool nlos little wave.xlsx'
}

nlos_high_big_wave = {
    220: '2024-07-26-14-42-37_220GHz big wave nlos.xlsx',
    225: '2024-07-26-14-45-20_225GHz big wave nlos.xlsx',
    229: '2024-07-26-14-54-19_229GHz big wave nlos.xlsx'
}

nlos_high_400m = {
    220: [
        "2024-07-26-14-59-20_220GHz 400m.xlsx",
        "2024-07-26-15-05-11_220.xlsx"
    ],
    225: "2024-07-26-15-01-35_225.xlsx",
    229: "2024-07-26-15-03-20_229.xlsx"
}

los_low_no_wave = {
    140: '2024-07-26-15-46-59_140GHz swmmingpool los.xlsx',
    120: '2024-07-26-15-50-42_120GHz swmming pool los.xlsx',
    160: '2024-07-26-15-54-39_160GHz swmming pool los.xlsx'
}

los_low_little_wave = {
    140: '2024-07-26-16-07-30_140GHz swmming pool los little wave.xlsx',
    120: '2024-07-26-16-09-11_120GHz swmming pool los little wave.xlsx',
    160: '2024-07-26-16-00-53_160GHz swmming pool los little wave.xlsx'
}

los_low_big_wave = {
    140: '2024-07-26-16-14-27_140GHz los big wave.xlsx',
    120: '2024-07-26-16-16-30_120GHz los big wave.xlsx',
    160: '2024-07-26-16-12-11_160GHz los big wave.xlsx'
}

nlos_low_no_wave = {
    140: '2024-07-26-16-38-53_140GHz nlos .xlsx',
    120: '2024-07-26-16-43-06_120GHz swmming pool nlos.xlsx',
    160: '2024-07-26-16-46-49_160GHz swmming pool nlos.xlsx'
}

nlos_low_little_wave = {
    140: '2024-07-26-16-53-28_140 nlos little wave.xlsx',
    120: '2024-07-26-16-51-31_120 nlos littile wave.xlsx',
    160: '2024-07-26-16-56-27_160 nlos little wave.xlsx'
}
nlos_low_big_wave = {
    140: '2024-07-26-17-01-07_140 nlos big wave.xlsx',
    120: '2024-07-26-17-03-12_120 nlos big wave.xlsx',
    160: '2024-07-26-16-58-19_160 nlos big wave.xlsx'
}

all_data = {
    'los_high_no_wave': los_high_no_wave,
    'los_high_little_wave': los_high_little_wave,
    'los_high_big_wave': los_high_big_wave,
    'nlos_high_no_wave': nlos_high_no_wave,
    'nlos_high_little_wave': nlos_high_little_wave,
    'nlos_high_big_wave': nlos_high_big_wave,
    'nlos_high_400m': nlos_high_400m,
    'los_low_no_wave': los_low_no_wave,
    'los_low_little_wave': los_low_little_wave,
    'los_low_big_wave': los_low_big_wave,
    'nlos_low_no_wave': nlos_low_no_wave,
    'nlos_low_little_wave': nlos_low_little_wave,
    'nlos_low_big_wave': nlos_low_big_wave
}

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '游泳池')


def read_data(file_name):
    data = pd.read_excel(os.path.join(base_path, file_name), header=None)

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
        if isinstance(data, dict) and "Time" in data:
            # 处理带时间的数据
            values = data["Value"][1:]/2
            x_values = np.arange(len(values))
            
            # 绘制半透明的原始数据
            ax1.plot(x_values, values, 
                    label=k,
                    color=colors[i % len(colors)],
                    linewidth=1,
                    alpha=0.3)
            
            # 计算滑动平均
            window_size = 50  # 调整窗口大小以改变平滑程度
            smoothed = pd.Series(values).rolling(window=window_size, center=True).mean()
            
            # 绘制平滑曲线
            ax1.plot(x_values, smoothed, 
                    color=colors[i % len(colors)],
                    linewidth=2,
                    label=f'{k} Trend')
            
        else:
            # 处理普通数据
            x_values = np.arange(len(data[4][1:])) / 7.0  # 转换为秒
            values = data[4][1:]/2
            
            # 绘制半透明的原始数据
            ax1.plot(x_values, values,
                    label=k,
                    color=colors[i % len(colors)],
                    linewidth=1,
                    alpha=0.3)
            
            # 计算滑动平均
            window_size = 100  # 调整窗口大小以改变平滑程度
            smoothed = pd.Series(values).rolling(window=window_size, center=True).mean()
            
            # 绘制平滑曲线
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
    ax1.legend(loc='upper right',
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
    # 设置全局字体为 Times New Roman
    plt.rcParams.update({
        'font.family': 'Times New Roman',
        'font.size': 12,  # 增大默认字体
        'mathtext.fontset': 'stix'
    })
    
    start_time = pd.to_datetime(start_time)
    
    # 设置图片尺寸和DPI
    plt.rcParams['figure.figsize'] = [8, 4]
    plt.rcParams['figure.dpi'] = 300
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    # 定义颜色方案
    signal_color = '#1f77b4'  # 蓝色用于信号强度
    wave_color = '#ff7f0e'    # 橙色用于波高
    
    for k, data in data_list.items():
        if "Time" in data:
            fixed_date = datetime(2024, 7, 26).date()
            data['DateTime'] = data['Time'].apply(lambda t: datetime.combine(fixed_date, t))
            data['TimeDelta'] = data['DateTime'].apply(lambda x: (x - start_time).total_seconds() + 5)
            
            ax2.plot(data["TimeDelta"][1:], data["Value"][1:], 
                    color=wave_color, 
                    label='Wave Height',
                    linewidth=1.5)
        else:
            df = data[1:].copy()
            df['timestamp'] = pd.to_datetime(df[1])
            df['TimeDelta'] = df['timestamp'].apply(lambda x: (x - start_time).total_seconds())
            
            ax1.plot(df['TimeDelta'], data[4][1:], 
                    color=signal_color, 
                    label='Signal Strength',
                    linewidth=1.5)
    
    # 设置标题和标签，增大字体
    plt.title(title, pad=10, fontsize=14, fontweight='bold')
    ax1.set_xlabel('Time (s)', fontsize=12, labelpad=8)
    ax1.set_ylabel('Amplitude (dBm)', fontsize=12, labelpad=8)
    ax2.set_ylabel('Wave Height (mm)', fontsize=12, labelpad=8)
    
    # 设置刻度，增大字体
    ax1.tick_params(axis='both', direction='in', labelsize=11)
    ax2.tick_params(axis='both', direction='in', labelsize=11)
    
    # 添加网格线
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # 优化图例位置，放在图内右上角
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, 
              loc='upper right',  # 改为右上角
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


if __name__ == '__main__':
    pic_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swimming_pool_pic')
    data_dict = read_all_data()
    print(data_dict.keys())
    
    # Los High频段数据
    los_high_list = {
        220: {
            "No Wave": data_dict['los_high_no_wave'][220][:400],
            "Small wave": data_dict['los_high_little_wave'][220][:400],
            "Big Wave": data_dict['los_high_big_wave'][220][:400]
        },
        225: {
            "No Wave": data_dict['los_high_no_wave'][225][:400],
            "Small wave": data_dict['los_high_little_wave'][225][:400],
            "Big Wave": data_dict['los_high_big_wave'][225][:400]
        },
        229: {
            "No Wave": data_dict['los_high_no_wave'][229][:400],
            "Small wave": data_dict['los_high_little_wave'][229][:400],
            "Big Wave": data_dict['los_high_big_wave'][229][:400]
        }
    }
    plot_data_list(los_high_list[220], "Los 220GHz", os.path.join(pic_base, "los_high_220.png"))
    plot_data_list(los_high_list[225], "Los 225GHz", os.path.join(pic_base, "los_high_225.png"))
    plot_data_list(los_high_list[229], "Los 229GHz", os.path.join(pic_base, "los_high_229.png"))

    nlos_high_list = {
        220: {
            "No Wave": data_dict['nlos_high_no_wave'][220][:400],
            "Small wave": data_dict['nlos_high_little_wave'][220][100:],
            "Big Wave": data_dict['nlos_high_big_wave'][220][100:]
        },
        225: {
            "No Wave": data_dict['nlos_high_no_wave'][225][:400],
            "Small wave": data_dict['nlos_high_little_wave'][225][0:400],
            "Big Wave": data_dict['nlos_high_big_wave'][225][220:600]
        },
        229: {
            "No Wave": data_dict['nlos_high_no_wave'][229][:400],
            "Small wave": data_dict['nlos_high_little_wave'][229][0:400],
            "Big Wave": data_dict['nlos_high_big_wave'][229][150:550]
        }
    }
    plot_data_list(nlos_high_list[220], "(b) N-Los 220GHz", os.path.join(pic_base, "nlos_high_220.png"))
    plot_data_list(nlos_high_list[225], "N-Los 225GHz", os.path.join(pic_base, "nlos_high_225.png"))
    plot_data_list(nlos_high_list[229], "N-Los 229GHz", os.path.join(pic_base, "nlos_high_229.png"))
    #
    # # nlos_high_400m_list = {
    # #     220: {
    # #         "No Wave": data_dict['nlos_high_400m'][220][0],
    # #         "Small wave": data_dict['nlos_high_400m'][220][1]
    # #     },
    # #     225: data_dict['nlos_high_400m'][225],
    # #     229: data_dict['nlos_high_400m'][229]
    # # }
    # nlos_high_people_swimmming_list = {
    #     "220-1": data_dict['nlos_high_400m'][220][0],
    #     "220-2": data_dict['nlos_high_400m'][220][1],
    #     "225": data_dict['nlos_high_400m'][225],
    #     "229": data_dict['nlos_high_400m'][229]
    # }
    # wave_height_data = pd.read_excel(os.path.join(os.path.dirname(os.path.abspath(__file__)), "swimming_pool_wave_height", "wave_height_data.xlsx"))
    #
    # plot_data_list(nlos_high_people_swimmming_list, "N-Los High 400m People Swimming", os.path.join(pic_base, "nlos_high_400m_people_swimming.png"))
    # plot_data_list_with_wave_height(
    #     {"220-1": data_dict['nlos_high_400m'][220][0], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][220][0][1][1].split()[1]+".000", data_dict['nlos_high_400m'][220][0][1][len(data_dict['nlos_high_400m'][220][0][1])-1].split()[1]+".000")},
    #     "N-Los High 400m People Swimming 220-1",
    #     data_dict['nlos_high_400m'][220][0][1][1] + ".000",
    #     os.path.join(pic_base, "nlos_high_400m_people_swimming_220-1.png"))
    # plot_data_list_with_wave_height(
    #     {"220-2": data_dict['nlos_high_400m'][220][1], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][220][1][1][1].split()[1]+".000", data_dict['nlos_high_400m'][220][1][1][len(data_dict['nlos_high_400m'][220][1][1])-1].split()[1]+".000")},
    #     "N-Los High 400m People Swimming 220-2",
    #     data_dict['nlos_high_400m'][220][1][1][1] + ".000",
    #     os.path.join(pic_base, "nlos_high_400m_people_swimming_220-2.png"))
    # plot_data_list_with_wave_height(
    #     {"225": data_dict['nlos_high_400m'][225], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][225][1][1].split()[1]+".000", data_dict['nlos_high_400m'][225][1][len(data_dict['nlos_high_400m'][225][1])-1].split()[1]+".000")},
    #     "N-Los High 400m People Swimming 225",
    #     data_dict['nlos_high_400m'][225][1][1] + ".000", os.path.join(pic_base, "nlos_high_400m_people_swimming_225.png"))
    # plot_data_list_with_wave_height(
    #     {"229": data_dict['nlos_high_400m'][229], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][229][1][1].split()[1]+".000", data_dict['nlos_high_400m'][229][1][len(data_dict['nlos_high_400m'][229][1])-1].split()[1]+".000")},
    #     "N-Los High 400m People Swimming 229",
    #     data_dict['nlos_high_400m'][229][1][1] + ".000", os.path.join(pic_base, "nlos_high_400m_people_swimming_229.png"))

    los_low_list = {
        140: {
            "No Wave": data_dict['los_low_no_wave'][140][:400],
            "Small wave": data_dict['los_low_little_wave'][140][:400],
            "Big Wave": data_dict['los_low_big_wave'][140][50:400]
        },
        120: {
            "No Wave": data_dict['los_low_no_wave'][120][:400],
            "Small wave": data_dict['los_low_little_wave'][120][:400],
            "Big Wave": data_dict['los_low_big_wave'][120][100:450]
        },
        160: {
            "No Wave": data_dict['los_low_no_wave'][160][:400],
            "Small wave": data_dict['los_low_little_wave'][160][:400],
            "Big Wave": data_dict['los_low_big_wave'][160][50:450]
        }
    }
    plot_data_list(los_low_list[140], "Los 140GHz", os.path.join(pic_base, "los_low_140.png"))
    plot_data_list(los_low_list[120], "Los 120GHz", os.path.join(pic_base, "los_low_120.png"))
    plot_data_list(los_low_list[160], "Los 160GHz", os.path.join(pic_base, "los_low_160.png"))

    nlos_low_list = {
        140: {
            "No Wave": data_dict['nlos_low_no_wave'][140][100:500],
            "Small wave": data_dict['nlos_low_little_wave'][140][100:450],
            "Big Wave": data_dict['nlos_low_big_wave'][140][100:450]
        },
        120: {
            "No Wave": data_dict['nlos_low_no_wave'][120][:400],
            "Small wave": data_dict['nlos_low_little_wave'][120][:400],
            "Big Wave": data_dict['nlos_low_big_wave'][120][100:450]
        },
        160: {
            "No Wave": data_dict['nlos_low_no_wave'][160][:400],
            "Small wave": data_dict['nlos_low_little_wave'][160][50:450],
            "Big Wave": data_dict['nlos_low_big_wave'][160][50:450]
        }
    }
    plot_data_list(nlos_low_list[140], "N-Los 140GHz", os.path.join(pic_base, "nlos_low_140.png"))
    plot_data_list(nlos_low_list[120], "N-Los 120GHz", os.path.join(pic_base, "nlos_low_120.png"))
    plot_data_list(nlos_low_list[160], "(a) N-Los 160GHz", os.path.join(pic_base, "nlos_low_160.png"))


