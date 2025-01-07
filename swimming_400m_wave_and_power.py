import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

base_dir = "/Users/liou/project/thz/water/LiangXiangExperiment-2024-MeetingRoomAndSwimmingPool/swimming_pool_wave_height"
wave_height_data_files = [
    "2024-07-26 14.27.22 label0(2407501)_1.xlsx",
    "2024-07-26 14.27.22 label0(2407501)_2.xlsx",
    "2024-07-26 14.27.22 label0(2407501)_3.xlsx",
    "2024-07-26 15.05.33 label0(2407501).xlsx"
]


def read_wave_height_data(files):
    wave_height_data = []
    beggning_time = []
    for file in files:
        # 提取开始时间 (hh.mm.ss)
        beggning_time.append(file.split(" ")[1])
        df = pd.read_excel(os.path.join(base_dir, file), header=None)
        # 删除前7行数据
        df = df.drop(df.index[0:7])
        tmp_time, tmp_value = df[1], df[2]

        # 确保 tmp_time 是字符串类型
        tmp_time = tmp_time.astype(str)

        # 将时间拆分为小时、分钟、秒、毫秒
        tmp_split_time = tmp_time.str.split(".", expand=True)
        # tmp_h = tmp_split_time[0].astype(int)
        # tmp_m = tmp_split_time[1].astype(int)
        tmp_s = tmp_split_time[0].astype(int)
        tmp_ms = tmp_split_time[1].fillna("000")  # 毫秒部分，如果缺失填充默认值
        # tmp_ms = tmp_ms.apply(lambda x: f"{float(x):.3f}")

        # 获取初始时间
        old_h, old_m, old_s = map(int, beggning_time[-1].split("."))

        # 矢量化处理秒进位、分钟进位和小时进位
        new_s = (old_s + tmp_s) % 60
        carry_m = (old_s + tmp_s) // 60

        new_m = (old_m + carry_m) % 60
        carry_h = (old_m + carry_m) // 60

        new_h = old_h + carry_h

        # 合成新的时间列
        tmp_time = (
                new_h.astype(str).str.zfill(2) + "." +
                new_m.astype(str).str.zfill(2) + "." +
                new_s.astype(str).str.zfill(2) + "." +
                tmp_ms
        )

        new_df = pd.DataFrame({"Time": tmp_time, "Value": tmp_value})
        wave_height_data.append(new_df)

    # 合并所有文件数据
    df = pd.concat(wave_height_data).reset_index(drop=True)

    return df


def fix_time_format(time_str):
    parts = time_str.split(".")
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


def plot_wave_height_data(df):
    plt.plot(df["Time"], df["Value"], marker="o")
    plt.xlabel("Time")
    plt.ylabel("Wave Height (m)")
    plt.title("Wave Height Data")
    plt.show()


if __name__ == "__main__":
    start_time = "14:58:00.000"
    end_time = "15:08:00.000"
    df = read_wave_height_data(wave_height_data_files)
    df = filter_by_time_range(df, start_time, end_time)
    df.to_excel(os.path.join(base_dir, "wave_height_data.xlsx"), index=False)
    plot_wave_height_data(df)
