import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import json
from scipy.signal import find_peaks
from draw_meeting_room_2d import draw_meeting_room_with_angles

base_path = os.path.join(os.path.dirname(__file__), "meeting_room_data_2")
first_data_name = "2024-10-10-09-43-45_后侧门 二次反射.xlsx"
second_data_name = "2024-10-09-21-32-59_一次反射第二次测量.xlsx"
third_data_name = "2024-10-10-16-10-48_前门二次反射  重新测.xlsx"
fourth_data_name = "2024-10-09-20-02-40_有窗帘 一侧160度扫描.xlsx"
# fourth_data_name = "2024-10-10-15-26-50_无窗帘一侧的反射 160度.xlsx"


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


def shifting_angle(df, angle200_bias, angle300_bias, reverse=False):
    tmp = 1
    if reverse:
        tmp = -1
    df['angle200'] = df['angle200'] * tmp + angle200_bias
    df['angle300'] = df['angle300'] * tmp + angle300_bias
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

    plt.scatter(df.angle200 - 90, df.angle300 - 90, c=df.value, cmap='viridis', s=s_size)
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
    save_path_base = os.path.join(os.path.dirname(__file__), "meeting_room_pic_220_chuanglian")

    raw_first_data, raw_second_data, raw_third_data, raw_fourth_data = load_all_data()
    first_data = shifting_angle(filter_data(raw_first_data), 0, 90, reverse=True)
    second_data = shifting_angle(filter_data(raw_second_data), 15, 15)
    third_data = shifting_angle(filter_data(raw_third_data), 90, 0, reverse=True)
    fourth_data = shifting_angle(filter_data(raw_fourth_data), 90, 90)

    no_filter_first_data = shifting_angle(raw_first_data, 0, 90, reverse=True)
    no_filter_second_data = shifting_angle(raw_second_data, 15, 15)
    no_filter_third_data = shifting_angle(raw_third_data, 90, 0, reverse=True)
    no_filter_fourth_data = shifting_angle(raw_fourth_data, 90, 90)

    no_filter_new_data = concat_df(no_filter_first_data, no_filter_second_data, no_filter_third_data, no_filter_fourth_data)
    no_filter_new_data.to_excel(os.path.join(save_path_base, "meeting_room_data.xlsx"))

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
