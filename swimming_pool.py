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
    cut_data_base_path = os.path.join(os.path.dirname(__file__), 'swimming_pool_after_cut_data')
    plt.rcParams['figure.figsize'] = [12, 4]
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    for k, data in data_list.items():
        data.to_excel(os.path.join(cut_data_base_path, title + str(k) + ".xlsx"))
        if "Time" in data:
            ax2.plot(data["Time"][1:], data["Value"][1:], label=k)
        else:
            # 创建一个从0开始的新索引序列
            x_values = np.arange(len(data[4][1:]))
            ax1.plot(x_values, data[4][1:], label=k)
    plt.title(title)
    ax1.set_xlabel('Time Index')
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_ylabel('Amplitude (dbm)')
    ax2.set_ylabel('WaveHeight(mm)')
    ax1.legend()
    if save_path:
        plt.savefig(save_path)
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


if __name__ == '__main__':
    pic_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swimming_pool_pic')
    data_dict = read_all_data()
    print(data_dict.keys())
    los_high_list = {
        220: {
            "No Wave":data_dict['los_high_no_wave'][220][:400],
            "Little Wave": data_dict['los_high_little_wave'][220][:400],
            "Big Wave": data_dict['los_high_big_wave'][220][:400]
        },
        225: {
            "No Wave": data_dict['los_high_no_wave'][225][:400],
            "Little Wave": data_dict['los_high_little_wave'][225][:400],
            "Big Wave": data_dict['los_high_big_wave'][225][:400]
        },
        229: {
            "No Wave": data_dict['los_high_no_wave'][229][:400],
            "Little Wave": data_dict['los_high_little_wave'][229][:400],
            "Big Wave": data_dict['los_high_big_wave'][229][:400]
        }
    }
    plot_data_list(los_high_list[220], "LOS High 220GHz", os.path.join(pic_base, "los_high_220.png"))
    plot_data_list(los_high_list[225], "LOS High 225GHz", os.path.join(pic_base, "los_high_225.png"))
    plot_data_list(los_high_list[229], "LOS High 229GHz", os.path.join(pic_base, "los_high_229.png"))

    nlos_high_list = {
        220: {
            "No Wave": data_dict['nlos_high_no_wave'][220][:400],
            "Little Wave": data_dict['nlos_high_little_wave'][220][100:],
            "Big Wave": data_dict['nlos_high_big_wave'][220][100:]
        },
        225: {
            "No Wave": data_dict['nlos_high_no_wave'][225][:400],
            "Little Wave": data_dict['nlos_high_little_wave'][225][0:400],
            "Big Wave": data_dict['nlos_high_big_wave'][225][220:600]
        },
        229: {
            "No Wave": data_dict['nlos_high_no_wave'][229][:400],
            "Little Wave": data_dict['nlos_high_little_wave'][229][0:400],
            "Big Wave": data_dict['nlos_high_big_wave'][229][150:550]
        }
    }
    plot_data_list(nlos_high_list[220], "NLOS High 220GHz", os.path.join(pic_base, "nlos_high_220.png"))
    plot_data_list(nlos_high_list[225], "NLOS High 225GHz", os.path.join(pic_base, "nlos_high_225.png"))
    plot_data_list(nlos_high_list[229], "NLOS High 229GHz", os.path.join(pic_base, "nlos_high_229.png"))
    #
    # # nlos_high_400m_list = {
    # #     220: {
    # #         "No Wave": data_dict['nlos_high_400m'][220][0],
    # #         "Little Wave": data_dict['nlos_high_400m'][220][1]
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
    # plot_data_list(nlos_high_people_swimmming_list, "NLOS High 400m People Swimming", os.path.join(pic_base, "nlos_high_400m_people_swimming.png"))
    # plot_data_list_with_wave_height(
    #     {"220-1": data_dict['nlos_high_400m'][220][0], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][220][0][1][1].split()[1]+".000", data_dict['nlos_high_400m'][220][0][1][len(data_dict['nlos_high_400m'][220][0][1])-1].split()[1]+".000")},
    #     "NLOS High 400m People Swimming 220-1",
    #     data_dict['nlos_high_400m'][220][0][1][1] + ".000",
    #     os.path.join(pic_base, "nlos_high_400m_people_swimming_220-1.png"))
    # plot_data_list_with_wave_height(
    #     {"220-2": data_dict['nlos_high_400m'][220][1], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][220][1][1][1].split()[1]+".000", data_dict['nlos_high_400m'][220][1][1][len(data_dict['nlos_high_400m'][220][1][1])-1].split()[1]+".000")},
    #     "NLOS High 400m People Swimming 220-2",
    #     data_dict['nlos_high_400m'][220][1][1][1] + ".000",
    #     os.path.join(pic_base, "nlos_high_400m_people_swimming_220-2.png"))
    # plot_data_list_with_wave_height(
    #     {"225": data_dict['nlos_high_400m'][225], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][225][1][1].split()[1]+".000", data_dict['nlos_high_400m'][225][1][len(data_dict['nlos_high_400m'][225][1])-1].split()[1]+".000")},
    #     "NLOS High 400m People Swimming 225",
    #     data_dict['nlos_high_400m'][225][1][1] + ".000", os.path.join(pic_base, "nlos_high_400m_people_swimming_225.png"))
    # plot_data_list_with_wave_height(
    #     {"229": data_dict['nlos_high_400m'][229], "wave_height": filter_by_time_range(wave_height_data, data_dict['nlos_high_400m'][229][1][1].split()[1]+".000", data_dict['nlos_high_400m'][229][1][len(data_dict['nlos_high_400m'][229][1])-1].split()[1]+".000")},
    #     "NLOS High 400m People Swimming 229",
    #     data_dict['nlos_high_400m'][229][1][1] + ".000", os.path.join(pic_base, "nlos_high_400m_people_swimming_229.png"))

    los_low_list = {
        140: {
            "No Wave": data_dict['los_low_no_wave'][140][:400],
            "Little Wave": data_dict['los_low_little_wave'][140][:400],
            "Big Wave": data_dict['los_low_big_wave'][140][50:400]
        },
        120: {
            "No Wave": data_dict['los_low_no_wave'][120][:400],
            "Little Wave": data_dict['los_low_little_wave'][120][:400],
            "Big Wave": data_dict['los_low_big_wave'][120][100:450]
        },
        160: {
            "No Wave": data_dict['los_low_no_wave'][160][:400],
            "Little Wave": data_dict['los_low_little_wave'][160][:400],
            "Big Wave": data_dict['los_low_big_wave'][160][50:450]
        }
    }
    plot_data_list(los_low_list[140], "LOS Low 140GHz", os.path.join(pic_base, "los_low_140.png"))
    plot_data_list(los_low_list[120], "LOS Low 120GHz", os.path.join(pic_base, "los_low_120.png"))
    plot_data_list(los_low_list[160], "LOS Low 160GHz", os.path.join(pic_base, "los_low_160.png"))

    nlos_low_list = {
        140: {
            "No Wave": data_dict['nlos_low_no_wave'][140][100:500],
            "Little Wave": data_dict['nlos_low_little_wave'][140][100:450],
            "Big Wave": data_dict['nlos_low_big_wave'][140][100:450]
        },
        120: {
            "No Wave": data_dict['nlos_low_no_wave'][120][:400],
            "Little Wave": data_dict['nlos_low_little_wave'][120][:400],
            "Big Wave": data_dict['nlos_low_big_wave'][120][100:450]
        },
        160: {
            "No Wave": data_dict['nlos_low_no_wave'][160][:400],
            "Little Wave": data_dict['nlos_low_little_wave'][160][50:450],
            "Big Wave": data_dict['nlos_low_big_wave'][160][50:450]
        }
    }
    plot_data_list(nlos_low_list[140], "NLOS Low 140GHz", os.path.join(pic_base, "nlos_low_140.png"))
    plot_data_list(nlos_low_list[120], "NLOS Low 120GHz", os.path.join(pic_base, "nlos_low_120.png"))
    plot_data_list(nlos_low_list[160], "NLOS Low 160GHz", os.path.join(pic_base, "nlos_low_160.png"))


