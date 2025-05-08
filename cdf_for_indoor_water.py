import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rice, rayleigh, weibull_min
import os
import pandas as pd
from indoor_water_height import get_indoor_data_after_cut

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "实验室水面实验", "时序")
# base_path = '/Users/liou/project/thz/water/实验室水面实验/时序'

def read_data(file_name):
    data = pd.read_excel(os.path.join(base_path, file_name), header=None)
    return data


def read_all_data():
    data_dict = {}
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".xlsx"):
                file_path = os.path.join(root, file)
                file_name = file.split(".")[0].split("_")[-1]
                file_degree = file_name.split("度")[0]
                file_freq = file_name.split("度")[1][:3]
                file_wave = file_name.split("度")[1][3:]
                if file_degree not in data_dict:
                    data_dict[file_degree] = {}
                if file_freq not in data_dict[file_degree]:
                    data_dict[file_degree][file_freq] = {}
                data = read_data(file_path)
                data_dict[file_degree][file_freq][file_wave] = data

    return data_dict


def cut_data(data_dict, start=0, length=None):
    data = data_dict
    if length is None:
        return data[4][start:].reset_index(drop=True)
    return data[4][start:start + length].reset_index(drop=True)


def cdf_rice(data_list, save_path=None, title=None, noice_level=None):
    # 设置全局字体为 Times New Roman
    plt.rcParams.update({
        'font.family': 'Times New Roman',
        'font.size': 12,  # 增大默认字体
        'mathtext.fontset': 'stix'
    })
    
    # 设置图片尺寸为正方形
    plt.rcParams['figure.figsize'] = [5, 3]  # 修改为正方形尺寸
    plt.rcParams['figure.dpi'] = 300
    
    data1, data2, data3 = data_list
    rmax1 = min(len(data1), len(data2), len(data3)) - 1

    Power11 = []
    Power12 = []
    Power13 = []
    data11_linear = []
    data12_linear = []
    data13_linear = []

    for ii in range(rmax1):
        Power11_val = (data1[ii + 1] + noice_level) / 2
        Power12_val = (data2[ii + 1] + noice_level) / 2
        Power13_val = (data3[ii + 1] + noice_level) / 2

        Power11.append(Power11_val)
        Power12.append(Power12_val)
        Power13.append(Power13_val)

        data11_linear.append(10 ** (Power11_val / 10))
        data12_linear.append(10 ** (Power12_val / 10))
        data13_linear.append(10 ** (Power13_val / 10))

    power11 = np.array(data11_linear)
    power12 = np.array(data12_linear)
    power13 = np.array(data13_linear)

    x_values1 = np.linspace(min(power11), max(power11), 200)
    rice_params1 = rice.fit(power11, floc=0)
    shape_param1, _, _ = rice_params1
    k_factor1 = (shape_param1 ** 2) / 2
    cdf_rician1 = rice.cdf(x_values1, *rice_params1)
    cdf_rayleigh1 = rayleigh.cdf(x_values1, *rayleigh.fit(power11))
    cdf_weibull1 = weibull_min.cdf(x_values1, *weibull_min.fit(power11))

    x_values2 = np.linspace(min(power12), max(power12), 200)
    rice_params2 = rice.fit(power12, floc=0)
    shape_param2, _, _ = rice_params2
    k_factor2 = (shape_param2 ** 2) / 2
    cdf_rician2 = rice.cdf(x_values2, *rice_params2)
    cdf_rayleigh2 = rayleigh.cdf(x_values2, *rayleigh.fit(power12))
    cdf_weibull2 = weibull_min.cdf(x_values2, *weibull_min.fit(power12))

    x_values3 = np.linspace(min(power13), max(power13), 200)
    rice_params3 = rice.fit(power13, floc=0)
    shape_param3, _, _ = rice_params3
    k_factor3 = (shape_param3 ** 2) / 2
    cdf_rician3 = rice.cdf(x_values3, *rice_params3)
    cdf_rayleigh3 = rayleigh.cdf(x_values3, *rayleigh.fit(power13))
    cdf_weibull3 = weibull_min.cdf(x_values3, *weibull_min.fit(power13))

    # Plotting the empirical and fitted CDFs
    plt.figure()
    plt.grid(False)

    counts11, bins11 = np.histogram(power11, bins=200, density=True)
    counts12, bins12 = np.histogram(power12, bins=200, density=True)
    counts13, bins13 = np.histogram(power13, bins=200, density=True)

    # 计算累积分布
    cdf11 = np.cumsum(counts11) / np.sum(counts11)
    cdf12 = np.cumsum(counts12) / np.sum(counts12)
    cdf13 = np.cumsum(counts13) / np.sum(counts13)

    # 计算 bin 的中心点
    bin_centers11 = (bins11[:-1] + bins11[1:]) / 2
    bin_centers12 = (bins12[:-1] + bins12[1:]) / 2
    bin_centers13 = (bins13[:-1] + bins13[1:]) / 2

    # 绘制散点图，使用更小的点和统一的实线
    plt.scatter(bin_centers11, cdf11, color='#1f77b4', s=0.5, label='No Wave (Measured)')
    plt.scatter(bin_centers12, cdf12, color='#ff7f0e', s=0.5, label='Small Wave (Measured)')
    plt.scatter(bin_centers13, cdf13, color='#2ca02c', s=0.5, label='Big Wave (Measured)')

    # 绘制拟合曲线，使用实线
    plt.plot(x_values1, cdf_weibull1, color='#1f77b4', linewidth=1, label='No Wave (Weibull)')
    plt.plot(x_values2, cdf_weibull2, color='#ff7f0e', linewidth=1, label='Small Wave (Weibull)')
    plt.plot(x_values3, cdf_weibull3, color='#2ca02c', linewidth=1, label='Big Wave (Weibull)')

    # 设置轴标签和标题，使用更大的字体
    plt.xlabel('SNR', fontsize=12, labelpad=8)
    plt.ylabel('CDF', fontsize=12, labelpad=8)
    
    # if title is not None:
    #     plt.title(title, pad=10, fontsize=14, fontweight='bold')
    
    # 设置刻度，增大字体
    plt.tick_params(axis='both', direction='in', labelsize=11)
    
    # 去除四周边框
    ax = plt.gca()
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    # 图例放到图片外部右侧
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(
        handles, labels,
        loc='center left',
        bbox_to_anchor=(1.01, 0.5),
        frameon=False,
        fontsize=10,
        ncol=1
    )

    plt.tight_layout()  # 右侧留出空间给图例
    
    # 保存图片时保持正方形比例
    if save_path:
        plt.savefig(save_path, 
                   bbox_inches='tight',
                   pad_inches=0.1,
                   dpi=300)
    
    plt.show()


def cdf_for_indoor_water():
    save_path_base = os.path.join(os.path.dirname(__file__), 'indoor_water_cdf_pic')
    data_dict = read_all_data()

    for degree in data_dict:
        for freq in data_dict[degree]:
            data_list = [None, None, None]
            for wave in data_dict[degree][freq]:
                if wave == '小浪':
                    idx = 1
                elif wave == '大浪':
                    idx = 2
                else:
                    idx = 0
                data_list[idx] = data_dict[degree][freq][wave]

            cdf_rice([cut_data(x) for x in data_list],
                     save_path=os.path.join(save_path_base, f'_{degree}度_{freq}GHz_{wave}.png'),
                     title=f'{degree}Degree, {freq}GHz', noice_level=39)


def cdf_for_indoor_water_with_cut_data():
    cut_data_base_path = os.path.join(os.path.dirname(__file__), 'indoor_water_after_cut_data')
    save_path_base = os.path.join(os.path.dirname(__file__), 'indoor_water_cdf_pic_after_cut')
    
    # 确保输出目录存在
    os.makedirs(cut_data_base_path, exist_ok=True)
    os.makedirs(save_path_base, exist_ok=True)
    
    data_30, data_45 = get_indoor_data_after_cut()

    all_data = {
        '30': data_30,
        '45': data_45
    }
    
    for degree, degree_list in all_data.items():
        for freq, freq_data in degree_list.items():
            data_list = []
            # 确保按照固定顺序处理数据
            wave_types = ['No Wave', 'Small Wave', 'Big Wave']
            for wave_type in wave_types:
                if wave_type in freq_data:
                    wave_data = freq_data[wave_type]
                    if wave_data is not None:
                        # 保存切分后的数据
                        save_path = os.path.join(cut_data_base_path, f'_{degree}度_{freq}GHz_{wave_type}.xlsx')
                        wave_data.to_excel(save_path)
                        data_list.append(wave_data)
                    else:
                        print(f"Warning: No data for {degree}度 {freq}GHz {wave_type}")
                else:
                    print(f"Warning: Missing {wave_type} data for {degree}度 {freq}GHz")
            
            # 只在有足够数据时绘图
            if len(data_list) == 3:
                if degree == '30' and freq == 160:
                    prefix = '(a) '
                elif degree == '30' and freq == 221:
                    prefix = '(b) '
                elif degree == '30' and freq == 320:
                    prefix = '(c) '
                elif degree == '45' and freq == 160:
                    prefix = '(d) '
                elif degree == '45' and freq == 221:
                    prefix = '(e) '
                elif degree == '45' and freq == 320:
                    prefix = '(f) '
                else:
                    prefix = ''
                cdf_rice(
                    [cut_data(x) for x in data_list],
                    save_path=os.path.join(save_path_base, f'_{degree}度_{freq}GHz.png'),
                    title=f'{prefix}{freq}GHz-{degree}°',
                    noice_level=39 if degree == '30' else 41
                )
            else:
                print(f"Skipping plot for {degree}度 {freq}GHz due to insufficient data")


if __name__ == '__main__':
    cdf_for_indoor_water_with_cut_data()
