import pandas as pd
import numpy as np

data220_with_chuanglian_file = {
    "2024-10-09-21-32-59_一次反射第二次测量.xlsx": (),

    "2024-10-10-09-43-45_后侧门 二次反射.xlsx": 0,
    "2024-10-10-16-10-48_前门二次反射  重新测.xlsx": (-135, -135),

    "2024-10-09-20-02-40_有窗帘 一侧160度扫描.xlsx": (0, 0),
}


def shifting_angle(df, angle200_bias, angle300_bias):
    df['angle200'] = df['angle200'] + angle200_bias
    df['angle300'] = df['angle300'] + angle300_bias
    return df


def shift_and_merge(data, save_name=None):
    tmp_df = []
    for file_name, shift in data.items():
        df = pd.read_excel(file_name)
        tmp_df.append(shifting_angle(df, shift[0], shift[1]))
    merged_df = pd.concat(tmp_df)
    
    if save_name:
        merged_df.to_excel(save_name)

    return merged_df
