import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import json
from scipy.signal import find_peaks
from draw_meeting_room_2d import draw_meeting_room_with_angles

base_path = os.path.join(os.path.dirname(__file__), "办公室全散射第三次补全", "data")
first_data_name = "2024-07-25-15-09-29_test.xlsx"
second_data_name = "2024-07-25-16-08-09_靠窗tx30度.xlsx"
third_data_name = "2024-07-25-18-09-07_第二次补充rx靠窗背后.xlsx"
fourth_data_name = "2024-07-25-19-12-30_第三次补充.xlsx"


def load_data(file_name):
    data = []
    file_path = os.path.join(base_path, file_name)
    df = pd.read_excel(file_path)
    # for i in range(len(df)):
    #     data.append()

    return df


def load_all_data():
    first_data = load_data(first_data_name)
    second_data = load_data(second_data_name)
    third_data = load_data(third_data_name)
    fourth_data = load_data(fourth_data_name)
    return first_data, second_data, third_data, fourth_data
    # return first_data


def shifting_angle(df, angle200_bias, angle300_bias):
    df['angle200'] = df['angle200'] + angle200_bias
    df['angle300'] = df['angle300'] + angle300_bias
    return df


def plot_data(data, title):
    plt.plot(data.time, data.value, label=title)
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title(title)
    plt.legend()
    plt.show()


def concat_df(*dfs):
    return pd.concat(dfs, ignore_index=True)


# 以df.angle200 df.angel300为横纵轴， df.value为值画出热力散点图，缺少的颜色用某个特殊的颜色表示
def plot_heatmap(df, title, s_size=1, save_path=None):
    plt.clf()
    # 颜色不明显，让图变大，颜色对比更强烈,换个好的颜色

    plt.scatter(df.angle200, df.angle300, c=df.value, cmap='viridis', s=s_size)
    plt.colorbar()
    plt.xlabel('Angle200')
    plt.ylabel('Angle300')
    plt.title(title)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def filter_data(df, value_min=-39):
    df = df.loc[df['value'] > value_min]
    df = df.reset_index(drop=True)
    return df


def find_peaks_in_group(group):
    angles = group['angle300'].values
    values = group['value'].values

    peaks, _ = find_peaks(values)

    peak_points = group.iloc[peaks]

    return peak_points


def keep_max_in_window(group):
    group['angle300_group'] = (group['angle300'] // 5) * 5
    max_points = group.loc[group.groupby('angle300_group')['value'].idxmax()]
    return max_points


def draw_angle_300_line(df, angle200, save_path=None):
    plt.clf()
    df = df.loc[df['angle200'] == angle200]
    plt.plot(df.angle300, df.value, label=f"angle200={angle200}")
    plt.xlabel('Angle300')
    plt.ylabel('Value')
    plt.title(f"Angle300 Line, angle200={angle200}")
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()


if __name__ == '__main__':
    save_path_base = os.path.join(os.path.dirname(__file__), "meeting_room_pic")

    first_data, second_data, third_data, fourth_data = load_all_data()
    first_data = shifting_angle(filter_data(first_data), 30, 30)
    second_data = shifting_angle(filter_data(second_data), 150, 30)
    third_data = shifting_angle(filter_data(third_data), 90, 90)
    fourth_data = shifting_angle(filter_data(fourth_data), 0, 0)

    new_data = concat_df(first_data, second_data, third_data, fourth_data)
    plot_heatmap(new_data, "All Data", save_path=os.path.join(save_path_base, "all_data.png"))

    new_data = new_data[((new_data['angle200'] < 85) | (new_data['angle200'] > 95)) &
                        ((new_data['angle300'] < 85) | (new_data['angle300'] > 95))]

    new_data = new_data.reset_index(drop=True)
    print(len(new_data))
    print(new_data)

    peak_points_list = []
    for angle200, group in new_data.groupby('angle200'):
        peak_points = find_peaks_in_group(group)
        peak_points_list.append(peak_points)
    peaks_df = pd.concat(peak_points_list).reset_index(drop=True)

    result_list = []
    for angle200, group in peaks_df.groupby('angle200'):
        max_points = keep_max_in_window(group)
        result_list.append(max_points)

    # 合并结果
    result = pd.concat(result_list).reset_index(drop=True)

    print(result)
    for i in range(len(result)):
        draw_meeting_room_with_angles(result.iloc[i]['angle200'], result.iloc[i]['angle300'],
                                      value=result.iloc[i]['value'], save_path=os.path.join(save_path_base, f"{i}.png"), tx_three=True, max_reflections=3, draw_rx_beam=False, check_rx_in_tx_beam=True)

    print(result)
